// Lightweight, dependency-free table for previewing dataset / result rows.
export default function DataTable({ rows, maxRows = 10 }) {
  if (!rows || rows.length === 0) {
    return <p className="text-sm text-slate-400">No rows to display.</p>;
  }
  const columns = Object.keys(rows[0]);
  const shown = rows.slice(0, maxRows);

  const renderCell = (value) => {
    if (value === null || value === undefined) return "—";
    if (typeof value === "number") return Number(value.toFixed(4)).toString();
    if (typeof value === "boolean") return value ? "true" : "false";
    return String(value);
  };

  return (
    <div className="max-h-80 overflow-auto rounded-xl border border-slate-700/40">
      <table className="min-w-full text-left text-xs">
        <thead className="sticky top-0 bg-space-700/90 text-slate-300">
          <tr>
            {columns.map((col) => (
              <th key={col} className="whitespace-nowrap px-3 py-2 font-semibold">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700/40">
          {shown.map((row, i) => (
            <tr key={i} className="hover:bg-slate-700/20">
              {columns.map((col) => (
                <td key={col} className="whitespace-nowrap px-3 py-1.5 text-slate-300">
                  {renderCell(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
