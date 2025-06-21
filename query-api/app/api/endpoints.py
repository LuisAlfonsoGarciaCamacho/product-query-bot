import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger
import httpx

from app.models.schemas import QueryRequest, QueryResponse, ProcessingResponse
from app.agents.orchestrator import chat_orchestrator
from app.core.config import settings

router = APIRouter()

query_queue: asyncio.Queue = asyncio.Queue()
_processor_running = False

async def process_query_background():
    global _processor_running
    
    if _processor_running:
        logger.warning("Background processor already running")
        return
    
    _processor_running = True
    logger.info("Background query processor started")
    
    try:
        while True:
            try:
                logger.debug("Waiting for query in queue...")
                query_data = await query_queue.get()
                logger.info(f"Processing query from user: {query_data['user_id']}")
                
                user_id = query_data["user_id"]
                query = query_data["query"]
                
                logger.debug(f"Sending query to orchestrator: '{query}'")
                response = await chat_orchestrator.process_query(user_id, query)
                logger.info(f"Got response from orchestrator: {response[:100]}...")
                
                await send_callback_with_retry(user_id, response)
                
                query_queue.task_done()
                logger.success("Query processing completed")
                
            except asyncio.CancelledError:
                logger.info("Background processor cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                
    finally:
        _processor_running = False
        logger.info("Background query processor stopped")

async def send_callback_with_retry(user_id: str, answer: str, max_retries: int = 3):
    logger.debug(f"Sending callback for user {user_id}")
    
    if not settings.callback_url:
        logger.warning(f"No callback URL configured. Response for {user_id}: {answer}")
        return
    
    response_data = QueryResponse(
        user_id=user_id,
        answer=answer,
        timestamp=datetime.utcnow().isoformat()
    )
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Callback attempt {attempt + 1} for user {user_id}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    settings.callback_url,
                    json=response_data.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.success(f"Callback sent successfully: {response.status_code}")
                    return
                else:
                    logger.warning(f"Callback failed with status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending callback (attempt {attempt + 1}): {e}")
            
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
    
    logger.error(f"Failed to send callback after {max_retries} attempts")

@router.post("/query", response_model=ProcessingResponse)
async def query_endpoint(request: QueryRequest):
    try:
        logger.info(f"Received query from {request.user_id}: '{request.query}'")
        
        await query_queue.put({
            "user_id": request.user_id,
            "query": request.query
        })
        
        logger.info(f"Query queued successfully. Queue size: {query_queue.qsize()}")
        
        return ProcessingResponse()
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.get("/health")
async def health_check():
    try:
        system_status = await chat_orchestrator.get_system_status()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "queue_size": query_queue.qsize(),
            "processor_running": _processor_running,
            "callback_url": settings.callback_url,
            "system": system_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/queue-status")
async def queue_status():
    return {
        "queue_size": query_queue.qsize(),
        "processor_running": _processor_running,
        "timestamp": datetime.utcnow().isoformat(),
        "callback_url": settings.callback_url,
        "settings": {
            "top_k": settings.top_k,
        }
    }

@router.get("/system-info")
async def system_info():
    try:
        system_status = await chat_orchestrator.get_system_status()
        return {
            "project": settings.project_name,
            "version": settings.version,
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": {
                "embedding_model": settings.embedding_model,
                "vector_table": settings.vector_table_name,
                "top_k": settings.top_k,
                "callback_url": settings.callback_url
            },
            "queue": {
                "size": query_queue.qsize(),
                "processor_running": _processor_running
            },
            "system_status": system_status
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
