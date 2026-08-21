from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

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

app = FastAPI()

@app.post("/holdings", response_model=Holding)
def create_holding(holding: HoldingCreate):
    "Global is not good practice. Later it will be replaced with PostgreSQL"
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

@app.get("/")
def root():
    return{"message": "Крипто-портфель трекер"}
