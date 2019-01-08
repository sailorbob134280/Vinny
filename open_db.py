import sqlite3
import os
from sqlite3 import Error

def connect_db(db_filename='wininv-data'):
    conn = None
    try:
        db_dir = os.getcwd()
        db_path = db_dir + db_filename
        conn = sqlite3.connect(db_path)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return conn


connect_db()