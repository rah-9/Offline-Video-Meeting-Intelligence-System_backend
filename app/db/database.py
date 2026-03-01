from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, DateTime
import uuid
import datetime
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="queued") # queued, downloading, transcribing, summarizing, completed, failed
    progress = Column(Float, default=0.0)
    file_path = Column(String, nullable=True)
    result_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    result = relationship("Result", back_populates="job", uselist=False, cascade="all, delete-orphan")

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), unique=True)
    summary_short = Column(Text, nullable=True)
    summary_detailed = Column(Text, nullable=True)
    topics_json = Column(Text, nullable=True)
    action_items_json = Column(Text, nullable=True)
    qa_json = Column(Text, nullable=True)
    
    job = relationship("Job", back_populates="result")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
