import json
import psycopg2
from confluent_kafka import Consumer
from datetime import datetime, timezone

# Kafka config
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'stock-consumer-group',
    'auto.offset.reset': 'earliest'
})
c.subscribe(['fakestock'])

# PostgreSQL config
conn = psycopg2.connect(
    dbname='trades',
    user='sultanalzoghaibi',
    password='',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

print("Listening for stock events...")

try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"[Kafka Error] {msg.error()}")
            continue

        event = json.loads(msg.value().decode('utf-8'))

        symbol = event.get("ticker")
        trade_time_str = event.get("timestamp")  # e.g. "2025-11-29T12:00:46" or "2025-11-29 12:00:46"
        price = event.get("price")
        quantity = event.get("volume")

        # --- convert to epoch ms to match BIGINT column ---
        try:
            try:
                # handles "2025-11-29T12:00:46"
                dt = datetime.fromisoformat(trade_time_str)
            except ValueError:
                # handles "2025-11-29 12:00:46"
                dt = datetime.strptime(trade_time_str, "%Y-%m-%d %H:%M:%S")

            dt = dt.replace(tzinfo=timezone.utc)
            trade_time_ms = int(dt.timestamp() * 1000)
        except Exception as e:
            print(f"[Time parse error] raw={trade_time_str} err={e}")
            continue

        cursor.execute("""
            INSERT INTO trades (symbol, trade_time, price, quantity)
            VALUES (%s, %s, %s, %s)
        """, (symbol, trade_time_ms, price, quantity))
        conn.commit()

        print(f"[Inserted] {symbol} at {price} x {quantity} at {trade_time_ms} (ms)")

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    c.close()
    cursor.close()
    conn.close()