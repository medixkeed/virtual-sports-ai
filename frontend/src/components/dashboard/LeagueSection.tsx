import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { MatchCard } from "./MatchCard";
import type { MarketType, MatchListItem } from "../../types/api";

export function LeagueSection({
  leagueName,
  matches,
  market,
  defaultOpen = true,
}: {
  leagueName: string;
  matches: MatchListItem[];
  market: MarketType;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  if (matches.length === 0) return null;

  return (
    <section className="card-surface overflow-hidden">
      <button
        type="button"
        className="league-header w-full text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <span>
          {leagueName}{" "}
          <span className="ml-2 rounded-full bg-black/20 px-2 py-0.5 text-xs">
            {matches.length}
          </span>
        </span>
        {open ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </button>
      {open && (
        <div>
          {matches.map((m) => (
            <MatchCard key={m.id} match={m} market={market} />
          ))}
        </div>
      )}
    </section>
  );
}
