import random
import time

# Generate 100 realistic stock tickers (e.g., FAKE1, FAKE2...)
TICKERS = [f"STK{str(i).zfill(3)}" for i in range(1, 101)]

# Assign realistic starting prices
prices = {}
for t in TICKERS:
    # Simulate different types of stocks: small cap, mid cap, blue chip
    base = random.choice([
        random.uniform(5, 30),      # penny stocks / low-cap
        random.uniform(50, 200),    # mid-cap
        random.uniform(300, 2000)   # high-cap / FAANG
    ])
    prices[t] = base

# Tracking stats
update_count = 0
start_time = time.time()

try:
    while True:
        for ticker in TICKERS:
            # Apply a small random price delta
            delta = random.uniform(-0.5, 0.5)
            prices[ticker] = max(0.01, prices[ticker] + delta)  # Ensure price stays positive

            # Simulate an update (send to Kafka, print, etc.)
            # Example structure:
            # event = {
            #     "ticker": ticker,
            #     "price": round(prices[ticker], 2),
            #     "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            # }

            update_count += 1

        # Optional: print 1 example every 50k updates to avoid console spam
        if update_count % 50000 == 0:
            sample = random.choice(TICKERS)

            print({
                "ticker": sample,
                "price": round(prices[ticker], 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

        # Control rate: small sleep (~100k updates/sec total)
        time.sleep(0.001)

        # Print stats every 5 seconds
        elapsed = time.time() - start_time
        if elapsed >= 5:
            print(f"\n[Stats] {update_count} updates in {elapsed:.2f} sec — {update_count / elapsed:.2f} updates/sec\n")
            update_count = 0
            start_time = time.time()

except KeyboardInterrupt:
    print("Stopped.")