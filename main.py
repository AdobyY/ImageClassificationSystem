from streamlit_option_menu import option_menu
import streamlit as st
from pages.predict import show_predict_page
from pages.models import show_models_page
from pages.upload import show_upload_page
from database import add_user, get_user
from database import create_table, create_models_table
import bcrypt

create_table()
create_models_table()

# Функція для реєстрації користувачів
def register_user():
    st.title("Реєстрація")
    username = st.text_input("Введіть ім'я користувача")
    password = st.text_input("Введіть пароль", type="password")
    confirm_password = st.text_input("Підтвердіть пароль", type="password")
    if st.button("Зареєструватися"):
        if username and password and confirm_password:
            if password != confirm_password:
                st.error("Паролі не збігаються")
            else:
                user = get_user(username)
                if user:
                    st.error("Користувач з таким ім'ям вже існує")
                else:
                    add_user(username, password)
                    st.success("Реєстрація успішна. Тепер ви можете увійти.")
        else:
            st.error("Будь ласка, введіть ім'я користувача та пароль")

def login_user():
    st.title("Вхід")
    username = st.text_input("Введіть ім'я користувача")
    password = st.text_input("Введіть пароль", type="password")
    if st.button("Увійти"):
        if username and password:
            user = get_user(username)
            if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Невірне ім'я користувача або пароль")
        else:
            st.error("Будь ласка, введіть ім'я користувача та пароль")

# Перевірка, чи користувач увійшов
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["Predict", "Models", "Model Upload"],
            icons=["house", "book", "download"]
        )
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.rerun()

    if selected == "Predict":
        show_predict_page()
    elif selected == "Models":
        show_models_page()
    elif selected == "Model Upload":
        show_upload_page()
        
else:
    auth_option = st.sidebar.radio("Виберіть опцію", ["Вхід", "Реєстрація"])
    if auth_option == "Вхід":
        login_user()
    elif auth_option == "Реєстрація":
        register_user()