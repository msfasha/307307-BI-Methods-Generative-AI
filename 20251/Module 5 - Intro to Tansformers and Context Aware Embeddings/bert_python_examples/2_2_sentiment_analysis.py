# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="Multiple Sentiment Analysis", layout="centered")

st.title("Multiple Text Sentiment Analysis")

# Load classifier
@st.cache_resource
def load_classifier():
    return pipeline("sentiment-analysis")

classifier = load_classifier()

# Multi-line text input
texts_raw = st.text_area(
    "Enter one text per line:",
    "I hate this product\nThis is amazing!\nIt's okay, nothing special"
)

# Button
if st.button("Analyze All"):
    # Convert text area into list of non-empty lines
    texts = []
    for line in texts_raw.split("\n"):
        stripped_line = line.strip()
        if stripped_line:
            texts.append(stripped_line)

    if not texts:
        st.warning("Please enter at least one line.")
    else:
        results = classifier(texts)

        st.write("### Results")
        for txt, res in zip(texts, results):
            st.write(f"**Text:** {txt}")
            st.write(f"Sentiment: **{res['label']}**, Score: **{res['score']:.4f}**")
            st.write("---")
