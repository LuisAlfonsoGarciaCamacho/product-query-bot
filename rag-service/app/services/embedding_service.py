import asyncio
from sentence_transformers import SentenceTransformer
from loguru import logger
from app.core.config import settings


class EmbeddingService:
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance.model = None
        return cls._instance
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            try:
                logger.info(f"Loading embedding model: {settings.embedding_model}")
                
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None,
                    lambda: SentenceTransformer(
                        settings.embedding_model,
                        cache_folder=".cache/sentence_transformers",
                        device="cpu"
                    )
                )
                
                self._initialized = True
                logger.success("Embedding service initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize embedding service: {e}")
                raise
    
    async def encode(self, texts: list[str]) -> list[list[float]]:
        if not self._initialized:
            await self.initialize()
        
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_tensor=False)
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    async def encode_single(self, text: str) -> list[float]:
        embeddings = await self.encode([text])
        return embeddings[0]


embedding_service = EmbeddingService()