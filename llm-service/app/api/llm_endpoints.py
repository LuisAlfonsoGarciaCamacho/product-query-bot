from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from app.services.llm_service import llm_service

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int | None = None
    temperature: float | None = None

class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int | None = None
    temperature: float | None = None

class CompletionResponse(BaseModel):
    text: str
    model: str

@router.post("/completion", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    try:
        logger.info(f"Completion request: {request.prompt[:100]}...")
        
        response = await llm_service.generate_completion(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return CompletionResponse(
            text=response,
            model=llm_service.llm.model if llm_service.llm else "unknown"
        )
        
    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/completion", response_model=CompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    try:
        logger.info(f"Chat completion request with {len(request.messages)} messages")
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = await llm_service.generate_chat_completion(
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return CompletionResponse(
            text=response,
            model=llm_service.llm.model if llm_service.llm else "unknown"
        )
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_info": llm_service.get_model_info()
    }

@router.get("/model/info")
async def get_model_info():
    return llm_service.get_model_info()