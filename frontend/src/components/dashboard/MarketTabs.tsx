import type { MarketType } from "../../types/api";

const MARKETS: { id: MarketType; label: string }[] = [
  { id: "1X2", label: "1X2" },
  { id: "OU", label: "Over/Under" },
  { id: "BTTS", label: "BTTS" },
  { id: "DC", label: "Double Chance" },
  { id: "HTFT", label: "HT/FT" },
];

export function MarketTabs({
  active,
  onChange,
}: {
  active: MarketType;
  onChange: (m: MarketType) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {MARKETS.map((m) => (
        <button
          key={m.id}
          type="button"
          onClick={() => onChange(m.id)}
          className={`rounded-full px-4 py-1.5 text-xs font-semibold uppercase tracking-wide transition ${
            active === m.id
              ? "bg-purpleOdds text-white shadow"
              : "bg-navy-light text-muted hover:text-white"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
