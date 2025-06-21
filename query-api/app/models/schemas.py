from pydantic import BaseModel, Field
from datetime import datetime

class QueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User identifier")
    query: str = Field(..., min_length=1, description="User query")

class QueryResponse(BaseModel):
    user_id: str
    answer: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ProcessingResponse(BaseModel):
    message: str = "Query enqueued for processing"
    status: str = "accepted"