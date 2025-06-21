from typing import List


class TemplateSelector:
    
    @staticmethod
    def select_template(query: str, retrieved_docs: List[str]) -> str:
        return "simple"


class PromptBuilder:
    
    @staticmethod
    def build_context(documents: List[str]) -> str:
        if not documents:
            return "No products available."
        
        context = ""
        for i, doc in enumerate(documents[:3], 1):  # Max 3 docs
            clean_doc = doc.strip()[:200]  # Limit length
            context += f"{i}. {clean_doc}\n\n"
        return context.strip()   
