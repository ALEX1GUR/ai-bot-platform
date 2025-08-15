from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List
import os, uuid

from .config import STORAGE_DIR
from .services.ingest import ingest_file
from .services.retrieval import retrieve_context
from .services.llm import answer_with_citations

app = FastAPI(title="Private Hebrew RAG API", version="0.1.0")

class FolderCreate(BaseModel):
    path: str  # e.g., "׳—׳•׳–׳™׳/2025"

class ChatRequest(BaseModel):
    message: str
    folder_paths: List[str] = []
    top_k: int = 6
    answer_mode: str = "concise"

@app.post("/folders")
def create_folder(payload: FolderCreate):
    base = os.path.join(STORAGE_DIR, payload.path)
    try:
        os.makedirs(base, exist_ok=True)
    except Exception as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "path": payload.path}

@app.get("/folders")
def list_folders():
    out = []
    for root, dirs, files in os.walk(STORAGE_DIR):
        rel = os.path.relpath(root, STORAGE_DIR)
        if rel == ".": rel = ""
        out.append({"path": rel, "dirs": dirs, "files": files})
    return {"folders": out}

@app.post("/upload")
async def upload_file(folder_path: str = Form(...), file: UploadFile = File(...)):
    folder_abs = os.path.join(STORAGE_DIR, folder_path)
    if not os.path.isdir(folder_abs):
        raise HTTPException(400, f"Folder does not exist: {folder_path}")
    uid = str(uuid.uuid4())
    fname = f"{uid}_{file.filename}"
    dest = os.path.join(folder_abs, fname)
    with open(dest, "wb") as f:
        f.write(await file.read())
    try:
        stats = ingest_file(dest, folder_path=folder_path)
    except Exception as e:
        raise HTTPException(500, f"Ingest failed: {e}")
    return {"ok": True, "path": os.path.join(folder_path, fname), "stats": stats}

@app.post("/chat")
def chat(req: ChatRequest):
    matches = retrieve_context(req.message, folder_paths=req.folder_paths, top_k=req.top_k)
    if not matches:
        return {"answer": "׳׳ ׳ ׳׳¦׳׳• ׳׳§׳•׳¨׳•׳× ׳¨׳׳•׳•׳ ׳˜׳™׳™׳ ׳‘׳×׳™׳§׳™׳•׳× ׳©׳ ׳‘׳—׳¨׳•.", "citations": [], "confidence": 0.0}
    ans = answer_with_citations(query=req.message, matches=matches, mode=req.answer_mode)
    return ans
