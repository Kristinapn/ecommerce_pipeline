import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

schema_path = os.path.join(BASE_DIR, "..", "sql", "schema.sql")
db_path = os.path.join(BASE_DIR, "..", "ecommerce.db")

try:
    with open(schema_path, "r") as sql_file:
        sql_script = sql_file.read()

    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    cursor.executescript(sql_script)
    db.commit()
    db.close()

    print("Database initialized successfully.")

except FileNotFoundError:
    print(f"Error: schema file not found at {schema_path}")
except sqlite3.Error as e:
    print(f"Database error: {e}")
