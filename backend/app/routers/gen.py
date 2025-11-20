
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
import json

from backend.app.db.database import SessionLocal
from backend.app.db.models import Item
from backend.app.services.ai import (
    GenerateItemRequest,           
    generate_item_from_prompt_request,  
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ItemOut(BaseModel):
    id: int
    source: str
    prompt: Optional[str] = None
    stimulus: Optional[str] = None
    stem: Optional[str] = None
    choices: List[Any]
    answer: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

@router.post(
    "/generate",
    summary="Immediately send items to DB",
    response_model=ItemOut,
    response_model_exclude_none=True
)
def generate_item(
    request: GenerateItemRequest = Body(...),
    db: Session = Depends(get_db)
):
    # 1) 调用服务层拿到结构化题目（dict）
    try:
        gen = generate_item_from_prompt_request(request)  # {stimulus, stem, choices, answer, metadata}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")


    try:
        obj = Item(
            source="ai",

            prompt=(request.prompt_text or (f"[docx]{request.docx_path}" if request.docx_path else None)),
            stimulus=gen.get("stimulus"), 
            stem=(gen.get("stem") or ""),  
            choices=json.dumps(gen.get("choices") or []),
            answer=(gen.get("answer") or []), 
            meta_json=json.dumps(gen.get("metadata") or {}),  
            status = 'new',
            committed=False
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")


    return {
        "id": obj.id,
        "source": obj.source,
        "prompt": obj.prompt,
        "stimulus": obj.stimulus,
        "stem": obj.stem,
        "choices": json.loads(obj.choices) if obj.choices else [],
        "answer": obj.answer,
        "metadata": json.loads(obj.meta_json) if obj.meta_json else None,
        "created_at": obj.created_at.isoformat() if obj.created_at else None
    }
