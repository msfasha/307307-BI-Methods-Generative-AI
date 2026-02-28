# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.title("Example 5 — Text Generation")

generator = pipeline("text-generation", model="gpt2")

prompt = st.text_input("Prompt:", "The future of AI is")

if st.button("Generate"):
    output = generator(
        prompt,
        max_length=50,
        do_sample=True,
        temperature=0.7,
        num_return_sequences=1,
        pad_token_id=generator.tokenizer.eos_token_id
    )
    st.write(output)
