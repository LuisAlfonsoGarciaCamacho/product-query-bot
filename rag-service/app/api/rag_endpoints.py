from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from app.services.rag_service import rag_service
from app.utils.data_loader import DataLoader

router = APIRouter()

class DocumentAddRequest(BaseModel):
    documents: list[str]

class QueryRequest(BaseModel):
    query: str
    top_k: int | None = None

class DocumentsResponse(BaseModel):
    documents: list[str]
    count: int

@router.post("/documents")
async def add_documents(request: DocumentAddRequest):
    try:
        logger.info(f"Adding {len(request.documents)} documents")
        node_ids = await rag_service.add_documents(request.documents)
        
        return {
            "message": f"Added {len(node_ids)} documents",
            "node_ids": node_ids,
            "count": len(node_ids)
        }
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/reload")
async def reload_default_documents():
    try:
        logger.info("Reloading default documents")
        
        await rag_service.clear_documents()
        
        default_docs = DataLoader.load_sample_products()
        node_ids = await rag_service.add_documents(default_docs)
        
        return {
            "message": f"Reloaded {len(node_ids)} default documents",
            "node_ids": node_ids,
            "count": len(node_ids)
        }
    except Exception as e:
        logger.error(f"Error reloading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=DocumentsResponse)
async def query_documents(request: QueryRequest):
    try:
        logger.debug(f"Querying: '{request.query}' (top_k={request.top_k})")
        documents = await rag_service.query(request.query, request.top_k)
        
        return DocumentsResponse(
            documents=documents,
            count=len(documents)
        )
    except Exception as e:
        logger.error(f"Error querying documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents")
async def clear_documents():
    try:
        await rag_service.clear_documents()
        return {"message": "All documents cleared"}
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/count")
async def get_document_count():
    try:
        info = await rag_service.get_system_info()
        count = info.get("vector_store", {}).get("total_documents", 0)
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting document count: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-info")
async def get_system_info():
    try:
        info = await rag_service.get_system_info()
        return {
            "status": "healthy",
            "info": info
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    try:
        info = await rag_service.get_system_info()
        doc_count = info.get("vector_store", {}).get("total_documents", 0)
        
        return {
            "status": "healthy", 
            "service": "rag-service",
            "document_count": doc_count,
            "initialized": info.get("rag_service", {}).get("initialized", False)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "rag-service", 
            "error": str(e)
        }