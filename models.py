from pydantic import BaseModel

"""Model for creating of active (without id, currnet price)"""
class HoldingCreate(BaseModel):
    coin: str # BTC, ETH, SOL, etc...
    amount: float
    buy_price: float # price in USDT

"""Model for answer (with id, and additional fields)"""
class Holding(BaseModel):
    id: int
    coin: str
    amount: float
    buy_price: float
    currnet_price: float | None = None
    profit_loss: float | None = None

class PortfolioResponse(BaseModel):
    total_value: float
    total_invested: float
    profit_loss: float
    profit_percentage: float
    holdings_count: int
    holdings: list[Holding]