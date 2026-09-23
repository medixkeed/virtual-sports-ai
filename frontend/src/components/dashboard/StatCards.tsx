import type { DashboardStats } from "../../types/api";
import { Activity, Calendar, RefreshCw, Sparkles, Trophy } from "lucide-react";

const items = (
  stats: DashboardStats,
): { label: string; value: string; icon: typeof Trophy }[] => [
  { label: "Season", value: stats.season, icon: Calendar },
  { label: "Round", value: String(stats.round), icon: Trophy },
  {
    label: "Last updated",
    value: new Date(stats.last_updated).toLocaleString(),
    icon: RefreshCw,
  },
  { label: "Total events", value: String(stats.total_events), icon: Activity },
  {
    label: "Predictions",
    value: String(stats.available_predictions),
    icon: Sparkles,
  },
  { label: "Refresh", value: stats.refresh_status, icon: RefreshCw },
];

export function StatCards({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
      {items(stats).map(({ label, value, icon: Icon }) => (
        <div key={label} className="card-surface p-3">
          <div className="mb-1 flex items-center gap-2 text-xs text-muted">
            <Icon className="h-3.5 w-3.5" />
            {label}
          </div>
          <div className="truncate text-sm font-semibold" title={value}>
            {value}
          </div>
        </div>
      ))}
    </div>
  );
}
