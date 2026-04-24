PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id     TEXT PRIMARY KEY, -- UUID
    company_name    TEXT NOT NULL,
    contact_name    TEXT,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT,
    country         TEXT NOT NULL,
    lead_time       INTEGER NOT NULL CHECK (lead_time >= 0),
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_suppliers_country 
    ON suppliers(country);

CREATE TABLE IF NOT EXISTS customers (
    customer_id       TEXT PRIMARY KEY, -- UUID
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    age               INTEGER NOT NULL CHECK (age BETWEEN 18 AND 120),
    email             TEXT UNIQUE NOT NULL,
    country           TEXT NOT NULL,
    city              TEXT NOT NULL,
    postal_code       TEXT NOT NULL,
    phone_number      TEXT,
    registration_date TEXT NOT NULL DEFAULT (datetime('now')),
    last_login_date   TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at        TEXT DEFAULT (datetime('now')), 
    deleted_at        TEXT DEFAULT NULL -- soft delete (right to erasure)
);

CREATE INDEX IF NOT EXISTS idx_customers_email
    ON customers(email);

CREATE INDEX IF NOT EXISTS idx_customers_country
    ON customers(country);

CREATE INDEX IF NOT EXISTS idx_customers_registration_date
    ON customers(registration_date);

CREATE INDEX IF NOT EXISTS idx_customers_deleted_at  
    ON customers(deleted_at);

CREATE TABLE IF NOT EXISTS products (
    product_id      TEXT    PRIMARY KEY, -- UUID
    name            TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    subcategory     TEXT,
    price           REAL    NOT NULL CHECK (price > 0),
    cost            REAL    NOT NULL CHECK (cost > 0),
    supplier_id     TEXT    NOT NULL,
    stock_quantity  INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    weight          REAL    CHECK (weight > 0),
    dimensions      TEXT, -- Length x width x height
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE INDEX IF NOT EXISTS idx_products_category
    ON products(category);

CREATE INDEX IF NOT EXISTS idx_products_supplier_id
    ON products(supplier_id);

CREATE TABLE IF NOT EXISTS orders (
    order_id         TEXT  PRIMARY KEY, -- UUID
    customer_id      TEXT  NOT NULL,
    order_date       TEXT  NOT NULL DEFAULT (datetime('now')),
    total_amount     REAL  NOT NULL CHECK (total_amount >= 0),
    status           TEXT  NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 'refunded')),
    shipping_address TEXT  NOT NULL,
    payment_method   TEXT  NOT NULL CHECK (payment_method IN ('credit_card', 'debit_card', 'paypal', 'bank_transfer')),
    currency         TEXT  NOT NULL DEFAULT 'EUR' CHECK (length(currency) = 3),
    created_at       TEXT  DEFAULT (datetime('now')),
    updated_at       TEXT  DEFAULT (datetime('now')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
    ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_status
    ON orders(status);

CREATE INDEX IF NOT EXISTS idx_orders_order_date
    ON orders(order_date);

CREATE TABLE IF NOT EXISTS order_items (
    order_id        TEXT NOT NULL,
    product_id      TEXT NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      REAL NOT NULL CHECK (unit_price >= 0),
    discount_amount REAL NOT NULL DEFAULT 0 CHECK (discount_amount >= 0 AND discount_amount <= quantity * unit_price),
    total_price     REAL GENERATED ALWAYS AS (quantity * unit_price - discount_amount) VIRTUAL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
    ON order_items(product_id);

CREATE TABLE IF NOT EXISTS product_reviews (
    review_id   TEXT    PRIMARY KEY, -- UUID
    product_id  TEXT    NOT NULL,
    customer_id TEXT    NOT NULL,
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date TEXT    NOT NULL DEFAULT (date('now')),
    UNIQUE (product_id, customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX IF NOT EXISTS idx_product_reviews_product_id
    ON product_reviews(product_id);

CREATE INDEX IF NOT EXISTS idx_product_reviews_customer_id
    ON product_reviews(customer_id);
