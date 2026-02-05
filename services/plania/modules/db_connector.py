import mysql.connector
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("DBConnector")

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "plania_db"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return connection
    except mysql.connector.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None
