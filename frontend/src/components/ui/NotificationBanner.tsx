import { AlertTriangle, CheckCircle2, Info } from "lucide-react";
import type { DataStatus } from "../../types/api";

function mode(status: DataStatus | null): "DEMO" | "LIVE" | "STALE" {
  if (!status || status.data_source.toLowerCase().includes("demo")) return "DEMO";
  if (status.refresh_status === "ok") return "LIVE";
  return "STALE";
}

export function DataStatusBanner({ status }: { status: DataStatus | null }) {
  const currentMode = mode(status);
  const Icon = currentMode === "LIVE" ? CheckCircle2 : currentMode === "STALE" ? AlertTriangle : Info;
  const tone = currentMode === "LIVE" ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-100" : currentMode === "STALE" ? "border-amber-500/30 bg-amber-500/10 text-amber-100" : "border-sky-500/30 bg-sky-500/10 text-sky-100";
  const showingFallback = currentMode === "STALE" && status?.last_successful_provider?.toLowerCase().includes("demo");

  return (
    <div className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-xs ${tone}`}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" />
      <span>
        <strong>{currentMode}</strong> · {status?.data_source ?? "DEMO provider"}
        {showingFallback && <> · Showing preserved DEMO dataset</>}
        {status?.last_successful_refresh && (
          <> · Last successful dataset: {new Date(status.last_successful_refresh).toLocaleString()} ({status.last_successful_provider ?? "unknown provider"})</>
        )}
        {status?.last_error && <span className="block text-red-200">{status.last_error}</span>}
      </span>
    </div>
  );
}
