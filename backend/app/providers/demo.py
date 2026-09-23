from datetime import datetime, timedelta
import hashlib
import random

from app.providers.base import DataProvider, ProviderMatch, ProviderOddsOutcome

LEAGUES = [
    ("ENG", "English League (DEMO)", "England"),
    ("ESP", "Spanish League (DEMO)", "Spain"),
    ("ITA", "Italian League (DEMO)", "Italy"),
    ("GER", "German League (DEMO)", "Germany"),
]

TEAMS = {
    "ENG": ["London City DEMO", "Manchester DEMO", "Liverpool DEMO", "Leeds DEMO", "Brighton DEMO", "Newcastle DEMO"],
    "ESP": ["Madrid DEMO", "Barcelona DEMO", "Seville DEMO", "Valencia DEMO", "Bilbao DEMO", "Malaga DEMO"],
    "ITA": ["Milan DEMO", "Rome DEMO", "Turin DEMO", "Naples DEMO", "Florence DEMO", "Verona DEMO"],
    "GER": ["Munich DEMO", "Dortmund DEMO", "Berlin DEMO", "Leipzig DEMO", "Frankfurt DEMO", "Cologne DEMO"],
}


def _odds_1x2(rng: random.Random) -> list[ProviderOddsOutcome]:
    h, d, a = sorted([rng.uniform(1.4, 4.5) for _ in range(3)], reverse=True)
    return [
        ProviderOddsOutcome("home", "1", round(h, 2)),
        ProviderOddsOutcome("draw", "X", round(d, 2)),
        ProviderOddsOutcome("away", "2", round(a, 2)),
    ]


def _odds_ou(rng: random.Random) -> list[ProviderOddsOutcome]:
    return [
        ProviderOddsOutcome("over25", "O 2.5", round(rng.uniform(1.6, 2.2), 2)),
        ProviderOddsOutcome("under25", "U 2.5", round(rng.uniform(1.6, 2.2), 2)),
    ]


def _odds_btts(rng: random.Random) -> list[ProviderOddsOutcome]:
    return [
        ProviderOddsOutcome("yes", "Yes", round(rng.uniform(1.5, 2.1), 2)),
        ProviderOddsOutcome("no", "No", round(rng.uniform(1.7, 2.3), 2)),
    ]


def _odds_dc(rng: random.Random) -> list[ProviderOddsOutcome]:
    return [
        ProviderOddsOutcome("1x", "1X", round(rng.uniform(1.2, 1.8), 2)),
        ProviderOddsOutcome("12", "12", round(rng.uniform(1.2, 1.7), 2)),
        ProviderOddsOutcome("x2", "X2", round(rng.uniform(1.2, 1.8), 2)),
    ]


def _odds_htft(rng: random.Random) -> list[ProviderOddsOutcome]:
    return [
        ProviderOddsOutcome("hh", "H/H", round(rng.uniform(2.5, 5.0), 2)),
        ProviderOddsOutcome("hd", "H/D", round(rng.uniform(8.0, 15.0), 2)),
        ProviderOddsOutcome("ha", "H/A", round(rng.uniform(10.0, 20.0), 2)),
    ]


class DemoDataProvider(DataProvider):
    name = "DEMO provider"
    is_demo = True

    def fetch_matches(self) -> list[ProviderMatch]:
        base = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        seed = int(base.strftime("%Y%m%d"))
        rng = random.Random(seed)
        matches: list[ProviderMatch] = []
        round_num = (seed % 10) + 1

        for code, _, _ in LEAGUES:
            teams = TEAMS[code]
            pairings = [(teams[i], teams[i + 1]) for i in range(0, len(teams) - 1, 2)]
            for idx, (home, away) in enumerate(pairings):
                kickoff = base + timedelta(hours=2 + idx, days=abs(hash(code)) % 2)
                ext = f"DEMO-{code}-R{round_num}-{idx}"
                status = "scheduled"
                home_score = away_score = None
                if idx == 0:
                    status = "live"
                if idx == 1:
                    status = "finished"
                    home_score = rng.randint(0, 3)
                    away_score = rng.randint(0, 3)

                local_rng = random.Random(int(hashlib.md5(ext.encode()).hexdigest()[:8], 16))
                matches.append(
                    ProviderMatch(
                        external_key=ext,
                        league_code=code,
                        home_team=home,
                        away_team=away,
                        round=round_num,
                        season="DEMO 2025/26",
                        kickoff_at=kickoff,
                        status=status,
                        home_score=home_score,
                        away_score=away_score,
                        odds_by_market={
                            "1X2": _odds_1x2(local_rng),
                            "OU": _odds_ou(local_rng),
                            "BTTS": _odds_btts(local_rng),
                            "DC": _odds_dc(local_rng),
                            "HTFT": _odds_htft(local_rng),
                        },
                    ),
                )
        return matches
