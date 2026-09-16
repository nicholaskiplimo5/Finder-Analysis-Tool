from fastapi import APIRouter, Depends, Query

from app.analysis.streak_length_service import StreakLengthService
from app.api.dependencies import get_settings, get_streak_length_service, valid_symbol
from app.api.schemas import (
    MultipleComparisonResponse,
    StreakLengthResponse,
    StreakLengthSummaryResponse,
)
from app.config import Settings

router = APIRouter(prefix="/api/streak-length", tags=["streak-length"])


@router.get("/{symbol}", response_model=StreakLengthResponse)
async def get_streak_length(
    symbol: str = Depends(valid_symbol),
    window: int = Query(5000, ge=100, le=200_000),
    max_bin: int = Query(4, ge=2, le=20),
    service: StreakLengthService = Depends(get_streak_length_service),
) -> StreakLengthResponse:
    result = await service.get(symbol, window, max_bin=max_bin)
    return StreakLengthResponse.from_result(result)


@router.get("", response_model=StreakLengthSummaryResponse)
async def get_streak_length_summary(
    window: int = Query(5000, ge=100, le=200_000),
    service: StreakLengthService = Depends(get_streak_length_service),
    settings: Settings = Depends(get_settings),
) -> StreakLengthSummaryResponse:
    results, correction, skipped = await service.get_many(settings.symbols, window)
    return StreakLengthSummaryResponse(
        results={s: StreakLengthResponse.from_result(r) for s, r in results.items()},
        correction=MultipleComparisonResponse.from_result(correction),
        skipped=skipped,
    )
