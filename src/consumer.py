"""Kafka consumer for the customers topic.

Validates and transforms incoming events using the CustomerEvent pydantic
model and then inserts them into the customers table.
"""

import sqlite3
import json
import os
import logging
from kafka import KafkaConsumer
from pydantic import ValidationError

from models import CustomerEvent

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "consumer.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecommerce.db")


def persist_to_db(event: CustomerEvent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO customers (
                customer_id, first_name, last_name, age, email,
                country, city, postal_code, phone_number, registration_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(event.customer_id),
                event.first_name,
                event.last_name,
                event.age,
                event.email,
                event.country,
                event.city,
                event.postal_code,
                event.phone_number,
                event.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity Error (possible duplicate): {e}")
    finally:
        conn.close()


def consume_customers():
    consumer = KafkaConsumer(
        "customers",
        bootstrap_servers="localhost:9092",
        group_id="ecommerce_registration_group",
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    logger.info("Consumer started. Waiting for customer events...")

    for message in consumer:
        try:
            event = CustomerEvent.model_validate(message.value)
            persist_to_db(event)
            logger.info(f"Successfully processed and saved: {event.email}")
        except ValidationError as ve:
            logger.warning(
                f"Validation failed: {ve.errors(include_url=False, include_context=False)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    consume_customers()
