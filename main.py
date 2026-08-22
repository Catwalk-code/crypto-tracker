from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
import httpx

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

holdings = []
next_id = 1
app = FastAPI()

@app.post("/holdings", response_model=Holding)
def create_holding(holding: HoldingCreate):
    "Global is not a good practice. Later it will be replaced with PostgreSQL"
    global next_id # We say to Python use value that has been created globally (not in function)

    # Copy al fields from holding to the dictionary
    data = holding.model_dump()
    
    #Add id
    data["id"] = next_id
    next_id += 1

    #Create Holding from dictionary
    new_holding = Holding(**data)
    holdings.append(new_holding)

    return new_holding

@app.get("/holdings", response_model=list[Holding])
def get_holdings():
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

async def get_current_price(coin:str) -> float:
    """Getting current price of coin using Binance API"""
    
    #Binance use symols like BTCUSDT, ETHUSDT
    symbol = f"{coin}USDT"

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    '''I found that creating a user using a fuction is a bad idea, the app 
    will work faster in case if user is created in the start of server. This should be rewrite using lifespan'''
    async with httpx.AsyncCLient() as client:
        response = await client.get(url)

        #If not found
        if response.status_code != 200:
            print(f"Error when receiving the price {coin}: {response.status_code}")
            return 0
        
        data = response.json()
        price = float(data["price"])
        return price

@app.get("/")
def root():
    return{"message": "Крипто-портфель трекер"}