import { ProtectedRoute } from "../components/auth/ProtectedRoute";
import { useAuth } from "../contexts/AuthContext";

function ProfileContent() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Profile</h1>
      <div className="card-surface space-y-3 p-6 text-sm">
        <p>
          <span className="text-muted">Name:</span> {user.display_name}
        </p>
        <p>
          <span className="text-muted">Email:</span> {user.email}
        </p>
        <p>
          <span className="text-muted">Role:</span>{" "}
          <span className="uppercase">{user.role}</span>
        </p>
        <p>
          <span className="text-muted">Premium:</span>{" "}
          {user.is_premium ? "Yes" : "No"}
        </p>
        <p>
          <span className="text-muted">Predictions today:</span>{" "}
          {user.predictions_used_today} / {user.free_prediction_limit}
        </p>
      </div>
    </div>
  );
}

export function ProfilePage() {
  return (
    <ProtectedRoute requireAuth>
      <ProfileContent />
    </ProtectedRoute>
  );
}
