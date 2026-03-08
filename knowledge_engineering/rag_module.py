"""
RAG Module - Retrieves supporting text from FAISS vector database.
"""

import os
import logging

logger = logging.getLogger(__name__)


class RAGModule:
    """Retrieves supporting legal text from FAISS vector database."""
    
    def __init__(self, faiss_db_path: str = "ipc_vector_db"):
        self._db = None
        self._embeddings = None
        # Fix path - if relative, make it absolute from project root
        if not os.path.isabs(faiss_db_path):
            # Get project root (parent of knowledge_engineering)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            faiss_db_path = os.path.join(project_root, faiss_db_path)
        self._load_db(faiss_db_path)
    
    def _load_db(self, path: str) -> None:
        """
        Load FAISS DB. Sets self._db to None if unavailable.
        
        Args:
            path: Path to the FAISS database directory
        """
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings
            
            # Check if DB exists
            if not os.path.exists(path):
                logger.warning(f"FAISS database not found at {path}")
                return
            
            # Load embeddings (same config as existing system)
            self._embeddings = HuggingFaceEmbeddings(
                model_name="nomic-ai/nomic-embed-text-v1",
                model_kwargs={
                    "trust_remote_code": True,
                    "revision": "289f532e14dbbbd5a04753fa58739e9ba766f3c7"
                }
            )
            
            # Load FAISS DB
            self._db = FAISS.load_local(
                path,
                self._embeddings,
                allow_dangerous_deserialization=True
            )
            
            logger.info(f"Successfully loaded FAISS database from {path}")
            
        except Exception as e:
            logger.warning(f"Failed to load FAISS database: {e}")
            self._db = None
    
    def retrieve(self, section_ids: list[str], k: int = 3) -> dict[str, list[str]]:
        """
        For each section ID, query FAISS for relevant text chunks.
        
        Args:
            section_ids: List of IPC section identifiers
            k: Number of chunks to retrieve per section
            
        Returns:
            Dictionary mapping section_id to list of text chunks
            Returns empty dict if DB is unavailable
        """
        if not self.is_available():
            return {}
        
        results = {}
        
        for section_id in section_ids:
            try:
                # Query for this section
                query = f"IPC Section {section_id}"
                docs = self._db.similarity_search(query, k=k)
                
                # Extract text content
                texts = [doc.page_content for doc in docs]
                results[section_id] = texts
                
            except Exception as e:
                logger.warning(f"Failed to retrieve text for section {section_id}: {e}")
                results[section_id] = []
        
        return results
    
    def is_available(self) -> bool:
        """Check if FAISS DB was loaded successfully."""
        return self._db is not None
