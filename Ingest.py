import json
import hashlib
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = Path("data")
DB_DIR = "chroma_db"
COLLECTION = "jyotish_veda_ai"

EMBED_MODEL = "all-MiniLM-L6-v2"

def get_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    embed_fun = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_or_create_collection(name = COLLECTION, embedding_function=embed_fun, metadata={"hnsw:space": "cosine"})


def _doc_id(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]

def load_json_rules():
    docs, metas, ids = [], [], []
    for path in DATA_DIR.glob("*.json"):
        rules = json.loads(path.read_text(encoding="utf-8"))
        for rule in rules:
            docs.append(rule["text"])
            meta = {k: v for k, v in rule.get("metadata", {}).items() if v is not None}
            meta["file"] = path.name
            metas.append(meta)
            ids.append(_doc_id(rule["text"]))
    return docs, metas, ids

def load_pdfs(chunk_size = 800, overlap = 100):
    from pypdf import PdfReader
    docs, metas, ids = [], [], []
    for path in DATA_DIR.glob("*.pdf"):
        reader = PdfReader(str(path))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        paras = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        chunks, current = [] , ""
        for p in paras:
            if len(current) + len(p) > chunk_size and current:
                chunks.append(current)
                current = current[-overlap:]  + " " + p# keep overlap for next chunk
                
            else:
                current = (current + "\n" + p).strip()
        if current:
            chunks.append(current)
            
        for i, chunk in enumerate(chunks):
            docs.append(chunk)
            metas.append({"file": path.name, "chunk": i, "source": "pdf"})
            ids.append(_doc_id(f"{path.name}:{i}:{chunk[:50]}"))
        print(f"  {path.name}: {len(chunks)} chunks")
    return docs, metas, ids
 
 
def main():
    col = get_collection()
 
    print("Loading JSON rules...")
    docs, metas, ids = load_json_rules()
 
    print("Loading PDFs...")
    d2, m2, i2 = load_pdfs()
    docs += d2; metas += m2; ids += i2
 
    if not docs:
        print("No documents found in ./data — add JSON rules or PDFs.")
        return
 
    # upsert in batches
    BATCH = 100
    for i in range(0, len(docs), BATCH):
        col.upsert(
            documents=docs[i:i + BATCH],
            metadatas=metas[i:i + BATCH],
            ids=ids[i:i + BATCH],
        )
    print(f"\nIngested {len(docs)} chunks into '{COLLECTION}' "
          f"(total in DB: {col.count()})")
 
 
if __name__ == "__main__":
    main()