from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.analysis.acf_service import ACFService
from app.analysis.conditional_digit_service import ConditionalDigitService
from app.analysis.digit_frequency_service import DigitFrequencyService
from app.analysis.rise_fall_service import RiseFallService
from app.analysis.streak_length_service import StreakLengthService
from app.api.errors import install_error_handlers
from app.api.routes import (
    acf,
    conditional_digit,
    digit_frequency,
    health,
    live,
    rise_fall,
    streak_length,
    symbols,
)
from app.config import Settings
from app.db import create_pool

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    pool = await create_pool(settings.database_url)

    app.state.settings = settings
    app.state.pool = pool
    app.state.digit_frequency_service = DigitFrequencyService(pool)
    app.state.acf_service = ACFService(pool)
    app.state.conditional_digit_service = ConditionalDigitService(pool)
    app.state.streak_length_service = StreakLengthService(pool)
    app.state.rise_fall_service = RiseFallService(pool)

    yield

    await pool.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Finder Analysis Tool API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    install_error_handlers(app)

    app.include_router(health.router)
    app.include_router(symbols.router)
    app.include_router(digit_frequency.router)
    app.include_router(acf.router)
    app.include_router(conditional_digit.router)
    app.include_router(streak_length.router)
    app.include_router(rise_fall.router)
    app.include_router(live.router)

    return app


app = create_app()
