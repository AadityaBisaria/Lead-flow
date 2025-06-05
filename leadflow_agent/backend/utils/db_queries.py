import psycopg2
from psycopg2.extras import RealDictCursor

def run_query(query: str, params: list = []):
    try:
        # Connect to your PostgreSQL DB
        conn = psycopg2.connect(
            dbname="leadflow",       # or your DB name
            user="postgres",
            password="Postgres",
            host="localhost",
            port="5432"
        )

        # Create a cursor with dictionary-like results
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Execute query with optional parameters
        cursor.execute(query, params)

        # Fetch results if it's a SELECT query
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
        else:
            conn.commit()
            results = []

        # Close connection
        cursor.close()
        conn.close()
        return results

    except Exception as e:
        print(f"[DB ERROR] {e}")
        return []
