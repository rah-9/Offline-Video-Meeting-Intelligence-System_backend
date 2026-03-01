from app.utils.logger import logger

def chunk_transcript_sync(transcript_data: list, job_id: str, max_chunk_minutes: float = 3.0) -> list:
    """
    Chunks transcript into time-based logical windows.
    Returns list of chunks, each chunk containing combined text, start_time, end_time.
    """
    logger.info(f"Chunking transcript for job {job_id}")
    
    chunks = []
    current_chunk_text = []
    current_chunk_start = 0.0
    current_chunk_end = 0.0
    chunk_id = 0
    
    max_duration_seconds = max_chunk_minutes * 60
    
    if not transcript_data:
        return []
        
    current_chunk_start = transcript_data[0]["start"]
    
    for i, segment in enumerate(transcript_data):
        current_chunk_text.append(segment["text"])
        current_chunk_end = segment["end"]
        
        duration = current_chunk_end - current_chunk_start
        
        # If we exceed max duration or this is the last segment
        if duration >= max_duration_seconds or i == len(transcript_data) - 1:
            chunks.append({
                "chunk_id": chunk_id,
                "start_time": current_chunk_start,
                "end_time": current_chunk_end,
                "text": " ".join(current_chunk_text)
            })
            chunk_id += 1
            current_chunk_text = []
            if i < len(transcript_data) - 1:
                current_chunk_start = transcript_data[i+1]["start"]
                
    return chunks
