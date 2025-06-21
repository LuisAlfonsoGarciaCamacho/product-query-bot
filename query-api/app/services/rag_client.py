import httpx
from loguru import logger
from app.core.config import settings

class RAGClient:
    def __init__(self):
        self.rag_service_url = settings.rag_service_url
        self._initialized = False
        self._client = None
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        try:
            self._client = httpx.AsyncClient(timeout=30.0)
            
            response = await self._client.get(f"{self.rag_service_url}/api/v1/health")
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get("document_count", 0)
                logger.success(f"Connected to RAG service ({doc_count} documents)")
                self._initialized = True
            else:
                raise Exception(f"RAG service health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to RAG service: {e}")
            if self._client:
                await self._client.aclose()
                self._client = None
    
    async def query_documents(self, query: str, top_k: int | None = None) -> list[str]:
        if not self._initialized:
            await self.initialize()
        
        if not self._client:
            logger.error("RAG client not initialized")
            return []
        
        try:
            logger.debug(f"Querying RAG service: '{query}' (top_k={top_k})")
            
            response = await self._client.post(
                f"{self.rag_service_url}/api/v1/query",
                json={
                    "query": query,
                    "top_k": top_k or settings.top_k
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                logger.debug(f"Retrieved {len(documents)} documents")
                return documents
            else:
                logger.error(f"RAG service query error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error querying RAG service: {e}")
            return []
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
            self._initialized = False

rag_client = RAGClient()