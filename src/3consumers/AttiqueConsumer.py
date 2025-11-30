import json
import psycopg2
from decimal import Decimal
from confluent_kafka import Consumer

# --- PostgreSQL connection ---
# This connects our Python code to the "trades" database in PostgreSQL.
conn = psycopg2.connect(
    dbname='trades',
    user='sultanalzoghaibi',
    password='',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

# --- Kafka Consumer config ---
# This sets up the Kafka consumer to read messages from the "binance" topic.
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(conf)
consumer.subscribe(['binance'])

print("📡 Listening for messages...\n")

# How sensitive we want the alerts to be (extra % beyond normal)
X = 3.0  # this can be changed if needed

# EWMA weight: 10% new data, 90% past avg
ALPHA = 0.1

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"⚠️ Kafka error: {msg.error()}")
            continue

        # Some producers may send messages without a key,
        # so we guard against msg.key() being None.
        raw_key = msg.key().decode('utf-8') if msg.key() else None

        raw_value = msg.value().decode('utf-8')

        try:
            parsed = json.loads(raw_value)
            trade = parsed["data"]

            symbol = trade["s"]
            trade_time = trade["T"]
            price = Decimal(trade["p"])
            quantity = Decimal(trade["q"])
            stream = parsed.get("stream", "")

            # ----------------------------------------------------------------------
            # SCHEMA USAGE: "asset_volatility" table = where each symbol is organized
            # ----------------------------------------------------------------------
            # This table stores:
            #   symbol (name such as BTCUSDT)
            #   avr_volatility (normal volatility % that we are learning)
            #   last_price (needed to compare new prices)
            #
            # We SELECT values from this schema so we know:
            #   - what is normal movement for this crypto?
            #   - what price did we see last?
            cursor.execute("""
                SELECT avr_volatility, last_price
                FROM asset_volatility
                WHERE symbol = %s
            """, (symbol,))
            row = cursor.fetchone()

            if row is None:
                # ------------------------------------------------------------------
                # SCHEMA MAINTENANCE: inserting new symbol into asset_volatility
                # ------------------------------------------------------------------
                # If crypto symbol not found, we add it into the schema.
                cursor.execute("""
                    INSERT INTO asset_volatility (symbol, avr_volatility, last_price)
                    VALUES (%s, %s, %s)
                """, (symbol, 5.0, price))
                conn.commit()
            else:
                avr_vol, last_price = row

                if last_price is not None and last_price != 0:
                    change_pct = abs((price - last_price) / last_price) * 100

                    # ------------------------------------------------------------------
                    # NOTIFIER BLOCK: detects movement > (normal + X)
                    # ------------------------------------------------------------------
                    if float(change_pct) > (float(avr_vol) + X):
                        alert_text = (
                            f"🚨 {symbol} abnormal move! Change: {float(change_pct):.2f}% "
                            f"(normal ~{float(avr_vol):.2f}% + X={X}%)"
                        )
                        print(alert_text)

                        # Save alert in alerts table
                        cursor.execute("""
                            INSERT INTO alerts (symbol, message)
                            VALUES (%s, %s)
                        """, (symbol, alert_text))
                        conn.commit()

                    # ------------------------------------------------------------------
                    # SCHEMA UPDATE: keeping avr_volatility current using EWMA
                    # ------------------------------------------------------------------
                    # EWMA formula updates the volatility stored in the schema
                    new_avr = ALPHA * float(change_pct) + (1 - ALPHA) * float(avr_vol)

                    cursor.execute("""
                        UPDATE asset_volatility
                        SET last_price = %s,
                            avr_volatility = %s
                        WHERE symbol = %s
                    """, (price, new_avr, symbol))
                    conn.commit()
                else:
                    cursor.execute("""
                        UPDATE asset_volatility
                        SET last_price = %s
                        WHERE symbol = %s
                    """, (price, symbol))
                    conn.commit()

            # ----------------------------------------------------------------------
            # RAW MARKET DATA STORAGE: "trades" table = historical data
            # ----------------------------------------------------------------------
            # This table stores EVERY trade event we receive from Binance:
            #   symbol       → which crypto was traded (ex: BTCUSDT)
            #   trade_time   → exact timestamp of the trade (ms)
            #   price        → price for this specific trade
            #   quantity     → how much crypto was traded
            #   stream       → Binance stream type (trade feed source)
            #
            # Purpose of this table:
            #   ✓ Historical analytics (candlesticks, volatility analysis)
            #   ✓ Debugging and traceability
            #   ✓ Future ML or statistical research
            #
            # This table is NOT used for volatility threshold alerts.
            # It is only storing raw market history for analysis.
            # ----------------------------------------------------------------------
            cursor.execute("""
                INSERT INTO trades (symbol, trade_time, price, quantity, stream)
                VALUES (%s, %s, %s, %s, %s)
            """, (symbol, trade_time, price, quantity, stream))
            conn.commit()

            print(f"✅ Saved {symbol} @ ${price} x {quantity}")

        except Exception as e:
            print(f"❌ Parse/store error: {e}")
            conn.rollback()  # important: reset transaction after error

except KeyboardInterrupt:
    print("🛑 Stopping...")
finally:
    consumer.close()
    cursor.close()
    conn.close()
