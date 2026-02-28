# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.title("Example 7 — Translation EN → FR")

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")

text = st.text_input("English text:", "Hello, how are you?")

if st.button("Translate"):
    st.write(translator(text)[0]["translation_text"])
