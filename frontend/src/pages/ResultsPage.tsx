import { useEffect, useState } from "react";
import { MarketTabs } from "../components/dashboard/MarketTabs";
import { MatchCard } from "../components/dashboard/MatchCard";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { MarketType, MatchListItem } from "../types/api";

export function ResultsPage() {
  const [market, setMarket] = useState<MarketType>("1X2");
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.results(market).then(setMatches).finally(() => setLoading(false));
  }, [market]);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Results</h1>
        <p className="text-sm text-muted">Completed BetPawa virtual football matches</p>
      </div>
      <MarketTabs active={market} onChange={setMarket} />
      {loading ? <LoadingSpinner label="Loading results..." /> : (
        <div className="card-surface divide-y divide-white/5">
          {matches.length === 0 ? (
            <p className="p-6 text-center text-muted">No completed results yet.</p>
          ) : matches.map((match) => (
            <MatchCard key={match.id} match={match} market={market} />
          ))}
        </div>
      )}
    </div>
  );
}