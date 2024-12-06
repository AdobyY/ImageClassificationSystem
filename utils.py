import streamlit as st
import tensorflow as tf
import numpy as np

@st.cache_resource
def load_model(name):
    model = tf.keras.models.load_model(name)
    return model

def predict(image, model):
    input_shape = model.input_shape
    input_size = (input_shape[1], input_shape[2])
    image = image.resize(input_size)
    image = image.convert('RGB')
    image = np.array(image) / 255.0  # Нормалізація
    image = np.expand_dims(image, axis=0)  # Додавання виміру для батчу
    predictions = model.predict(image)  # Прогнозування
    return predictions