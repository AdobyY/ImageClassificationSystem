from streamlit_option_menu import option_menu
import streamlit as st
from pages.predict import show_predict_page
from pages.models import show_models_page

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Predict", "Models"],
        icons = ["house", "book"]
    )

if selected == "Predict":
    show_predict_page()
elif selected == "Models":
    show_models_page()