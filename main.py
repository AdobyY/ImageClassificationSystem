from streamlit_option_menu import option_menu
import streamlit as st
from pages.predict import show_predict_page
from pages.analysis import show_models_page
from pages.upload import show_upload_page
from pages.my_models import show_my_models
from database import add_user, get_user
from database import create_table, create_models_table
import bcrypt

# Create tables
create_table()
create_models_table()

# Initialize session state for persistent login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

@st.cache_resource
def get_auth_manager():
    return {
        "current_user": None,
        "auth_status": False
    }

auth_manager = get_auth_manager()

def register_user():
    st.title("Реєстрація")
    with st.form("register_form"):
        username = st.text_input("Введіть ім'я користувача")
        password = st.text_input("Введіть пароль", type="password")
        confirm_password = st.text_input("Підтвердіть пароль", type="password")
        submit_button = st.form_submit_button("Зареєструватися")
        
        if submit_button:
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
    with st.form("login_form"):
        username = st.text_input("Введіть ім'я користувача")
        password = st.text_input("Введіть пароль", type="password")
        submit_button = st.form_submit_button("Увійти")
        
        if submit_button:
            if username and password:
                user = get_user(username)
                if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    auth_manager["current_user"] = username
                    auth_manager["auth_status"] = True
                    st.rerun()
                else:
                    st.error("Невірне ім'я користувача або пароль")
            else:
                st.error("Будь ласка, введіть ім'я користувача та пароль")

# Check if user is already authenticated
if auth_manager["auth_status"]:
    st.session_state['logged_in'] = True
    st.session_state['username'] = auth_manager["current_user"]

# Main application logic
if st.session_state['logged_in']:
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["Predict", "Analysis", "Model Upload", "My Models"],
            icons=["house", "clipboard-data", "download", "bookmark"]
        )
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            auth_manager["current_user"] = None
            auth_manager["auth_status"] = False
            st.rerun()
    
    if selected == "Predict":
        show_predict_page()
    elif selected == "Analysis":
        show_models_page()
    elif selected == "Model Upload":
        show_upload_page()
    elif selected == "My Models":
        show_my_models()        

else:
    auth_option = st.sidebar.radio("Виберіть опцію", ["Вхід", "Реєстрація"])
    if auth_option == "Вхід":
        login_user()
    elif auth_option == "Реєстрація":
        register_user()