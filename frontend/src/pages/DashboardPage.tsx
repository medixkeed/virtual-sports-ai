import { BrainCircuit, RefreshCw, Search } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { LeagueSection } from "../components/dashboard/LeagueSection";
import { MarketTabs } from "../components/dashboard/MarketTabs";
import { SelectionPanel } from "../components/dashboard/SelectionPanel";
import { StatCards } from "../components/dashboard/StatCards";
import { ErrorMessage } from "../components/ui/ErrorMessage";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { api } from "../services/api";
import type { DashboardPrediction, DashboardStats, League, MarketType, MatchListItem } from "../types/api";

const LEAGUE_ORDER = ["ENG", "ESP", "ITA", "GER"];

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [results, setResults] = useState<MatchListItem[]>([]);
  const [predictions, setPredictions] = useState<DashboardPrediction[]>([]);
  const [view, setView] = useState<"matches" | "results">("matches");
  const [market, setMarket] = useState<MarketType>("1X2");
  const [search, setSearch] = useState("");
  const [leagueFilter, setLeagueFilter] = useState<number | "all">("all");
  const [roundFilter, setRoundFilter] = useState<number | "all">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [s, l, m, r, p] = await Promise.all([
        api.dashboardStats(),
        api.leagues(),
        api.matches({ market }),
        api.results(market),
        api.dashboardPredictions(market),
      ]);
      setStats(s);
      setLeagues(l);
      setMatches(m);
      setResults(r);
      setPredictions(p);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }, [market]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      load();
    }, 30_000);
    return () => window.clearInterval(interval);
  }, [load]);

  const filtered = useMemo(() => {
    let list = matches;
    if (leagueFilter !== "all") {
      list = list.filter((m) => m.league_id === leagueFilter);
    }
    if (roundFilter !== "all") {
      list = list.filter((m) => m.round === roundFilter);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (m) =>
          m.home_team.toLowerCase().includes(q) ||
          m.away_team.toLowerCase().includes(q) ||
          m.league_name.toLowerCase().includes(q),
      );
    }
    return list;
  }, [matches, leagueFilter, roundFilter, search]);

  const grouped = useMemo(() => {
    const map = new Map<string, MatchListItem[]>();
    for (const m of filtered) {
      const key = m.league_name;
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(m);
    }
    const entries = [...map.entries()];
    entries.sort((a, b) => {
      const codeA = a[1][0]?.league_code ?? "";
      const codeB = b[1][0]?.league_code ?? "";
      return LEAGUE_ORDER.indexOf(codeA) - LEAGUE_ORDER.indexOf(codeB);
    });
    return entries;
  }, [filtered]);

  const rounds = useMemo(
    () => [...new Set(matches.map((m) => m.round))].sort((a, b) => a - b),
    [matches],
  );

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await api.refreshData();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  if (loading && !stats) return <LoadingSpinner label="Loading dashboard…" />;
  if (error && !stats)
    return <ErrorMessage message={error} onRetry={() => load()} />;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted">
            Virtual football markets &amp; AI insights
            {stats?.data_source ? ` · ${stats.data_source}` : ""}
          </p>
        </div>
        <button
          type="button"
          disabled={refreshing}
          onClick={onRefresh}
          className="inline-flex items-center gap-2 rounded-lg bg-electric px-4 py-2 text-sm font-medium hover:bg-electric-dim disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
          Refresh data
        </button>
      </div>

      {stats && <StatCards stats={stats} />}

      {predictions.length > 0 && (
        <section className="card-surface overflow-hidden">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold">
                <BrainCircuit className="h-4 w-4 text-electric" />
                Available predictions
              </div>
              <p className="mt-1 text-xs text-muted">Live current-round estimates from odds, last-five form, and goal signals.</p>
            </div>
            <span className="text-xs text-muted">{predictions.length} matches</span>
          </div>
          {[...new Set(predictions.map((item) => item.league_name))].map((leagueName) => (
            <div key={leagueName} className="border-b border-white/5 last:border-b-0">
              <div className="bg-navy-light/50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-muted">
                {leagueName}
              </div>
              <div className="grid gap-px bg-white/5 sm:grid-cols-2 xl:grid-cols-3">
                {predictions.filter((item) => item.league_name === leagueName).map((prediction) => (
                  <div key={prediction.match_id} className="bg-navy p-4">
                    <div className="text-sm font-semibold">
                      {prediction.home_team} <span className="text-muted">vs</span> {prediction.away_team}
                    </div>
                    {prediction.outcomes.length === 0 ? (
                      <p className="mt-3 text-xs text-muted">Prediction unavailable for this market.</p>
                    ) : (
                      <div className="mt-3 grid grid-cols-2 gap-2 text-center sm:grid-cols-3">
                        {prediction.outcomes.map((outcome) => (
                          <PredictionValue key={outcome.key} label={outcome.label} value={outcome.probability} />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>
      )}

      <MarketTabs active={market} onChange={setMarket} />

      <div className="flex border-b border-white/10" role="tablist" aria-label="Dashboard view">
        <button
          type="button"
          role="tab"
          aria-selected={view === "matches"}
          onClick={() => setView("matches")}
          className={`border-b-2 px-4 py-2 text-sm font-semibold ${view === "matches" ? "border-electric text-white" : "border-transparent text-muted hover:text-white"}`}
        >
          Matches
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={view === "results"}
          onClick={() => setView("results")}
          className={`border-b-2 px-4 py-2 text-sm font-semibold ${view === "results" ? "border-electric text-white" : "border-transparent text-muted hover:text-white"}`}
        >
          Results ({results.length})
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
        <div className="space-y-4">
          {view === "matches" && <div className="card-surface flex flex-col gap-3 p-3 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                type="search"
                placeholder="Search teams or leagues…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-navy-light py-2 pl-9 pr-3 text-sm outline-none focus:border-electric"
              />
            </div>
            <select
              value={leagueFilter === "all" ? "all" : String(leagueFilter)}
              onChange={(e) =>
                setLeagueFilter(
                  e.target.value === "all" ? "all" : Number(e.target.value),
                )
              }
              className="rounded-lg border border-white/10 bg-navy-light px-3 py-2 text-sm"
            >
              <option value="all">All leagues</option>
              {leagues.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
            <select
              value={roundFilter === "all" ? "all" : String(roundFilter)}
              onChange={(e) =>
                setRoundFilter(
                  e.target.value === "all" ? "all" : Number(e.target.value),
                )
              }
              className="rounded-lg border border-white/10 bg-navy-light px-3 py-2 text-sm"
            >
              <option value="all">All rounds</option>
              {rounds.map((r) => (
                <option key={r} value={r}>
                  Round {r}
                </option>
              ))}
            </select>
          </div>}

          {error && (
            <p className="text-sm text-red-300" role="alert">
              {error}
            </p>
          )}

          {view === "results" ? (
            <div className="card-surface divide-y divide-white/5">
              {results.length === 0 ? (
                <p className="p-8 text-center text-muted">No finished matches yet.</p>
              ) : results.map((match) => (
                <MatchResultRow key={match.id} match={match} />
              ))}
            </div>
          ) : grouped.length === 0 ? (
            <div className="card-surface p-8 text-center text-muted">
              No matches match your filters.
            </div>
          ) : (
            grouped.map(([name, leagueMatches]) => (
              <LeagueSection
                key={name}
                leagueName={name}
                matches={leagueMatches}
                market={market}
              />
            ))
          )}
        </div>
        <SelectionPanel />
      </div>
    </div>
  );
}

function MatchResultRow({ match }: { match: MatchListItem }) {
  return (
    <div className="px-3 py-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <div className="text-xs text-muted">{match.league_name}</div>
          <div className="text-sm font-semibold">
            {match.home_team} <span className="text-muted">vs</span> {match.away_team}
          </div>
          <div className="text-xs text-muted">
            Final {match.home_score} - {match.away_score} · {new Date(`${match.kickoff_at}Z`).toLocaleString([], { timeZone: "Africa/Kampala" })}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {match.odds.map((outcome) => (
            <span key={outcome.key} className="rounded bg-navy-light px-2 py-1 text-xs text-muted">
              {outcome.label} {outcome.odds.toFixed(2)}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function PredictionValue({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-navy-light px-2 py-2">
      <div className="truncate text-[11px] text-muted">{label}</div>
      <div className="mt-1 text-sm font-bold text-electric">{value.toFixed(1)}%</div>
    </div>
  );
}
