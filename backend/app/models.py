from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, PyEnum):
    guest = "guest"
    free = "free"
    premium = "premium"
    admin = "admin"


class MatchStatus(str, PyEnum):
    scheduled = "scheduled"
    live = "live"
    finished = "finished"


class MarketType(str, PyEnum):
    X1X2 = "1X2"
    OU = "OU"
    BTTS = "BTTS"
    DC = "DC"
    HTFT = "HTFT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.free)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    predictions_used_today: Mapped[int] = mapped_column(Integer, default=0)
    predictions_day: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    selections: Mapped[list["UserSelection"]] = relationship(back_populates="user")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="user")


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(80))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    teams: Mapped[list["Team"]] = relationship(back_populates="league")
    matches: Mapped[list["Match"]] = relationship(back_populates="league")


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("league_id", "name", name="uq_team_league_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    short_name: Mapped[str] = mapped_column(String(20))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)

    league: Mapped["League"] = relationship(back_populates="teams")


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        Index("ix_matches_league_round", "league_id", "round"),
        UniqueConstraint("external_key", name="uq_match_external_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    round: Mapped[int] = mapped_column(Integer, default=1)
    season: Mapped[str] = mapped_column(String(20), default="DEMO 2025/26")
    kickoff_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.scheduled)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    external_key: Mapped[str] = mapped_column(String(64))
    provider_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    league: Mapped["League"] = relationship(back_populates="matches")
    odds: Mapped[list["MarketOdds"]] = relationship(back_populates="match")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="match")


class MarketOdds(Base):
    __tablename__ = "market_odds"
    __table_args__ = (
        UniqueConstraint("match_id", "market", "outcome_key", name="uq_odds_outcome"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    market: Mapped[MarketType] = mapped_column(Enum(MarketType))
    outcome_key: Mapped[str] = mapped_column(String(32))
    outcome_label: Mapped[str] = mapped_column(String(64))
    odds_value: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    match: Mapped["Match"] = relationship(back_populates="odds")


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    market: Mapped[MarketType] = mapped_column(Enum(MarketType))
    payload_json: Mapped[str] = mapped_column(Text)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    market: Mapped[MarketType] = mapped_column(Enum(MarketType))
    home_prob: Mapped[float | None] = mapped_column(Float, nullable=True)
    draw_prob: Mapped[float | None] = mapped_column(Float, nullable=True)
    away_prob: Mapped[float | None] = mapped_column(Float, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    model_version_id: Mapped[int | None] = mapped_column(ForeignKey("model_versions.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    match: Mapped["Match"] = relationship(back_populates="predictions")
    user: Mapped["User | None"] = relationship(back_populates="predictions")
    result: Mapped["PredictionResult | None"] = relationship(back_populates="prediction")


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), unique=True)
    actual_outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)
    brier_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    prediction: Mapped["Prediction"] = relationship(back_populates="result")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan: Mapped[str] = mapped_column(String(32), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class UserSelection(Base):
    __tablename__ = "user_selections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    market: Mapped[str] = mapped_column(String(16))
    outcome_key: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User | None"] = relationship(back_populates="selections")


class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    value: Mapped[str] = mapped_column(String(255))


class RefreshState(Base):
    __tablename__ = "refresh_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_successful_refresh: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_successful_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refresh_status: Mapped[str] = mapped_column(String(32), default="idle")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(String(64), default="DEMO provider")
