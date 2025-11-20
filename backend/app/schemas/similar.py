from pydantic import BaseModel
from typing import List

class SimilarCandidate(BaseModel):
    id: int
    score: float 

class SimilarResponse(BaseModel):
    query_id: int
    top_k:int
    results: List[SimilarCandidate]