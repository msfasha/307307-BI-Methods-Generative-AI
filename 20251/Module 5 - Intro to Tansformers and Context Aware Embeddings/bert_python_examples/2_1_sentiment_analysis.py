# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="Single Sentiment Analysis", layout="centered")

st.title("Single Text Sentiment Analysis")

# Load classifier once
@st.cache_resource
def load_classifier():
    return pipeline("sentiment-analysis")

classifier = load_classifier()

# Input box
text = st.text_input("Enter text:", "I love using Hugging Face!")

# Button
if st.button("Analyze"):
    result = classifier(text)[0]
    st.write("### Result")
    st.write(f"**Sentiment:** {result['label']}")
    st.write(f"**Score:** {result['score']:.4f}")
