"""
Chroma DB Integration for Code Embeddings
Semantic code search powered by Chroma
"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import hashlib


class ChromaCodeSearch:
    """Semantic code search using Chroma DB"""
    
    def __init__(self):
        """Initialize Chroma client and collection"""
        
        # Persistent storage location
        persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        
        # Initialize Chroma client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Get or create collection for code embeddings
        self.collection = self.client.get_or_create_collection(
            name="code_embeddings",
            metadata={
                "description": "OPS-X semantic code search",
                "hnsw:space": "cosine"  # Use cosine similarity
            }
        )
        
        print(f"Chroma initialized: {self.collection.count()} embeddings stored")
    
    def add_code_file(
        self,
        project_id: str,
        file_path: str,
        content: str,
        embedding: List[float],
        language: Optional[str] = None
    ) -> str:
        """
        Add a code file to Chroma for semantic search
        
        Args:
            project_id: Project identifier
            file_path: Path to the file
            content: File content (will store snippet)
            embedding: Vector embedding of the content
            language: Programming language
            
        Returns:
            Chroma document ID
        """
        
        # Generate unique ID
        chroma_id = self._generate_id(project_id, file_path)
        
        # Store only a snippet for context (not full file)
        snippet = content[:1000] if len(content) > 1000 else content
        
        try:
            self.collection.add(
                ids=[chroma_id],
                embeddings=[embedding],
                documents=[snippet],
                metadatas=[{
                    "project_id": project_id,
                    "file_path": file_path,
                    "language": language or self._detect_language(file_path),
                    "size": len(content)
                }]
            )
            
            print(f"Added to Chroma: {file_path}")
            return chroma_id
            
        except Exception as e:
            print(f"Error adding to Chroma: {e}")
            raise
    
    def search_code(
        self,
        query_embedding: List[float],
        project_id: Optional[str] = None,
        n_results: int = 5
    ) -> Dict:
        """
        Semantic search for code
        
        Args:
            query_embedding: Vector embedding of search query
            project_id: Optional filter by project
            n_results: Number of results to return
            
        Returns:
            Search results with file paths and snippets
        """
        
        where_filter = {"project_id": project_id} if project_id else None
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                where=where_filter,
                n_results=n_results
            )
            
            return {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
            
        except Exception as e:
            print(f"Error searching Chroma: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}
    
    def delete_project_embeddings(self, project_id: str):
        """Delete all embeddings for a project"""
        
        try:
            # Get all IDs for this project
            results = self.collection.get(
                where={"project_id": project_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"Deleted {len(results['ids'])} embeddings for project {project_id}")
        
        except Exception as e:
            print(f"Error deleting embeddings: {e}")
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "total_embeddings": self.collection.count(),
            "collection_name": self.collection.name
        }
    
    def _generate_id(self, project_id: str, file_path: str) -> str:
        """Generate unique ID for Chroma"""
        combined = f"{project_id}:{file_path}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".php": "php",
            ".css": "css",
            ".html": "html",
            ".json": "json",
            ".md": "markdown"
        }
        
        for ext, lang in ext_to_lang.items():
            if file_path.endswith(ext):
                return lang
        
        return "unknown"


# Singleton instance
try:
    chroma_search = ChromaCodeSearch()
except Exception as e:
    print(f"WARNING: Chroma initialization failed: {e}")
    print("Semantic search will be disabled.")
    chroma_search = None


# Helper function to generate embeddings (placeholder)
def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text
    TODO: Replace with actual embedding model (OpenAI, Sentence Transformers, etc.)
    
    For now, returns a dummy embedding for testing
    """
    # This is a placeholder - integrate with actual embedding model
    # Options:
    # 1. OpenAI: openai.Embedding.create(input=text, model="text-embedding-ada-002")
    # 2. Sentence Transformers: model.encode(text)
    # 3. Google Gemini embeddings
    
    import random
    random.seed(hash(text) % 2**32)
    return [random.random() for _ in range(384)]  # Standard embedding dimension


if __name__ == "__main__":
    # Quick test
    if chroma_search:
        print("Chroma search initialized successfully!")
        print(f"Stats: {chroma_search.get_stats()}")
    else:
        print("Chroma search initialization failed.")

