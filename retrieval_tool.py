import os
from dotenv import load_dotenv

from langchain_core.tools import create_retriever_tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ================= ENV =================
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# ================= EMBEDDING =================
embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1",
    model_kwargs={"trust_remote_code": True}
)

# ================= LOAD EXISTING COLLECTION =================
# Using FAISS as fallback since weaviate has circular import issues
vector_store_path = "Data/faiss_index"
if os.path.exists(vector_store_path):
    vector_store = FAISS.load_local(vector_store_path, embedding_model, allow_dangerous_deserialization=True)
else:
    # Create empty vector store if none exists
    vector_store = FAISS.from_texts(["placeholder"], embedding_model)

# ================= RETRIEVER =================
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

# ================= TOOL =================
