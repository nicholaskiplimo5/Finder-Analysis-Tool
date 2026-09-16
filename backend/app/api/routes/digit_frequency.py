from fastapi import APIRouter, Depends, Query

from app.analysis.digit_frequency_service import DigitFrequencyService
from app.api.dependencies import get_digit_frequency_service, get_settings, valid_symbol
from app.api.schemas import DigitFrequencyResponse, DigitFrequencySummaryResponse, MultipleComparisonResponse
from app.config import Settings

router = APIRouter(prefix="/api/digit-frequency", tags=["digit-frequency"])


@router.get("/{symbol}", response_model=DigitFrequencyResponse)
async def get_digit_frequency(
    symbol: str = Depends(valid_symbol),
    window: int = Query(5000, ge=100, le=200_000),
    service: DigitFrequencyService = Depends(get_digit_frequency_service),
) -> DigitFrequencyResponse:
    result = await service.get(symbol, window)
    return DigitFrequencyResponse.from_result(result)


@router.get("", response_model=DigitFrequencySummaryResponse)
async def get_digit_frequency_summary(
    window: int = Query(5000, ge=100, le=200_000),
    service: DigitFrequencyService = Depends(get_digit_frequency_service),
    settings: Settings = Depends(get_settings),
) -> DigitFrequencySummaryResponse:
    results, correction = await service.get_many(settings.symbols, window)
    return DigitFrequencySummaryResponse(
        results={s: DigitFrequencyResponse.from_result(r) for s, r in results.items()},
        correction=MultipleComparisonResponse.from_result(correction),
    )
