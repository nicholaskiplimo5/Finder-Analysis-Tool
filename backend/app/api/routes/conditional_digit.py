from fastapi import APIRouter, Depends, Query

from app.analysis.conditional_digit_service import ConditionalDigitService
from app.api.dependencies import get_conditional_digit_service, get_settings, valid_symbol
from app.api.schemas import (
    ConditionalDigitResponse,
    ConditionalDigitSummaryResponse,
    MultipleComparisonResponse,
)
from app.config import Settings

router = APIRouter(prefix="/api/conditional-digit", tags=["conditional-digit"])


@router.get("/{symbol}", response_model=ConditionalDigitResponse)
async def get_conditional_digit(
    symbol: str = Depends(valid_symbol),
    window: int = Query(5000, ge=100, le=200_000),
    service: ConditionalDigitService = Depends(get_conditional_digit_service),
) -> ConditionalDigitResponse:
    result = await service.get(symbol, window)
    return ConditionalDigitResponse.from_result(result)


@router.get("", response_model=ConditionalDigitSummaryResponse)
async def get_conditional_digit_summary(
    window: int = Query(5000, ge=100, le=200_000),
    service: ConditionalDigitService = Depends(get_conditional_digit_service),
    settings: Settings = Depends(get_settings),
) -> ConditionalDigitSummaryResponse:
    results, correction, skipped = await service.get_many(settings.symbols, window)
    return ConditionalDigitSummaryResponse(
        results={s: ConditionalDigitResponse.from_result(r) for s, r in results.items()},
        correction=MultipleComparisonResponse.from_result(correction),
        skipped=skipped,
    )
