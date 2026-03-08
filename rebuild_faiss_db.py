"""
Rebuild FAISS vector database from IPC PDF.
Run once: python rebuild_faiss_db.py
"""

import os
import sys

# Use the venv python packages
venv_site = os.path.join("knowledge_engineering", "venv", "Lib", "site-packages")
if os.path.exists(venv_site):
    sys.path.insert(0, venv_site)

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

PDF_PATH = os.path.join("data", "ipc_law.pdf")
DB_PATH = "ipc_vector_db"

def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)

    print(f"[1/4] Loading PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"      Loaded {len(documents)} pages")

    print("[2/4] Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"      Created {len(chunks)} chunks")

    print("[3/4] Creating embeddings (this takes a few minutes)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1",
        model_kwargs={
            "trust_remote_code": True,
            "revision": "289f532e14dbbbd5a04753fa58739e9ba766f3c7"
        }
    )

    print("[4/4] Building and saving FAISS database...")
    faiss_db = FAISS.from_documents(chunks, embeddings)
    faiss_db.save_local(DB_PATH)

    print()
    print(f"Done! Database saved to {DB_PATH}/")
    print(f"  index.faiss + index.pkl created")

if __name__ == "__main__":
    main()
