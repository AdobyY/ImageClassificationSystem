import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image

files = st.sidebar.file_uploader("Add your files", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
class_indices = {0: '2S1', 1: 'BMP2', 2: 'BRDM2', 3: 'BTR60', 4: 'BTR70', 5: 'D7', 6: 'SLICY', 7: 'T62', 8: 'T72', 9: 'ZIL131', 10: 'ZSU_23_4'}

models = {}

model_files = {
    "model-10": "model-10.h5",
    "model-20": "model-20.h5",
    "model-30": "model-30.h5"
}

# Load the models
for model_name, model_path in model_files.items():
    models[model_name] = tf.keras.models.load_model(model_path)

# Select model from sidebar
selected_model = st.sidebar.selectbox("Select a model", list(models.keys()))

def predict(image, model):
    image = image.resize((368, 368))
    image = image.convert('RGB')
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    predictions = model.predict(image)
    return predictions

button = st.button("Predict")
if button:
    if files:
        for file in files:
            image = Image.open(file)

            prediction = predict(image, models[selected_model])
            # Assuming the model outputs probabilities for multiple classes
            st.image(image, width=50)
            st.write(prediction)

    else:
        st.warning("Please upload a file first")

