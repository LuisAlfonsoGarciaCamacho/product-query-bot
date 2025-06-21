from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "RAG Service"
    version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8003
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "product_query_bot"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    vector_table_name: str = "document_embeddings"
    vector_schema_name: str = "public"
    top_k: int = 5
    log_level: str = "INFO"
    
    model_config = {"env_file": ".env"}

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()