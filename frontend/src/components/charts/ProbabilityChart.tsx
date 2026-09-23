import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function ProbabilityChart({
  home,
  draw,
  away,
}: {
  home: number;
  draw: number;
  away: number;
}) {
  const data = [
    { name: "Home", pct: home },
    { name: "Draw", pct: draw },
    { name: "Away", pct: away },
  ];

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} unit="%" domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              background: "#1a2332",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
            }}
            formatter={(v: number) => [`${v.toFixed(1)}%`, "Probability"]}
          />
          <Bar dataKey="pct" fill="#2d8cff" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
