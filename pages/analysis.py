import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from utils import *
from database import get_user, get_models

def show_models_page():
    files = st.sidebar.file_uploader("Add your files", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
    models, models_df = get_models_dict_and_df()
    
    selected_models = st.sidebar.multiselect("Select models", list(models.keys()))

    # Create tabs
    tab1, tab2 = st.tabs(["Datasets", "Saliency Maps"])

    if files and selected_models:
        with tab1:
            # Create predictions for each model
            for model_name in selected_models:
                st.subheader(f"Model: {model_name}")
                
                # Get class indices
                class_indices = models_df.loc[models_df['model_name'] == model_name, 'class_indices'].values[0]
                if isinstance(class_indices, str):
                    class_indices = eval(class_indices)
                class_names = [class_indices[str(i)] for i in range(len(class_indices))]
                
                # Create DataFrame
                results = []
                file_names = []
                for file in files:
                    image = Image.open(file)
                    prediction = predict(image, models[model_name])
                    results.append(prediction)
                    file_names.append(file.name)
                
                # Create and display DataFrame
                probabilities_df = pd.DataFrame(columns=class_names)
                for file, result in zip(file_names, results):
                    row = pd.Series(result.flatten(), index=class_names, name=file)
                    probabilities_df = pd.concat([probabilities_df, row.to_frame().T], ignore_index=False)
                
                st.dataframe(probabilities_df)
                st.markdown("---")

        with tab2:
            # Saliency controls in main area
            power = st.slider('Power (Intensity)', 1.0, 5.0, 2.0, 0.1)
            alpha = st.slider('Alpha (Overlay)', 0.0, 1.0, 0.4, 0.1)    
            colormap = st.selectbox('Colormap', ['jet', 'viridis', 'plasma', 'inferno', 'cividis'])
            
            # Button to generate saliency maps
            generate_button = st.button("Generate Saliency Maps")
            
            # Only process and show saliency maps when button is pressed
            if generate_button:
                # Validate that files and models are selected
                if not files or not selected_models:
                    st.warning("Please upload files and select models")
                else:
                    # Store current parameters in session state
                    st.session_state['saliency_params'] = {
                        'power': power,
                        'alpha': alpha,
                        'colormap': colormap
                    }
                    
                    # Use the first selected model
                    model = models[selected_models[0]]
                    processed_images = []
                    
                    for file in files:
                        image = Image.open(file)
                        processed_image, _ = load_and_preprocess_image(file, model=model)
                        saliency_map, predicted_class = generate_saliency_map(model, processed_image)
                        
                        fig = visualize_saliency_on_image(
                            processed_image,
                            saliency_map,
                            alpha=alpha,
                            power=power,
                            colormap_name=colormap
                        )
                        processed_images.append((fig, file.name))
                    
                    # Store processed images in session state
                    st.session_state['processed_images'] = processed_images
            
            # Display grid of processed images only when they exist in session state
            if 'processed_images' in st.session_state:
                for i in range(0, len(st.session_state['processed_images']), 4):
                    cols = st.columns(4)
                    for j, col in enumerate(cols):
                        if i + j < len(st.session_state['processed_images']):
                            with col:
                                fig, filename = st.session_state['processed_images'][i + j]
                                st.pyplot(fig, use_container_width=True)
                                plt.close(fig)
                                st.caption(filename)
    else:
        st.warning("Please upload files and select models")

def get_models_dict_and_df():
    user = get_user(st.session_state['username'])
    if not user:
        st.error("No user found")
        return {}, pd.DataFrame()
    
    models_df = pd.DataFrame(get_models(user[0]), columns=['model_name', 'class_indices', 'model_path'])
    models = {name: load_model(path) for name, path in 
             models_df.set_index('model_name')['model_path'].items()}
    
    return models, models_df