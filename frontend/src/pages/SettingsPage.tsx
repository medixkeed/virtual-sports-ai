import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { DataStatus } from "../types/api";

export function SettingsPage() {
  const [status, setStatus] = useState<DataStatus | null>(null);

  useEffect(() => {
    api.dataStatus().then(setStatus).catch(() => undefined);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="card-surface space-y-2 p-6 text-sm">
        <h2 className="font-semibold">Data refresh</h2>
        {status ? (
          <>
            <p>
              <span className="text-muted">Source:</span> {status.data_source}
            </p>
            <p>
              <span className="text-muted">Interval:</span>{" "}
              {status.refresh_interval_minutes} minutes
            </p>
            <p>
              <span className="text-muted">Status:</span> {status.refresh_status}
            </p>
            <p>
              <span className="text-muted">Last success:</span>{" "}
              {status.last_successful_refresh
                ? new Date(status.last_successful_refresh).toLocaleString()
                : "Never"}
            </p>
            {status.last_error && (
              <p className="text-red-300">Last error: {status.last_error}</p>
            )}
          </>
        ) : (
          <p className="text-muted">Connect backend to view refresh settings.</p>
        )}
      </div>
      <div className="card-surface p-6 text-sm text-muted">
        Selections are stored locally in your browser for analytics tracking
        only.
      </div>
    </div>
  );
}
