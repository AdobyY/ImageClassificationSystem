import streamlit as st

files = st.sidebar.file_uploader("Add your files",accept_multiple_files=True)

st.write(files)