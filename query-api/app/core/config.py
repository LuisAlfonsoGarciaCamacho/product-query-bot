from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Product Query Bot"
    version: str = "0.1.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    llm_service_url: str = "http://llm-service:8001"
    rag_service_url: str = "http://rag-service:8003"
    callback_url: str | None = "http://host.docker.internal:3001/webhook"
    top_k: int = 5
    max_response_length: int = 300
    llm_temperature: float = 0.2
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "qwen2.5-0.5b"
    vector_table_name: str = "document_embeddings"
    log_level: str = "INFO"
    
    model_config = {"env_file": ".env"}

settings = Settings()