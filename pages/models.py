import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from utils import *
from database import get_user, get_models


def show_models_page():
    files = st.sidebar.file_uploader("Add your files", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
    
    # Отримуємо користувача з сесії
    user = get_user(st.session_state['username'])
    if user:
        models_df = pd.DataFrame(get_models(user[0]), columns=['model_name', 'class_indices', 'model_path'])
    else:
        st.error("No user found")
        return
    
    # Створюємо словник моделей
    model_files = models_df.set_index('model_name')['model_path'].to_dict()
    
    models = {}
    for model_name, model_path in model_files.items():
        models[model_name] = load_model(model_path)
    
    selected_model = st.sidebar.selectbox("Select a model", list(models.keys()))
    
    # Отримуємо індекси класів для вибраної моделі
    class_indices = models_df.loc[models_df['model_name'] == selected_model, 'class_indices'].values[0]
    if isinstance(class_indices, str):
        class_indices = eval(class_indices)  # Конвертуємо JSON зі строки в словник
    
    # Імена класів у правильному порядку
    class_names = [class_indices[str(i)] for i in range(len(class_indices))]
    
    button = st.sidebar.button("Predict")
    if button:
        results = []
        if files:
            for file in files:
                image = Image.open(file)
                prediction = predict(image, models[selected_model])
                results.append(prediction)
            
            file_names = [file.name for file in files]
            
            # Створюємо DataFrame для ймовірностей
            probabilities_df = pd.DataFrame(columns=class_names)
            
            # Заповнюємо DataFrame значеннями
            for file, result in zip(file_names, results):
                row = pd.Series(result.flatten(), index=class_names, name=file)
                probabilities_df = pd.concat([probabilities_df, row.to_frame().T], ignore_index=False)
        else:
            st.warning("Please upload a file first")
            return
        
        st.write(probabilities_df)
