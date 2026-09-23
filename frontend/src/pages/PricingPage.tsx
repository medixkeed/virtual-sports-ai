import { Check } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { PricingPlan } from "../types/api";

export function PricingPage() {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.pricing().then(setPlans).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Pricing</h1>
        <p className="text-sm text-muted">
          No payment processing in v1 — admins can grant premium manually.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`card-surface p-6 ${plan.highlighted ? "ring-2 ring-purpleOdds" : ""}`}
          >
            <h2 className="text-lg font-bold">{plan.name}</h2>
            <p className="mt-2 text-3xl font-bold text-electric">{plan.price_label}</p>
            <ul className="mt-4 space-y-2 text-sm text-muted">
              {plan.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <Check className="h-4 w-4 shrink-0 text-electric" />
                  {f}
                </li>
              ))}
            </ul>
            <Link
              to="/register"
              className="mt-6 block rounded-lg bg-electric py-2 text-center text-sm font-semibold hover:bg-electric-dim"
            >
              Get started
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
