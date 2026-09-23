import { useSelections } from "../../contexts/SelectionContext";
import type { MarketType } from "../../types/api";

export function OddsButton({
  matchId,
  market,
  homeTeam,
  awayTeam,
  outcomeKey,
  label,
  odds,
}: {
  matchId: number;
  market: MarketType;
  homeTeam: string;
  awayTeam: string;
  outcomeKey: string;
  label: string;
  odds: number;
}) {
  const { toggleSelection, isSelected } = useSelections();
  const selected = isSelected(matchId, outcomeKey);

  return (
    <button
      type="button"
      className={`odds-btn ${selected ? "odds-btn-selected" : ""}`}
      onClick={() =>
        toggleSelection({
          matchId,
          market,
          outcomeKey,
          label,
          odds,
          homeTeam,
          awayTeam,
        })
      }
    >
      <span className="text-[10px] text-muted">{label}</span>
      <span className="text-sm font-bold text-white">{odds.toFixed(2)}</span>
    </button>
  );
}
