import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize chat model
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit app setup
st.set_page_config(page_title="Chat with Gemini", page_icon="💬")
st.title("💬 Chat with Gemini")

# Initialize chat history in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    role = "🧑‍💻 You" if msg["role"] == "user" else "🤖 Gemini"
    st.markdown(f"**{role}:** {msg['content']}")

# User input
prompt = st.chat_input("Type your message...")

if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"**🧑‍💻 You:** {prompt}")

    # Send to Gemini
    with st.spinner("Gemini is thinking..."):
        chat = model.start_chat(history=st.session_state.messages)
        response = chat.send_message(prompt)
        reply = response.text

    # Save and display model response
    st.session_state.messages.append({"role": "model", "content": reply})
    st.markdown(f"**🤖 Gemini:** {reply}")
