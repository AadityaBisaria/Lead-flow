import argparse
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, inspect

# DB connection
DB_URL = "postgresql+psycopg2://postgres:Postgres@localhost:5432/leadflow"
engine = create_engine(DB_URL)
metadata = MetaData()

def preview_table(table_name: str, limit: int = 10):
    try:
        with engine.connect() as connection:
            inspector = inspect(engine)
            table_names = inspector.get_table_names(schema='public')

            if table_name not in table_names:
                print(f"❌ Table '{table_name}' does not exist.")
                return

            print(f"\n🔍 Previewing top {limit} rows from table: {table_name}")
            table = Table(table_name, metadata, autoload_with=engine)
            result = connection.execute(table.select().limit(limit)).mappings().all()

            if not result:
                print("⚠️ No data found in this table.")
                return

            for idx, row in enumerate(result, 1):
                print(f"{idx:02d}. {row}")


    except sqlalchemy.exc.SQLAlchemyError as e:
        print("❌ Error querying the table:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preview rows from a PostgreSQL table.")
    parser.add_argument("table", help="Name of the table to preview")
    parser.add_argument("--limit", type=int, default=10, help="Number of rows to display (default: 10)")
    args = parser.parse_args()

    preview_table(args.table, args.limit)
