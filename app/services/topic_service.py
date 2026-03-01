from sklearn.cluster import KMeans
import numpy as np
from app.utils.logger import logger
from fastapi import Request

def extract_topics_sync(request: Request, chunks: list, job_id: str, num_clusters: int = 5):
    logger.info(f"Extracting topics for job {job_id}")
    
    if not chunks or len(chunks) < num_clusters:
        return [{"topic_id": 0, "name": "General Discussion", "content": " ".join([c["text"] for c in chunks]), "start_time": chunks[0]["start_time"] if chunks else 0.0, "end_time": chunks[-1]["end_time"] if chunks else 0.0}]
        
    embedder = request.app.state.embedder
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(embeddings)
    
    topics = []
    for i in range(num_clusters):
        cluster_indices = np.where(clusters == i)[0]
        cluster_chunks = [chunks[idx] for idx in cluster_indices]
        
        # Sort chunks by time
        cluster_chunks.sort(key=lambda x: x["start_time"])
        
        topics.append({
            "topic_id": i,
            "name": f"Topic {i+1}",
            "content": " ".join([c["text"] for c in cluster_chunks]),
            "start_time": cluster_chunks[0]["start_time"],
            "end_time": cluster_chunks[-1]["end_time"]
        })
        
    topics.sort(key=lambda x: x["start_time"])
    return topics
