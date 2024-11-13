import streamlit as st
from database import add_model, get_user
import json
import os
import uuid

def show_upload_page():
    st.title("Завантаження моделі")
    
    # Перевірка, чи користувач увійшов
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.error("Будь ласка, увійдіть, щоб завантажити модель.")
        return
    
    # Ввід імені моделі
    model_name = st.text_input("Введіть ім'я моделі")
    
    # Ввід class_indices
    class_indices_input = st.text_area("Введіть class_indices у форматі JSON (наприклад, {0: '2S1', 1: 'BMP2'})")
    
    # Завантаження файлу моделі
    uploaded_model = st.file_uploader("Завантажте файл моделі (.h5)", type=["h5"])
    
    if st.button("Завантажити модель"):
        if not model_name:
            st.error("Будь ласка, введіть ім'я моделі.")
        elif not class_indices_input:
            st.error("Будь ласка, введіть class_indices.")
        elif not uploaded_model:
            st.error("Будь ласка, завантажте файл моделі.")
        else:
            # Перевірка формату class_indices
            try:
                class_indices = eval(class_indices_input)
                if not isinstance(class_indices, dict):
                    st.error("class_indices повинні бути словником.")
                    return
                if not all(isinstance(v, str) for v in class_indices.values()):
                    st.error("Всі значення в словнику повинні бути текстовими.")
                    return
            except (SyntaxError, NameError, TypeError):
                st.error("Неправильний формат словника Python.")
                return
            
            # Отримання ID користувача
            user = get_user(st.session_state['username'])
            if not user:
                st.error("Користувач не знайдено.")
                return
            user_id = user[0]
            
            # Визначення директорії для збереження моделей
            models_dir = os.path.join("user_models", f"user_{st.session_state['username']}")
            os.makedirs(models_dir, exist_ok=True)
            
            # Створення унікальної назви файлу
            unique_suffix = uuid.uuid4().hex
            safe_model_name = "".join(c if c.isalnum() else "_" for c in model_name)
            full_model_name = f"{safe_model_name}_{st.session_state['username']}_{unique_suffix}.h5"
            model_path = os.path.join(models_dir, full_model_name)
            
            # Збереження завантаженої моделі на файлову систему
            try:
                with open(model_path, "wb") as f:
                    f.write(uploaded_model.getbuffer())
            except Exception as e:
                st.error(f"Сталася помилка при збереженні файлу моделі: {e}")
                return
            
            # Додавання моделі до бази даних
            try:
                add_model(user_id, safe_model_name, class_indices, full_model_name, models_dir)
                st.success("Модель успішно завантажена.")
            except Exception as e:
                st.error(f"Сталася помилка при додаванні моделі до бази даних: {e}")
                # Видалення збереженого файлу, якщо не вдалося додати його до бази даних
                if os.path.exists(model_path):
                    os.remove(model_path)