import os
import mysql.connector
from mysql.connector import Error

def load_env():
    """Load variables from .env file into os.environ"""
    # The .env file is in the root directory, which is one level up from database/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    # Strip quotes if present
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val

# Load environmental variables
load_env()

def get_db_connection():
    """Establish and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DATABASE', 'virtual_classroom'),
            autocommit=True
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
