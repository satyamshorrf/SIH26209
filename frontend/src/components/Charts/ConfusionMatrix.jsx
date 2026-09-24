/**
 * Renders a 2x2 (or NxN) confusion matrix as a coloured grid.
 * matrix: number[][], labels: string[]
 */
export default function ConfusionMatrix({ matrix, labels = ["No-Ice", "Ice"] }) {
  if (!matrix || matrix.length === 0) {
    return <p className="text-sm text-slate-400">No confusion matrix available.</p>;
  }
  const max = Math.max(...matrix.flat(), 1);

  const cellColor = (v) => {
    const intensity = v / max;
    return `rgba(79,140,255,${0.15 + intensity * 0.7})`;
  };

  return (
    <div className="inline-block">
      <div className="flex">
        <div className="w-20" />
        {labels.map((l) => (
          <div key={l} className="w-20 pb-1 text-center text-xs font-medium text-slate-300">
            Pred {l}
          </div>
        ))}
      </div>
      {matrix.map((row, i) => (
        <div key={i} className="flex items-center">
          <div className="w-20 pr-2 text-right text-xs font-medium text-slate-300">
            True {labels[i]}
          </div>
          {row.map((value, j) => (
            <div
              key={j}
              className="m-0.5 flex h-16 w-20 items-center justify-center rounded-lg text-lg font-bold text-white"
              style={{ background: cellColor(value) }}
            >
              {value}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
