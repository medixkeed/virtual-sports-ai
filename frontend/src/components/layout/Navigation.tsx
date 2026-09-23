import { NavLink } from "react-router-dom";
import {
  BarChart3,
  Brain,
  History,
  LayoutDashboard,
  Settings,
  Shield,
  Tag,
  Trophy,
  User,
} from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/predictions", label: "Predictions", icon: Brain },
  { to: "/history", label: "History", icon: History },
  { to: "/results", label: "Results", icon: Trophy },
  { to: "/pricing", label: "Pricing", icon: Tag },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  const { user, isAdmin } = useAuth();

  return (
    <nav className="flex flex-col gap-1">
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-electric/20 text-white"
                : "text-muted hover:bg-white/5 hover:text-white"
            }`
          }
        >
          <Icon className="h-4 w-4" />
          {label}
        </NavLink>
      ))}
      {user && (
        <NavLink
          to="/profile"
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-electric/20 text-white"
                : "text-muted hover:bg-white/5 hover:text-white"
            }`
          }
        >
          <User className="h-4 w-4" />
          Profile
        </NavLink>
      )}
      {isAdmin && (
        <NavLink
          to="/admin"
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-purpleOdds/30 text-white"
                : "text-muted hover:bg-white/5 hover:text-white"
            }`
          }
        >
          <Shield className="h-4 w-4" />
          Admin
        </NavLink>
      )}
    </nav>
  );
}
