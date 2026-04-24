"""Kafka producer, simulates real-time customer registrations."""

import json
import time
import uuid
import random
import logging
from kafka import KafkaProducer
from datetime import datetime
from faker import Faker
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "producer.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

LOCALES = ["en_US", "de_DE", "fr_FR", "en_GB", "it_IT", "es_ES", "sv_SE"]
fake = Faker(LOCALES)

LOCALE_COUNTRY = {
    "en_US": "United States",
    "de_DE": "Germany",
    "fr_FR": "France",
    "en_GB": "United Kingdom",
    "it_IT": "Italy",
    "es_ES": "Spain",
    "sv_SE": "Sweden",
}


def get_producer():
    return KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
    )


def generate_customer_event():
    locale = random.choice(LOCALES)
    loc = fake[locale]
    return {
        "customer_id": str(uuid.uuid4()),
        "first_name": loc.first_name(),
        "last_name": loc.last_name(),
        "age": random.randint(18, 90),
        "email": loc.email(),
        "country": LOCALE_COUNTRY[locale],
        "city": loc.city(),
        "postal_code": loc.postcode(),
        "phone_number": loc.phone_number(),
        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def run_simulation():
    producer = get_producer()
    logger.info("Starting real-time customer simulation...")
    try:
        while True:
            customer_data = generate_customer_event()
            producer.send("customers", value=customer_data)
            logger.info(f"Sent registration event: {customer_data['email']}")
            time.sleep(random.uniform(1, 4))
    except KeyboardInterrupt:
        logger.info("Simulation stopped.")
    finally:
        producer.flush()


if __name__ == "__main__":
    run_simulation()
