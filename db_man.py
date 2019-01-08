import sqlite3
import os
from sqlite3 import Error


class DatabaseManager:

    def __init__(self, db_filename)

    def get_version(db_filename='wininv-data'):
        conn = None
        try:
            db_dir = os.getcwd()
            db_path = db_dir + db_filename
            conn = sqlite3.connect(db_path)
            version = sqlite3.version
            return version
        except Error as e:
            print(e)
        finally:
            if conn is not None:
                conn.close()


