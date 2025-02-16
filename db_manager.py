import mysql.connector
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger('AlphaLLM')

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.conn = None
        self.cursor = None
        
        if not all([self.host, self.user, self.password, self.database]):
            logger.error("Missing database credentials in .env file.")
            raise ValueError("Missing database credentials in .env file.")

        try:
            self.connect()
            logger.info("Database connection established.")
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            logger.error(f"Database query failed: {e}")
            self.conn.rollback()
            return False

    def fetchone(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except mysql.connector.Error as e:
            logger.error(f"Database query failed: {e}")
            return None

    def fetchall(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error(f"Database query failed: {e}")
            return None

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logger.info("Database connection closed.")