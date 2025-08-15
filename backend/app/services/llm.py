from typing import List, Dict, Any
from openai import OpenAI
from ..config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBED_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def embed_texts(texts: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(model=OPENAI_EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

SYSTEM_PROMPT = (
    "׳׳×/׳” ׳¢׳•׳–׳¨/׳× ׳׳¨׳’׳•׳ ׳™/׳× ׳”׳“׳•׳‘׳¨/׳× ׳¢׳‘׳¨׳™׳× ׳‘׳׳•׳₪׳ ׳˜׳‘׳¢׳™. "
    "׳¢׳ /׳™ ׳‘׳§׳¦׳¨׳” ׳•׳‘׳׳§׳¦׳•׳¢׳™׳•׳×, ׳•׳×׳׳™׳“ ׳¦׳™׳™׳/׳™ ׳¦׳™׳˜׳•׳˜׳™ ׳׳§׳•׳¨ ׳׳×׳•׳ ׳”׳”׳§׳©׳¨׳™׳ ׳©׳¡׳•׳₪׳§׳•. "
    "׳׳ ׳׳™׳ ׳׳¡׳₪׳™׳§ ׳¨׳׳™׳•׳× ג€“ ׳׳׳¨/׳™ ׳–׳׳× ׳‘׳׳₪׳•׳¨׳©."
)

def build_context_instructions(matches: List[Dict[str, Any]]) -> str:
    lines = []
    for i, m in enumerate(matches, 1):
        ident = f"[{i}] {m.get('file_path')}#chunk={m.get('chunk_ord')}"
        preview = (m.get('preview') or "").replace("\n", " ")
        lines.append(f"{ident}\n{preview}")
    return "\n\n".join(lines)

def answer_with_citations(query: str, matches: List[Dict[str, Any]], mode: str = "concise") -> Dict[str, Any]:
    context_block = build_context_instructions(matches)
    user_prompt = (
        f"׳©׳׳׳”: {query}\n\n"
        f"׳”׳§׳©׳¨׳™׳ ׳•׳׳§׳•׳¨׳•׳×:\n{context_block}\n\n"
        f"׳”׳ ׳—׳™׳•׳× ׳¡׳’׳ ׳•׳: ׳¢׳ ׳” ׳‘׳¢׳‘׳¨׳™׳×, ׳׳¦׳‘: {mode}. ׳›׳׳•׳ ׳¦׳™׳˜׳•׳˜׳™׳ ׳‘׳¡׳•׳£ ׳‘׳₪׳•׳¨׳׳˜ [index]."
    )
    chat = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": user_prompt}],
        temperature=0.2,
    )
    answer = chat.choices[0].message.content
    citations = [{"index": i+1, **m} for i, m in enumerate(matches)]
    return {"answer": answer, "citations": citations, "confidence": 0.0}
