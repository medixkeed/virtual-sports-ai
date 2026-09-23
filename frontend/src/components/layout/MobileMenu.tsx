import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Navigation } from "./Navigation";
import { useAuth } from "../../contexts/AuthContext";

export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();

  return (
    <div className="lg:hidden">
      <button
        type="button"
        className="rounded-lg border border-white/10 p-2"
        aria-label={open ? "Close menu" : "Open menu"}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>
      {open && (
        <div className="fixed inset-0 z-50 bg-black/60" onClick={() => setOpen(false)}>
          <div
            className="absolute left-0 top-0 h-full w-72 bg-charcoal p-4 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <span className="font-bold text-electric">Virtual Sports AI</span>
              <button type="button" onClick={() => setOpen(false)} aria-label="Close">
                <X className="h-5 w-5" />
              </button>
            </div>
            <Navigation onNavigate={() => setOpen(false)} />
            <div className="mt-6 border-t border-white/10 pt-4 text-sm">
              {user ? (
                <button
                  type="button"
                  className="w-full rounded-lg bg-white/10 py-2"
                  onClick={() => {
                    logout();
                    setOpen(false);
                  }}
                >
                  Log out
                </button>
              ) : (
                <div className="flex flex-col gap-2">
                  <Link
                    to="/login"
                    className="rounded-lg bg-electric py-2 text-center font-medium"
                    onClick={() => setOpen(false)}
                  >
                    Log in
                  </Link>
                  <Link
                    to="/register"
                    className="rounded-lg border border-white/20 py-2 text-center"
                    onClick={() => setOpen(false)}
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
