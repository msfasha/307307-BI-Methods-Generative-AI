# pip install streamlit sentence-transformers faiss-cpu google-generativeai

import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from google import genai

# Initialize the embedding model (cached for performance)
@st.cache_resource
def load_embedding_model():
    """Loads the SentenceTransformer model and caches it."""
    return SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = load_embedding_model()
LLM_MODEL = "gemini-2.5-flash" # The generation model

# --- Streamlit UI and Logic ---
st.title("Simple Context-Based Question Answering (RAG)")
st.caption(f"Powered by **`all-MiniLM-L6-v2`** (Retrieval) and **`{LLM_MODEL}`** (Generation)")

# 0. API Key Input Section
st.sidebar.header("🔑 API Configuration")
api_key_input = st.sidebar.text_input(
    "Enter your Gemini API Key", 
    type="password" 
)

# 1. Context Input
st.header("1. Knowledge Context")
default_context = """
Our product warranty covers all manufacturing defects for a period of 1 year from the date of purchase. It does not cover accidental damage or wear and tear. 
The standard battery life is approximately 10 hours under normal use, which includes web browsing and light document editing. 
If you are streaming video, the battery life will drop to about 6 hours.
To perform a factory reset on the device, you must first turn it off, then hold the power button for 5 seconds while simultaneously pressing the volume down button.
Software updates are released on the first Monday of every month.
"""
context_input = st.text_area(
    "Paste your documents/context here (separate statements/paragraphs with newlines):",
    default_context,
    height=300
)

# 2. Question Input
st.header("2. Ask a Question")
query = st.text_input(
    "Enter your question about the context:",
    "How do I reset my device?"
)

# --- RAG Processing on Button Click ---
if st.button("Get Answer"):
    
    # --- Configuration/Key Check ---
    # 1. Use key from Textbox
    # 2. Fallback to Streamlit secrets (for cloud deployment)
    # 3. Fallback to OS environment variable
    final_api_key = api_key_input or st.secrets.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not final_api_key:
        st.error("Error: Please enter your **Gemini API Key** in the sidebar to proceed.")
        st.stop()
    
    try:
        # Initialize client with the determined key
        client = genai.Client(api_key=final_api_key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        st.stop()
    
    if not context_input or not query:
        st.warning("Please enter both context and a question.")
    else:
        # Split context into document chunks
        docs = [line.strip() for line in context_input.split('\n') if line.strip()]

        if not docs:
            st.warning("The context is empty or contains only whitespace.")
            st.stop()

        with st.spinner("Step 1: Embedding context chunks..."):
            # Step 1 & 2: Embed documents
            doc_embeds = embedding_model.encode(docs)

            # Step 3: Build vector store (FAISS)
            index = faiss.IndexFlatL2(doc_embeds.shape[1])
            index.add(np.array(doc_embeds))

        with st.spinner("Step 2: Retrieving most relevant chunk..."):
            # Embed the query
            query_vec = embedding_model.encode([query])

            # Retrieve top 1
            D, I = index.search(np.array(query_vec), k=1)
            retrieved_doc = docs[I[0][0]]

            st.subheader("Retrieval Result (Source Document)")
            st.success(f"**Distance (L2):** {D[0][0]:.4f}")
            st.markdown(f"> **{retrieved_doc}**") 

        with st.spinner("Step 3: Generating final answer with Gemini..."):
            # Step 4: Generation Prompt
            prompt = f"""
            You are a helpful assistant. Answer the Question concisely and accurately 
            using ONLY the provided Context. If the context does not contain the answer, 
            state that you cannot find the answer based on the provided information.

            ---
            Context:
            {retrieved_doc}
            ---
            Question:
            {query}
            """

            try:
                # Call the Gemini model
                response = client.models.generate_content(
                    model=LLM_MODEL,
                    contents=prompt,
                )

                st.subheader("Final Answer (Gemini Output)")
                st.info(response.text)
            
            except Exception as e:
                st.error(f"Error calling the Gemini model: {e}")