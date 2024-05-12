import mysql
from mysql.connector import Error
import config
# Connect to the MySQL database
def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**config.db_config)
    except Error as e:
        print(e)
    return conn

def db_connection_close(cursor, conn):
    if cursor:
        cursor.close()
    if conn:
        conn.close()