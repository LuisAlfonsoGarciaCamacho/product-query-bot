from typing import List
from loguru import logger
from app.services.llm_client import llm_client
from app.core.config import settings


class ResponderAgent:
    
    def __init__(self):
        self.llm_client = llm_client
    
    async def generate_response(self, query: str, retrieved_docs: List[str]) -> str:
        try:
            logger.debug(f"Generating response for: '{query}' with {len(retrieved_docs)} documents")
            
            if not retrieved_docs:
                return self._create_no_documents_response()
            
            query_lower = query.lower().strip()
            
            if query_lower in ['hi', 'hello', 'hey', 'hola']:
                return self._create_greeting_response(retrieved_docs)
            
            if any(term in query_lower for term in ['price', 'cost', 'expensive', 'cheap', '$']):
                return "I don't have pricing information available. Please contact our sales team for current prices."
            
            if any(term in query_lower for term in ['products', 'list', 'show me', 'what do you have', 'available']):
                return self._create_product_listing(retrieved_docs)
            
            return await self._create_llm_response(query, retrieved_docs)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error. Please try again."
    
    def _create_greeting_response(self, docs: List[str]) -> str:
        categories = self._get_product_categories(docs)
        
        response = "Hello! Welcome to our electronics store. 👋\n\n"
        response += f"We have **{len(docs)} products** available:\n"
        
        for category, count in categories.items():
            response += f"• {category}: {count} available\n"
        
        response += "\nWhat can I help you find today?"
        return response
    
    def _create_product_listing(self, docs: List[str]) -> str:
        if not docs:
            return self._create_no_documents_response()
        
        docs = docs[:5]
        
        response = f"Here are our available products ({len(docs)} shown):\n\n"
        
        for i, doc in enumerate(docs, 1):
            if ':' in doc:
                name, desc = doc.split(':', 1)
                desc = desc.strip()[:150] + "..." if len(desc.strip()) > 150 else desc.strip()
                response += f"**{i}. {name.strip()}**\n{desc}\n\n"
            else:
                text = doc[:150] + "..." if len(doc) > 150 else doc
                response += f"**{i}. Product**\n{text}\n\n"
        
        response += "Would you like more details about any specific product?"
        return response
    
    async def _create_llm_response(self, query: str, docs: List[str]) -> str:
        try:
            context_docs = docs[:2]
            
            context = ""
            for i, doc in enumerate(context_docs, 1):
                clean_doc = doc.strip()[:300]
                context += f"Product {i}: {clean_doc}\n\n"
            
            prompt = f"""You are a helpful electronics store assistant.

Products available:
{context}

Customer question: {query}

Instructions:
- Answer using ONLY the product information above
- Be specific and helpful
- Use markdown with **bold** for product names
- Keep response under 100 words
- Do not mention prices
- If you can't answer from the information, say so

Response:"""

            response = await self.llm_client.generate_response(
                prompt=prompt,
                max_length=150,  # Shorter responses
                temperature=0.1  # More focused
            )
            
            return self._clean_response(response, query)
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._create_fallback_response(docs[:1])
    
    def _clean_response(self, response: str, original_query: str) -> str:
        """Aggressive response cleaning"""
        if not response or len(response.strip()) < 5:
            return "I couldn't generate a proper response. Please rephrase your question."
        
        response = response.strip()
        
        # Remove system prompts and instructions
        lines = response.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip system-related lines
            if any(skip_word in line.lower() for skip_word in [
                'instructions:', 'customer question:', 'products available:', 
                'response:', 'assistant', 'system', 'prompt'
            ]):
                continue
            
            if line and len(line) > 3:  # Only keep meaningful lines
                clean_lines.append(line)
        
        if not clean_lines:
            return f"I found some information but couldn't format it properly. Please ask about specific products."
        
        # Join and limit
        final_response = '\n'.join(clean_lines[:5])  # Max 5 lines
        
        # Final length check
        if len(final_response) > 300:
            final_response = final_response[:300] + "..."
        
        return final_response
    
    def _get_product_categories(self, docs: List[str]) -> dict:
        """Count products by category"""
        categories = {}
        
        for doc in docs:
            doc_lower = doc.lower()
            if any(term in doc_lower for term in ['phone', 'iphone', 'galaxy', 'pixel']):
                categories['Smartphones'] = categories.get('Smartphones', 0) + 1
            elif any(term in doc_lower for term in ['laptop', 'macbook', 'surface']):
                categories['Laptops'] = categories.get('Laptops', 0) + 1
            elif any(term in doc_lower for term in ['tablet', 'ipad']):
                categories['Tablets'] = categories.get('Tablets', 0) + 1
            elif any(term in doc_lower for term in ['airpods', 'headphones', 'earbuds']):
                categories['Audio'] = categories.get('Audio', 0) + 1
            elif any(term in doc_lower for term in ['watch']):
                categories['Wearables'] = categories.get('Wearables', 0) + 1
            else:
                categories['Electronics'] = categories.get('Electronics', 0) + 1
        
        return categories
    
    def _create_fallback_response(self, docs: List[str]) -> str:
        """Simple fallback response"""
        if not docs:
            return self._create_no_documents_response()
        
        doc = docs[0]
        if ':' in doc:
            name, desc = doc.split(':', 1)
            desc = desc.strip()[:100] + "..." if len(desc.strip()) > 100 else desc.strip()
            return f"**{name.strip()}**\n\n{desc}\n\nWould you like to know more?"
        
        return f"I found this product:\n\n{doc[:150]}...\n\nCan I help with anything specific?"
    
    def _create_no_documents_response(self) -> str:
        return """I don't have information about that specific item.

**I can help you with:**
• Smartphones (iPhone, Samsung, Google)
• Laptops (MacBook, Dell, Surface)  
• Tablets (iPad, Android tablets)
• Audio devices (AirPods, headphones)
• Smartwatches

Please ask about one of these categories."""


# Global instance
responder_agent = ResponderAgent()