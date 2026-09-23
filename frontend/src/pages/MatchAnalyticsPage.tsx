import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ProbabilityChart } from "../components/charts/ProbabilityChart";
import { ErrorMessage } from "../components/ui/ErrorMessage";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { MatchDetail, PredictionOut } from "../types/api";

export function MatchAnalyticsPage() {
  const { id } = useParams();
  const matchId = Number(id);
  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [predictions, setPredictions] = useState<PredictionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) return;
    (async () => {
      try {
        const [m, p] = await Promise.all([
          api.match(matchId),
          api.matchPredictions(matchId),
        ]);
        setMatch(m);
        setPredictions(p);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load match");
      } finally {
        setLoading(false);
      }
    })();
  }, [matchId]);

  if (loading) return <LoadingSpinner />;
  if (error || !match)
    return (
      <ErrorMessage
        message={error ?? "Match not found"}
        onRetry={() => window.location.reload()}
      />
    );

  const latest1x2 = predictions.find((p) => p.market === "1X2");

  return (
    <div className="space-y-4">
      <Link to="/" className="text-sm text-electric hover:underline">
        ← Back to dashboard
      </Link>
      <div className="card-surface p-5">
        <p className="text-xs uppercase text-muted">{match.league_name}</p>
        <h1 className="mt-1 text-2xl font-bold">
          {match.home_team} vs {match.away_team}
        </h1>
        <p className="text-sm text-muted">
          Round {match.round} · {new Date(match.kickoff_at).toLocaleString()} ·{" "}
          {match.status}
          {match.is_demo && " · DEMO"}
        </p>
        {match.status === "finished" && match.home_score != null && (
          <p className="mt-2 text-lg font-semibold">
            Final: {match.home_score} – {match.away_score}
          </p>
        )}
      </div>

      <div className="card-surface p-5">
        <h2 className="mb-3 text-lg font-semibold">AI 1X2 estimate</h2>
        {latest1x2?.message ? (
          <p className="text-sm text-muted">{latest1x2.message}</p>
        ) : latest1x2?.home_prob != null ? (
          <>
            <p className="mb-3 text-xs text-muted">
              Model {latest1x2.model_version}
              {latest1x2.is_demo
                ? " · DEMO baseline — not validated on live data"
                : ""}
            </p>
            <ProbabilityChart
              home={latest1x2.home_prob}
              draw={latest1x2.draw_prob ?? 0}
              away={latest1x2.away_prob ?? 0}
            />
          </>
        ) : (
          <p className="text-sm text-muted">
            Prediction unavailable — insufficient data.
          </p>
        )}
      </div>

      <div className="card-surface p-5">
        <h2 className="mb-2 text-lg font-semibold">All stored predictions</h2>
        <ul className="divide-y divide-white/5 text-sm">
          {predictions.length === 0 && (
            <li className="py-3 text-muted">No predictions yet.</li>
          )}
          {predictions.map((p) => (
            <li key={p.id} className="flex justify-between py-2">
              <span>
                {p.market} · {p.status}
                {p.is_demo && " · DEMO"}
              </span>
              <span className="text-muted">
                {new Date(p.created_at).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
