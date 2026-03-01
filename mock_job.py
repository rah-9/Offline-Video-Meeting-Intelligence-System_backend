import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

# Adjusted for absolute path to the local database file.
DATABASE_URL = "sqlite+aiosqlite:///d:/SPEECH/backend/db.sqlite3"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def inject_mock_job():
    # We will import the models here so they register with SQLAlchemy
    from app.db.database import Job, Result
    
    async with AsyncSessionLocal() as db:
        job_id = str(uuid.uuid4())
        mock_job = Job(id=job_id, status="completed", file_path="mock.mp3", result_path="mock.json")
        db.add(mock_job)
        
        mock_result = Result(
            job_id=job_id,
            summary_short="The quick brown fox jumps over the lazy dog.",
            summary_detailed="The quick brown fox jumps over the lazy dog. Buster is a dog.",
            topics_json='[{"topic_id":1,"name":"Animals","content":"The quick brown fox jumps over the lazy dog. The dog\'s name is Buster and he likes to sleep.","start_time":0,"end_time":10}]',
            action_items_json='[]',
            qa_json='[]'
        )
        db.add(mock_result)
        
        await db.commit()
        print(job_id)

if __name__ == "__main__":
    asyncio.run(inject_mock_job())
