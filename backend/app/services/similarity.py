
from typing import List,Tuple, Optional 
import json
import numpy as np 
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session


_ST_NAME_DEFAULT = "sentence-transformers/all-MiniLM-L6-v2"
# _ST_MODEL = None  


# Vectors let me compare the meaning of text. 
# Sentence embeddings map text into high dimensional coordinates, where semantically similar sentneces are close together.
# Cache embeddings in DB and reuse them for fast retrieval. (real system requires PostgreSQL to support scale nad updates.)

# Lazy load the SentenceTransformer to keep cold-start fast and memory usage low.
# def _get_model(model_name:str):
#     global _ST_MODEL
#     if _ST_MODEL is None: 
#         from sentence_transformers import SentenceTransformer 
#         _ST_MODEL = SentenceTransformer(model_name)
#     return _ST_MODEL
import threading
from sentence_transformers import SentenceTransformer
_model_lock = threading.Lock()
_ST_MODEL = None

def _get_model(name="all-MiniLM-L6-v2"):
    global _ST_MODEL
    if _ST_MODEL is None:
        with _model_lock:
            if _ST_MODEL is None:
                _ST_MODEL = SentenceTransformer(name, device="cpu")  # safest
    return _ST_MODEL


def build_item_text(item) -> str: 
    """
    Return the exact text(stimulus) used for similarity embedding
    """
    return (getattr(item, "stimulus",None) or "").strip()


# Turn JSON to vectors and vice versa. SQLite doesn't have active vector or json type. 
def _vec_to_json_bytes(vec: np.ndarray) -> bytes: 
    # ndarray -> list -> JSON str => UTF-8 bytes
    return json.dumps(vec.tolist()).encode("utf-8")

def _vec_from_json_bytes(blob: bytes) -> np.ndarray:
    # bytes -> JSON str -> list -> ndarray(float32)
    return np.array(json.loads(blob.decode("utf-8")), dtype=np.float32)


### Below are placeholders for the next steps
   
def get_or_encode_embedding(db: Session, item_id: int, text: str, model: str = _ST_NAME_DEFAULT) -> np.ndarray:
    """
    Return the embedding for `item_id` (persisted in SQLite).
    """

    row = db.execute(
        sql_text("SELECT embedding FROM item_embeddings WHERE item_id = :item_id"),
        {"item_id": item_id},
    ).fetchone()

    if row and row[0] is not None:
        return _vec_from_json_bytes(row[0])

    # when text is empty
    clean = (text or "").strip()
    if not clean:
        return np.zeros(384, dtype=np.float32) #all zeros vector

    model_inst = _get_model(model)
    vec = model_inst.encode(clean, normalize_embeddings=True) #calculate vector
    vec = np.asarray(vec, dtype=np.float32) # turn to float32

    # Upsert
    db.execute(
        sql_text(
            """
            INSERT INTO item_embeddings (item_id, model, embedding, updated_at)
            VALUES (:item_id, :model, :embedding, datetime('now'))
            ON CONFLICT(item_id) DO UPDATE SET
              model      = excluded.model,
              embedding  = excluded.embedding,
              updated_at = excluded.updated_at
            """
        ),
        {
            "item_id": item_id,
            "model": model,
            "embedding": _vec_to_json_bytes(vec),
        },
    )
    db.commit()
    return vec



def load_all_embeddings_except(db:Session, item_id: int) -> List[Tuple[int, "np.ndarray"]]: 
    """
    Return [(other_item_id, embedding),...] for the ENTIRE DB except `item_id`.
    """
    rows = db.execute(
        sql_text("""
            SELECT item_id, embedding
            FROM item_embeddings
            WHERE item_id != :item_id
              AND embedding IS NOT NULL
        """),
        {"item_id": item_id},
    ).fetchall()

    out: List[Tuple[int, np.ndarray]] = []
    for r in rows:
        try:
            out.append((int(r[0]), _vec_from_json_bytes(r[1])))
        except Exception:
           
            continue
    return out


def cosine(u: np.ndarray, v: np.ndarray) -> float:
    nu = float(np.linalg.norm(u))
    nv = float(np.linalg.norm(v))
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return float(np.dot(u, v) / (nu * nv))


def top_k_score(scores: List[Tuple[int,float]], k:int) -> List[Tuple[int,float]]:
    """
    Sort scores desc and return top-k pairs (item_id, score).
    """
    return sorted(scores, key=lambda x: x[1], reverse=True)[:k]