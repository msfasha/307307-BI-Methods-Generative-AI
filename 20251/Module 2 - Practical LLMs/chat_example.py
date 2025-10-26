import streamlit as st
import google.generativeai as genai

# --- Set up Gemini API key directly ---
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
# --- Initialize model ---
model = genai.GenerativeModel("gemini-1.5-flash")
# --- Streamlit UI setup ---
st.set_page_config(page_title="Chat with Gemini", page_icon="💬")
st.title("Chat with Gemini")
# --- Maintain conversation state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
# --- Display chat history ---
for msg in st.session_state.messages:
    role = "You" if msg["role"] == "user" else "Gemini"
    st.markdown(f"**{role}:** {msg['content']}")
# --- Handle user input ---
prompt = st.chat_input("Type your message...")


if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"**You:** {prompt}")


    # Send prompt to Gemini
    with st.spinner("Gemini is thinking..."):
        chat = model.start_chat(history=st.session_state.messages)
        response = chat.send_message(prompt)
        reply = response.text


    # Add and display model response
    st.session_state.messages.append({"role": "model", "content": reply})
    st.markdown(f"**Gemini:** {reply}")


