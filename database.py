import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    """Create tables when start server"""
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execite("""
        CREATE TABLE IF NOT EXISTS holdings (
            id SERIAL PRIMARY KEY,
            coin VARCHAR(10) NOT NULL,
            amount DECIMAL(20, 8) NOT NULL,
            buy_price DECIMAL(20,8) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await conn.close()
    print("Database initialized")

async def get_all_holdings() -> list[dict]:
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM holdings ORDER BY id")
    await conn.close()
    return [dict(row) for row in rows]

async def get_holding_by_id(holding_id: int) -> dict | None:
    conn = await asyncpg.connect(DATABASE_URL)
    row = await asyncpg.fetchrow("SELECT * FROM holdings WHERE id = $1", holding_id)
    await conn.close()
    return dict(row) if row else None

async def create_holding(coin: str, amount: float, buy_price:float) -> dict:
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow(
        """
        INSERT INTO holdings (coin, amount, buy_price)
        VALUES ($1, $2, $3)
        RETURNING *
        """, 
        coin, amount, buy_price
    )
    await conn.close()
    return dict(row)

async def delete_holding(holding_id: int) -> bool:
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.execute("DELETE FROM holdings WHERE id = $1", holding_id)
    await conn.close()
    return result == "DELETE 1"