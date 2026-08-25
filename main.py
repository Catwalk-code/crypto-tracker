from fastapi import FastAPI
from fastapi import HTTPException

from models import  Holding, HoldingCreate, PortfolioResponse
from services import get_current_price
from database import init_db, get_holdings, get_holding_by_id, create_holding, delete_holding


app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/holdings", response_model=Holding)
async def create_holding_endpoint(holding: HoldingCreate):
    price = await get_current_price(holding.coin)

    #If price = None, than coin doesn't exist
    if price is None:
        raise HTTPException(status_code=400, detail="Coin not found")

    new_holding = await create_holding(
        coin=holding.coin,
        amount=holding.amount,
        buy_price=holding.buy_price
    )

    new_holding["current_price"] = price
    invested = new_holding["amount"] * new_holding["buy_price"]
    current_value = new_holding["amount"] * price
    new_holding["profit_loss"] = current_value - invested

    return new_holding


@app.get("/holdings", response_model=list[Holding])
async def get_holdings_endpoint():
    holdings = await get_holdings()

    for h in holdings:
        current_price = await get_current_price(h["coin"])

        #If None, than coin is not found
        if current_price is None:
            h["currnet_price"] = 0.0 #set 0 so as not to fall
            h["profit_loss"] = 0.0
            continue #Skip this coin add go to the next

        h["currnet_price"] = current_price
        invested = h["amount"] * h["buy_price"]
        current_value= h["amount"] * current_price
        h["profit_loss"] = current_value - invested

    return holdings


@app.get("/holdings/{holding_id}", response_model=Holding)
async def get_holding_by_id_endpoint(holding_id: int):
    holding = await get_holding_by_id(holding_id)

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    current_price = await get_current_price(holding["coin"])
    if current_price is not None:
        holding["current_price"] = current_price
        invested = holding["amount"] * holding["buy_price"]
        current_value = holding["amount"] * current_price
        holding["profit_loss"] = current_value - invested
    else:
        holding["current_price"] = 0.0
        holding["profit_loss"] = 0.0

    return holding
    

@app.delete("/holdings/{holding_id}")
async def delete_holding_endpoint(holding_id: int):
    deleted = await delete_holding(holding_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Holding not found")

    return {"message": f"Holding {holding_id} deleted"}


@app.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    holdings = await get_holdings()

    if not holdings:
        return PortfolioResponse(
            total_value=0.0,
            total_invested=0.0,
            profit_loss=0.0,
            profit_percentage=0.0,
            holdings_count=0.0,
            holdings=[]
        )

    total_value = 0.0
    total_invested = 0.0

    #Update prices for all actives
    for h in holdings:
        current_price = await get_current_price(h["coin"])
        
        if current_price is None:
            h["current_price"] = 0.0
            h["profit_loss"] = 0.0
            continue
        
        h["currnet_price"] = current_price

        invested = h["amount"] * h["buy_price"]
        current_value = h["amount"] * current_price

        h["profit_loss"] = current_value - invested

        total_value+= current_value
        total_invested+=invested

    profit_loss = total_value - total_invested

    #Protection against divison by zero
    if total_invested > 0:
        profit_percentage = (profit_loss / total_invested) * 100
    else:
        profit_percentage = 0.0
    
    return PortfolioResponse(
        total_value=total_value,
        total_invested=total_invested,
        profit_loss=profit_loss,
        profit_percentage=round(profit_percentage, 2),
        holdings_count=len(holdings),
        holdings=holdings
    )


@app.get("/")
def root():
    return{"message": "Crypto Portfolio tracker"}