# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st

from transformers import (
    BertTokenizer, BertModel,
    pipeline, AutoTokenizer,
    AutoModelForQuestionAnswering
)
import torch
import torch.nn.functional as F

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Context-Aware Embeddings and NLP Pipelines",
    layout="wide"
)

st.title("Context-Aware Word Embeddings and NLP Pipelines")
st.markdown("### Streamlit Version of the Notebook")

# -------------------------------------------------------------
# Helper Function: BERT Embedding Extraction
# -------------------------------------------------------------

@st.cache_resource
def load_bert_base():
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")
    return tokenizer, model

def get_token_embedding(sentence, target_word, tokenizer, model):
    """Extract contextual embedding for a specific word."""
    inputs = tokenizer(sentence, return_tensors='pt')
    outputs = model(**inputs)

    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    embeddings = outputs.last_hidden_state.squeeze(0)

    target_tokens = tokenizer.tokenize(target_word)

    matches = []
    for i in range(len(tokens) - len(target_tokens) + 1):
        if tokens[i:i + len(target_tokens)] == target_tokens:
            matches = list(range(i, i + len(target_tokens)))
            break

    if not matches:
        raise ValueError(f"'{target_word}' not found in tokens: {tokens}")

    return embeddings[matches].mean(dim=0)


# -------------------------------------------------------------
# Section 1 — Context-Aware BERT Embeddings
# -------------------------------------------------------------
st.header("Context-Aware Word Embeddings using BERT")

tokenizer, bert_model = load_bert_base()

with st.expander("Show Embedding Comparison Example"):
    st.write("Compare contextual meaning of *apple* depending on sentence context.")

    sentence_fruit = "He ate a fresh apple and enjoyed the fruit."
    sentence_company = "Apple released a new product in the computer market."
    sentence_orange = "An orange is a juicy fruit."
    sentence_microsoft = "Microsoft computer was running the latest software."

    apple_fruit = get_token_embedding(sentence_fruit, "apple", tokenizer, bert_model)
    apple_company = get_token_embedding(sentence_company, "apple", tokenizer, bert_model)
    orange = get_token_embedding(sentence_orange, "orange", tokenizer, bert_model)
    microsoft = get_token_embedding(sentence_microsoft, "Microsoft", tokenizer, bert_model)

    sim_fruit = F.cosine_similarity(apple_fruit, orange, dim=0).item()
    sim_company = F.cosine_similarity(apple_company, microsoft, dim=0).item()

    st.write(f"Similarity between 'apple' (fruit) and 'orange': **{sim_fruit:.4f}**")
    st.write(f"Similarity between 'apple' (company) and 'Microsoft': **{sim_company:.4f}**")


# -------------------------------------------------------------
# Section 2 — NLP Pipelines
# -------------------------------------------------------------
st.header("NLP Pipelines using Hugging Face")

# ---------------- Sentiment Analysis -------------------------
with st.expander("Text Classification (Sentiment Analysis)"):
    classifier = pipeline("sentiment-analysis")

    user_text = st.text_input("Enter text for sentiment analysis:", "I love using Hugging Face!")
    if st.button("Analyze Sentiment"):
        result = classifier(user_text)[0]
        st.write(result)

# ---------------- Named Entity Recognition -------------------
with st.expander("Named Entity Recognition (NER)"):
    ner = pipeline("ner", aggregation_strategy="simple")
    ner_text = st.text_area(
        "Enter text for NER:",
        "My name is John and I live in New York. I work at Google."
    )
    if st.button("Run NER"):
        entities = ner(ner_text)
        st.write(entities)

# ---------------- Question Answering -------------------------
with st.expander("Question Answering"):
    qa = pipeline("question-answering")

    context = st.text_area("Context", 
    """Hugging Face is a company that develops tools for building applications using machine learning.
They are especially known for their work in natural language processing.
The company was founded in 2016 and is headquartered in New York.""")

    question = st.text_input("Question", "When was Hugging Face founded?")
    
    if st.button("Get Answer"):
        result = qa(question=question, context=context)
        st.write(result)

# ---------------- Text Generation ----------------------------
with st.expander("Text Generation"):
    generator = pipeline("text-generation", model="gpt2")

    prompt = st.text_input("Enter prompt:", "The future of artificial intelligence is")
    if st.button("Generate Text"):
        outputs = generator(
            prompt,
            max_length=50,
            num_return_sequences=2,
            temperature=0.7,
            do_sample=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        st.write(outputs)

# ---------------- Summarization -------------------------------
with st.expander("Text Summarization"):
    summarizer = pipeline("summarization")

    article = st.text_area("Enter text to summarize:", 
    """Machine learning is a subset of artificial intelligence that enables computers to learn and improve 
from experience without being explicitly programmed. It focuses on the development of computer programs 
that can access data and use it to learn for themselves. The process of learning begins with observations 
or data, such as examples, direct experience, or instruction, in order to look for patterns in data and 
make better decisions in the future based on the examples that we provide. The primary aim is to allow 
the computers to learn automatically without human intervention or assistance and adjust actions accordingly.""")

    if st.button("Summarize"):
        summary = summarizer(article, max_length=50, min_length=25, do_sample=False)
        st.write(summary[0]["summary_text"])

# ---------------- Translation -------------------------------
with st.expander("Translation (English → French)"):
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")

    text_to_translate = st.text_input("Enter English text:", "Hello, how are you today?")
    if st.button("Translate"):
        translated = translator(text_to_translate)
        st.write(translated[0]["translation_text"])

# -------------------------------------------------------------
# Section 3 — Specific BERT QA Model
# -------------------------------------------------------------
st.header("Question Answering with BERT (SQuAD Fine-tuned)")

with st.expander("Use BERT-large for Question Answering"):
    qa_pipeline = pipeline(
        "question-answering",
        model="bert-large-uncased-whole-word-masking-finetuned-squad",
        tokenizer="bert-large-uncased-whole-word-masking-finetuned-squad"
    )

    context = st.text_area("Context for BERT QA",
    """BERT is a method of pre-training language representations,
meaning that it trains a general-purpose language understanding
model on a large text corpus (like Wikipedia),
and then uses that model for downstream NLP tasks like question answering.""")

    question = st.text_input("Question for BERT QA", "What is BERT?")

    if st.button("Answer with BERT"):
        result = qa_pipeline(question=question, context=context)
        st.write(f"Answer: {result['answer']}")
        st.write(f"Confidence: {result['score']:.4f}")

# -------------------------------------------------------------
# End
# -------------------------------------------------------------
st.markdown("---")
st.write("Streamlit version of the full Jupyter Notebook workflow.")
