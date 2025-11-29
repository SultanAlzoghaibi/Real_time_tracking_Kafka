import random
import time
import json
from confluent_kafka import Producer

# Initialize Kafka producer
p = Producer({'bootstrap.servers': 'localhost:9092'})

# Simulated stock tickers
TICKERS = [f"STK{str(i).zfill(3)}" for i in range(1, 10)]

# Assign realistic starting prices
prices = {}
for t in TICKERS:
    base = random.choice([
        random.uniform(5, 30),      # penny stocks
        random.uniform(50, 200),    # mid-cap
        random.uniform(300, 2000)   # large-cap
    ])
    prices[t] = base

# Kafka topic
TOPIC = "fakestock"

# Send message to Kafka
def send_to_kafka(event):
    p.produce(TOPIC, json.dumps(event).encode('utf-8'))
    p.poll(0)

update_count = 0
start_time = time.time()

try:
    while True:
        for ticker in TICKERS:
            delta = random.uniform(-0.5, 0.5)
            prices[ticker] = max(0.01, prices[ticker] + delta)

            event = {
                "ticker": ticker,
                "price": round(prices[ticker], 2),
                "volume": random.randint(10, 1000),  # fake volume
                "exchange": random.choice(["NASDAQ", "NYSE", "TSX", "CSE"]),
                "sector": random.choice(["Tech", "Finance", "Energy", "Health", "Retail"]),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            send_to_kafka(event)
            update_count += 1

        if update_count % 5000 == 0:
            print(f"Sample Event:\n{event}")

        time.sleep(0.1)

        elapsed = time.time() - start_time
        if elapsed >= 5:
            print(f"\n[Stats] {update_count} updates in {elapsed:.2f} sec — {update_count / elapsed:.2f} updates/sec\n")
            update_count = 0
            start_time = time.time()

except KeyboardInterrupt:
    print("Stopped.")
    p.flush()