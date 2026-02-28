# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
from transformers import BertTokenizer, BertModel
import torch.nn.functional as F

st.title("Contextual Embedding Comparison with BERT")

# Load BERT once
@st.cache_resource
def load_bert():
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")
    return tokenizer, model

tokenizer, model = load_bert()


def get_embedding(sentence, word):
    """Return contextual BERT embedding using a simple loop."""
    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    token_embs = outputs.last_hidden_state[0]

    word_tokens = tokenizer.tokenize(word)

    # Direct loop to find tokens
    start = -1
    for i in range(len(tokens) - len(word_tokens) + 1):
        if tokens[i:i + len(word_tokens)] == word_tokens:
            start = i
            break

    if start == -1:
        raise ValueError(f"'{word}' not found in: {tokens}")

    # Average over any subword pieces
    return token_embs[start:start + len(word_tokens)].mean(dim=0)


# -----------------------------------------------------------
# Default sentences + words
# -----------------------------------------------------------
default_s1 = "He ate a fresh apple and enjoyed the fruit."
default_s2 = "Apple released a new product in the computer market."
default_s3 = "An orange is a juicy fruit."

default_w1 = "apple"
default_w2 = "apple"
default_w3 = "orange"


# -----------------------------------------------------------
# Streamlit Inputs
# -----------------------------------------------------------
st.subheader("Enter Sentences")
s1 = st.text_input("Sentence 1", default_s1)
s2 = st.text_input("Sentence 2", default_s2)
s3 = st.text_input("Sentence 3", default_s3)

st.subheader("Enter Target Words (must appear in the sentences)")
w1 = st.text_input("Word from Sentence 1", default_w1)
w2 = st.text_input("Word from Sentence 2", default_w2)
w3 = st.text_input("Word from Sentence 3", default_w3)


# -----------------------------------------------------------
# Compute on Button Click
# -----------------------------------------------------------
if st.button("Compare Embeddings"):
    try:
        emb1 = get_embedding(s1, w1)
        emb2 = get_embedding(s2, w2)
        emb3 = get_embedding(s3, w3)

        sim12 = F.cosine_similarity(emb1, emb2, dim=0).item()
        sim13 = F.cosine_similarity(emb1, emb3, dim=0).item()
        sim23 = F.cosine_similarity(emb2, emb3, dim=0).item()

        st.subheader("Cosine Similarity Results")

        st.write(f"**{w1} (Sentence 1) ↔ {w2} (Sentence 2):** {sim12:.4f}")
        st.write(f"**{w1} (Sentence 1) ↔ {w3} (Sentence 3):** {sim13:.4f}")
        st.write(f"**{w2} (Sentence 2) ↔ {w3} (Sentence 3):** {sim23:.4f}")

    except Exception as e:
        st.error(str(e))
