import tensorflow as tf
import streamlit as st
import io


# Load the model
@st.cache_resource
def load_model(name):
    model = tf.keras.models.load_model(name)
    return model

# Capture the model summary
summary = io.StringIO()
model = load_model('model-10.h5')
model.summary(print_fn=lambda x: summary.write(x + '\n'))
summary_str = summary.getvalue()

st.markdown(
    """
<style>
div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
    width: 50vw;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.dialog("show_dialog")
def show_dialog():
    st.code(summary_str, language='python')
    st.html("<span class='big-dialog'></span>")
    if st.button("Close"):
        st.rerun()

if st.button("Show Model"):
    show_dialog()

