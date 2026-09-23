from datetime import datetime
from types import SimpleNamespace

import pytest

from app.providers.betpawa import BetPawaProvider
from app.providers.base import ProviderError, ProviderMatch, ProviderOddsOutcome
from app.services.refresh import _validate_matches


class FakeClient:
    def __init__(self, responses):
        self.responses = responses
        self.requested_path = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def get(self, path, **_kwargs):
        self.requested_path = path
        return self.responses[path]


def test_betpawa_parses_json_fixture(monkeypatch):
    event = {
        "id": "123",
        "name": "AAA - BBB",
        "participants": [{"id": "1", "name": "AAA"}, {"id": "2", "name": "BBB"}],
        "startTime": "2026-09-23T10:00:00Z",
        "competition": {"id": "7794", "name": "English League"},
        "region": {"name": "England"},
        "markets": [
            {"marketType": {"name": "1X2 - FT"}, "row": [{"prices": [
                {"name": "1", "odds": 2.1}, {"name": "X", "odds": 3.2}, {"name": "2", "odds": 3.4}
            ]}]},
            {"marketType": {"name": "Total Score Over/Under - FT"}, "row": [{
                "specifier": {"total": "2.5"}, "prices": [{"name": "Over", "odds": 1.8}, {"name": "Under", "odds": 2.0}]
            }]},
            {"marketType": {"name": "Both Teams To Score - FT"}, "row": [{"prices": [{"name": "Yes", "odds": 1.7}]}]},
            {"marketType": {"name": "Double Chance - FT"}, "row": [{"prices": [{"name": "1X", "odds": 1.3}]}]},
            {"marketType": {"name": "HT / FT"}, "row": [{"prices": [{"name": "1/1", "odds": 3.5}]}]},
        ],
    }
    seasons = {"items": [{"name": "#1", "rounds": [{"id": "round-1", "name": "01", "tradingTime": {"start": "2026-09-23T00:00:00Z"}}]}]}
    responses = {
        BetPawaProvider.seasons_path: SimpleNamespace(status_code=200, json=lambda: seasons),
        BetPawaProvider.events_path.format(round_id="round-1"): SimpleNamespace(status_code=200, json=lambda: {"responses": [event]}),
    }
    client = FakeClient(responses)
    monkeypatch.setattr(BetPawaProvider, "_client", lambda _self: client)

    matches = BetPawaProvider().fetch_matches()

    assert matches[0].external_key == "BETPAWA-123"
    assert matches[0].home_team == "AAA"
    assert matches[0].league_name == "English League"
    assert set(matches[0].odds_by_market) == {"1X2", "OU", "BTTS", "DC", "HTFT"}
    assert matches[0].odds_by_market["OU"][0].label == "Over 2.5"


def test_betpawa_reports_http_failures(monkeypatch):
    response = SimpleNamespace(status_code=403)
    client = FakeClient({BetPawaProvider.seasons_path: response})
    monkeypatch.setattr(BetPawaProvider, "_client", lambda _self: client)

    with pytest.raises(ProviderError, match="HTTP 403"):
        BetPawaProvider().fetch_matches()


def _match(odds_by_market):
    return ProviderMatch(
        external_key="source-1",
        league_code="L1",
        home_team="Home",
        away_team="Away",
        round=1,
        season="2026",
        kickoff_at=datetime.utcnow(),
        status="scheduled",
        home_score=None,
        away_score=None,
        odds_by_market=odds_by_market,
    )


def test_validation_allows_missing_optional_odds():
    _validate_matches([_match({})])


def test_validation_rejects_invalid_odds():
    with pytest.raises(ProviderError, match="invalid odds"):
        _validate_matches(
            [_match({"1X2": [ProviderOddsOutcome("home", "1", 0.5)]})]
        )
