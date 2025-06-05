import os
import json
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.types import String, Float, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict

# Define SQLAlchemy DB connection URL
DB_URL = "postgresql+psycopg2://postgres:Postgres@localhost:5432/leadflow"
engine = create_engine(DB_URL)
metadata = MetaData()

def infer_unified_type(values):
    is_list = any(isinstance(v, list) for v in values if v is not None)
    flat_values = []
    for v in values:
        if isinstance(v, list):
            flat_values.extend(v)
        elif v is not None:
            flat_values.append(v)

    if not flat_values:
        return String

    if all(isinstance(i, bool) for i in flat_values):
        base_type = Boolean
    elif all(isinstance(i, int) for i in flat_values):
        base_type = Integer
    elif all(isinstance(i, float) or isinstance(i, int) for i in flat_values):
        base_type = Float
    elif all(isinstance(i, str) for i in flat_values):
        base_type = String
    else:
        base_type = JSON

    return ARRAY(base_type) if is_list else base_type

json_folder = r"C:\Users\Admin\Desktop\test\Project- main\data"

try:
    with engine.begin() as connection:
        print("✅ Connected to the database successfully!")

        for file in os.listdir(json_folder):
            if not file.endswith(".json"):
                continue

            table_name = os.path.splitext(file)[0].replace("-", "_").lower()
            file_path = os.path.join(json_folder, file)

            print(f"\n📄 Processing file: {file}")

            with open(file_path, "r") as f:
                records = json.load(f)

            if not isinstance(records, list) or not records:
                print(f"⚠️ Skipping {file}: Not a list or is empty.")
                continue

            print(f"🔍 {len(records)} records found in {file}")

            field_values = defaultdict(list)
            for row in records:
                for key, value in row.items():
                    field_values[key].append(value)

            columns = []
            column_types = {}

            for key, values in field_values.items():
                inferred_type = infer_unified_type(values)
                print(f"🧠 Inferred column '{key}' as {inferred_type}")
                columns.append(Column(key, inferred_type))
                column_types[key] = inferred_type

            table = Table(table_name, metadata, *columns)
            table.drop(engine, checkfirst=True)
            table.create(engine)
            print(f"✅ Table '{table_name}' created")

            def normalize_value(val, expected_type):
                if isinstance(expected_type, ARRAY):
                    return val if isinstance(val, list) else [val]
                return val

            normalized_records = []
            for row in records:
                normalized_row = {
                    key: normalize_value(row.get(key), column_types[key])
                    for key in column_types
                }
                normalized_records.append(normalized_row)

            print(f"📦 Ready to insert {len(normalized_records)} records into '{table_name}'")
            print(f"🔍 First row preview:\n{normalized_records[0] if normalized_records else 'No data'}")

            result = connection.execute(table.insert(), normalized_records)
            print(f"✅ Inserted rows: {result.rowcount if result else 'unknown'}")

except SQLAlchemyError as e:
    print("❌ Failed to process the JSON files")
    print("Error:", e)
