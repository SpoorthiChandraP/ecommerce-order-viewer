import sqlite3
import pandas as pd
import os

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "ecommerce.db")

# Delete old DB if it exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Map CSV filenames to table names
csv_tables = {
    "distribution_centers.csv": "distribution_centers",
    "inventory_items.csv": "inventory_items",
    "order_items.csv": "order_items",
    "orders.csv": "orders",
    "products.csv": "products",
    "users.csv": "users"
}

# Load each CSV into SQLite
for csv_file, table_name in csv_tables.items():
    path = os.path.join(DATA_DIR, csv_file)
    print(f"Loading {csv_file} → {table_name}...")
    df = pd.read_csv(path)
    df.to_sql(table_name, conn, index=False)

conn.commit()
conn.close()
print(f"Database created at {DB_PATH}")
