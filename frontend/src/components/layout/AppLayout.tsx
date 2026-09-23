import { Link, Outlet } from "react-router-dom";
import { MobileMenu } from "./MobileMenu";
import { Navigation } from "./Navigation";
import { useAuth } from "../../contexts/AuthContext";
import { useEffect, useState } from "react";
import { api } from "../../services/api";
import type { DataStatus } from "../../types/api";
import { DataStatusBanner } from "../ui/NotificationBanner";

export function AppLayout() {
  const { user, logout } = useAuth();
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);

  useEffect(() => {
    const loadStatus = () => {
      api.dataStatus().then(setDataStatus).catch(() => undefined);
    };
    loadStatus();
    const interval = window.setInterval(loadStatus, 30_000);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-charcoal/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-3">
            <MobileMenu />
            <Link to="/" className="text-lg font-bold tracking-tight">
              <span className="text-electric">Virtual</span> Sports AI
            </Link>
          </div>
          <div className="hidden items-center gap-3 lg:flex">
            {user ? (
              <>
                <span className="text-sm text-muted">
                  {user.display_name}{" "}
                  <span className="rounded bg-white/10 px-1.5 py-0.5 text-xs uppercase">
                    {user.role}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={logout}
                  className="rounded-lg border border-white/15 px-3 py-1.5 text-sm hover:bg-white/5"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-lg px-3 py-1.5 text-sm text-muted hover:text-white"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="rounded-lg bg-electric px-3 py-1.5 text-sm font-medium hover:bg-electric-dim"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        <aside className="hidden w-56 shrink-0 lg:block">
          <Navigation />
        </aside>
        <main className="min-w-0 flex-1 space-y-4">
          <DataStatusBanner status={dataStatus} />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
