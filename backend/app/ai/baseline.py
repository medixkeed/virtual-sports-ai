"""Transparent statistical baseline — not a trained ML model on demo outcomes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PredictionResultDTO:
    home_prob: float | None
    draw_prob: float | None
    away_prob: float | None
    message: str | None
    is_demo: bool
    input_ref: str


def _normalize(h: float, d: float, a: float) -> tuple[float, float, float]:
    total = h + d + a
    if total <= 0:
        return 33.33, 33.33, 33.34
    return (h / total * 100, d / total * 100, a / total * 100)


def predict_from_odds(
    odds_home: float | None,
    odds_draw: float | None,
    odds_away: float | None,
    *,
    is_demo: bool,
    match_id: int,
    form_signal: tuple[float, float, float] | None = None,
) -> PredictionResultDTO:
    if not odds_home or not odds_draw or not odds_away:
        return PredictionResultDTO(
            None,
            None,
            None,
            "Prediction unavailable — insufficient data.",
            is_demo,
            f"match:{match_id}",
        )

    implied_h = 1.0 / odds_home
    implied_d = 1.0 / odds_draw
    implied_a = 1.0 / odds_away
    h, d, a = _normalize(implied_h, implied_d, implied_a)

    msg = (
        "Live PDF-inspired heuristic: odds blended with last-five form and goal signals. "
        "Patterns are experimental; no outcome is guaranteed."
    )
    if form_signal is not None:
        h, d, a = _normalize(
            h * 0.7 + form_signal[0] * 0.3,
            d * 0.7 + form_signal[1] * 0.3,
            a * 0.7 + form_signal[2] * 0.3,
        )
    if is_demo:
        msg = (
            "DEMO baseline: implied probabilities from sample odds only. "
            "Not validated for real betting decisions."
        )

    return PredictionResultDTO(h, d, a, msg, is_demo, f"odds:1x2:match:{match_id}")


def predict_non_1x2(market: str, is_demo: bool, match_id: int) -> PredictionResultDTO:
    return PredictionResultDTO(
        None,
        None,
        None,
        f"DEMO baseline for {market}: detailed probabilities require validated historical data.",
        is_demo,
        f"market:{market}:match:{match_id}",
    )
