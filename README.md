# ImageClassificationSystem

## Overview

ImageClassificationSystem is a web-based application built using Streamlit that allows users to upload, manage, and use machine learning models for image classification. The system supports user authentication, model management, and visualization of model predictions and saliency maps.

## Features

- **User Authentication**: Secure user registration and login.
- **Model Upload**: Upload and manage machine learning models.
- **Image Classification**: Predict image classes using uploaded models.
- **Saliency Maps**: Generate and visualize saliency maps to understand model predictions.
- **Batch Analysis**: Perform batch analysis on multiple images and visualize results.

## Project Structure

```
ImageClassificationSystem/
├── __pycache__/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── database.py
├── main.py
├── pages/
│   ├── __pycache__/
│   ├── analysis.py
│   ├── my_models.py
│   ├── predict.py
│   ├── upload.py
├── README.md
├── user_models/
│   ├── user_1/
│   └── user_a/
│       ├── DenseNeet_a.h5
│       ├── EfficientNet_a.h5
│       ├── MobileNet_a.h5
│       └── ResNet_a.h5
└── utils.py
```

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/ImageClassificationSystem.git
    cd ImageClassificationSystem
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    - Ensure you have PostgreSQL installed and running.
    - Update the database connection settings in [`database.py`](database.py).

5. **Run the application**:
    ```sh
    streamlit run main.py
    ```

## Usage

### User Authentication

- **Register**: Create a new account by providing a username and password.
- **Login**: Access your account by entering your username and password.

### Model Management

- **Upload Model**: Navigate to the "Model Upload" page to upload a new model. Provide the model name, class indices, and the model file (.h5).
- **Manage Models**: View, delete, and inspect your uploaded models on the "My Models" page.

### Image Classification

- **Predict**: Upload an image and select a model to predict its class on the "Predict" page. View the top predictions and their probabilities.
- **Saliency Maps**: Generate and visualize saliency maps to understand which parts of the image contributed to the model's prediction.

### Batch Analysis

- **Batch Analysis**: Upload multiple images and select models to perform batch analysis on the "Analysis" page. View the results in a tabular format and generate saliency maps for the images.

## Configuration

The application can be configured using the [`.streamlit/config.toml`](.streamlit/config.toml) file. For example, you can set the maximum upload size and toggle the sidebar navigation.

```toml
[server]
maxUploadSize = 500

[client]
showSidebarNavigation = false
```

## Coursework

The project includes a coursework document that provides detailed information about the development and functionality of the ImageClassificationSystem. You can find the coursework document in the `Ярінко Богдан КА-42мп Курсова робота.docx` file.


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.


## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [TensorFlow](https://www.tensorflow.org/)
- [PostgreSQL](https://www.postgresql.org/)
