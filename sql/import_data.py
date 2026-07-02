import os
import sqlite3
import pandas as pd

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SQL_DIR = os.path.join(BASE_DIR, "sql")
DB_PATH = os.path.join(DATA_DIR, "smart_city.db")
SCHEMA_PATH = os.path.join(SQL_DIR, "database.sql")

print("Initializing SQLite database...")
if os.path.exists(DB_PATH):
    print("Database already exists. Deleting to avoid duplicate entries...")
    os.remove(DB_PATH)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Run SQL schema
print("Applying database schema...")
with open(SCHEMA_PATH, "r") as f:
    schema_sql = f.read()
cursor.executescript(schema_sql)
conn.commit()

# CSV files and their corresponding database tables
CSV_TABLE_MAPPING = {
    "weather.csv": "weather",
    "pollution.csv": "pollution",
    "traffic.csv": "traffic",
    "crime.csv": "crime",
    "transport.csv": "transport",
    "energy.csv": "energy",
    "water.csv": "water",
    "healthcare.csv": "healthcare",
    "population.csv": "population",
    "education.csv": "education",
    "economy.csv": "economy"
}

# Import each file
for csv_file, table_name in CSV_TABLE_MAPPING.items():
    csv_path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(csv_path):
        print(f"Warning: CSV file {csv_file} not found. Skipping.")
        continue
        
    print(f"Importing {csv_file} into '{table_name}' table...")
    df = pd.read_csv(csv_path)
    
    # We use if_exists='append' because schema is already created with constraints
    # If the table has an auto-increment id, we let SQLite handle it (e.g. crime table)
    # Pandas to_sql can write index, we skip writing df index as separate column
    df.to_sql(table_name, conn, if_exists='append', index=False)

conn.commit()
conn.close()
print(f"Successfully created and imported database at: {DB_PATH}")
