# ingestion.py

import os
from dotenv import load_dotenv
import weaviate
from weaviate.auth import Auth

from langchain_weaviate import WeaviateVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from DataIngestion import docs

load_dotenv()

# ================= EMBEDDING =================
embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1",
    model_kwargs={"trust_remote_code": True}
)
# ================= CONNECT =================
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
)

# ================= INGEST DATA =================
vector_store = WeaviateVectorStore.from_documents(
    documents=docs,
    embedding=embedding_model,
    client=client,
    collection_name="youtube"
)

print("Documents uploaded successfully!")