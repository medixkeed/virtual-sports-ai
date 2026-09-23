import { FormEvent, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/api";

export function RegisterPage() {
  const { register, user } = useAuth();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register(email, password, displayName);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-6 py-8">
      <h1 className="text-2xl font-bold">Create account</h1>
      <form onSubmit={onSubmit} className="card-surface space-y-4 p-6">
        {error && (
          <p className="text-sm text-red-300" role="alert">
            {error}
          </p>
        )}
        <label className="block text-sm">
          Display name
          <input
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/10 bg-navy-light px-3 py-2"
          />
        </label>
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
          Password (min 8 characters)
          <input
            type="password"
            required
            minLength={8}
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
          {loading ? "Creating…" : "Register"}
        </button>
      </form>
      <p className="text-center text-sm text-muted">
        Already have an account?{" "}
        <Link to="/login" className="text-electric hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
