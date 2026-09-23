import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { ApiError } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const { login, user } = useAuth();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from
    ?.pathname;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to={from ?? "/"} replace />;

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-6 py-8">
      <h1 className="text-2xl font-bold">Log in</h1>
      <form onSubmit={onSubmit} className="card-surface space-y-4 p-6">
        {error && (
          <p className="text-sm text-red-300" role="alert">
            {error}
          </p>
        )}
        <label className="block text-sm">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/10 bg-navy-light px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/10 bg-navy-light px-3 py-2"
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-electric py-2 font-semibold disabled:opacity-50"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="text-center text-sm text-muted">
        No account?{" "}
        <Link to="/register" className="text-electric hover:underline">
          Register
        </Link>
      </p>
      <p className="text-center text-xs text-muted">
        Demo admin: admin@virtualsports.ai / Admin123!
      </p>
    </div>
  );
}
