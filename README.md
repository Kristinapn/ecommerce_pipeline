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

# 5. Stream (two terminals, venv active in both)
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

## Notes on choices

- **GDPR.** `customers.deleted_at` for soft delete (right to erasure) preserves referential integrity. Logs contain IDs/emails only, never full payloads.
- **Locale-consistent data.** Generator uses 7 Faker locales with a `LOCALE_COUNTRY` map so a German customer gets a German name, city, phone, and postal code. The producer uses the same mapping for consistency with the batch data.
- **Causality.** `updated_at` ≥ `created_at`; orders after registration; reviews after both the customer's registration and the product's creation; deleted customers don't place orders or leave reviews.
- **Validation + transformation.** Incoming Kafka messages are parsed through a pydantic `CustomerEvent` model - field presence, types, age range, email syntax, UUID format. Name/email normalization lives on the model as `field_validator`s. Invalid messages are logged with field-level detail and skipped.

## Known limitations

- Invalid messages are logged and dropped; a production version would use a dead-letter topic or file.
- Consumer opens a new SQLite connection per message - fine at this volume, not ideal under load.
- No graceful shutdown handler; Ctrl+C raises `KeyboardInterrupt` out of the loop.
- `LOCALE_COUNTRY` is duplicated between `generator.py` and `producer.py` - would extract to `src/constants.py`.