#!/usr/bin/env python3
"""Properly create FAISS index from video resources"""

from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import re
import os

# Load video resources
loader = TextLoader('video_resources.txt', encoding='utf-8')
documents = loader.load()
text = documents[0].page_content

# Parse videos - better pattern
videos = text.split('----------------------------------------')
videos = [v.strip() for v in videos if v.strip()]

print(f'Total videos found: {len(videos)}')

# Create documents with metadata
docs = []
for video in videos:
    lines = [line.strip() for line in video.strip().split('\n') if line.strip()]
    
    title = ''
    url = ''
    thumbnail = ''
    
    for line in lines:
        # Match numbered lines like "1. Title" or "2246. Title"
        match = re.match(r'^\d+\.\s*(.+)$', line)
        if match and not title:
            title = match.group(1)
        elif line.startswith('Video:'):
            url = line.replace('Video:', '').strip()
        elif line.startswith('Thumbnail:'):
            thumbnail = line.replace('Thumbnail:', '').strip()
    
    if title:
        docs.append({
            'title': title,
            'url': url,
            'thumbnail': thumbnail,
            'content': video
        })

print(f'Successfully parsed documents: {len(docs)}')

# Create embeddings
print('Loading embedding model...')
embedding_model = HuggingFaceEmbeddings(
    model_name='nomic-ai/nomic-embed-text-v1',
    model_kwargs={'trust_remote_code': True}
)

# Create FAISS index
print('Creating FAISS index...')
texts = [f"{doc['title']}. {doc['content']}" for doc in docs]
metadatas = [{'title': doc['title'], 'url': doc['url'], 'thumbnail': doc['thumbnail']} for doc in docs]

vector_store = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)

# Save index
os.makedirs('Data', exist_ok=True)
vector_store.save_local('Data/faiss_index')
print('✅ FAISS index created and saved successfully!')
print(f'Index location: Data/faiss_index')
print(f'Total documents indexed: {len(docs)}')
