from fastapi import FastAPI
from fastapi import HTTPException

from models import  Holding, HoldingCreate, PortfolioResponse
from services import get_current_price

holdings = []
next_id = 1
app = FastAPI()


@app.post("/holdings", response_model=Holding)
async def create_holding(holding: HoldingCreate):
    '''Using global value is not a good practice. Later it will be replaced 
    with PostgreSQL'''
    # We say to Python use value that has been created 
    # globally (not in function)
    global next_id 

    price = await get_current_price(holding.coin)

    #If price = None, than coin doesn't exist
    if price is None:
        raise HTTPException(status_code=400, detail="Coin not found")

    # Copy all fields from holding to the dictionary
    data = holding.model_dump()
    
    #Add id
    data["id"] = next_id
    next_id += 1

    #Create Holding from dictionary
    new_holding = Holding(**data)
    holdings.append(new_holding)

    return new_holding



@app.get("/holdings", response_model=list[Holding])
async def get_holdings():
    for h in holdings:
        current_price = await get_current_price(h.coin)

        #If None, than coin is not found
        if current_price is None:
            h.currnet_price = 0.0 #set 0 so as not to fall
            h.profit_loss = 0.0
            continue #Skip this coin add go to the next

        h.currnet_price = current_price
        invested = h.amount * h.buy_price
        current_value= h.amount * current_price
        h.profit_loss = current_value - invested

    return holdings



@app.get("/holdings/{holding_id}", response_model=Holding)
def get_holding(holding_id: int):
    for h in holdings:
        if h.id == holding_id:
            return h

    raise HTTPException(status_code=404, detail="holding not found")



@app.delete("/holdings/{holding_id}")
def delete_holding(holding_id: int):
    global holdings
    for i, h in enumerate(holdings):
        if h.id == holding_id:
            holdings.pop(i)
            return {"message": f"Holding {holding_id} deleted"}

    # If not found        
    raise HTTPException(status_code=404, detail="Holding not found")



@app.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
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
        current_price = await get_current_price(h.coin)
        h.currnet_price = current_price

        invested = h.amount * h.buy_price
        current_value = h.amount * current_price

        h.profit_loss = current_value - invested

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