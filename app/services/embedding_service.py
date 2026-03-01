from fastapi import Request
import faiss
import numpy as np
import json
import os
from app.utils.logger import logger
from app.utils.file_manager import get_vector_store_dir
import asyncio

def create_embeddings_sync(request: Request, chunks: list, job_id: str):
    logger.info(f"Generating embeddings and FAISS index for job {job_id}")
    embedder = request.app.state.embedder
    
    texts = [chunk["text"] for chunk in chunks]
    if not texts:
        return
        
    embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    vs_dir = get_vector_store_dir(job_id)
    faiss.write_index(index, os.path.join(vs_dir, "faiss.index"))
    
    with open(os.path.join(vs_dir, "metadata.json"), "w") as f:
        json.dump(chunks, f)

async def search_embeddings_sync(request: Request, query: str, job_id: str, top_k: int = 3):
    embedder = request.app.state.embedder
    
    vs_dir = get_vector_store_dir(job_id)
    index_path = os.path.join(vs_dir, "faiss.index")
    meta_path = os.path.join(vs_dir, "metadata.json")
    
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        return []
        
    index = faiss.read_index(index_path)
    with open(meta_path, "r") as f:
        chunks = json.load(f)
        
    query_vector = embedder.encode([query], show_progress_bar=False, convert_to_numpy=True).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1 and idx < len(chunks):
            results.append({
                "chunk": chunks[idx],
                "score": float(distances[0][i])
            })
            
    return results
