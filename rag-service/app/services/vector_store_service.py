from llama_index.core.schema import TextNode
from llama_index.vector_stores.postgres import PGVectorStore
from loguru import logger
from app.core.config import settings
from app.services.embedding_service import embedding_service
import asyncpg

class VectorStoreService:
    def __init__(self):
        self.vector_store = None
        self._initialized = False
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        try:
            logger.info("Initializing vector store")
            
            await embedding_service.initialize()
            
            self.vector_store = PGVectorStore.from_params(
                database=settings.postgres_db,
                host=settings.postgres_host,
                password=settings.postgres_password,
                port=settings.postgres_port,
                user=settings.postgres_user,
                table_name=settings.vector_table_name,
                embed_dim=settings.embedding_dimension,
                schema_name=settings.vector_schema_name
            )
            
            self._initialized = True
            logger.success("Vector store initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_documents(self, documents: list[str]) -> list[str]:
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Adding {len(documents)} documents")
            
            embeddings = await embedding_service.encode(documents)
            
            nodes = [
                TextNode(
                    text=doc,
                    id_=f"doc_{hash(doc[:50])}_{i}",
                    embedding=embedding,
                    metadata={
                        "doc_index": i,
                        "doc_length": len(doc),
                        "doc_preview": doc[:100]
                    }
                )
                for i, (doc, embedding) in enumerate(zip(documents, embeddings))
            ]
            
            node_ids = self.vector_store.add(nodes)
            logger.success(f"Added {len(node_ids)} documents")
            return node_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def query_documents(self, query: str, top_k: int | None = None) -> list[str]:
        if not self._initialized:
            await self.initialize()
        
        try:
            k = min(top_k or settings.top_k, 10)
            logger.debug(f"Querying: '{query}' (top_k={k})")
            
            query_embedding = await embedding_service.encode_single(query)
            
            from llama_index.core.vector_stores import VectorStoreQuery
            
            vector_query = VectorStoreQuery(
                query_embedding=query_embedding,
                similarity_top_k=k * 2,
                mode="default"
            )
            
            result = self.vector_store.query(vector_query)
            
            documents = []
            seen_texts = set()
            
            for node in result.nodes:
                doc_text = node.text.strip()
                doc_key = doc_text[:50].lower().strip()
                
                if doc_key not in seen_texts and len(doc_text) > 20:
                    documents.append(doc_text)
                    seen_texts.add(doc_key)
                    
                    if len(documents) >= k:
                        break
            
            logger.debug(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    async def clear_store(self) -> None:
        if not self._initialized:
            await self.initialize()
        
        try:
            conn = await asyncpg.connect(settings.postgres_dsn)
            try:
                table_full_name = f"{settings.vector_schema_name}.{settings.vector_table_name}"
                await conn.execute(f"DELETE FROM {table_full_name}")
                logger.info("Vector store cleared")
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
    
    async def get_store_info(self) -> dict[str, any]:
        if not self._initialized:
            await self.initialize()
        
        try:
            conn = await asyncpg.connect(settings.postgres_dsn)
            try:
                table_full_name = f"{settings.vector_schema_name}.{settings.vector_table_name}"
                count_result = await conn.fetchval(f"SELECT COUNT(*) FROM {table_full_name}")
                
                return {
                    "table_name": settings.vector_table_name,
                    "schema_name": settings.vector_schema_name,
                    "embedding_dimension": settings.embedding_dimension,
                    "total_documents": count_result or 0,
                    "initialized": self._initialized
                }
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error getting store info: {e}")
            return {
                "table_name": settings.vector_table_name,
                "schema_name": settings.vector_schema_name,
                "embedding_dimension": settings.embedding_dimension,
                "total_documents": 0,
                "initialized": self._initialized,
                "error": str(e)
            }

vector_store_service = VectorStoreService()