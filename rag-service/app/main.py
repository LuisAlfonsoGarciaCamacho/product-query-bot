import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.services.rag_service import rag_service
from app.api.rag_endpoints import router as rag_router
from app.utils.data_loader import DataLoader

logger.remove()
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RAG service...")
    
    try:
        await rag_service.initialize()
        
        store_info = await rag_service.get_system_info()
        total_docs = store_info.get("vector_store", {}).get("total_documents", 0)
        
        if total_docs == 0:
            logger.info("Loading default documents...")
            default_docs = DataLoader.load_sample_products()
            node_ids = await rag_service.add_documents(default_docs)
            logger.success(f"Loaded {len(node_ids)} default documents")
        else:
            logger.info(f"Vector store contains {total_docs} documents")
        
        logger.success("RAG service startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        raise
    
    yield
    
    logger.info("Shutting down RAG service...")


app = FastAPI(
    title="RAG Service",
    description="Retrieval-Augmented Generation Service",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(rag_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )