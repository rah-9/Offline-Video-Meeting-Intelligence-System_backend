import json
import os
import time
import requests

API_URL = "http://localhost:8000/api/v1"

def test_qa():
    job_id = "2978cbe4-1c95-45d9-bec7-7bacdd8d644d"
    print(f"Using Mock Job ID: {job_id}")

    from app.utils.file_manager import get_vector_store_dir
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    
    # We will import the models here so they register with SQLAlchemy
    from app.db.database import Job, Result
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    import asyncio
    
    DATABASE_URL = "sqlite+aiosqlite:///d:/SPEECH/backend/db.sqlite3"
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def inject_mock_job():
        async with AsyncSessionLocal() as db:
            existing_job = await db.get(Job, job_id)
            if not existing_job:
                mock_job = Job(id=job_id, status="completed", file_path="mock.mp3", result_path="mock.json")
                db.add(mock_job)
                await db.commit()
    
    asyncio.run(inject_mock_job())

    vs_dir = get_vector_store_dir(job_id)
    os.makedirs(vs_dir, exist_ok=True)
    
    chunks = [
        {"text": "In 2021, a hacker uncovered a fatal weakness in the world's most important operating system. At the time, just about everyone believed that hacking the system was impossible, but they were wrong."},
        {"text": "Stallman created the Free Software Foundation to promote four basic freedoms. He created a legal license that developers could attach to their code, called the general public license."},
        {"text": "There are an estimated 30 million Linux users out there. Of the top 500 supercomputers in the world, every single one runs Linux. Android, with over 3 billion devices, is built on Linux."},
        {"text": "Tattu Ullonen created Secure Shell, a protocol for remote logins between machines. Secure Shell was soon adopted on almost every machine that ran Linux. Today, when you control a machine remotely, there's a good chance you're using Secure Shell."},
        {"text": "Andres Freund spent two and a half years infiltrating the XZ project and weaving in this ingenious backdoor."},
        {"text": "Red Hat's Fedora software has a backdoor that could have compromised millions of systems. The researcher who discovered the bug is a hero, but the mainstream media hasn't covered it very much. The hacker may have been working for two and a half years on the project."},
        {"text": "Geotan himself just disappeared as soon as this exploit became publicly known and never heard from again."}
    ]
    
    print("Generating mock FAISS embeddings...")
    embedder = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    embeddings = embedder.encode([c["text"] for c in chunks], show_progress_bar=False, convert_to_numpy=True).astype('float32')
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, os.path.join(vs_dir, "faiss.index"))
    with open(os.path.join(vs_dir, "metadata.json"), "w") as f:
        json.dump(chunks, f)

    print("Job complete! Testing QA Context vs General...")
    
    # Test 1: Specific Context
    print("\n--- Test 1: Specific Knowledge ---")
    q1 = "what hacker has discovered"
    print(f"Q: {q1}")
    resp = requests.post(f"{API_URL}/ask", json={"job_id": job_id, "question": q1, "history": []})
    a1 = resp.json()
    print(f"A: {a1['answer']}")
        
    # Test 2: Specific Theme
    print("\n--- Test 2: Specific Theme ---")
    q2 = "what is the main theme of the video"
    print(f"Q: {q2}")
    history = [{"q": q1, "a": a1['answer']}]
    resp = requests.post(f"{API_URL}/ask", json={"job_id": job_id, "question": q2, "history": history})
    a2 = resp.json()
    print(f"A: {a2['answer']}")

if __name__ == "__main__":
    test_qa()
