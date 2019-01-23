import sqlite3
import os
from sqlite3 import Error


class DatabaseManager:

    def __init__(self, db_filename='wineinv_data.db'):
        self.db_filename = db_filename
        self.db_path = os.getcwd() + '\\' + db_filename

    def get_version(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            version = sqlite3.version
            return version
        except Error as e:
            print(e)
        finally:
            if conn is not None:
                conn.close()
    
    def db_execute(self, command, placeholders=(), ret_id=False):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(command, placeholders)
            if ret_id == True:
                last_id = cursor.lastrowid
            conn.commit()
        except Error as e:
            print(e)
            conn.rollback()
            print('Transaction failed due to an error. Database has been rolled back.')
        finally:
            if conn is not None:
                conn.close()
            if ret_id == True:
                return last_id

    def db_fetch(self, command, placeholders=(), rows='one'):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(command, placeholders)
            if rows is 'one' or rows is 1:
                return cursor.fetchone()
            elif rows is 'all':
                return cursor.fetchall()
            elif isinstance(rows, not int) or rows is 0:
                raise FetchError('Rows must be one, all, or a non-zero integer')
            else:
                return cursor.fetchmany(rows)
        except FetchError as fe:
            print(fe)
        except Error as e:
            print(e)
        finally:
            if conn is not None:
                conn.close()
        
    def db_getcolnames(self, table='winedata'):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ' + table)
            row = cursor.fetchone()
            return row.keys()
        except Error as e:
            print(e)
            print('Transaction failed due to an error')
        finally:
            if conn is not None:
                conn.close()  

########
#Errors#
########
# class Error(Exception):
#     '''Base class for custom error handling during database operations'''
#     pass

class FetchError(Error):
    '''Error to be raised if rows argument is out of range'''
    def __init__(self, message):
        self.message = message
