import asyncpg
from fastapi import APIRouter, Depends

from app.api.dependencies import get_pool
from app.api.schemas import SymbolInfo
from app.db import fetch_all_symbol_meta

router = APIRouter(prefix="/api", tags=["symbols"])


@router.get("/symbols", response_model=list[SymbolInfo])
async def list_symbols(pool: asyncpg.Pool = Depends(get_pool)) -> list[SymbolInfo]:
    metas = await fetch_all_symbol_meta(pool)
    return [
        SymbolInfo(symbol=m.symbol, pip_size=str(m.pip_size), decimals=m.decimals)
        for m in metas
    ]
