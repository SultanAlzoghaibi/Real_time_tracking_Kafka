from confluent_kafka import Producer
import json


# Config
conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

# Optional delivery callback
def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [partition {msg.partition()}]")

# BTC -> Partition 0
btc_message = {
    "stream": "btcusdt@trade",
    "data": {
        "e": "trade",
        "E": 1762979951734,
        "s": "BTCUSDT",
        "t": 5475861466,
        "p": "101629.99000000",
        "q": "0.00007000",
        "T": 1762979951733,
        "m": False,
        "M": True
    }
}

# ETH -> Partition 1
eth_message = {
    "stream": "ethusdt@trade",
    "data": {
        "e": "trade",
        "E": 1762979951735,
        "s": "ETHUSDT",
        "t": 3153149109,
        "p": "3424.84000000",
        "q": "0.00160000",
        "T": 1762979951735,
        "m": False,
        "M": True
    }
}



# Send to specific partitions
producer.produce(
    topic="binance",
    key="BTC",
    value=json.dumps(btc_message),
    partition=0,
    callback=delivery_report
)

producer.produce(
    topic="binance",
    key="ETH",
    value=json.dumps(eth_message),
    partition=1,
    callback=delivery_report
)

# Ensure delivery
producer.flush()