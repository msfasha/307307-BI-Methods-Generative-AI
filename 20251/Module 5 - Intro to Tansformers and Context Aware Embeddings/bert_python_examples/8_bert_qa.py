# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import pipeline

st.title("Example 8 — BERT-Large SQuAD QA")

qa = pipeline(
    "question-answering",
    model="bert-large-uncased-whole-word-masking-finetuned-squad",
    tokenizer="bert-large-uncased-whole-word-masking-finetuned-squad"
)

context = st.text_area("Context:",
        """BERT is a general-purpose language model developed by Google. 
        It stands for Bidirectional Encoder Representations from Transformers.
        Unlike previous language models, BERT is designed to pre-train deep bidirectional 
        epresentations from unlabeled text by jointly conditioning on both left and right 
        ontext in all layers. As a result, the pre-trained BERT model can be fine-tuned with 
        ust one additional output layer to create state-of-the-art models for a 
        wide range of tasks, such as question answering and language inference, without 
        substantial task-specific architecture modifications.""", height=250)

question = st.text_input("Question:", "What is BERT?")

if st.button("Answer"):
    result = qa(question=question, context=context)
    st.write("Answer:", result["answer"])
    st.write("Confidence:", result["score"])
