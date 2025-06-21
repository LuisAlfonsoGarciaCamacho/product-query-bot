from typing import Any
from llama_index.llms.openai_like import OpenAILike
from loguru import logger
from app.core.config import settings


class LLMService:    
    def __init__(self):
        self.llm = None
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
        
        try:
            logger.info(f"Connecting to VLLM at: {settings.vllm_api_base}")
            
            self.llm = OpenAILike(
                model=settings.model_name,
                api_base=settings.vllm_api_base,
                api_key=settings.vllm_api_key,
                is_chat_model=True,
                context_window=settings.context_window,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                timeout=60.0,
                max_retries=3
            )
            
            await self._test_connection()
            self._initialized = True
            logger.success("LLM service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise
    
    async def _test_connection(self):
        try:
            response = await self.llm.acomplete("Hello")
            logger.info("VLLM connection test successful")
        except Exception as e:
            logger.error(f"VLLM connection test failed: {e}")
            raise
    
    async def generate_completion(
        self, 
        prompt: str, 
        max_tokens: int | None = None,
        temperature: float | None = None
    ) -> str:
        if not self._initialized:
            await self.initialize()
        
        try:
            kwargs = {}
            if max_tokens is not None:
                kwargs['max_tokens'] = max_tokens
            if temperature is not None:
                kwargs['temperature'] = temperature
            
            response = await self.llm.acomplete(prompt, **kwargs)
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    async def generate_chat_completion(
        self, 
        messages: list[dict[str, str]], 
        max_tokens: int | None = None,
        temperature: float | None = None
    ) -> str:
        if not self._initialized:
            await self.initialize()
        
        try:
            from llama_index.core.base.llms.types import ChatMessage
            
            chat_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            
            kwargs = {}
            if max_tokens is not None:
                kwargs['max_tokens'] = max_tokens
            if temperature is not None:
                kwargs['temperature'] = temperature
            
            response = await self.llm.achat(chat_messages, **kwargs)
            return str(response.message.content)
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            raise
    
    def get_model_info(self) -> dict[str, Any]:
        """Get model information"""
        return {
            "model": settings.model_name,
            "api_base": settings.vllm_api_base,
            "max_tokens": settings.max_tokens,
            "context_window": settings.context_window,
            "initialized": self._initialized
        }


# Global instance
llm_service = LLMService()