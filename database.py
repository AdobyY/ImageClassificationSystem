import psycopg2
import bcrypt

# Налаштування пулу з'єднань
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",  # змініть на ваш хост
    database="test",
    user="postgres",  # стандартний користувач PostgreSQL
    password="root"  # змініть на ваш пароль
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

def create_table():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            password BYTEA NOT NULL)''')
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"Помилка при створенні таблиці: {error}")
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

def add_user(username, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)',
                      (username, hashed_password))
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"Помилка при додаванні користувача: {error}")
        raise
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

def get_user(username):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        if user:
            # Конвертуємо memoryview в bytes для паролю
            return (user[0], user[1], bytes(user[2]))
        return user
    except (Exception, psycopg2.Error) as error:
        print(f"Помилка при отриманні користувача: {error}")
        return None
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

# Створення таблиці при запуску
create_table()