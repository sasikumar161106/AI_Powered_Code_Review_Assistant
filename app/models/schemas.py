from pydantic import BaseModel
from typing import List, Optional

class ReviewComment(BaseModel):
    path: str
    position: int
    body: str

class ReviewResponse(BaseModel):
    comments: List[ReviewComment]
    summary: str
