import httpx
from loguru import logger
from app.core.config import settings


class LLMClient:
    def __init__(self):
        self.llm_service_url = settings.llm_service_url
        self._initialized = False
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.llm_service_url}/api/v1/health")
                if response.status_code == 200:
                    logger.success("Connected to LLM service")
                    self._initialized = True
                else:
                    raise Exception(f"LLM service health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to LLM service: {e}")
            raise
    
    async def generate_response(
        self, 
        prompt: str, 
        max_length: int = 200, 
        temperature: float = 0.2
    ) -> str:
        if not self._initialized:
            await self.initialize()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.llm_service_url}/api/v1/completion",
                    json={
                        "prompt": prompt,
                        "max_tokens": max_length,
                        "temperature": temperature
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    generated_text = data.get("text", "").strip()
                    
                    if not generated_text or len(generated_text) < 10:
                        return "I apologize, but I couldn't generate a proper response."
                    
                    return generated_text
                else:
                    logger.error(f"LLM service error: {response.status_code}")
                    return "I apologize, but I'm currently unable to generate a response."
                    
        except Exception as e:
            logger.error(f"Error calling LLM service: {e}")
            return "I apologize, but I encountered an error while generating a response."


# Global instance
llm_client = LLMClient()