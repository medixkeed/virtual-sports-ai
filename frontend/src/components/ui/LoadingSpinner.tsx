import { Loader2 } from "lucide-react";

export function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted">
      <Loader2 className="h-8 w-8 animate-spin text-electric" aria-hidden />
      <p className="text-sm">{label}</p>
    </div>
  );
}
