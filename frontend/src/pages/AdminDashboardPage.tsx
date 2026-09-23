import { useEffect, useState } from "react";
import { ProtectedRoute } from "../components/auth/ProtectedRoute";
import { ErrorMessage } from "../components/ui/ErrorMessage";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { AdminStats, AdminUser, ScraperLog } from "../types/api";

function AdminContent() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [logs, setLogs] = useState<ScraperLog[]>([]);
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setError(null);
    try {
      const [s, u, l, settings] = await Promise.all([
        api.adminStats(),
        api.adminUsers(),
        api.adminLogs(),
        api.adminSettings(),
      ]);
      setStats(s);
      setUsers(u);
      setLogs(l);
      setLimit(settings.free_prediction_limit);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Admin load failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingSpinner label="Loading admin…" />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Admin dashboard</h1>
        <button
          type="button"
          onClick={() => api.adminTriggerRefresh().then(load)}
          className="rounded-lg bg-electric px-4 py-2 text-sm font-medium"
        >
          Trigger data refresh
        </button>
      </div>

      {stats && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {[
            ["Users", stats.users_count],
            ["Matches", stats.matches_count],
            ["Predictions", stats.predictions_count],
            ["Model", stats.model_version],
            ["Refresh", stats.refresh_status],
          ].map(([k, v]) => (
            <div key={k} className="card-surface p-4">
              <p className="text-xs text-muted">{k}</p>
              <p className="font-bold">{v}</p>
            </div>
          ))}
        </div>
      )}

      <div className="card-surface p-4">
        <h2 className="mb-3 font-semibold">Free tier limit</h2>
        <div className="flex gap-2">
          <input
            type="number"
            min={1}
            max={100}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="w-24 rounded border border-white/10 bg-navy-light px-2 py-1"
          />
          <button
            type="button"
            onClick={() => api.adminUpdateSettings(limit).then(load)}
            className="rounded bg-purpleOdds px-3 py-1 text-sm"
          >
            Save
          </button>
        </div>
      </div>

      <div className="card-surface overflow-x-auto">
        <h2 className="border-b border-white/10 px-4 py-3 font-semibold">Users</h2>
        <table className="w-full text-left text-sm">
          <thead className="text-xs text-muted">
            <tr>
              <th className="px-4 py-2">Email</th>
              <th className="px-4 py-2">Role</th>
              <th className="px-4 py-2">Premium</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-white/5">
                <td className="px-4 py-2">{u.email}</td>
                <td className="px-4 py-2 uppercase">{u.role}</td>
                <td className="px-4 py-2">{u.is_premium ? "Yes" : "No"}</td>
                <td className="px-4 py-2">
                  <div className="flex flex-wrap gap-1">
                    {(["free", "premium", "admin"] as const).map((role) => (
                      <button
                        key={role}
                        type="button"
                        className="rounded border border-white/15 px-2 py-0.5 text-xs"
                        onClick={() => api.adminSetRole(u.id, role).then(load)}
                      >
                        {role}
                      </button>
                    ))}
                    <button
                      type="button"
                      className="rounded border border-purpleOdds/50 px-2 py-0.5 text-xs"
                      onClick={() =>
                        api.adminSetPremium(u.id, !u.is_premium).then(load)
                      }
                    >
                      Toggle premium
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card-surface p-4">
        <h2 className="mb-2 font-semibold">Scraper / refresh logs</h2>
        <ul className="max-h-64 space-y-2 overflow-y-auto text-xs text-muted">
          {logs.map((log) => (
            <li key={log.id} className="rounded bg-navy-light/50 px-2 py-1">
              [{new Date(log.created_at).toLocaleString()}] {log.provider} —{" "}
              {log.status}: {log.message}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export function AdminDashboardPage() {
  return (
    <ProtectedRoute requireAuth requireAdmin>
      <AdminContent />
    </ProtectedRoute>
  );
}
