from datetime import datetime, timezone

import httpx

from app.config import settings
from app.providers.base import DataProvider, ProviderError, ProviderMatch, ProviderOddsOutcome


class BetPawaProvider(DataProvider):
    """Public BetPawa Uganda JSON source adapter."""

    name = "BETPAWA Uganda"
    is_demo = False
    next_refresh_at: datetime | None = None

    base_url = "https://www.betpawa.ug"
    seasons_path = "/api/sportsbook/virtual/v2/seasons/list/actual"
    events_path = "/api/sportsbook/virtual/v3/events/list/by-round/{round_id}"

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=settings.betpawa_base_url.rstrip("/"),
            timeout=settings.betpawa_timeout_seconds,
            headers={
                "Accept": "application/x-protobuf",
                "Content-Type": "application/json",
                "Referer": f"{settings.betpawa_base_url.rstrip('/')}/virtual-sports",
                "User-Agent": settings.betpawa_user_agent,
                "x-pawa-brand": "betpawa-uganda",
                "x-pawa-language": "en",
                "devicetype": "web",
            },
        )

    def fetch_matches(self) -> list[ProviderMatch]:
        try:
            with self._client() as client:
                seasons = client.get(
                    self.seasons_path,
                    headers={"Accept": "application/json"},
                )
                if seasons.status_code >= 400:
                    raise ProviderError(f"BetPawa source returned HTTP {seasons.status_code}")
                season_data = seasons.json()
                round_id, season_name, round_number = self._select_round(season_data)
                previous_round = self._previous_round(season_data)
                self.next_refresh_at = self._next_round_start(season_data)
                round_requests = [(round_id, season_name, round_number)]
                if previous_round:
                    round_requests.append(previous_round)
                responses = []
                for index, (requested_round_id, requested_season, requested_number) in enumerate(round_requests):
                    response = client.get(
                        self.events_path.format(round_id=requested_round_id),
                        headers={"Accept": "application/json"},
                    )
                    if response.status_code >= 400:
                        raise ProviderError(f"BetPawa source returned HTTP {response.status_code}")
                    responses.extend(
                        self._parse_event(
                            event,
                            requested_season,
                            requested_number,
                            round_finished=index > 0,
                        )
                        for event in response.json()["responses"]
                    )
                return responses
        except httpx.HTTPError as exc:
            raise ProviderError(f"BetPawa request failed: {type(exc).__name__}") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise ProviderError("BetPawa source returned malformed JSON") from exc

    def fetch_historical_seasons(self, season_ids: list[str]) -> list[ProviderMatch]:
        matches: list[ProviderMatch] = []
        try:
            with self._client() as client:
                for season_id in season_ids:
                    standings = client.get(
                        f"/api/sportsbook/virtual/v2/standings/by-season/{season_id}",
                        headers={"Accept": "application/json"},
                    )
                    standings.raise_for_status()
                    data = standings.json()
                    round_ids = data.get("roundIds", [])
                    if not isinstance(round_ids, list):
                        continue
                    for round_number, round_id in enumerate(round_ids, start=1):
                        response = client.get(
                            self.events_path.format(round_id=round_id),
                            headers={"Accept": "application/json"},
                        )
                        response.raise_for_status()
                        matches.extend(
                            self._parse_event(
                                event,
                                f"#{season_id}",
                                round_number,
                                round_finished=True,
                            )
                            for event in response.json()["responses"]
                        )
        except httpx.HTTPError as exc:
            raise ProviderError(f"BetPawa historical request failed: {type(exc).__name__}") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise ProviderError("BetPawa historical response was malformed") from exc
        if not matches:
            raise ProviderError("BetPawa returned no historical matches")
        return matches

    def get_next_refresh_at(self) -> datetime | None:
        try:
            with self._client() as client:
                response = client.get(self.seasons_path, headers={"Accept": "application/json"})
                response.raise_for_status()
                return self._next_round_start(response.json())
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return None

    def discover_historical_season_ids(self, count: int) -> list[str]:
        if count < 1:
            return []
        try:
            with self._client() as client:
                response = client.get(self.seasons_path, headers={"Accept": "application/json"})
                response.raise_for_status()
                payload = response.json()
                current_ids = [int(item["id"]) for item in payload["items"] if str(item.get("id", "")).isdigit()]
                if not current_ids:
                    raise ProviderError("BetPawa returned no season identifiers")
                candidate = min(current_ids)
                season_ids = set(str(item_id) for item_id in current_ids)
                while len(season_ids) < count and candidate > 0:
                    candidate -= 1
                    standings = client.get(
                        f"/api/sportsbook/virtual/v2/standings/by-season/{candidate}",
                        headers={"Accept": "application/json"},
                    )
                    if standings.status_code == 200:
                        season_ids.add(str(candidate))
                return sorted(season_ids, key=int)[-count:]
        except httpx.HTTPError as exc:
            raise ProviderError(f"BetPawa season discovery failed: {type(exc).__name__}") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise ProviderError("BetPawa season metadata was malformed") from exc

    @staticmethod
    def _select_round(payload: dict) -> tuple[str, str, int]:
        selected = BetPawaProvider._round_candidates(payload)[-1]
        return selected[2], selected[1], selected[3]

    @staticmethod
    def _round_candidates(payload: dict) -> list[tuple[datetime, str, str, int]]:
        now = datetime.now(timezone.utc)
        candidates = []
        for season in payload["items"]:
            for round_data in season["rounds"]:
                start = datetime.fromisoformat(round_data["tradingTime"]["start"].replace("Z", "+00:00"))
                candidates.append((start, season["name"], round_data["id"], int(round_data["name"])))
        if not candidates:
            raise ProviderError("BetPawa returned no rounds")
        active = [candidate for candidate in candidates if candidate[0] <= now]
        return sorted(active or candidates, key=lambda candidate: candidate[0])

    @staticmethod
    def _previous_round(payload: dict) -> tuple[str, str, int] | None:
        candidates = BetPawaProvider._round_candidates(payload)
        if len(candidates) < 2:
            return None
        selected = candidates[-1]
        previous = candidates[-2]
        return previous[2], previous[1], previous[3]

    @staticmethod
    def _next_round_start(payload: dict) -> datetime | None:
        now = datetime.now(timezone.utc)
        starts = [
            datetime.fromisoformat(round_data["tradingTime"]["start"].replace("Z", "+00:00"))
            for season in payload["items"]
            for round_data in season["rounds"]
        ]
        future = [start for start in starts if start > now]
        return min(future) if future else None

    @staticmethod
    def _parse_event(
        event: dict,
        season: str,
        round_number: int,
        round_finished: bool = False,
    ) -> ProviderMatch:
        participants = event["participants"]
        results = event.get("results", {}).get("participantPeriodResults", [])
        participant_types = {
            item["participant"]["id"]: item["participant"].get("type")
            for item in results
        }
        home = next((p for p in participants if participant_types.get(p["id"]) == "HOME"), participants[0])
        away = next((p for p in participants if participant_types.get(p["id"]) == "AWAY"), participants[-1])

        display = event.get("results", {}).get("display", {})
        minute = int(display.get("minute", "0") or 0)
        status = "finished" if round_finished or minute >= 90 else "live" if event.get("results") else "scheduled"

        full_time_scores: dict[str, int] = {}
        current_scores: dict[str, int] = {}
        for item in results:
            for result in item.get("periodResults", []):
                if result.get("type") == "SCORE":
                    participant_id = item["participant"]["id"]
                    if result.get("period", {}).get("slug") == "FULL_TIME_EXCLUDING_OVERTIME":
                        full_time_scores[participant_id] = int(result["result"])
                    if result.get("period", {}).get("slug") == display.get("currentPeriod", {}).get("slug"):
                        current_scores[participant_id] = int(result["result"])

        scores = full_time_scores if status == "finished" else current_scores

        competition = event["competition"]
        return ProviderMatch(
            external_key=f"BETPAWA-{event['id']}",
            league_code=f"BP-{competition['id']}",
            league_name=competition["name"],
            league_country=event.get("region", {}).get("name", ""),
            home_team=home["name"],
            away_team=away["name"],
            round=round_number,
            season=season,
            kickoff_at=datetime.fromisoformat(event["startTime"].replace("Z", "+00:00")).replace(tzinfo=None),
            status=status,
            home_score=scores.get(home["id"]),
            away_score=scores.get(away["id"]),
            odds_by_market=BetPawaProvider._parse_markets(event.get("markets", [])),
        )

    @staticmethod
    def _parse_markets(markets: list[dict]) -> dict[str, list[ProviderOddsOutcome]]:
        market_map = {
            "1X2 - FT": "1X2",
            "Total Score Over/Under - FT": "OU",
            "Both Teams To Score - FT": "BTTS",
            "Double Chance - FT": "DC",
            "HT / FT": "HTFT",
        }
        parsed: dict[str, list[ProviderOddsOutcome]] = {}
        for market in markets:
            market_key = market_map.get(market.get("marketType", {}).get("name"))
            if not market_key:
                continue
            outcomes = parsed.setdefault(market_key, [])
            for row in market.get("row", []):
                handicap = row.get("specifier", {}).get("total") or row.get("handicap")
                for price in row.get("prices", []):
                    odds = price.get("odds")
                    if not isinstance(odds, (int, float)):
                        continue
                    name = str(price.get("name", "")).strip()
                    suffix = f" {handicap}" if market_key == "OU" and handicap else ""
                    outcomes.append(
                        ProviderOddsOutcome(
                            key=f"{name.lower().replace('/', '')}{('_' + str(handicap)).replace('.', '_') if market_key == 'OU' and handicap else ''}",
                            label=f"{name}{suffix}",
                            odds=float(odds),
                        )
                    )
        return parsed
