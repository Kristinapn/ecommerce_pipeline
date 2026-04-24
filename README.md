# Ecommerce Pipeline

GDPR-aware ecommerce database with Kafka-based real-time ingestion for customer registrations.

## Run

Requires Python 3.10+ and Docker Desktop. Run all commands from the project root.

```bash
# 1. Venv
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# 2. Dependencies
pip install -r requirements.txt

# 3. Kafka
cd docker && docker compose up -d && cd ..

# 4. DB
python src/db.py
python src/generator.py

# 5. Stream (in two separate terminals - venv active in both)
python src/consumer.py          # terminal 1
python src/producer.py          # terminal 2
```

Stop with Ctrl+C. Shut down Kafka with `cd docker && docker compose down`.

Logs can be found in the terminal and  `logs/consumer.log` / `logs/producer.log` (the folder gets auto-created).

## Layout

```
sql/schema.sql              tables, constraints, indexes
src/db.py                   initializes ecommerce.db from schema.sql
src/generator.py            seeds all tables with coherent fake data
src/models.py               pydantic schema for Kafka customer events
src/producer.py             publishes customer events to the `customers` topic
src/consumer.py             reads the topic, validates, inserts
docker/docker-compose.yml   single-node Kafka (KRaft)
```

## Notes

- **GDPR.** Soft delete via `customers.deleted_at`. Logs contain IDs/emails only.
- **Locale consistency.** Generator and producer share a `LOCALE_COUNTRY` map so a German customer has a German name, city, phone, and postal code.
- **Validation + transformation.** Handled by the `CustomerEvent` pydantic model: field presence, types, age range, email syntax, UUID format, name/email normalization. Invalid messages are logged and skipped.
- **Causality.** Orders after registration; reviews after both registration and product creation; deleted customers don't place orders or leave reviews.

## Possible improvements
- The consumer opens a new SQLite connection for every message. Keeping a single connection open would be faster under more load.
- The `LOCALE_COUNTRY` map is duplicated in `generator.py` and `producer.py`. Moving it to a shared `src/constants.py` would remove the duplication. 
