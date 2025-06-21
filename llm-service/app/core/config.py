from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "LLM Service"
    version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    vllm_api_base: str = "http://vllm-service:8000/v1"
    vllm_api_key: str = "fake_key"
    model_name: str = "qwen2.5-0.5b"
    max_tokens: int = 300
    temperature: float = 0.2
    context_window: int = 4096
    log_level: str = "INFO"
    
    model_config = {"env_file": ".env"}

settings = Settings()