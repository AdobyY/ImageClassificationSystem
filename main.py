import streamlit as st
from PIL import Image
import tensorflow as tf
import numpy as np
import pandas as pd

# Завантаження попередньо навченої моделі
# model = tf.keras.models.load_model('model-10.h5')
class_indices = {0: '2S1', 1: 'BMP2', 2: 'BRDM2', 3: 'BTR60', 4: 'BTR70', 5: 'D7', 6: 'SLICY', 7: 'T62', 8: 'T72', 9: 'ZIL131', 10: 'ZSU_23_4'}

# Функція для передбачення класу зображення
def predict(image, model):
    image = image.resize((368, 368))
    image = image.convert('RGB')
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    predictions = model.predict(image)
    return predictions

# Інтерфейс Streamlit
st.write('## Image Classification System')

# if 'selected_models' not in st.session_state:
#     st.session_state.selected_models = ['model-10.h5']

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'all_predictions' not in st.session_state:
    st.session_state.all_predictions = []

selected_models = st.sidebar.multiselect(
    'Оберіть моделі для передбачення',
    ['model-10.h5', 'model-20.h5', 'model-30.h5']
)

uploaded_file = st.sidebar.file_uploader("Завантажте своє зображення", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

if st.session_state.uploaded_file is not None:
    image = Image.open(st.session_state.uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, use_container_width=True)
    
    if st.button('Predict'):
        if not selected_models:
            st.warning('Будь ласка, оберіть хоча б одну модель для передбачення.')
        else:
            st.session_state.all_predictions.clear()  # Очищаємо попередні передбачення

            for model_name in selected_models:
                model = tf.keras.models.load_model(model_name)
                predictions = predict(image, model)
                top_3_indices = np.argsort(predictions[0])[-3:][::-1]
                top_3_predictions = [(class_indices[index], predictions[0][index]) for index in top_3_indices]
                st.session_state.all_predictions.append((model_name, top_3_predictions))

    with col2:
        Graph, Data = st.tabs(["Graph", "Data"])
        with Graph:
        # Підготовка даних для стовпчикової діаграми
            chart_data = pd.DataFrame(columns=['Model', 'Class', 'Probability'])
            for model_name, top_3_predictions in st.session_state.all_predictions:
                for class_name, probability in top_3_predictions:
                    new_row = pd.DataFrame({'Model': [model_name], 'Class': [class_name], 'Probability': [probability]})
                    chart_data = pd.concat([chart_data, new_row], ignore_index=True)
            
            if selected_models:
                # chart_data = chart_data[chart_data['Model'].isin(selected_models)]
                # Побудова стовпчикової діаграми
                if len(selected_models) == 1:
                    chart_data = chart_data.set_index('Class')
                    st.bar_chart(chart_data[['Probability']])
                else:
                    chart_data = chart_data.pivot(index='Class', columns='Model', values='Probability')
                    st.bar_chart(chart_data, stack=False)

        with Data:
            st.write(chart_data, use_container_width=True)
