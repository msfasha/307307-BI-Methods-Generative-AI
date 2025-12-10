# install streamlit transformers torch
# pip install streamlit transformers torch

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Sample documents
docs = [
  "Our warranty covers manufacturing defects for 1 year.",
  "Battery life is approximately 10 hours under normal use.",
  "To reset the device, hold the power button for 5 seconds."
]

# Step 1: Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 2: Embed documents
doc_embeds = model.encode(docs)

# Step 3: Build vector store
index = faiss.IndexFlatL2(doc_embeds.shape[1])
index.add(np.array(doc_embeds))


query = "How long does the battery last?"
query_vec = model.encode([query])

# Retrieve top 1
D, I = index.search(np.array(query_vec), k=1)
retrieved_doc = docs[I[0][0]]

print("Retrieved:", retrieved_doc)


import os
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

context = retrieved_doc
prompt = f"""
Answer the question using the context below.
 Context:
{context}
 Question:
{query}
"""

# Call a Gemini chat / text model 
response = client.models.generate_content(
  model="gemini-1.5-flash", # or "gemini-1.5-pro"
  contents=prompt,
)

# Print the text output
print(response.text)
