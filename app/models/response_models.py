from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    error_message: Optional[str] = None

class TopicResponse(BaseModel):
    topic_id: int
    name: str
    content: str
    start_time: float
    end_time: float

class ActionItemResponse(BaseModel):
    text: str
    assignee: Optional[str] = None

class DecisionResponse(BaseModel):
    text: str

class QAPairResponse(BaseModel):
    question: str
    answer: str

class ProcessResultResponse(BaseModel):
    job_id: str
    summary_short: str
    summary_detailed: str
    topics: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    decisions: List[str]
    qa_pairs: List[Dict[str, Any]]

class AskResponse(BaseModel):
    answer: str
