"""
Simple RAG Application for Business Students
============================================

This app demonstrates RAG in 3 steps:
1. Upload a PDF
2. Ask a question
3. Get an answer based on the PDF content

Required packages:
pip install streamlit google-generativeai sentence-transformers chromadb PyPDF2
"""

import streamlit as st
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb
import PyPDF2

# =============================================================================
# STEP 1: EXTRACT TEXT FROM PDF
# =============================================================================

def get_text_from_pdf(pdf_file):
    """Read PDF and return all text"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# =============================================================================
# STEP 2: BREAK TEXT INTO CHUNKS
# =============================================================================

def split_into_chunks(text, chunk_size=1000):
    """
    Split text into smaller pieces
    Why? ChatGPT can't read entire books at once
    """
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks


# =============================================================================
# STEP 3: STORE IN VECTOR DATABASE
# =============================================================================

def store_in_database(chunks, filename):
    """
    Convert chunks to vectors and store them
    This is the "preparation" phase of RAG
    """
    # Initialize the vector database
    client = chromadb.Client()
    collection = client.get_or_create_collection("documents")
    
    # Initialize embedding model (converts text to vectors)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Convert each chunk to a vector
    for i, chunk in enumerate(chunks):
        # Create unique ID for this chunk
        chunk_id = f"{filename}_chunk_{i}"
        
        # Convert text to vector
        vector = model.encode(chunk)
        
        # Store in database
        collection.add(
            ids=[chunk_id],
            embeddings=[vector.tolist()],
            documents=[chunk],
            metadatas=[{"source": filename, "chunk_number": i}]
        )
    
    return collection


# =============================================================================
# STEP 4: SEARCH FOR RELEVANT CHUNKS
# =============================================================================

def find_relevant_chunks(question, collection):
    """
    Search the database for chunks related to the question
    This is the "retrieval" phase of RAG
    """
    # Convert question to vector
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_vector = model.encode(question)
    
    # Search database for similar vectors
    results = collection.query(
        query_embeddings=[question_vector.tolist()],
        n_results=3  # Get top 3 most relevant chunks
    )
    
    return results['documents'][0]  # Return the text chunks


# =============================================================================
# STEP 5: GENERATE ANSWER WITH GEMINI
# =============================================================================

def generate_answer(question, relevant_chunks, api_key):
    """
    Use Gemini to answer the question based on retrieved chunks
    This is the "generation" phase of RAG
    """
    # Set up Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Combine the chunks into context
    context = "\n\n".join(relevant_chunks)
    
    # Create the prompt
    prompt = f"""Answer the question based only on the following context:

Context:
{context}

Question: {question}

Answer the question using only the information from the context above. If the context doesn't contain the answer, say so."""
    
    # Get answer from Gemini
    response = model.generate_content(prompt)
    return response.text


# =============================================================================
# USER INTERFACE
# =============================================================================

st.title("Simple RAG Demo")
st.write("Upload a PDF and ask questions about it")

# Sidebar for API key
with st.sidebar:
    api_key = st.text_input("Enter Google API Key", type="password")
    st.write("Get your key at: https://makersuite.google.com/app/apikey")

# Main area - two columns
col1, col2 = st.columns(2)

# LEFT SIDE: Upload PDF
with col1:
    st.subheader("Step 1: Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing..."):
            # Extract text
            text = get_text_from_pdf(uploaded_file)
            st.success(f"Extracted {len(text)} characters")
            
            # Split into chunks
            chunks = split_into_chunks(text)
            st.success(f"Created {len(chunks)} chunks")
            
            # Store in database
            collection = store_in_database(chunks, uploaded_file.name)
            st.session_state.collection = collection
            st.session_state.pdf_name = uploaded_file.name
            st.success("Stored in vector database")

# RIGHT SIDE: Ask questions
with col2:
    st.subheader("Step 2: Ask Questions")
    
    if 'collection' not in st.session_state:
        st.info("Please upload and process a PDF first")
    else:
        st.write(f"Ready to answer questions about: {st.session_state.pdf_name}")
        
        question = st.text_input("Your question:")
        
        if question and st.button("Get Answer"):
            if not api_key:
                st.error("Please enter your API key in the sidebar")
            else:
                with st.spinner("Finding answer..."):
                    # Find relevant chunks
                    relevant_chunks = find_relevant_chunks(
                        question, 
                        st.session_state.collection
                    )
                    
                    # Show what was found
                    with st.expander("Retrieved Context"):
                        for i, chunk in enumerate(relevant_chunks):
                            st.write(f"**Chunk {i+1}:**")
                            st.write(chunk[:200] + "...")
                    
                    # Generate answer
                    answer = generate_answer(question, relevant_chunks, api_key)
                    
                    st.subheader("Answer:")
                    st.write(answer)

# Bottom explanation
st.markdown("---")
st.subheader("How This Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**1. Preparation**")
    st.write("PDF → Text → Chunks → Vectors → Database")

with col2:
    st.write("**2. Retrieval**")
    st.write("Question → Vector → Search → Top 3 Chunks")

with col3:
    st.write("**3. Generation**")
    st.write("Question + Chunks → Gemini → Answer")