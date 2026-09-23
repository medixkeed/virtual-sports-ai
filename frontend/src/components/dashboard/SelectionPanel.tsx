import { Trash2 } from "lucide-react";
import { useSelections } from "../../contexts/SelectionContext";

export function SelectionPanel() {
  const { selections, clearSelections } = useSelections();

  if (selections.length === 0) {
    return (
      <div className="card-surface p-4 text-sm text-muted">
        Tap odds to track selections for analytics (not real-money betting).
      </div>
    );
  }

  return (
    <div className="card-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">
          Your selections ({selections.length})
        </h3>
        <button
          type="button"
          onClick={clearSelections}
          className="inline-flex items-center gap-1 text-xs text-red-300 hover:text-red-200"
        >
          <Trash2 className="h-3.5 w-3.5" />
          Clear all
        </button>
      </div>
      <ul className="space-y-2 text-xs">
        {selections.map((s) => (
          <li
            key={`${s.matchId}-${s.outcomeKey}`}
            className="flex justify-between gap-2 rounded-lg bg-navy-light/80 px-2 py-2"
          >
            <span className="truncate">
              {s.homeTeam} vs {s.awayTeam} — {s.label} @ {s.odds.toFixed(2)}
            </span>
            <span className="shrink-0 text-muted">{s.market}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
