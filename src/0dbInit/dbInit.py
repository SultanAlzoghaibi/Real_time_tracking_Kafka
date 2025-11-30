import psycopg2
from psycopg2 import sql

# -----------------------------
# PostgreSQL connection config
# -----------------------------
DB_NAME = "trades"
DB_USER = "sultanalzoghaibi"
DB_PASS = ""         # update if needed
DB_HOST = "localhost"
DB_PORT = "5432"


# -----------------------------
# SQL SCHEMA DEFINITIONS
# -----------------------------

CREATE_TRADES_TABLE = """
CREATE TABLE IF NOT EXISTS public.trades (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    trade_time BIGINT,
    price NUMERIC,
    quantity NUMERIC,
    stream TEXT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ASSET_VOLATILITY = """
CREATE TABLE IF NOT EXISTS public.asset_volatility (
    symbol TEXT PRIMARY KEY,
    avr_volatility DOUBLE PRECISION NOT NULL,
    last_price NUMERIC(18,8)
);
"""

CREATE_ALERTS_TABLE = """
CREATE TABLE IF NOT EXISTS public.alerts (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""


# -----------------------------
# MAIN INITIALIZER FUNCTION
# -----------------------------
def init_database():
    print("📡 Connecting to PostgreSQL...")

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
    )
    cursor = conn.cursor()

    print("⚙️ Creating tables (if not exist)...")

    cursor.execute(CREATE_TRADES_TABLE)
    cursor.execute(CREATE_ASSET_VOLATILITY)
    cursor.execute(CREATE_ALERTS_TABLE)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Database schema initialized successfully!")


# -----------------------------
# RUN INITIALIZER
# -----------------------------
if __name__ == "__main__":
    init_database()