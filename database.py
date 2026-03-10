import sqlite3
SQL_DB_NAME = 'query.db'

def get_db_connection():
    connection = sqlite3.connect(SQL_DB_NAME)
    connection.row_factory = sqlite3.Row # Để truy xuất cột bằng tên: row['ten_cot']
    return connection