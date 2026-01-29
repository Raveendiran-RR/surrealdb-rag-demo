"""
Custom OpenAI Embeddings for Docker Model Runner

This module provides a custom embeddings class that uses Docker Model Runner's
OpenAI-compatible API endpoint for generating embeddings.
"""

from typing import List
from langchain_core.embeddings import Embeddings
import requests


class DockerModelRunnerEmbeddings(Embeddings):
    """
    Custom embeddings class for Docker Model Runner using OpenAI-compatible API.
    
    Docker Model Runner supports the OpenAI /v1/embeddings endpoint but not
    the Ollama /api/embed endpoint.
    """
    
    def __init__(
        self,
        model: str = "embeddinggemma",
        base_url: str = "http://localhost:12434",
    ):
        """
        Initialize Docker Model Runner embeddings.
        
        Args:
            model: Model name (e.g., "embeddinggemma")
            base_url: Base URL for Docker Model Runner (default: http://localhost:12434)
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/v1/embeddings"
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        response = requests.post(
            self.api_url,
            json={
                "model": self.model,
                "input": texts
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Embedding request failed: {response.text}")
        
        result = response.json()
        
        # Extract embeddings from response
        # OpenAI format: {"data": [{"embedding": [...]}, ...]}
        embeddings = [item["embedding"] for item in result["data"]]
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
        """
        return self.embed_documents([text])[0]
