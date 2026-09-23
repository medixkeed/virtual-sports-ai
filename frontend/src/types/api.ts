export type MarketType = "1X2" | "OU" | "BTTS" | "DC" | "HTFT";
export type UserRole = "guest" | "free" | "premium" | "admin";
export type MatchStatus = "scheduled" | "live" | "finished";

export interface DashboardStats {
  season: string;
  round: number;
  last_updated: string;
  total_events: number;
  available_predictions: number;
  refresh_status: string;
  data_source: string;
}

export interface DashboardPrediction {
  match_id: number;
  league_name: string;
  home_team: string;
  away_team: string;
  kickoff_at: string;
  market: MarketType;
  outcomes: { key: string; label: string; odds: number; probability: number }[];
  home_prob: number | null;
  draw_prob: number | null;
  away_prob: number | null;
  message: string | null;
  status: string;
}

export interface League {
  id: number;
  name: string;
  code: string;
  country: string;
  is_demo: boolean;
}

export interface Team {
  id: number;
  name: string;
  short_name: string;
}

export interface MatchOddsOutcome {
  key: string;
  label: string;
  odds: number;
}

export interface MatchListItem {
  id: number;
  league_id: number;
  league_name: string;
  league_code: string;
  round: number;
  home_team: string;
  away_team: string;
  kickoff_at: string;
  status: MatchStatus;
  home_score: number | null;
  away_score: number | null;
  is_demo: boolean;
  odds: MatchOddsOutcome[];
}

export interface MatchDetail extends MatchListItem {
  home_team_id: number;
  away_team_id: number;
  home_score: number | null;
  away_score: number | null;
}

export interface PredictionOut {
  id: number;
  match_id: number;
  market: MarketType;
  home_prob: number | null;
  draw_prob: number | null;
  away_prob: number | null;
  message: string | null;
  is_demo: boolean;
  model_version: string;
  status: string;
  created_at: string;
}

export interface UserPublic {
  id: number;
  email: string;
  display_name: string;
  role: UserRole;
  is_premium: boolean;
  predictions_used_today: number;
  free_prediction_limit: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserPublic;
}

export interface DataStatus {
  last_fetched_at: string | null;
  last_successful_refresh: string | null;
  last_successful_provider: string | null;
  refresh_status: string;
  refresh_interval_minutes: number;
  data_source: string;
  last_error: string | null;
}

export interface PricingPlan {
  id: string;
  name: string;
  price_label: string;
  features: string[];
  highlighted: boolean;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface AnalyticsOverview {
  total_matches: number;
  finished_matches: number;
  avg_goals_per_match: number;
  home_win_rate: number;
  draw_rate: number;
  away_win_rate: number;
  data_source: string;
}

export interface AdminStats {
  users_count: number;
  matches_count: number;
  predictions_count: number;
  model_version: string;
  refresh_status: string;
}

export interface AdminUser {
  id: number;
  email: string;
  display_name: string;
  role: UserRole;
  is_premium: boolean;
  created_at: string;
}

export interface ScraperLog {
  id: number;
  provider: string;
  status: string;
  message: string;
  created_at: string;
}
