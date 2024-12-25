import streamlit as st
from database import add_model, get_user, get_models
import os
import uuid
import pandas as pd


def show_upload_page():
    st.title("Upload Model")
    
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.error("Please log in to upload a model.")
        return
    
    # Model name input
    model_name = st.text_input("Enter model name")
    
    # Class indices input
    class_indices_input = st.text_area("Enter class_indices in JSON format (e.g., {0: '2S1', 1: 'BMP2'})")
    
    # Upload model file
    uploaded_model = st.file_uploader("Upload model file (.h5)", type=["h5"])
    
    if st.button("Upload Model"):
        if not model_name:
            st.error("Please enter a model name.")
        elif not class_indices_input:
            st.error("Please enter class_indices.")
        elif not uploaded_model:
            st.error("Please upload a model file.")
        else:
            # Validate class_indices format
            try:
                class_indices = eval(class_indices_input)
                if not isinstance(class_indices, dict):
                    st.error("class_indices must be a dictionary.")
                    return
                if not all(isinstance(v, str) for v in class_indices.values()):
                    st.error("All values in the dictionary must be strings.")
                    return
            except (SyntaxError, NameError, TypeError):
                st.error("Invalid Python dictionary format.")
                return
            
            # Get user ID
            user = get_user(st.session_state['username'])
            if not user:
                st.error("User not found.")
                return
            user_id = user[0]
            
            models_df = pd.DataFrame(get_models(user[0]), columns=['model_name', 'model_path', 'class_indices'])
            if not models_df.empty and model_name in models_df['model_name'].values:
                st.error(f"Model with name '{model_name}' already exists. Please choose a different name.")
                return

            # Define directory for saving models
            models_dir = os.path.join("user_models", f"user_{st.session_state['username']}")
            os.makedirs(models_dir, exist_ok=True)
            
            full_model_name = f"{model_name}_{st.session_state['username']}.h5"
            model_path = os.path.join(models_dir, full_model_name)
            
            # Save uploaded model to filesystem
            try:
                with open(model_path, "wb") as f:
                    f.write(uploaded_model.getbuffer())
            except Exception as e:
                st.error(f"An error occurred while saving the model file: {e}")
                return
            
            # Add model to database
            try:
                add_model(user_id, model_name, class_indices, models_dir)
                st.success("Model successfully uploaded.")
            except Exception as e:
                st.error(f"An error occurred while adding the model to the database: {e}")
                # Delete saved file if database insertion failed
                if os.path.exists(model_path):
                    os.remove(model_path)
        st.rerun()

