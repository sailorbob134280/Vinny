import sqlite3
from sqlite3 import Error
import os


command = '''SELECT * FROM winedata WHERE wine_id LIKE ?'''
placeholders = ('wine_id', 1)
rows = 'all'
db_path = os.getcwd() + '\\' + 'wineinv_data.db'

conn = None
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(command, (1,))
    if rows is 'one':
        result = cursor.fetchone()
    elif rows is 'all':
        result = cursor.fetchall()
    # elif isinstance(rows, not int):
    #     raise FetchError('Rows must be one, all, or an integer')
    else:
        result = cursor.fetchmany(rows)
# except FetchError as fe:
#     print(fe)
except Error as e:
    print(e)
finally:
    if conn is not None:
        conn.close()

print(result)