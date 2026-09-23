import type {
  AdminStats,
  AdminUser,
  AnalyticsOverview,
  AuthResponse,
  DashboardStats,
  DashboardPrediction,
  DataStatus,
  League,
  MatchDetail,
  MatchListItem,
  MarketType,
  Paginated,
  PredictionOut,
  PricingPlan,
  ScraperLog,
  UserPublic,
} from "../types/api";

const API_BASE = (import.meta.env.VITE_API_URL ?? "/api").replace(/\/$/, "");

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  return localStorage.getItem("vsa_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body.message ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, String(detail));
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; data_source: string }>("/health"),

  dashboardStats: () => request<DashboardStats>("/dashboard/stats"),

  dashboardPredictions: (market: MarketType = "1X2") =>
    request<DashboardPrediction[]>(`/dashboard/predictions?market=${market}`),

  leagues: () => request<League[]>("/leagues"),

  matches: (params?: {
    league_id?: number;
    round?: number;
    provider?: string;
    search?: string;
    market?: MarketType;
  }) => {
    const q = new URLSearchParams();
    if (params?.league_id) q.set("league_id", String(params.league_id));
    if (params?.round) q.set("round", String(params.round));
    if (params?.provider) q.set("provider", params.provider);
    if (params?.search) q.set("search", params.search);
    if (params?.market) q.set("market", params.market);
    const qs = q.toString();
    return request<MatchListItem[]>(`/matches${qs ? `?${qs}` : ""}`);
  },

  results: (market: MarketType = "1X2") =>
    request<MatchListItem[]>(`/matches/results?market=${market}`),

  match: (id: number) => request<MatchDetail>(`/matches/${id}`),

  matchOdds: (id: number, market: MarketType) =>
    request<{ market: MarketType; outcomes: { key: string; label: string; odds: number }[] }>(
      `/matches/${id}/odds?market=${market}`,
    ),

  matchPredictions: (id: number) =>
    request<PredictionOut[]>(`/matches/${id}/predictions`),

  predictionHistory: (page = 1) =>
    request<Paginated<PredictionOut>>(
      `/predictions/history?page=${page}&page_size=20`,
    ),

  analyticsOverview: () => request<AnalyticsOverview>("/analytics/overview"),

  register: (email: string, password: string, display_name: string) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<UserPublic>("/auth/me"),

  refreshData: () =>
    request<DataStatus>("/data/refresh", { method: "POST" }),

  dataStatus: () => request<DataStatus>("/data/status"),

  pricing: () => request<PricingPlan[]>("/pricing"),

  saveSelections: (selections: { match_id: number; market: string; outcome_key: string }[]) =>
    request<{ saved: number }>("/selections", {
      method: "POST",
      body: JSON.stringify({ selections }),
    }),

  adminStats: () => request<AdminStats>("/admin/stats"),

  adminUsers: () => request<AdminUser[]>("/admin/users"),

  adminSetRole: (userId: number, role: string) =>
    request<AdminUser>(`/admin/users/${userId}/role`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    }),

  adminSetPremium: (userId: number, is_premium: boolean) =>
    request<AdminUser>(`/admin/users/${userId}/premium`, {
      method: "PATCH",
      body: JSON.stringify({ is_premium }),
    }),

  adminLogs: () => request<ScraperLog[]>("/admin/scraper-logs"),

  adminSettings: () =>
    request<{ free_prediction_limit: number }>("/admin/settings"),

  adminUpdateSettings: (free_prediction_limit: number) =>
    request<{ free_prediction_limit: number }>("/admin/settings", {
      method: "PATCH",
      body: JSON.stringify({ free_prediction_limit }),
    }),

  adminTriggerRefresh: () =>
    request<DataStatus>("/admin/refresh", { method: "POST" }),

  createPrediction: (match_id: number, market: MarketType) =>
    request<PredictionOut>("/predictions", {
      method: "POST",
      body: JSON.stringify({ match_id, market }),
    }),
};

export { ApiError };
