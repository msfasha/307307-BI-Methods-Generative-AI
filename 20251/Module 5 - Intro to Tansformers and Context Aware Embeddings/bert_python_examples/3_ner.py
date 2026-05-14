# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.title("Example 3 — Named Entity Recognition")

ner = pipeline("ner", aggregation_strategy="simple")

text = st.text_area("Enter text:",
                    "John lives in New York and works at Google.")

if st.button("Run NER"):
    st.write(ner(text))
