import { Link } from "react-router-dom";
import { ChevronRight, Clock } from "lucide-react";
import { OddsButton } from "./OddsButton";
import type { MarketType, MatchListItem } from "../../types/api";

export function MatchCard({
  match,
  market,
}: {
  match: MatchListItem;
  market: MarketType;
}) {
  const kickoff = new Date(`${match.kickoff_at}Z`).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Africa/Kampala",
  });

  return (
    <div className="border-t border-white/5 px-3 py-3 first:border-t-0">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span className="truncate">{match.home_team}</span>
            <span className="text-muted">vs</span>
            <span className="truncate">{match.away_team}</span>
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-muted">
            <span className="inline-flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {kickoff}
            </span>
            <span className="rounded bg-white/5 px-1.5 py-0.5 uppercase">
              {match.status}
            </span>
            {match.status === "finished" && match.home_score != null && (
              <span className="font-semibold text-white">
                Final {match.home_score} - {match.away_score}
              </span>
            )}
            {match.is_demo && (
              <span className="text-amber-400/90">DEMO</span>
            )}
          </div>
        </div>
        <Link
          to={`/matches/${match.id}`}
          className="inline-flex items-center gap-1 text-xs text-electric hover:underline"
        >
          Analytics
          <ChevronRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="flex flex-wrap gap-2">
        {match.odds.map((o) => (
          <OddsButton
            key={o.key}
            matchId={match.id}
            market={market}
            homeTeam={match.home_team}
            awayTeam={match.away_team}
            outcomeKey={o.key}
            label={o.label}
            odds={o.odds}
          />
        ))}
      </div>
    </div>
  );
}
