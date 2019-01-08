import sqlite3
import os
from sqlite3 import Error

conn = None

def create_connection():
    try:
        conn = sqlite3.connect(':memory:')
        print(sqlite3.version)

        cursor = conn.cursor()
        cursor.execute('CREATE TABLE testdb(id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT unique, password TEXT)')
        conn.commit()

        name1 = 'Dave'
        phone1 = '1234567890'
        email1 = 'test@example.com'
        password1 = 'asdfg'

        cursor.execute('INSERT INTO testdb(name, phone, email, password) VALUES(?,?,?,?)', (name1, phone1, email1, password1))
        cursor.execute('SELECT id FROM testdb WHERE name=?', (name1,))
        id1 = cursor.fetchone()
        print('User {} inserted'.format(id1))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


create_connection()
print(os.getcwd())