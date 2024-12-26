import bcrypt
import streamlit as st

from streamlit_option_menu import option_menu

from pages.predict import show_predict_page
from pages.analysis import show_models_page
from pages.upload import show_upload_page
from pages.my_models import show_my_models
from database import add_user, get_user
from database import create_table, create_models_table

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
    st.title("Registration")
    with st.form("register_form"):
        username = st.text_input("Enter username")
        password = st.text_input("Enter password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if username and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    user = get_user(username)
                    if user:
                        st.error("User with this username already exists")
                    else:
                        add_user(username, password)
                        st.success("Registration successful. You can now log in.")
            else:
                st.error("Please enter a username and password")

def login_user():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Enter username")
        password = st.text_input("Enter password", type="password")
        submit_button = st.form_submit_button("Login")
        
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
                    st.error("Invalid username or password")
            else:
                st.error("Please enter a username and password")

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
    auth_option = st.sidebar.radio("Choose an option", ["Login", "Register"])
    if auth_option == "Login":
        login_user()
    elif auth_option == "Register":
        register_user()