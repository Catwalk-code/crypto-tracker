import asyncpg
import os
from dotenv import load_dotenv
from decimal import Decimal
from services import get_current_price

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def convert_decimal_to_float(data: dict) -> dict:
    return {
        key: float(value) if isinstance(value, Decimal) else value
        for key, value in data.items()
    }


async def init_db():
    """Create tables when start server"""
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id SERIAL PRIMARY KEY,
            coin VARCHAR(10) NOT NULL,
            amount DECIMAL(20, 8) NOT NULL,
            buy_price DECIMAL(20,8) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await conn.close()

async def get_holdings() -> list[dict]:
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM holdings ORDER BY id")
    await conn.close()
    
    result = []
    for r in rows:
        dictionary = dict(r.items())
        converted = convert_decimal_to_float(dictionary)
        result.append(converted)

    return result 

async def get_holding_by_id(holding_id: int) -> dict | None:
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM holdings WHERE id = $1", holding_id)
    await conn.close()
    dictionary = dict(row)

    return convert_decimal_to_float(dictionary)

async def create_holding(coin: str, amount: float, buy_price:float) -> dict:
    conn = await asyncpg.connect(DATABASE_URL)
    
    price = await get_current_price(coin)
    if price is None:
        await conn.close()
        raise HTTPException(status_code=404, detail="Coin not found on Binance")

    row = await conn.fetchrow(
        """
        INSERT INTO holdings (coin, amount, buy_price)
        VALUES ($1, $2, $3)
        RETURNING *
        """, 
        coin, amount, buy_price
    )
    await conn.close()

    result = convert_decimal_to_float(dict(row.items()))
    result["current_price"] = price
    invested = result["amount"] * result["buy_price"]
    current_value = result["amount"] * price
    result["profit_loss"] = current_value - invested

    return result

async def delete_holding(holding_id: int) -> bool:
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.execute("DELETE FROM holdings WHERE id = $1", holding_id)
    await conn.close()
    return result == "DELETE 1"