# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- Set up Gemini API key directly ---
genai.configure(api_key="Your_Gemini_API_Key_Here")

# --- Initialize model ---
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# --- Streamlit UI setup ---
st.set_page_config(page_title="Chat with Gemini + CSV Analysis", page_icon="💬")
st.title("💬 Chat with Gemini + 📊 CSV Analysis")

# --- Maintain chat session ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []  # store messages in Gemini's expected format

# --- File upload section ---
uploaded_file = st.file_uploader("Upload a CSV file for Gemini to analyze", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ CSV file uploaded successfully!")
    st.dataframe(df.head())
else:
    df = None

# --- Display chat history ---
for msg in st.session_state.messages:
    role = "You" if msg["role"] == "user" else "Gemini"
    st.markdown(f"**{role}:** {msg['parts'][0]['text']}")

# --- Handle user input ---
prompt = st.chat_input("Ask Gemini something (it can use the uploaded CSV if provided)...")

if prompt:
    # Add user message
    user_msg = {"role": "user", "parts": [{"text": prompt}]}
    st.session_state.messages.append(user_msg)
    st.markdown(f"**You:** {prompt}")

    # If a CSV is uploaded, include a small preview or summary in the prompt
    if df is not None:
        csv_preview = df.head(5).to_csv(index=False)
        full_prompt = (
            f"The user uploaded a CSV file. Here's a small sample of its contents:\n\n"
            f"{csv_preview}\n\n"
            f"Now, based on this data, answer the following question:\n{prompt}"
        )
    else:
        full_prompt = prompt

    # Send message to Gemini
    with st.spinner("Gemini is analyzing..."):
        response = st.session_state.chat.send_message(full_prompt)
        reply = response.text

    # Add and display Gemini's reply
    model_msg = {"role": "model", "parts": [{"text": reply}]}
    st.session_state.messages.append(model_msg)
    st.markdown(f"**Gemini:** {reply}")
