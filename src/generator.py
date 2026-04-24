from datetime import datetime, timedelta
import sqlite3
import os
import uuid
import random
from faker import Faker

LOCALES = ["en_US", "de_DE", "fr_FR", "en_GB", "it_IT", "es_ES", "sv_SE"]

fake = Faker(LOCALES)
Faker.seed(0)
random.seed(0)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecommerce.db")

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"DB not found at {DB_PATH}. Run schema.sql first.")

NUM_SUPPLIERS = 20
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 500
NUM_ORDERS = 1000
NUM_REVIEWS = 800

CATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Accessories", "Cameras"],
    "Clothing": ["Men", "Women", "Kids", "Accessories"],
    "Home": ["Furniture", "Kitchen", "Bedroom", "Bathroom"],
    "Books": ["Fiction", "Psychology", "Science", "History", "Mystery"],
    "Sports": ["Gym", "Outdoor", "Football", "Cycling", "Swimming"],
}

STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled", "refunded"]
PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer"]
CURRENCIES = ["EUR", "USD", "GBP", "CHF", "SEK"]

LOCALE_COUNTRY = {
    "en_US": "United States",
    "de_DE": "Germany",
    "fr_FR": "France",
    "en_GB": "United Kingdom",
    "it_IT": "Italy",
    "es_ES": "Spain",
    "sv_SE": "Sweden",
}


def generate_suppliers():
    fake.unique.clear()
    suppliers = []
    for _ in range(NUM_SUPPLIERS):
        locale = random.choice(LOCALES)
        loc = fake[locale]

        created_dt = fake.date_time_between(start_date="-5y", end_date="now")
        updated_dt = fake.date_time_between(start_date=created_dt, end_date="now")
        created = created_dt.strftime("%Y-%m-%d %H:%M:%S")
        updated = updated_dt.strftime("%Y-%m-%d %H:%M:%S")

        suppliers.append(
            (
                str(uuid.uuid4()),
                loc.company(),
                loc.name(),
                fake.unique.company_email(),
                loc.phone_number(),
                LOCALE_COUNTRY[locale],
                random.randint(1, 30),
                created,
                updated,
            )
        )
    return suppliers


def generate_customers():
    fake.unique.clear()
    customers = []
    now = datetime.now()
    five_years_ago = now - timedelta(days=5 * 365)

    for _ in range(NUM_CUSTOMERS):
        locale = random.choice(LOCALES)
        loc = fake[locale]

        dob_date = fake.date_time_between(start_date="-80y", end_date="-18y").date()
        age = (
            now.year
            - dob_date.year
            - ((now.month, now.day) < (dob_date.month, dob_date.day))
        )

        # Customer should not register before 18th birthday
        try:
            eighteenth_date = dob_date.replace(year=dob_date.year + 18)
        except ValueError:  # 29 February
            eighteenth_date = dob_date.replace(year=dob_date.year + 18, day=28)
        eighteenth = datetime.combine(eighteenth_date, datetime.min.time())

        earliest_reg = max(eighteenth, five_years_ago)
        reg_date_dt = fake.date_time_between(start_date=earliest_reg, end_date=now)
        reg_date = reg_date_dt.strftime("%Y-%m-%d %H:%M:%S")

        last_login = (
            fake.date_time_between(start_date=reg_date_dt, end_date=now).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if random.random() > 0.1
            else None
        )

        updated_at = fake.date_time_between(
            start_date=reg_date_dt, end_date=now
        ).strftime("%Y-%m-%d %H:%M:%S")

        deleted_at = (
            fake.date_time_between(start_date=reg_date_dt, end_date=now).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if random.random() < 0.02
            else None
        )

        customers.append(
            (
                str(uuid.uuid4()),
                loc.first_name(),
                loc.last_name(),
                age,
                fake.unique.email(),
                LOCALE_COUNTRY[locale],
                loc.city(),
                loc.postcode(),
                loc.phone_number(),
                reg_date,
                last_login,
                reg_date,
                updated_at,
                deleted_at,
            )
        )
    return customers


def generate_products(suppliers):
    products = []
    now = datetime.now()
    five_years_ago = now - timedelta(days=5 * 365)

    for _ in range(NUM_PRODUCTS):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        price = round(random.uniform(5, 1500), 2)
        cost = round(price * random.uniform(0.3, 0.7), 2)

        supplier = random.choice(suppliers)
        supplier_id = supplier[0]
        supplier_created = datetime.strptime(supplier[7], "%Y-%m-%d %H:%M:%S")

        earliest = max(supplier_created, five_years_ago)
        created_dt = fake.date_time_between(start_date=earliest, end_date=now)
        updated_dt = fake.date_time_between(start_date=created_dt, end_date=now)

        products.append(
            (
                str(uuid.uuid4()),
                f"{fake.word().capitalize()} {subcategory[:-1] if subcategory.endswith('s') else subcategory}",
                category,
                subcategory,
                price,
                cost,
                supplier_id,
                random.randint(0, 500),
                round(random.uniform(0.1, 30), 2),
                f"{random.randint(1,100)}x{random.randint(1,100)}x{random.randint(1,100)} cm",
                created_dt.strftime("%Y-%m-%d %H:%M:%S"),
                updated_dt.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
    return products


def generate_orders(customers):
    orders = []
    now = datetime.now()

    # Only non-deleted customers can place orders
    active_customers = [c for c in customers if c[13] is None]

    for _ in range(NUM_ORDERS):
        customer = random.choice(active_customers)
        customer_id = customer[0]
        reg_date_dt = datetime.strptime(customer[9], "%Y-%m-%d %H:%M:%S")

        # Orders can't precede registration
        order_date_dt = fake.date_time_between(start_date=reg_date_dt, end_date=now)
        order_date = order_date_dt.strftime("%Y-%m-%d %H:%M:%S")

        updated_dt = fake.date_time_between(start_date=order_date_dt, end_date=now)

        orders.append(
            (
                str(uuid.uuid4()),
                customer_id,
                order_date,
                0,  # total_amount, updated after order_items
                random.choice(STATUSES),
                fake.address().replace("\n", ", "),
                random.choice(PAYMENT_METHODS),
                random.choice(CURRENCIES),
                order_date,  # created_at same as order_date
                updated_dt.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
    return orders


def generate_order_items(orders, products):
    order_items = []
    order_totals = {}

    for order in orders:
        order_id = order[0]
        selected = random.sample(products, random.randint(1, 5))
        total = 0

        for product in selected:
            product_id = product[0]
            unit_price = product[4]
            quantity = random.randint(1, 5)

            line_subtotal = quantity * unit_price
            discount = (
                round(random.uniform(0, line_subtotal * 0.2), 2)
                if random.random() > 0.7
                else 0
            )

            total += line_subtotal - discount
            order_items.append((order_id, product_id, quantity, unit_price, discount))

        order_totals[order_id] = round(total, 2)

    return order_items, order_totals


def generate_reviews(customers, products):
    reviews = []
    pairs = set()
    now = datetime.now()

    # Only not deleted customers can leave reviews
    active_customers = [c for c in customers if c[13] is None]

    attempts = 0
    max_attempts = NUM_REVIEWS * 3

    while len(reviews) < NUM_REVIEWS and attempts < max_attempts:
        attempts += 1
        customer = random.choice(active_customers)
        product = random.choice(products)
        customer_id = customer[0]
        product_id = product[0]

        if (customer_id, product_id) in pairs:
            continue
        pairs.add((customer_id, product_id))

        # Review cannot precede customer registration or product creation
        reg_date_dt = datetime.strptime(customer[9], "%Y-%m-%d %H:%M:%S")
        product_created_dt = datetime.strptime(product[10], "%Y-%m-%d %H:%M:%S")
        earliest = max(reg_date_dt, product_created_dt)

        review_date = fake.date_time_between(
            start_date=earliest, end_date=now
        ).strftime("%Y-%m-%d")

        reviews.append(
            (
                str(uuid.uuid4()),
                product_id,
                customer_id,
                random.randint(1, 5),
                fake.sentence(nb_words=12) if random.random() > 0.3 else None,
                review_date,
            )
        )

    return reviews


def insert_data():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript("""
        DELETE FROM product_reviews;
        DELETE FROM order_items;
        DELETE FROM orders;
        DELETE FROM products;
        DELETE FROM customers;
        DELETE FROM suppliers;
    """)

    print("Generating suppliers...")
    suppliers = generate_suppliers()
    cursor.executemany("INSERT INTO suppliers VALUES (?,?,?,?,?,?,?,?,?)", suppliers)

    print("Generating customers...")
    customers = generate_customers()
    cursor.executemany(
        "INSERT INTO customers (customer_id, first_name, last_name, age, email, country, city, postal_code, phone_number, registration_date, last_login_date, created_at, updated_at, deleted_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        customers,
    )

    print("Generating products...")
    products = generate_products(suppliers)
    cursor.executemany(
        "INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", products
    )

    print("Generating orders...")
    orders = generate_orders(customers)
    cursor.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?)", orders)

    print("Generating order items...")
    order_items, order_totals = generate_order_items(orders, products)
    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount) VALUES (?,?,?,?,?)",
        order_items,
    )

    print("Updating order totals...")
    cursor.executemany(
        "UPDATE orders SET total_amount = ? WHERE order_id = ?",
        [(total, order_id) for order_id, total in order_totals.items()],
    )

    print("Generating product reviews...")
    reviews = generate_reviews(customers, products)
    cursor.executemany("INSERT INTO product_reviews VALUES (?,?,?,?,?,?)", reviews)

    db.commit()
    db.close()
    print(
        f"\nDone. Inserted: {len(suppliers)} suppliers, {len(customers)} customers, "
        f"{len(products)} products, {len(orders)} orders, "
        f"{len(order_items)} order items, {len(reviews)} reviews."
    )


if __name__ == "__main__":
    insert_data()
