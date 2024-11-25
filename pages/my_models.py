import streamlit_antd_components as sac
import streamlit as st
import pandas as pd
import io
import os

from database import get_user, get_models
from utils import *


def show_my_models():
    user = get_user(st.session_state['username'])
    if user:
        models_df = pd.DataFrame(get_models(user[0]), columns=['model_name', 'class_indices', 'model_path'])
        st.dataframe(models_df)

        for _, row in models_df.iterrows():
            model_name, model_path = row['model_name'], row['model_path']

            if not os.path.exists(model_path):
                st.error(f"Файл моделі '{model_path}' не знайдено.")
                continue 

            with st.container():
                col_name, col_button = st.columns([1, 3])
                with col_name:
                    st.write(f"Модель: {model_name}")
                with col_button:
                    if st.button("Показати модель", key=model_name):
                        show_model(model_name, model_path)
                # st.divider()

            


def show_model(model_name, model_path):
    summary = io.StringIO()
    model = load_model(model_path)
    model.summary(print_fn=lambda x: summary.write(x + '\n'))
    summary_str = summary.getvalue()

    st.markdown(
        """
        <style>
        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 50vw;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    @st.dialog("show_dialog")
    def show_dialog():
        st.code(summary_str, language='python')
        st.html("<span class='big-dialog'></span>")
        if st.button("Close"):
            st.rerun()

    show_dialog()