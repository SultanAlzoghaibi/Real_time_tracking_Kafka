import json
import time
import threading
import websocket
from confluent_kafka import Producer
import json


# Binance base WebSocket endpoint for combined streams
BINANCE_SOCKET_URL = "wss://stream.binance.com:9443/stream?streams="

# 10 popular symbols (trading pairs), all lowercase with 'usdt' (Binance format)
symbols = [
    "btcusdt",  # Bitcoin
    "ethusdt",  # Ethereum
    "bnbusdt",  # Binance Coin
    "solusdt",  # Solana
    "xrpusdt",  # XRP
    "adausdt",  # Cardano
    "dogeusdt", # Dogecoin
    "avaxusdt", # Avalanche
    "trxusdt",  # TRON
    "linkusdt"  # Chainlink
]

# Combine them into a single stream of 'trade' data
streams = "/".join([f"{symbol}@trade" for symbol in symbols])
FULL_SOCKET_URL = BINANCE_SOCKET_URL + streams

msg_count = 0
start_time = None

conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

partition_map = {
    "btcusdt": 0,
    "ethusdt": 1,
    "bnbusdt": 2,
    "solusdt": 3,
    "xrpusdt": 4,
    "adausdt": 5,
    "dogeusdt": 6,
    "avaxusdt": 7,
    "trxusdt": 8,
    "linkusdt": 9
}

def on_message(ws, message):
    global msg_count
    msg_count += 1

    data = json.loads(message)

    # Extract symbol from stream key, e.g. "btcusdt@trade"
    stream = data.get("stream", "")
    symbol = stream.split("@")[0] if "@" in stream else ""

    # Send full raw message as JSON string to Kafka with key as symbol
    try:
        producer.produce(
            topic="binance",
            key=symbol,
            value=json.dumps(data),
            partition=partition_map.get(symbol, 10)
        )
        producer.poll(0)
    except Exception as e:
        print(f"Failed to send message to Kafka: {e}")



    # Uncomment to see messages:
    # print(json.dumps(json.loads(message), indent=2))

def on_open(ws):
    global start_time
    start_time = time.time()
    print(f"[Connected] Listening to trades for: {', '.join(symbols)}")

def on_close(ws, close_status_code, close_msg):
    duration = time.time() - start_time
    print(f"[Closed] Received {msg_count} messages in {duration:.2f} seconds")
    print(f"Average rate: {msg_count / duration:.2f} messages/sec")

def main():
    ws = websocket.WebSocketApp(
        FULL_SOCKET_URL,
        on_open=on_open,
    on_message=on_message,
        on_close=on_close
    )

    def run_ws():
        ws.run_forever()

    thread = threading.Thread(target=run_ws)
    thread.start()

    # Let it run for 10 seconds
    time.sleep(2)
    ws.close()


def sendToKafka():
    # Set up configuration (where to send data)
    conf = {
        'bootstrap.servers': 'localhost:9092'  # <-- This is where you're sending the data
    }

    producer = Producer(conf)

    # Callback on delivery (optional)
    def delivery_report(err, msg):
        if err is not None:
            print(f"Delivery failed: {err}")
        else:
            print(f"Delivered message to {msg.topic()} [{msg.partition()}]")

    # Send data to topic "crypto"
    producer.produce("coinbase", key="ETH", value="ETH price is 3500", callback=delivery_report)

    # Wait for delivery
    producer.flush()

if __name__ == "__main__":
    main()
