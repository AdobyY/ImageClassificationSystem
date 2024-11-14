import psycopg2
import bcrypt
import json
from psycopg2 import pool
import os
import streamlit as st
import uuid  # Add import for unique identifiers

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
        print(f"Помилка при створенні таблиці users: {error}")
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

def create_models_table():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS models (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            model_name TEXT NOT NULL,
                            model_path TEXT NOT NULL,
                            class_indices JSON NOT NULL)''')  # Removed BYTEA
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"Помилка при створенні таблиці models: {error}")
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

def add_user(username, password):
    try:
        conn = get_connection()
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

st.cache_data
def get_user(username):
    try:
        conn = get_connection()
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

def add_model(user_id, model_name, class_indices, model_filename, model_path):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        unique_suffix = uuid.uuid4().hex  # Generate unique identifier
        full_model_name = f"{model_name}_{st.session_state['username']}_{unique_suffix}.h5"  # Naming convention
        full_model_path = os.path.join(model_path, full_model_name)  # Complete file path
        cursor.execute('INSERT INTO models (user_id, model_name, model_path, class_indices) VALUES (%s, %s, %s, %s)',
                      (user_id, model_name, full_model_path, json.dumps(class_indices)))
        conn.commit()
        return full_model_path  # Return the path for saving the file
    except (Exception, psycopg2.Error) as error:
        print(f"Помилка при додаванні моделі: {error}")
        raise
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

@st.cache_data
def get_models(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT model_name, class_indices, model_path FROM models WHERE user_id = %s', (user_id,))
        models = cursor.fetchall()
        return models
    except (Exception, psycopg2.Error) as error:
        print(f"Помилка при отриманні моделей: {error}")
        return []
    finally:
        if cursor:
            cursor.close()
        release_connection(conn)

# Створення таблиці при запуску
create_table()
create_models_table()