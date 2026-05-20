from pydantic import BaseModel
from typing import Optional
from app.config import TOP_K


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = TOP_K
    doc_id: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    top_k: int = TOP_K