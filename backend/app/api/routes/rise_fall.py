from fastapi import APIRouter, Depends, Query

from app.analysis.rise_fall_service import RiseFallService
from app.api.dependencies import get_rise_fall_service, get_settings, valid_symbol
from app.api.schemas import MultipleComparisonResponse, RiseFallResponse, RiseFallSummaryResponse
from app.config import Settings

router = APIRouter(prefix="/api/rise-fall", tags=["rise-fall"])


@router.get("/{symbol}", response_model=RiseFallResponse)
async def get_rise_fall(
    symbol: str = Depends(valid_symbol),
    window: int = Query(5000, ge=100, le=200_000),
    service: RiseFallService = Depends(get_rise_fall_service),
) -> RiseFallResponse:
    result = await service.get(symbol, window)
    return RiseFallResponse.from_result(result)


@router.get("", response_model=RiseFallSummaryResponse)
async def get_rise_fall_summary(
    window: int = Query(5000, ge=100, le=200_000),
    service: RiseFallService = Depends(get_rise_fall_service),
    settings: Settings = Depends(get_settings),
) -> RiseFallSummaryResponse:
    results, correction, skipped = await service.get_many(settings.symbols, window)
    return RiseFallSummaryResponse(
        results={s: RiseFallResponse.from_result(r) for s, r in results.items()},
        correction=MultipleComparisonResponse.from_result(correction),
        skipped=skipped,
    )
