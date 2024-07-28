import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def test_connection():
    try:
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")

        print(f"Trying to connect to database {dbname} on host {host}:{port} with user {user}")

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print("Connection successful")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")



if __name__ == "__main__":
    test_connection()
