import websocket
import json
import time

received_count = 0

def on_open(ws):
    print("🔌 Connected")

    payload = {"OMSId": 1, "InstrumentId": 1}  # BTC/CAD
    message = {
        "m": 0,
        "i": 1,
        "n": "SubscribeTrades",
        "o": json.dumps(payload)
    }

    ws.send(json.dumps(message))
    print("📡 Sent SubscribeTrades for BTC/CAD")

def on_message(ws, message):
    global received_count
    parsed = json.loads(message)

    if parsed.get("n") == "TradeDataUpdateEvent":
        received_count += 1
        print(f"📨 Trade: {parsed['o']}")

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 Disconnected")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "wss://api.ndax.io/WSGateway/",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    start = time.time()
    duration = 13

    def run_forever_limited():
        while time.time() - start < duration:
            ws.run_forever()
            time.sleep(0.1)  # reconnect if needed
        ws.close()

    run_forever_limited()

    print(f"\n⏱ Test duration: {duration:.2f}s")
    print(f"📈 Total trades received: {received_count}")
    print(f"⚡ Avg rate: {received_count/duration:.2f} trades/sec")