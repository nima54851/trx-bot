"""
能量API路由
"""
from fastapi import APIRouter, HTTPException
from schemas import EnergyPriceRequest, EnergyPriceResponse, EnergyQuoteResponse
from services import lease_service
from config import settings

router = APIRouter()


@router.post("/price", response_model=EnergyPriceResponse)
async def calculate_energy_price(req: EnergyPriceRequest):
    """计算能量租赁价格"""
    if req.energy_amount < settings.MIN_ENERGY or req.energy_amount > settings.MAX_ENERGY:
        raise HTTPException(
            status_code=400,
            detail=f"能量范围: {settings.MIN_ENERGY} ~ {settings.MAX_ENERGY}"
        )
    if req.rent_days < settings.MIN_RENT_DAYS or req.rent_days > settings.MAX_RENT_DAYS:
        raise HTTPException(
            status_code=400,
            detail=f"租用天数: {settings.MIN_RENT_DAYS} ~ {settings.MAX_RENT_DAYS}"
        )

    trx_amount = lease_service.calculate_price(req.energy_amount, req.rent_days)
    return EnergyPriceResponse(
        energy_amount=req.energy_amount,
        rent_days=req.rent_days,
        trx_amount=trx_amount,
        energy_price_per_day=settings.ENERGY_PRICE_PER_DAY,
    )


@router.get("/quote", response_model=EnergyQuoteResponse)
async def get_price_quote():
    """获取能量定价表"""
    prices = []
    for energy in [5000, 10000, 50000, 100000, 200000, 500000]:
        for days in [1, 3, 7, 15, 30]:
            trx = lease_service.calculate_price(energy, days)
            prices.append({
                "energy": energy,
                "days": days,
                "trx": trx,
            })
    return EnergyQuoteResponse(prices=prices)


@router.get("/config")
async def get_energy_config():
    """获取能量配置"""
    return {
        "min_energy": settings.MIN_ENERGY,
        "max_energy": settings.MAX_ENERGY,
        "min_days": settings.MIN_RENT_DAYS,
        "max_days": settings.MAX_RENT_DAYS,
        "price_per_1000_per_day": settings.ENERGY_PRICE_PER_DAY,
        "network": settings.TRON_NETWORK,
    }
