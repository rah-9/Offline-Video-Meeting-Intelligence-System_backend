from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict

class ProcessUrlRequest(BaseModel):
    url: HttpUrl

class AskRequest(BaseModel):
    job_id: str
    question: str
    history: Optional[List[Dict[str, str]]] = []
