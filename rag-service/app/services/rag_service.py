from typing import Any
from loguru import logger
from app.core.config import settings
from app.services.vector_store_service import vector_store_service
from app.services.embedding_service import embedding_service


class RAGService:
    def __init__(self):
        self._initialized = False
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        try:
            logger.info("Initializing RAG service")
            
            await embedding_service.initialize()
            await vector_store_service.initialize()
            
            self._initialized = True
            logger.success("RAG service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    async def add_documents(self, documents: list[str]) -> list[str]:
        if not self._initialized:
            await self.initialize()
        
        return await vector_store_service.add_documents(documents)
    
    async def query(self, query: str, top_k: int | None = None) -> list[str]:
        if not self._initialized:
            await self.initialize()
        
        return await vector_store_service.query_documents(query, top_k)
    
    async def clear_documents(self) -> None:
        if not self._initialized:
            await self.initialize()
        
        await vector_store_service.clear_store()
    
    async def get_system_info(self) -> dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        store_info = await vector_store_service.get_store_info()
        return {
            "rag_service": {
                "initialized": self._initialized,
                "top_k": settings.top_k,
                "embedding_model": settings.embedding_model,
            },
            "vector_store": store_info
        }


# Global instance
rag_service = RAGService()