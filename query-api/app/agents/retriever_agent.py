from loguru import logger
from app.services.rag_client import rag_client

class RetrieverAgent:
    def __init__(self):
        self.rag_client = rag_client
    
    async def retrieve(self, query: str, top_k: int | None = None) -> list[str]:
        try:
            logger.debug(f"Retriever agent processing query: '{query}'")
            documents = await self.rag_client.query_documents(query, top_k)
            logger.debug(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return []

retriever_agent = RetrieverAgent()