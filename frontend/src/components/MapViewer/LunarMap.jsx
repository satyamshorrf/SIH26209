import { useEffect, useRef } from "react";
import L from "leaflet";

/**
 * Custom lunar point/route viewer built on Leaflet using a simple Cartesian CRS
 * (CRS.Simple) so it handles the south-polar coordinate ranges directly.
 *
 * Props:
 *   points: [{ lat, lon, value }]   - coloured scatter (value 0-1)
 *   path:   [{ lat, lon }]          - optional route polyline
 */
export default function LunarMap({ points = [], path = [], height = 360 }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const layerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    mapRef.current = L.map(containerRef.current, {
      crs: L.CRS.Simple,
      minZoom: -5,
      maxZoom: 5,
      attributionControl: false,
      zoomControl: true,
    });
    layerRef.current = L.layerGroup().addTo(mapRef.current);
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;
    layer.clearLayers();

    const all = [...points, ...path];
    if (all.length === 0) return;

    // Leaflet CRS.Simple uses [y, x]; map lon -> x, lat -> y.
    const colorFor = (v) => {
      const t = Math.max(0, Math.min(1, v ?? 0));
      const r = Math.round(255 * t);
      const b = Math.round(255 * (1 - t));
      return `rgb(${r},120,${b})`;
    };

    points.forEach((p) => {
      L.circleMarker([p.lat, p.lon], {
        radius: 3,
        color: colorFor(p.value),
        weight: 0,
        fillOpacity: 0.75,
        fillColor: colorFor(p.value),
      })
        .bindTooltip(
          `Lat ${p.lat.toFixed(3)}, Lon ${p.lon.toFixed(3)}` +
            (p.value !== undefined ? ` · ${(p.value * 100).toFixed(0)}%` : ""),
          { direction: "top" }
        )
        .addTo(layer);
    });

    if (path.length > 1) {
      const latlngs = path.map((p) => [p.lat, p.lon]);
      L.polyline(latlngs, { color: "#f97316", weight: 3 }).addTo(layer);
      L.circleMarker(latlngs[0], {
        radius: 6,
        color: "#22c55e",
        fillColor: "#22c55e",
        fillOpacity: 1,
      })
        .bindTooltip("Start", { permanent: false })
        .addTo(layer);
      L.circleMarker(latlngs[latlngs.length - 1], {
        radius: 6,
        color: "#ef4444",
        fillColor: "#ef4444",
        fillOpacity: 1,
      })
        .bindTooltip("Target", { permanent: false })
        .addTo(layer);
    }

    const lats = all.map((p) => p.lat);
    const lons = all.map((p) => p.lon);
    const bounds = [
      [Math.min(...lats), Math.min(...lons)],
      [Math.max(...lats), Math.max(...lons)],
    ];
    map.fitBounds(bounds, { padding: [20, 20] });
  }, [points, path]);

  return (
    <div
      ref={containerRef}
      style={{ height }}
      className="overflow-hidden rounded-xl border border-slate-700/40"
    />
  );
}
