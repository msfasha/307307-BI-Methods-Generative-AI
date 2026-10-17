# install streamlit transformers torch
# pip install streamlit transformers torch

import streamlit as st
import google.generativeai as genai

# --- Set up Gemini API key directly ---
genai.configure(api_key="Your_Gemini_API_Key_Here")

# --- Initialize model ---
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# --- Streamlit UI setup ---
st.set_page_config(page_title="Chat with Gemini", page_icon="💬")
st.title("💬 Chat with Gemini")

# --- Maintain chat session ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []  # store messages in Gemini's expected format

# --- Display chat history ---
for msg in st.session_state.messages:
    role = "You" if msg["role"] == "user" else "Gemini"
    st.markdown(f"**{role}:** {msg['parts'][0]['text']}")

# --- Handle user input ---
prompt = st.chat_input("Type your message...")

if prompt:
    # Add user message
    user_msg = {"role": "user", "parts": [{"text": prompt}]}
    st.session_state.messages.append(user_msg)
    st.markdown(f"**You:** {prompt}")

    # Send message to Gemini
    with st.spinner("Gemini is thinking..."):
        response = st.session_state.chat.send_message(prompt)
        reply = response.text

    # Add and display Gemini's reply
    model_msg = {"role": "model", "parts": [{"text": reply}]}
    st.session_state.messages.append(model_msg)
    st.markdown(f"**Gemini:** {reply}")
