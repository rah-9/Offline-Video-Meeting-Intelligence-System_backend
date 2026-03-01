from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.db.database import Job, Result
import json

async def create_job(db: AsyncSession, file_path: str = None) -> Job:
    job = Job(file_path=file_path)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def get_job(db: AsyncSession, job_id: str) -> Job:
    result = await db.execute(select(Job).filter(Job.id == job_id))
    return result.scalars().first()

async def update_job_status(db: AsyncSession, job_id: str, status: str, progress: float = None, error_message: str = None, result_path: str = None):
    values = {"status": status}
    if progress is not None:
        values["progress"] = progress
    if error_message is not None:
        values["error_message"] = error_message
    if result_path is not None:
        values["result_path"] = result_path
        
    await db.execute(update(Job).where(Job.id == job_id).values(**values))
    await db.commit()

async def save_result(db: AsyncSession, job_id: str, summary_short: str, summary_detailed: str, topics: list, action_items: list, qa_pairs: list) -> Result:
    result = Result(
        job_id=job_id,
        summary_short=summary_short,
        summary_detailed=summary_detailed,
        topics_json=json.dumps(topics),
        action_items_json=json.dumps(action_items),
        qa_json=json.dumps(qa_pairs)
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return result

async def get_result(db: AsyncSession, job_id: str) -> Result:
    result = await db.execute(select(Result).filter(Result.job_id == job_id))
    return result.scalars().first()
