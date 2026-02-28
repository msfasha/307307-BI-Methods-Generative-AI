# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.title("Example 6 — Text Summarization")

summarizer = pipeline("summarization")

text = st.text_area("Enter text:", 
    """Machine learning is a subset of artificial intelligence that enables computers to learn and improve 
from experience without being explicitly programmed. It focuses on the development of computer programs 
that can access data and use it to learn for themselves. The process of learning begins with observations 
or data, such as examples, direct experience, or instruction, in order to look for patterns in data and 
make better decisions in the future based on the examples that we provide. The primary aim is to allow 
the computers to learn automatically without human intervention or assistance and adjust actions accordingly.""")

if st.button("Summarize"):
    summary = summarizer(text, max_length=50, min_length=20)
    st.write(summary[0]["summary_text"])
