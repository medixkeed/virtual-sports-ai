import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage } from "../components/ui/ErrorMessage";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { PredictionOut } from "../types/api";

export function PredictionHistoryPage() {
  const [items, setItems] = useState<PredictionOut[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = (p: number) => {
    setLoading(true);
    api
      .predictionHistory(p)
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
        setPage(res.page);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load(1);
  }, []);

  const pages = Math.max(1, Math.ceil(total / 20));

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Prediction history</h1>
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} onRetry={() => load(page)} />}
      {!loading && !error && (
        <>
          <div className="card-surface divide-y divide-white/5">
            {items.length === 0 && (
              <p className="p-6 text-muted">No predictions recorded yet.</p>
            )}
            {items.map((p) => (
              <div
                key={p.id}
                className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
              >
                <div>
                  <Link
                    to={`/matches/${p.match_id}`}
                    className="font-medium text-electric hover:underline"
                  >
                    Match #{p.match_id}
                  </Link>
                  <span className="ml-2 text-muted">
                    {p.market} · {p.model_version}
                    {p.is_demo && " · DEMO"}
                  </span>
                </div>
                <span className="text-muted">
                  {new Date(p.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => load(page - 1)}
              className="rounded border border-white/15 px-3 py-1 text-sm disabled:opacity-40"
            >
              Previous
            </button>
            <span className="self-center text-sm text-muted">
              Page {page} of {pages}
            </span>
            <button
              type="button"
              disabled={page >= pages}
              onClick={() => load(page + 1)}
              className="rounded border border-white/15 px-3 py-1 text-sm disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
