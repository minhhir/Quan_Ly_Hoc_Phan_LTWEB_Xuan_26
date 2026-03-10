import sqlite3
SQL_DB_NAME = 'query.db'


def get_db_connection():
    connection = sqlite3.connect(SQL_DB_NAME)
    connection.row_factory = sqlite3.Row # Để truy xuất cột bằng tên: row['ten_cot']
    return connection


def init_auth_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (role_id) REFERENCES role(id)
        )
    ''')

    cursor.execute("INSERT OR IGNORE INTO role (name) VALUES ('admin')")
    cursor.execute("INSERT OR IGNORE INTO role (name) VALUES ('user')")

    conn.commit()
    conn.close()