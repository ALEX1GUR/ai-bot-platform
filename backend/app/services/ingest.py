import os, re
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
from ..config import QDRANT_COLLECTION
from .retrieval import get_qdrant, ensure_collection, upsert_points
from .llm import embed_texts

def clean_text(s: str) -> str:
    s = s.replace("\u200f", "").replace("\u200e", "")
    s = re.sub(r"[\u0591-\u05C7]", "", s)  # strip niqqud
    return s.strip()

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    text = text.replace("\r", "")
    chunks = []
    i = 0
    while i < len(text):
        end = min(i + max_chars, len(text))
        chunk = text[i:end]
        chunks.append(chunk)
        if end == len(text): break
        i = end - overlap
        if i < 0: i = 0
    return [c for c in (x.strip() for x in chunks) if c]

def extract_text_from_file(path: str) -> Tuple[str, Dict[str, Any]]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(path)
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n\n".join(pages), {"pages": len(pages)}
    elif ext in [".docx"]:
        d = DocxDocument(path)
        paras = [p.text for p in d.paragraphs]
        return "\n".join(paras), {"paras": len(paras)}
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(), {}

def ingest_file(path: str, folder_path: str) -> Dict[str, Any]:
    text, meta = extract_text_from_file(path)
    text = clean_text(text)
    chunks = chunk_text(text)
    if not chunks:
        return {"chunks": 0, "skipped": True}
    vectors = embed_texts(chunks)
    client = get_qdrant()
    ensure_collection(client)
    payloads = []
    for i, chunk in enumerate(chunks):
        payloads.append({"folder_path": folder_path, "file_path": path, "chunk_ord": i, "preview": chunk[:200]})
    upsert_points(client, vectors=vectors, payloads=payloads)
    return {"chunks": len(chunks), "skipped": False, "meta": meta}
