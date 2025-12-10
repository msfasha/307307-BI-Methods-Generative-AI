# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.title("Example 4 — Question Answering")

qa = pipeline("question-answering")

context = st.text_area("Context:", 
    """Hugging Face is a company that develops tools for building applications using machine learning. 
They are especially known for their work in natural language processing. The company was founded in 2016 
and is headquartered in New York.""")
question = st.text_input("Question:", "What does Hugging Face build?")

if st.button("Answer"):
    st.write(qa(question=question, context=context))
