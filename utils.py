import streamlit as st
import tensorflow as tf
import numpy as np

import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image

@st.cache_resource
def load_model(name):
    model = tf.keras.models.load_model(name)
    return model

def predict(image, model):
    """
    Make prediction with PIL Image or numpy array input
    """
    # Перетворюємо PIL Image у numpy array, якщо потрібно
    if not isinstance(image, np.ndarray):
        image = keras_image.img_to_array(image)
        image = image / 255.0  # Нормалізація
    
    # Отримуємо очікуваний розмір входу моделі
    if hasattr(model, 'input_shape'):
        input_size = (model.input_shape[1], model.input_shape[2])
        # Змінюємо розмір зображення, якщо потрібно
        if image.shape[1:3] != input_size:
            image = tf.image.resize(image, input_size)
    
    # Додаємо вимір батчу, якщо потрібно
    if len(image.shape) == 3:
        image = np.expand_dims(image, axis=0)
    
    return model.predict(image)


##### For Saliency Map Generator #####

def load_and_preprocess_image(image_path, model=None, target_size=None):
    """
    Load and preprocess image with automatic size detection
    
    Args:
        image_path: Path or file-like object of the image
        model: Optional model to determine target size
        target_size: Optional explicit target size
    
    Returns:
        Preprocessed image array and original image size
    """
    original_img = keras_image.load_img(image_path)
    original_size = original_img.size  # (width, height)
    
    # Якщо модель вказана, використовуємо її очікуваний розмір входу
    if model is not None and hasattr(model, 'input_shape'):
        model_input_size = (model.input_shape[1], model.input_shape[2])
        target_size = model_input_size
    
    # Завантажуємо та змінюємо розмір зображення за потребою
    if target_size:
        img = keras_image.load_img(image_path, target_size=target_size)
    else:
        img = original_img
    
    # Перетворюємо в масив та нормалізуємо
    img_array = keras_image.img_to_array(img)
    img_array = img_array / 255.0
    
    return img_array, original_size
def generate_saliency_map(model, image):
    """Generate saliency map for given image and model"""
    # Normalize input image
    image = tf.cast(image, tf.float32)
    if len(image.shape) == 3:
        image = tf.expand_dims(image, axis=0)
    
    # Ensure image values are in [0,1] range
    if tf.reduce_max(image) > 1.0:
        image = image / 255.0

    with tf.GradientTape() as tape:
        image_tensor = tf.Variable(image)
        predictions = model(image_tensor)
        predicted_class = tf.argmax(predictions[0])
        class_score = predictions[0, predicted_class]
    
    gradients = tape.gradient(class_score, image_tensor)
    
    if gradients is None:
        gradients = tape.jacobian(predictions, image_tensor)
        gradients = tf.reduce_sum(gradients, axis=2)
        gradients = gradients[0]  # Remove batch dimension
    
    # Ensure correct shape and squeeze extra dimensions
    saliency = tf.reduce_max(tf.abs(gradients), axis=-1)
    saliency = tf.squeeze(saliency)  # Remove any extra dimensions
    
    return saliency.numpy(), predicted_class.numpy()

def visualize_saliency_on_image(original_image, saliency_map, alpha=0.4, power=2.0, colormap_name='jet'):
    # Create figure and axis
    fig, ax = plt.subplots()
    
    # Ensure saliency map has correct shape
    if len(saliency_map.shape) == 2:
        saliency_map = np.expand_dims(saliency_map, axis=-1)
    
    # Normalize saliency map to [0,1]
    saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
    
    # Apply power enhancement
    saliency_map = np.power(saliency_map, power)
    
    # Create colored saliency map using matplotlib
    cmap = plt.get_cmap(colormap_name)
    colored_saliency = cmap(np.squeeze(saliency_map))[:, :, :3]
    
    # Resize colored saliency if needed
    if colored_saliency.shape[:2] != original_image.shape[:2]:
        h, w = original_image.shape[:2]
        colored_saliency = np.array(Image.fromarray((colored_saliency * 255).astype(np.uint8)).resize((w, h))) / 255.0
    
    # Ensure original image is float32 and normalized
    original_image = original_image.astype(np.float32)
    if original_image.max() > 1.0:
        original_image = original_image / 255.0
    
    # Create overlay
    overlay = original_image * (1 - alpha) + colored_saliency * alpha
    overlay = np.clip(overlay, 0, 1)
    
    # Display the overlay
    ax.imshow(overlay)
    ax.axis('off')
    
    return fig