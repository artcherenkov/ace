import psycopg2
from psycopg2.extensions import connection as _connection
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.conn = self.get_db_connection()

    def get_db_connection(self) -> _connection:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise
