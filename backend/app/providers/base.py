from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


class ProviderError(RuntimeError):
    """Expected provider failure that should not discard the current dataset."""


@dataclass
class ProviderOddsOutcome:
    key: str
    label: str
    odds: float


@dataclass
class ProviderMatch:
    external_key: str
    league_code: str
    home_team: str
    away_team: str
    round: int
    season: str
    kickoff_at: datetime
    status: str
    home_score: int | None
    away_score: int | None
    odds_by_market: dict[str, list[ProviderOddsOutcome]]
    league_name: str | None = None
    league_country: str | None = None


class DataProvider(ABC):
    name: str
    is_demo: bool

    def get_next_refresh_at(self) -> datetime | None:
        return None

    @abstractmethod
    def fetch_matches(self) -> list[ProviderMatch]:
        raise NotImplementedError
