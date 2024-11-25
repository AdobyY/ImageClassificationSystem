import streamlit as st
import pandas as pd
import io
import os

from database import get_user, get_models, remove_model_from_db
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
                col_name, col_button, col_button2 = st.columns([3, 1, 1])
                with col_name:
                    st.write("") 
                    st.write(f"📄 **{model_name.capitalize()}**")
                with col_button:
                    if st.button("🔍 View", key=model_name,
                                 use_container_width=True):
                        show_model(model_path)
                with col_button2:
                    if st.button("🗑️ Delete", key=f"{model_name}_delete",
                              use_container_width=True):
                            @st.dialog(f"🚨 Ви впевнені, що хочете видалити модель '{model_name.capitalize()}'?")
                            def delete_model_dialog():
                                st.write("")

                                st.html("<span class='big-dialog'></span>")

                                col1, col2, _ = st.columns([1, 1, 3])
                                with col1:
                                    if st.button("No", use_container_width=True):
                                        st.rerun()
                                with col2:
                                    if st.button("Yes", use_container_width=True):
                                        delete_model(model_name, model_path)
                                        st.rerun()

                            delete_model_dialog()
                                           


def show_model(model_path):
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


def delete_model(model_name, model_path):
    try:
        if os.path.exists(model_path):
            os.remove(model_path)
            remove_model_from_db(model_name)  
            st.rerun()
            st.success(f"✅ Модель '{model_name}' успішно видалена.")
        else:
            st.error(f"❌ Файл моделі '{model_path}' не знайдено.")
    except Exception as e:
        st.error(f"❌ Сталася помилка при видаленні моделі '{model_name}': {e}")
