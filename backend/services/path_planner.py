"""Rover path planning with A* and Dijkstra over a hazard-weighted grid.

The candidate points are rasterised onto a regular grid; each cell receives a
traversal cost combining hazard score, slope and an illumination (solar) penalty.
Both A* (with a Euclidean heuristic) and Dijkstra (via NetworkX) are provided so
the route can be compared between an informed and an uninformed search.
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from . import terrain as terrain_mod


def _normalise(arr: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def build_cost_grid(df: pd.DataFrame, grid_size: int = 40) -> Dict[str, object]:
    """Rasterise the dataset to a ``grid_size`` x ``grid_size`` cost grid.

    Returns a dict with the cost grid, the lat/lon edges and an obstacle mask.
    """
    terrain = terrain_mod.terrain_features(df)
    lat = terrain.get("Latitude")
    lon = terrain.get("Longitude")
    if lat is None or lon is None:
        raise ValueError("Path planning requires Latitude/Longitude columns.")
    lat = lat.to_numpy()
    lon = lon.to_numpy()

    slope = _normalise(terrain["Slope"].to_numpy())
    rough = terrain["Roughness"].to_numpy()
    boulder = terrain["BoulderDensity"].to_numpy()
    illum = terrain["Illumination"].to_numpy()

    # Hazard cost: terrain difficulty plus a solar constraint (dark = costly).
    hazard = 0.4 * slope + 0.25 * rough + 0.2 * boulder + 0.15 * (1.0 - illum)

    lat_edges = np.linspace(lat.min(), lat.max(), grid_size + 1)
    lon_edges = np.linspace(lon.min(), lon.max(), grid_size + 1)

    cost = np.full((grid_size, grid_size), np.nan)
    count = np.zeros((grid_size, grid_size))

    row_idx = np.clip(np.digitize(lat, lat_edges) - 1, 0, grid_size - 1)
    col_idx = np.clip(np.digitize(lon, lon_edges) - 1, 0, grid_size - 1)
    for r, c, h in zip(row_idx, col_idx, hazard):
        if np.isnan(cost[r, c]):
            cost[r, c] = 0.0
        cost[r, c] += h
        count[r, c] += 1

    # Average where multiple points share a cell; fill empty cells with the mean.
    with np.errstate(invalid="ignore"):
        cost = np.where(count > 0, cost / np.maximum(count, 1), np.nan)
    mean_cost = float(np.nanmean(cost)) if np.any(~np.isnan(cost)) else 1.0
    cost = np.where(np.isnan(cost), mean_cost, cost)
    cost = _normalise(cost) + 0.05  # keep strictly positive

    # Cells in the top 8% of cost are treated as impassable obstacles.
    obstacle = cost >= np.percentile(cost, 92)

    return {
        "cost": cost,
        "obstacle": obstacle,
        "lat_edges": lat_edges,
        "lon_edges": lon_edges,
        "grid_size": grid_size,
    }


def _neighbours(node: Tuple[int, int], n: int):
    r, c = node
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                step = 1.4142 if (dr != 0 and dc != 0) else 1.0
                yield (nr, nc), step


def astar(cost: np.ndarray, obstacle: np.ndarray,
          start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """A* search returning the lowest-cost passable path (or ``None``)."""
    n = cost.shape[0]

    def heuristic(a, b):
        return float(np.hypot(a[0] - b[0], a[1] - b[1]))

    open_heap = [(0.0, start)]
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    g_score = {start: 0.0}
    visited = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            return _reconstruct(came_from, current)
        if current in visited:
            continue
        visited.add(current)
        for neigh, step in _neighbours(current, n):
            if obstacle[neigh] and neigh != goal:
                continue
            tentative = g_score[current] + step * float(cost[neigh])
            if tentative < g_score.get(neigh, float("inf")):
                came_from[neigh] = current
                g_score[neigh] = tentative
                f = tentative + heuristic(neigh, goal)
                heapq.heappush(open_heap, (f, neigh))
    return None


def dijkstra(cost: np.ndarray, obstacle: np.ndarray,
             start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """Dijkstra shortest path via NetworkX over the grid graph."""
    import networkx as nx

    n = cost.shape[0]
    graph = nx.Graph()
    for r in range(n):
        for c in range(n):
            if obstacle[r, c] and (r, c) not in (start, goal):
                continue
            for (nr, nc), step in _neighbours((r, c), n):
                if obstacle[nr, nc] and (nr, nc) not in (start, goal):
                    continue
                weight = step * 0.5 * (float(cost[r, c]) + float(cost[nr, nc]))
                graph.add_edge((r, c), (nr, nc), weight=weight)
    try:
        return nx.dijkstra_path(graph, start, goal, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def _reconstruct(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def _grid_to_coord(node, grid):
    r, c = node
    lat = 0.5 * (grid["lat_edges"][r] + grid["lat_edges"][r + 1])
    lon = 0.5 * (grid["lon_edges"][c] + grid["lon_edges"][c + 1])
    return float(lat), float(lon)


def plan_route(df: pd.DataFrame, algorithm: str = "astar",
               grid_size: int = 40) -> Dict[str, object]:
    """Plan a rover route from the safest cell to the highest-ice/target cell.

    Start = lowest-cost (safest) cell, Goal = highest-cost reachable region edge,
    approximating a traverse from a safe landing zone toward a hazardous,
    ice-bearing crater.  Returns route coordinates, distance and travel time.
    """
    grid = build_cost_grid(df, grid_size=grid_size)
    cost = grid["cost"]
    obstacle = grid["obstacle"]
    n = grid["grid_size"]

    # Start: globally cheapest non-obstacle cell.
    masked = np.where(obstacle, np.inf, cost)
    start = tuple(np.unravel_index(np.argmin(masked), masked.shape))
    # Goal: the cell furthest from start among low-cost cells (long traverse).
    rr, cc = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    dist_from_start = np.hypot(rr - start[0], cc - start[1])
    goal_score = np.where(obstacle, -np.inf, dist_from_start - cost * 5)
    goal = tuple(np.unravel_index(np.argmax(goal_score), goal_score.shape))

    if algorithm.lower() == "dijkstra":
        path = dijkstra(cost, obstacle, start, goal)
        algo_name = "Dijkstra (uniform-cost search)"
    else:
        path = astar(cost, obstacle, start, goal)
        algo_name = "A* (Euclidean heuristic)"

    if not path:
        # Fall back to a direct interpolation if no path exists.
        path = [start, goal]

    coords = [_grid_to_coord(node, grid) for node in path]

    # Distance in km using lunar polar geometry: 1 deg latitude ~= 30.3 km, and
    # longitude degrees converge toward the pole by cos(latitude).
    km_per_deg = 30.3
    distance_km = 0.0
    for (la1, lo1), (la2, lo2) in zip(coords[:-1], coords[1:]):
        mean_lat_rad = np.radians((la1 + la2) / 2.0)
        d_lat = (la2 - la1) * km_per_deg
        d_lon = (lo2 - lo1) * km_per_deg * np.cos(mean_lat_rad)
        distance_km += float(np.hypot(d_lat, d_lon))
    total_cost = float(sum(cost[node] for node in path))
    # Assume a nominal rover speed of 0.09 km/h (Pragyan-class).
    travel_time_h = distance_km / 0.09 if distance_km > 0 else 0.0

    return {
        "algorithm": algo_name,
        "grid_size": n,
        "start": {"lat": coords[0][0], "lon": coords[0][1]},
        "goal": {"lat": coords[-1][0], "lon": coords[-1][1]},
        "waypoints": [
            {"step": i + 1, "lat": la, "lon": lo}
            for i, (la, lo) in enumerate(coords)
        ],
        "num_waypoints": len(coords),
        "distance_km": round(distance_km, 3),
        "path_cost": round(total_cost, 3),
        "travel_time_hours": round(travel_time_h, 2),
        "_grid": grid,
        "_path_nodes": path,
    }
