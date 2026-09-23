from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

MarketTypeStr = Literal["1X2", "OU", "BTTS", "DC", "HTFT"]
UserRoleStr = Literal["guest", "free", "premium", "admin"]
MatchStatusStr = Literal["scheduled", "live", "finished"]


class HealthOut(BaseModel):
    status: str
    data_source: str


class DashboardStatsOut(BaseModel):
    season: str
    round: int
    last_updated: datetime
    total_events: int
    available_predictions: int
    refresh_status: str
    data_source: str


class LeagueOut(BaseModel):
    id: int
    name: str
    code: str
    country: str
    is_demo: bool

    model_config = {"from_attributes": True}


class OddsOutcomeOut(BaseModel):
    key: str
    label: str
    odds: float


class DashboardPredictionOutcomeOut(OddsOutcomeOut):
    probability: float


class DashboardPredictionOut(BaseModel):
    match_id: int
    league_name: str
    home_team: str
    away_team: str
    kickoff_at: datetime
    market: MarketTypeStr
    outcomes: list[DashboardPredictionOutcomeOut]
    home_prob: float | None
    draw_prob: float | None
    away_prob: float | None
    message: str | None
    status: str


class MatchListOut(BaseModel):
    id: int
    league_id: int
    league_name: str
    league_code: str
    round: int
    home_team: str
    away_team: str
    kickoff_at: datetime
    status: MatchStatusStr
    home_score: int | None
    away_score: int | None
    is_demo: bool
    odds: list[OddsOutcomeOut]


class MatchDetailOut(MatchListOut):
    home_team_id: int
    away_team_id: int
    home_score: int | None
    away_score: int | None


class PredictionOut(BaseModel):
    id: int
    match_id: int
    market: MarketTypeStr
    home_prob: float | None
    draw_prob: float | None
    away_prob: float | None
    message: str | None
    is_demo: bool
    model_version: str
    status: str
    created_at: datetime


class PaginatedPredictions(BaseModel):
    items: list[PredictionOut]
    total: int
    page: int
    page_size: int


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=2, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    role: UserRoleStr
    is_premium: bool
    predictions_used_today: int
    free_prediction_limit: int


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class DataStatusOut(BaseModel):
    last_fetched_at: datetime | None
    last_successful_refresh: datetime | None
    last_successful_provider: str | None
    refresh_status: str
    refresh_interval_minutes: int
    data_source: str
    last_error: str | None


class AnalyticsOverviewOut(BaseModel):
    total_matches: int
    finished_matches: int
    avg_goals_per_match: float
    home_win_rate: float
    draw_rate: float
    away_win_rate: float
    data_source: str


class VFLBacktestOut(BaseModel):
    market: str
    sample_size: int
    hit_rate: float
    baseline_rate: float
    validated: bool


class PricingPlanOut(BaseModel):
    id: str
    name: str
    price_label: str
    features: list[str]
    highlighted: bool


class PredictionCreateIn(BaseModel):
    match_id: int
    market: MarketTypeStr = "1X2"


class SelectionItemIn(BaseModel):
    match_id: int
    market: str
    outcome_key: str


class SelectionsIn(BaseModel):
    selections: list[SelectionItemIn]


class AdminStatsOut(BaseModel):
    users_count: int
    matches_count: int
    predictions_count: int
    model_version: str
    refresh_status: str


class AdminUserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    role: UserRoleStr
    is_premium: bool
    created_at: datetime


class RoleUpdateIn(BaseModel):
    role: UserRoleStr


class PremiumUpdateIn(BaseModel):
    is_premium: bool


class SettingsUpdateIn(BaseModel):
    free_prediction_limit: int = Field(ge=1, le=100)


class ScraperLogOut(BaseModel):
    id: int
    provider: str
    status: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
