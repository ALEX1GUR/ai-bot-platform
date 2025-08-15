from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from ..config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, EMBED_DIM
from .llm import embed_texts

_qclient = None

def get_qdrant() -> QdrantClient:
    global _qclient
    if _qclient is None:
        _qclient = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _qclient

def ensure_collection(client: QdrantClient):
    cols = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in cols:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(size=EMBED_DIM, distance=qmodels.Distance.COSINE),
        )

def upsert_points(client: QdrantClient, vectors: List[List[float]], payloads: List[Dict[str, Any]]):
    points = [qmodels.PointStruct(id=None, vector=vec, payload=pl) for vec, pl in zip(vectors, payloads)]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)

def search_vectors(query: str, folder_paths: List[str], top_k: int = 6) -> List[Dict[str, Any]]:
    client = get_qdrant()
    vec = embed_texts([query])[0]
    must_filters = []
    if folder_paths:
        must_filters.append(qmodels.FieldCondition(key="folder_path", match=qmodels.MatchAny(any=folder_paths)))
    flt = qmodels.Filter(must=must_filters) if must_filters else None
    res = client.search(collection_name=QDRANT_COLLECTION, query_vector=vec, query_filter=flt, limit=top_k)
    out = []
    for r in res:
        payload = r.payload or {}
        out.append({"score": float(r.score), "folder_path": payload.get("folder_path"),
                    "file_path": payload.get("file_path"), "chunk_ord": payload.get("chunk_ord"),
                    "preview": payload.get("preview")})
    return out

def retrieve_context(query: str, folder_paths: List[str], top_k: int = 6):
    return search_vectors(query, folder_paths, top_k=top_k)
