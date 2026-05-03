import psycopg2
from config import load_config

def connect():
    config = load_config()          # loads credentials from database.ini
    conn = psycopg2.connect(**config)  # opens connection to postgresql
    return conn
