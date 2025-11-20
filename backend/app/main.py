
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db.models import Base
from backend.app.db.database import engine 
from backend.app.routers import gen 
from backend.app.routers import items as items_router
from backend.app.routers import gen

app = FastAPI(title="Exam Item Reviewer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(gen.router, prefix="/api/items", tags=["items"])
app.include_router(items_router.router, prefix="/api/items", tags=["items"])



@app.get("/health")
def health():
    return {"ok": True, "service": "api", "status": "healthy"}

#启动时建表
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)