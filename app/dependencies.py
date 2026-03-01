from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session

def get_request(request: Request) -> Request:
    return request
