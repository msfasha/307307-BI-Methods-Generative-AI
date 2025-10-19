# app.py
import streamlit as st
import google.generativeai as genai

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(page_title="Gemini Chatbot with Memory", page_icon="🤖")

# -------------------------
# API Key Input
# -------------------------
api_key = st.text_input("Enter your Gemini API key:", type="password")
if not api_key:
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------
# Session State (Memory)
# -------------------------
if "memory" not in st.session_state:
    st.session_state.memory = []  # stores (role, text) tuples

# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("⚙️ Settings")
use_memory = st.sidebar.checkbox("Enable Memory", value=True)
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.memory = []
    st.experimental_rerun()

st.sidebar.markdown(
    """
**Memory ON:** Model sees full chat history.  
**Memory OFF:** Model only sees the latest prompt.
"""
)

# -------------------------
# Chat UI
# -------------------------
st.title("💬 Gemini Chatbot (Memory Toggle Demo)")
st.caption("Demonstrating stateless vs. stateful LLM behavior using Gemini SDK")

# Display existing conversation
for role, text in st.session_state.memory:
    st.chat_message(role).markdown(text)

# User input
if prompt := st.chat_input("Type your message..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.memory.append(("user", prompt))

    # Build input context
    if use_memory:
        # Include full history
        context = "\n".join([f"{r}: {t}" for r, t in st.session_state.memory])
    else:
        # Only include latest user message
        context = f"user: {prompt}"

    # Generate response
    response = model.generate_content(context)
    reply = response.text

    # Append and show
    st.session_state.memory.append(("assistant", reply))
    st.chat_message("assistant").markdown(reply)
