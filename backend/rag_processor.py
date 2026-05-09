import os
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class RAGProcessor:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.initialized = False
        self.current_doc_id = None
        
    def initialize(self):
        """Initialize RAG components."""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.chroma_client.get_or_create_collection(
                name="studyai_docs",
                metadata={"hnsw:space": "cosine"}
            )
            self.initialized = True
            logger.info("RAG Processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            raise
    
    def process_document(self, text: str, doc_id: str = None):
        """Process document text and store in vector DB."""
        if not self.initialized:
            self.initialize()
        
        try:
            if doc_id:
                self.current_doc_id = doc_id
                self.collection.delete(where={"doc_id": doc_id})
            
            chunks = self._chunk_text(text)
            if not chunks:
                return {"status": "error", "message": "No text to process"}
            
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            ids = [f"{self.current_doc_id}_{i}" for i in range(len(chunks))]
            metadatas = [{"doc_id": self.current_doc_id, "chunk_index": i} 
                        for i in range(len(chunks))]
            
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            
            return {
                "status": "success",
                "message": f"Processed {len(chunks)} chunks",
                "chunks": len(chunks)
            }
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {"status": "error", "message": str(e)}
    
    def query(self, question: str, n_results: int = 3):
        """Query the RAG system for relevant context."""
        if not self.initialized:
            self.initialize()
        
        try:
            query_embedding = self.embedding_model.encode([question]).tolist()[0]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"doc_id": self.current_doc_id} if self.current_doc_id else None
            )
            
            if results and results.get('documents'):
                context = "\n\n".join(results['documents'][0])
                return {
                    "status": "success",
                    "context": context,
                    "sources": results.get('metadatas', [[]])[0]
                }
            return {"status": "no_results", "context": "", "sources": []}
        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            return {"status": "error", "message": str(e)}
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def clear_document(self, doc_id: str):
        """Clear a specific document from the vector store."""
        try:
            if self.collection:
                self.collection.delete(where={"doc_id": doc_id})
                logger.info(f"Cleared document {doc_id} from RAG")
        except Exception as e:
            logger.error(f"Error clearing document: {e}")
