import streamlit as st
import tensorflow as tf

@st.cache_resource
def load_model(name):
    model = tf.keras.models.load_model(name)
    return model