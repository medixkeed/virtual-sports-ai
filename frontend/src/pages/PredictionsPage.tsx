import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage } from "../components/ui/ErrorMessage";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/api";
import type { MarketType, MatchListItem } from "../types/api";

export function PredictionsPage() {
  const { user, refreshUser, isPremium } = useAuth();
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [market, setMarket] = useState<MarketType>("1X2");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    api
      .matches({ market: "1X2" })
      .then(setMatches)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const runPrediction = async (matchId: number) => {
    if (!user) {
      setMsg("Please log in to generate predictions.");
      return;
    }
    setBusyId(matchId);
    setMsg(null);
    try {
      const p = await api.createPrediction(matchId, market);
      setMsg(
        p.message ??
          `Prediction created (${p.home_prob?.toFixed(1)}% / ${p.draw_prob?.toFixed(1)}% / ${p.away_prob?.toFixed(1)}%)`,
      );
      await refreshUser();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Prediction failed");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Predictions</h1>
        <p className="text-sm text-muted">
          Statistical baseline estimates — not guaranteed outcomes.
        </p>
      </div>

      {user && (
        <div className="card-surface p-4 text-sm">
          Plan: <strong>{user.role}</strong>
          {!isPremium && (
            <>
              {" "}
              · Used today: {user.predictions_used_today} /{" "}
              {user.free_prediction_limit}
            </>
          )}
          {isPremium && " · Unlimited predictions"}
        </div>
      )}

      {msg && (
        <p className="rounded-lg border border-white/10 bg-navy-light px-3 py-2 text-sm">
          {msg}
        </p>
      )}

      {error && <ErrorMessage message={error} />}

      <div className="card-surface overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-navy-light text-xs uppercase text-muted">
            <tr>
              <th className="px-4 py-2">Match</th>
              <th className="px-4 py-2">Market</th>
              <th className="px-4 py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {matches.slice(0, 12).map((m) => (
              <tr key={m.id} className="border-t border-white/5">
                <td className="px-4 py-3">
                  <Link to={`/matches/${m.id}`} className="hover:text-electric">
                    {m.home_team} vs {m.away_team}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <select
                    value={market}
                    onChange={(e) => setMarket(e.target.value as MarketType)}
                    className="rounded border border-white/10 bg-charcoal px-2 py-1 text-xs"
                  >
                    <option value="1X2">1X2</option>
                    <option value="OU">Over/Under</option>
                    <option value="BTTS">BTTS</option>
                  </select>
                </td>
                <td className="px-4 py-3">
                  <button
                    type="button"
                    disabled={busyId === m.id}
                    onClick={() => runPrediction(m.id)}
                    className="rounded-lg bg-purpleOdds px-3 py-1.5 text-xs font-semibold disabled:opacity-50"
                  >
                    {busyId === m.id ? "Running…" : "Generate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
