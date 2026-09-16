from fastapi import APIRouter, Depends, Query

from app.analysis.acf_service import ACFService
from app.api.dependencies import get_acf_service, valid_symbol
from app.api.schemas import ACFResponse, ACFWithCorrectionResponse, MultipleComparisonResponse

router = APIRouter(prefix="/api/acf", tags=["acf"])

# No multi-symbol "/api/acf" summary endpoint: ACF produces one p-value
# per lag, not one per symbol, so there's no single scalar to correct
# across symbols without inventing an arbitrary reduction (worst lag?
# lag 1 only?). Each symbol's own per-lag correction is already returned
# below; a cross-symbol view can be added once there's a concrete need
# for it and a defensible way to collapse a symbol's lags to one number.


@router.get("/{symbol}", response_model=ACFWithCorrectionResponse)
async def get_acf(
    symbol: str = Depends(valid_symbol),
    window: int = Query(5000, ge=100, le=200_000),
    max_lag: int = Query(20, ge=1, le=500),
    service: ACFService = Depends(get_acf_service),
) -> ACFWithCorrectionResponse:
    result, correction = await service.get_with_lag_correction(symbol, window, max_lag)
    return ACFWithCorrectionResponse(
        acf=ACFResponse.from_result(result),
        lag_correction=MultipleComparisonResponse.from_result(correction),
    )
