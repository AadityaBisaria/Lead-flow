import argparse
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, inspect
from pprint import pprint

# DB connection
DB_URL = "postgresql+psycopg2://postgres:Postgres@localhost:5432/leadflow"
engine = create_engine(DB_URL)
metadata = MetaData()

inspector = inspect(engine)

# Get all table names
table_names = inspector.get_table_names()
print("\n=== Available Tables ===")
print(table_names)

# Get schema information for specific tables
tables_to_check = ["case"]
print("\n=== Table Schemas ===")
for table_name in tables_to_check:
    if table_name in table_names:
        print(f"\n--- {table_name} ---")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"Column: {column['name']}")
            print(f"  Type: {column['type']}")
            print(f"  Nullable: {column['nullable']}")
            if 'default' in column:
                print(f"  Default: {column['default']}")
            if 'primary_key' in column:
                print(f"  Primary Key: {column['primary_key']}")
            print()