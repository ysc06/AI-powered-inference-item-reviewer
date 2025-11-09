from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.db.database import SessionLocal
from backend.app.db.models import Item
from pydantic import BaseModel
from backend.app.schemas.similar import SimilarResponse, SimilarCandidate #new
from backend.app.services.similarity import (
    build_item_text,
    get_or_encode_embedding,
    load_all_embeddings_except,
    top_k_score,
    cosine)

from typing import Optional, Any, Dict, List
import json




router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ItemCreateIn(BaseModel):
    prompt: Optional[str] = None
    stimulus: Optional[str] = None
    stem: Optional[str]=None
    choices: List[Any]
    answer: str
    metadata: Optional[Dict[str, Any]] = {}
   

class ItemOut(BaseModel):
    id: int 
    source: str
    prompt: Optional[str] = None 
    stimulus: Optional[str] = None
    stem: Optional[str]=None
    choices: List[Any]
    answer: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

@router.post("/", summary="Manually add items.", response_model=ItemOut)
def create_item(payload: ItemCreateIn, db: Session = Depends(get_db)):
    #payload is a variable of request body
    try:
        item = Item(
            source="manual", prompt=None, stimulus=payload.stimulus,
            stem=payload.stem,
            choices=json.dumps(payload.choices),
            answer=payload.answer,
            meta_json=json.dumps(payload.metadata or {})
        )
        db.add(item)
        db.commit()
        db.refresh(item)
    except Exception:
        db.rollback()
        raise

    return {
        "id": item.id,
        "source": item.source,
        "prompt": item.prompt,
        "stimulus": item.stimulus,
        "stem": item.stem,
        "choices": json.loads(item.choices) if item.choices else [],
        "answer": item.answer,
        "metadata": json.loads(item.meta_json) if item.meta_json else None,
        "created_at": item.created_at.isoformat() if item.created_at else None
    }

@router.get("/", summary="List recent 50 items.", response_model=List[ItemOut], response_model_exclude_none = True)
def list_items(db: Session = Depends(get_db)):
    rows = db.query(Item).order_by(desc(Item.id)).limit(50).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "source": r.source,
            "prompt": r.prompt,
            "stimulus": r.stimulus,
            "stem": r.stem,
            "choices": json.loads(r.choices) if r.choices else [],
            "answer": r.answer,
            "metadata": json.loads(r.meta_json) if r.meta_json else None,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return out



@router.get("/{item_id}/similar", response_model=SimilarResponse,response_model_exclude_none = True)
def similar_items(
    item_id: int,
    top_k:int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code = 404,  detail="item not found")
    
    qtext = build_item_text(item)
    qvec =  get_or_encode_embedding(db=db, item_id = item.id, text=qtext)
    pool = load_all_embeddings_except(db=db, item_id = item.id)
    scores = [(tid, cosine(qvec, vec)) for (tid, vec)in pool]
    top = top_k_score(scores, k=top_k)


    results = [{"id":tid, "score": round(score,3)} for (tid, score) in top] 
   
    return {"query_id": item_id, "top_k": top_k, "results": results}


# @router.get("/{id}/similar", response_model=SimilarResponse)
# def get_similar(
#     id: int,
#     top_k: int = Query(6, ge=1, le=50),
#     db: Session = Depends(get_db),
# ):
#     # 1) 取条目
#     from backend.app.db.models import Item  # 路径按你的项目改；如果同目录 models.py，就 from models import Item
#     item = db.query(Item).filter(Item.id == id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="item not found")

#     try:
#         # 2) 构造查询文本 & 向量
#         query_text = build_item_text(item)  # 内部要能容忍 None/空字符串
#         query_vec = get_or_encode_embedding(db, id, query_text)

#         # 3) 取其它条目的向量
#         others = load_all_embeddings_except(db, id)  # -> List[Tuple[int, np.ndarray]]
#         scored = []
#         for oid, ovec in others:
#             if ovec is None:
#                 continue
#             s = cosine(query_vec, ovec)
#             scored.append(SimilarCandidate(id=int(oid), score=float(s)))

#         # 4) 排序 & 截断
#         scored.sort(key=lambda c: c.score, reverse=True)
#         results = scored[:top_k]

#         return SimilarResponse(query_id=id, top_k=top_k, results=results)
#     except HTTPException:
#         raise
#     except Exception as e:
      
#         raise HTTPException(status_code=500, detail=f"similar failed: {e}")

@router.post("/{item_id}/approve", summary = "Approve and item")
def approve_item(item_id: int, db:Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code = 404, detail = "Item not found")
    item.status = "approved"
    db.commit()
    db.refresh(item)
    return {"id": item_id, "status": item.status}

@router.post("/{item_id}/reject", summary = "Reject an item")
def reject_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code = 404, detail = "Item not found.")
    item.status = "rejected"
    db.commit()
    db.refresh(item)
    return {"id": item_id, "status": item.status}


@router.post("/cart", summary = "List approved but not committed items")
def get_cart(db:Session = Depends(get_db)):
    items = db.query(Item).filter(Item.status == "approved", Item.committed == 0).all()
    return [
        {
            "id": item.id,
            "stimulus": item.stimulus,
            "stem": item.stem, 
            "choices": item.choices, 
            "answer": item.answer, 
            "metadata": item.meta_json if item.meta_json else None,
            "status": item.status,
            "committed": item.committed,
        }
        for item in items 
    ]


@router.post("/cart/commit", summary = "Commit all approved items")
def commit_cart(db:Session = Depends(get_db)):
    items = db.query(Item).filter(Item.status == "approved", Item.committed == 0).all() 
    if not items:
        raise HTTPException(status_code = 400, detail = "No approved items to commit.")
    for item in items:
        item.committed = 1
    db.commit()

    return {"Committed count:", len(items)}