import os
from dotenv import load_dotenv

import weaviate
from weaviate.auth import Auth

from langchain_weaviate import WeaviateVectorStore
from langchain_core.tools import create_retriever_tool
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# ================= ENV =================
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# ================= EMBEDDING =================
embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1",
    model_kwargs={"trust_remote_code": True}
)

# ================= CONNECT =================
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
    skip_init_checks=True
)
print(client.is_ready())

# ================= LOAD EXISTING COLLECTION =================
vector_store_weaviate = WeaviateVectorStore(
    client=client,
    index_name="youtube",
    text_key="text",
    embedding=embedding_model
)

# ================= RETRIEVER =================
retriever = vector_store_weaviate.as_retriever(
    search_kwargs={"k": 3}
)

# ================= TOOL =================
