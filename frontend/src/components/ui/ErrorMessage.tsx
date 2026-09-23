import { AlertCircle } from "lucide-react";

export function ErrorMessage({
  title = "Something went wrong",
  message,
  onRetry,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="card-surface flex flex-col items-center gap-3 p-8 text-center"
      role="alert"
    >
      <AlertCircle className="h-10 w-10 text-red-400" />
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="max-w-md text-sm text-muted">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 rounded-lg bg-electric px-4 py-2 text-sm font-medium hover:bg-electric-dim"
        >
          Try again
        </button>
      )}
    </div>
  );
}
