import json
import psycopg2
from decimal import Decimal
from confluent_kafka import Consumer

# --- PostgreSQL connection ---
conn = psycopg2.connect(
    dbname='your_db',
    user='your_user',
    password='your_password',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

# --- Kafka Consumer config ---
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(conf)
consumer.subscribe(['binance'])

# --- Track last known prices for jump detection ---
latest_prices = {}

print("📡 Listening for messages...\n")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"⚠️ Kafka error: {msg.error()}")
            continue

        raw_key = msg.key().decode('utf-8')
        raw_value = msg.value().decode('utf-8')

        try:
            parsed = json.loads(raw_value)
            trade = parsed["data"]

            symbol = trade["s"]
            trade_time = trade["T"]
            price = Decimal(trade["p"])
            quantity = Decimal(trade["q"])
            stream = parsed.get("stream", "")

            # Price jump check
            if symbol in latest_prices:
                old_price = latest_prices[symbol]
                change = abs(price - old_price)
                percent = (change / old_price) * 100
                if percent >= 10:
                    print(f"🚨 {symbol} price jump: {old_price} ➝ {price} ({percent:.1f}%)")
            latest_prices[symbol] = price

            # Insert into DB (no raw JSON)
            cursor.execute("""
                INSERT INTO trades (symbol, trade_time, price, quantity, stream)
                VALUES (%s, %s, %s, %s, %s)
            """, (symbol, trade_time, price, quantity, stream))
            conn.commit()

            print(f"✅ Saved {symbol} @ ${price} x {quantity}")

        except Exception as e:
            print(f"❌ Parse/store error: {e}")

except KeyboardInterrupt:
    print("🛑 Stopping...")
finally:
    consumer.close()
    cursor.close()
    conn.close()