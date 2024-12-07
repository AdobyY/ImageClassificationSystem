import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd

from database import get_user, get_models
from utils import *

def show_predict_page():
    st.write("# Image Classification")
    # Initialize session state variables if not already set
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'all_predictions' not in st.session_state:
        st.session_state.all_predictions = []
    
    # Fetch models only once
    if 'models' not in st.session_state or 'models_df' not in st.session_state:
        st.session_state.models, st.session_state.models_df = get_models_dict_and_df()

    # Sidebar file uploader and model selection
    uploaded_file = st.sidebar.file_uploader("Завантажте своє зображення", type=["jpg", "jpeg", "png"], key='shared_uploader')
    
    # Unified model multiselect for both tabs
    selected_models = st.sidebar.multiselect(
        "Оберіть моделі", 
        list(st.session_state.models.keys())
    )

    # Create tabs
    col_stats, col_visualize = st.tabs(["Stats", "Visualize"])

    # Update uploaded file in session state
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        
    with col_stats:
        if st.session_state.uploaded_file is not None:
            image = Image.open(st.session_state.uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image, use_container_width=True)
                st.text("")
                st.text("")
                btn_predict = st.button('Predict')
            
            with col2:
                if btn_predict:
                    if not selected_models:
                        st.warning('Будь ласка, оберіть хоча б одну модель для передбачення.')
                    else:
                        st.session_state.all_predictions.clear()  # Clear previous predictions

                        for model_name in selected_models:
                            model = st.session_state.models[model_name]
                            # Get class indices for current model
                            class_indices = st.session_state.models_df.loc[
                                st.session_state.models_df['model_name'] == model_name, 
                                'class_indices'
                            ].values[0]
                            
                            if isinstance(class_indices, str):
                                class_indices = eval(class_indices)
                            
                            predictions = predict(image, model)
                            top_3_indices = np.argsort(predictions[0])[-3:][::-1]
                            top_3_predictions = [(class_indices[str(index)], predictions[0][index]) for index in top_3_indices]
                            st.session_state.all_predictions.append((model_name, top_3_predictions))

                # Visualization of predictions
                Graph, Data = st.tabs(["Graph", "Data"])
                with Graph:
                    if st.session_state.all_predictions:
                        # Prepare chart data
                        chart_data = pd.DataFrame(columns=['Model', 'Class', 'Probability'])
                        for model_name, top_3_predictions in st.session_state.all_predictions:
                            for class_name, probability in top_3_predictions:
                                new_row = pd.DataFrame({
                                    'Model': [model_name], 
                                    'Class': [class_name], 
                                    'Probability': [probability]
                                })
                                chart_data = pd.concat([chart_data, new_row], ignore_index=True)
                        
                        # Plot bar chart
                        if len(selected_models) == 1:
                            chart_data = chart_data.set_index('Class')
                            st.bar_chart(chart_data[['Probability']])
                        else:
                            chart_data = chart_data.pivot(index='Class', columns='Model', values='Probability')
                            st.bar_chart(chart_data, stack=False)

                with Data:
                    if 'chart_data' in locals():
                        st.write(chart_data)

        else:
            st.info('Завантажте своє зображення для передбачення.')

    with col_visualize:
        if st.session_state.uploaded_file is not None and selected_models:
            # Use first selected model for saliency map
            selected_model = selected_models[0]
            
            # Ensure image is preprocessed for saliency map
            image, original_size = load_and_preprocess_image(
                st.session_state.uploaded_file, 
                model=st.session_state.models[selected_model]
            )

            col1, col2 = st.columns(2)

            with col2:
                power = st.slider('Power (Підвищення важливості ознак)', 1.0, 5.0, 2.0, 0.1)
                alpha = st.slider('Alpha (Коефіцієнт накладення)', 0.0, 1.0, 0.7, 0.1)
                colormap_name = st.selectbox('Колірна карта', [
                    'coolwarm', 'viridis', 'plasma', 'inferno', 'cividis'
                ])

                if st.button('Згенерувати Saliency Map'):
                    # Ensure image is preprocessed for saliency map
                    image, original_size = load_and_preprocess_image(
                        st.session_state.uploaded_file, 
                        model=st.session_state.models[selected_model]
                    )
                    saliency_map, predicted_class = generate_saliency_map(
                        st.session_state.models[selected_model], 
                        image
                    )
                    st.session_state['saliency_map'] = saliency_map
                    st.session_state['predicted_class'] = predicted_class

            with col1:
                # Display saliency map
                if 'saliency_map' in st.session_state and st.session_state['saliency_map'] is not None:
                    fig = visualize_saliency_on_image(
                        image,
                        st.session_state['saliency_map'],
                        alpha=alpha,
                        power=power,
                        colormap_name=colormap_name
                    )
                    st.pyplot(fig)
                    plt.close(fig)

        else:
            st.warning('Будь ласка, завантажте зображення та оберіть модель для візуалізації.')

def get_models_dict_and_df():
    user = get_user(st.session_state['username'])
    if not user:
        st.error("No user found")
        return {}, pd.DataFrame()
    
    models_df = pd.DataFrame(get_models(user[0]), columns=['model_name', 'class_indices', 'model_path'])
    
    models = {}
    for _, row in models_df.iterrows():
        models[row['model_name']] = load_model(row['model_path'])

    return models, models_df