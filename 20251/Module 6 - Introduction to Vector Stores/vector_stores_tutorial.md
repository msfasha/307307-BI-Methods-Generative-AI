## Vector Stores Crash Course (Jupyter Notebook Format)

---

### **1. Introduction**

```markdown
# Vector Stores Crash Course

Vector stores are specialized databases designed to store and search **embeddings** — numerical representations of data such as text, images, or audio.

They enable *semantic search*, *retrieval-augmented generation (RAG)*, and *contextual reasoning* in AI systems.

In this notebook, we'll learn:
1. What embeddings are.
2. How to create embeddings using OpenAI or Hugging Face.
3. How to store and query them using vector stores like FAISS and Chroma.
4. How to integrate them with a simple retrieval pipeline.
```

---

### **2. Setup**

```python
# Install required libraries
!pip install faiss-cpu chromadb openai sentence-transformers
```

---

### **3. Create Embeddings**

Embeddings convert text into numerical vectors that capture **semantic meaning**.

```python
from sentence_transformers import SentenceTransformer

# Load a pre-trained embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

texts = [
    "The capital of France is Paris.",
    "Eiffel Tower is in Paris.",
    "Python is a programming language.",
    "I love writing code in Python."
]

# Create embeddings
embeddings = model.encode(texts)
embeddings.shape
```

Expected output: `(4, 384)`
Each text is now represented by a **384-dimensional vector**.

---

### **4. Store and Search with FAISS**

[FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search) is a high-performance library for similarity search.

```python
import faiss
import numpy as np

# Convert embeddings to numpy array (float32 required)
embeddings = np.array(embeddings).astype('float32')

# Create the FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add vectors to the index
index.add(embeddings)
print("Number of vectors in index:", index.ntotal)

# Perform similarity search
query = "Where is the Eiffel Tower?"
query_embedding = model.encode([query]).astype('float32')

k = 2  # number of results
distances, indices = index.search(query_embedding, k)

print("Nearest neighbors:")
for idx, distance in zip(indices[0], distances[0]):
    print(f"{texts[idx]} (distance: {distance:.4f})")
```

This finds **semantically similar texts** to the query.

---

### **5. Use Chroma for Persistent Vector Storage**

[Chroma](https://docs.trychroma.com) is an open-source vector database designed for AI retrieval tasks.

```python
import chromadb
from chromadb.utils import embedding_functions

# Initialize Chroma client
client = chromadb.Client()

# Create collection
collection = client.create_collection("my_texts")

# Add documents with embeddings automatically handled
collection.add(
    documents=texts,
    ids=[f"id{i}" for i in range(len(texts))]
)

# Query semantically
query = "What city has the Eiffel Tower?"
results = collection.query(
    query_texts=[query],
    n_results=2
)

print(results)
```

Chroma automatically computes embeddings (using a default model) and performs semantic search.

---

### **6. Integrate Vector Store with RAG (Retrieval-Augmented Generation)**

Vector stores are commonly used to retrieve relevant documents to feed into an **LLM** prompt.

```python
from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
client = OpenAI()

query = "Tell me about Paris."

# Step 1: Retrieve similar texts
results = collection.query(query_texts=[query], n_results=2)
context = "\n".join(results['documents'][0])

# Step 2: Use retrieved context in a prompt
prompt = f"""
Answer the question using the context below.

Context:
{context}

Question: {query}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

print(response.choices[0].message.content)
```

This demonstrates **RAG**: the LLM uses retrieved information from the vector store to generate better, context-aware answers.

---

### **7. Summary**

```markdown
## Summary

- **Embeddings** convert text into high-dimensional vectors that capture meaning.
- **Vector stores** (FAISS, Chroma, Pinecone, Weaviate, etc.) index and search these vectors efficiently.
- **Semantic search** retrieves contextually relevant results, even if exact keywords differ.
- **RAG systems** use vector stores to supply context to language models, reducing hallucinations and improving factuality.
```

---

### **8. Next Steps**

* Try **other vector databases** like:

  * **Pinecone**: managed, scalable cloud service.
  * **Weaviate**: schema-based vector DB with hybrid search.
  * **Milvus**: enterprise-grade open-source vector store.

* Explore **hybrid search** (text + vector similarity).

* Experiment with **chunking documents** and **metadata filtering**.

