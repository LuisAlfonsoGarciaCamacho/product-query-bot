from typing import Any
from loguru import logger
from app.agents.retriever_agent import retriever_agent
from app.agents.responder_agent import responder_agent

class ChatOrchestrator:
    def __init__(self):
        self._initialized = False
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        logger.info("Initializing chat orchestrator")
        self._initialized = True
        logger.success("Chat orchestrator initialized")
    
    async def process_query(self, user_id: str, query: str) -> str:
        try:
            if not self._initialized:
                await self.initialize()
            
            logger.info(f"Processing query for user {user_id}: '{query}'")
            
            logger.debug("Retrieving documents from RAG service...")
            retrieved_docs = await retriever_agent.retrieve(query)
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            logger.debug("Generating response...")
            response = await responder_agent.generate_response(query, retrieved_docs)
            logger.info(f"Generated response: {response[:100]}...")
            
            logger.success(f"Successfully processed query for user {user_id}")
            return response
        
        except Exception as e:
            logger.error(f"Error in orchestrator for user {user_id}: {e}")
            return f"I'm sorry, I encountered an error while processing your query. Please try again."
    
    async def get_system_status(self) -> dict[str, Any]:
        try:
            return {
                "orchestrator": {
                    "initialized": self._initialized,
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

chat_orchestrator = ChatOrchestrator()