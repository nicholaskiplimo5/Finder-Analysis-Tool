"""FastAPI dependency providers.

Everything pulls from `request.app.state`, set up once in the app
lifespan (real DB pool + services in production) or directly by a test
building a minimal app around fake services -- route code never
constructs a service or a pool itself.
"""

import asyncpg
from fastapi import Depends, HTTPException, Request

from app.analysis.acf_service import ACFService
from app.analysis.conditional_digit_service import ConditionalDigitService
from app.analysis.digit_frequency_service import DigitFrequencyService
from app.analysis.rise_fall_service import RiseFallService
from app.analysis.streak_length_service import StreakLengthService
from app.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.pool


def get_digit_frequency_service(request: Request) -> DigitFrequencyService:
    return request.app.state.digit_frequency_service


def get_acf_service(request: Request) -> ACFService:
    return request.app.state.acf_service


def get_conditional_digit_service(request: Request) -> ConditionalDigitService:
    return request.app.state.conditional_digit_service


def get_streak_length_service(request: Request) -> StreakLengthService:
    return request.app.state.streak_length_service


def get_rise_fall_service(request: Request) -> RiseFallService:
    return request.app.state.rise_fall_service


def valid_symbol(symbol: str, settings: Settings = Depends(get_settings)) -> str:
    """Path-param dependency: 404s on a symbol outside the configured
    universe, rather than letting an arbitrary string reach the DB layer
    and fail there with a less clear error."""
    if symbol not in settings.symbols:
        raise HTTPException(status_code=404, detail=f"unknown symbol: {symbol!r}")
    return symbol
