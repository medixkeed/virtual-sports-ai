import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ErrorMessage } from "../components/ui/ErrorMessage";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { AnalyticsOverview } from "../types/api";

export function AnalyticsOverviewPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .analyticsOverview()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error || !data)
    return (
      <ErrorMessage message={error ?? "No data"} onRetry={() => location.reload()} />
    );

  const chartData = [
    { name: "Home", rate: data.home_win_rate * 100 },
    { name: "Draw", rate: data.draw_rate * 100 },
    { name: "Away", rate: data.away_win_rate * 100 },
  ];

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Match analytics</h1>
      <p className="text-sm text-muted">Source: {data.data_source}</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Total matches", data.total_matches],
          ["Finished", data.finished_matches],
          ["Avg goals", data.avg_goals_per_match.toFixed(2)],
          ["Home win %", `${(data.home_win_rate * 100).toFixed(1)}%`],
        ].map(([label, value]) => (
          <div key={label} className="card-surface p-4">
            <p className="text-xs text-muted">{label}</p>
            <p className="text-xl font-bold">{value}</p>
          </div>
        ))}
      </div>
      <div className="card-surface p-4">
        <h2 className="mb-3 font-semibold">
          Outcome distribution (finished {data.data_source} matches)
        </h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" unit="%" />
              <Tooltip
                contentStyle={{
                  background: "#1a2332",
                  border: "1px solid rgba(255,255,255,0.1)",
                }}
              />
              <Bar dataKey="rate" fill="#7c3aed" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
