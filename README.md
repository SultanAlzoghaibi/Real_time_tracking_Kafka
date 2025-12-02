# Real-Time Tracking Pipeline (Kafka + PostgreSQL + Python)

## 1️⃣ Requirements
- PostgreSQL installed (must be running)
- Python 3 + pip + venv
- Kafka (included in folder `2kafka/kafka_2.13-4.1.0.tgz`)
- macOS / Linux terminal

---

## 2️⃣ Project Structure
```
src/
├── 0dbInit/
│   └── dbInit.py
├── 1producers/
│   ├── binanceProducer.py
│   ├── fakeStockProducer.py
├── 2kafka/
│   ├── kafka_2.13-4.1.0.tgz
│   └── versions.txt
├── 3consumers/
│   ├── AttiqueConsumer.py
│   ├── binanceConsumer.py
│   └── fakeStockConsumer.py
├── 4postgres/
│   └── tradeDBSample.sql
├── 6DashboardOrNotifier/
│   └── Dashboard.py
└── websockets/
    └── sample.py
```

---

## 3️⃣ Step 1 — Start PostgreSQL
Make sure PostgreSQL is running.

Default connection used:
```
DB_NAME = trades
DB_USER = sultanalzoghaibi
DB_PASS = ""
DB_HOST = localhost
DB_PORT = 5432
```

---

## 4️⃣ Step 2 — Initialize Database Tables
From the `src` folder:
```bash
cd src
python 0dbInit/dbInit.py
```

This creates:
- `trades`
- `asset_volatility`
- `alerts`

---

## Step 3 — Download & Start Kafka

Kafka is **NOT included** in this repo (GitHub file-size limit).  
You must download it manually.

### 1️⃣ Download Kafka
Go to:

https://kafka.apache.org/downloads

Download the **Binary**:
- `kafka_2.13-4.1.1.tgz`

### 2️⃣ Move it into the project
Place the file here: 
src/2kafka/kafka_2.13-4.1.1.tgz


### 3️⃣ Extract Kafka and run
```bash
cd src/2kafka
tar -xvf kafka_2.13-4.1.0.tgz
cd kafka_2.13-4.1.0
```

Format storage (KRaft mode):
```bash
bin/kafka-storage.sh format -t $(uuidgen) -c config/kraft/server.properties --standalone
```

Start Kafka:
```bash
bin/kafka-server-start.sh config/server.properties
```

---

## 6️⃣ Step 4 — Create Topics
In another terminal:

```bash
cd src/2kafka/kafka_2.13-4.1.0

bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
  --topic fakestock --partitions 10 --replication-factor 1

bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
  --topic binance --partitions 10 --replication-factor 1
```

---

## 7️⃣ Step 5 — Start Consumers
From `src`:

```bash
python 3consumers/AttiqueConsumer.py
python 3consumers/fakeStockConsumer.py
```

---

## 8️⃣ Step 6 — Start Producers
In separate terminals:

```bash
python 1producers/binanceProducer.py
python 1producers/fakeStockProducer.py
```

---

## 9️⃣ Step 7 — Start Dashboard
From `src`:

```bash
python 6DashboardOrNotifier/Dashboard.py
```

Dashboard runs on:
```
http://127.0.0.1:8050
```

---

## ✔️ Pipeline is now fully running
- WebSocket → Kafka → Consumers → PostgreSQL → Dashboard  
- Fake stocks used for testing  
- Binance stream used for real-time market data  

---
