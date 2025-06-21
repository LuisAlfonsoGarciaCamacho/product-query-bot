import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.services.llm_service import llm_service
from app.api.llm_endpoints import router as llm_router

logger.remove()
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting LLM service...")
    
    # Initialize LLM service
    try:
        await llm_service.initialize()
        logger.success("LLM service startup complete")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        raise
    
    yield
    
    logger.info("Shutting down LLM service...")


app = FastAPI(
    title="LLM Service",
    description="LLM Service using VLLM backend",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(llm_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )