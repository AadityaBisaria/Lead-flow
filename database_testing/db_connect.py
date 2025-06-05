import psycopg2

try:
# Define connection parameters
    conn = psycopg2.connect(
        dbname="leadflow",      # Replace with your actual database name
        user="postgres",          # Replace with your PostgreSQL username
        password="Postgres",  # Replace with your PostgreSQL password
        host="localhost",
        port="5432"
    )
    print("✅ Connected to the database successfully!")

    # Create and close a cursor to verify further
    cur = conn.cursor()
    cur.execute("SELECT version();")  # Simple command
    db_version = cur.fetchone()
    print("Database version:", db_version)

    cur.close()
    conn.close()

except psycopg2.Error as e:
    print("❌ Failed to connect to the database")
    print("Error:", e)
