-- file name: create_schema.sql
-- to run in terminal: psql -d trades -f create_schema.sql

CREATE TABLE IF NOT EXISTS asset_volatility (
    symbol TEXT PRIMARY KEY,
    avr_volatility NUMERIC,
    last_price NUMERIC
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    trade_time BIGINT,
    price NUMERIC,
    quantity NUMERIC,
    stream TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    message TEXT,
    alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
