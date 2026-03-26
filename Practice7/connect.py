import psycopg2
from config import load_config

def connect():
    config = load_config() #calls load_config() and stores the result in config
    conn = psycopg2.connect(**config) #opens a connection to postgresql using thelogin details
    return conn

