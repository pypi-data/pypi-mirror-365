"""Model factory module for creating LLM and embedding instances."""

from .factory import LLMFactory, EmbeddingFactory, get_available_providers

# Unified factory interface
class ModelFactory:
    """Unified factory for creating both LLM and embedding models."""
    
    @classmethod
    def create_llm(cls, provider: str, model: str, config: dict, **kwargs):
        """Create an LLM instance."""
        return LLMFactory.create_llm(provider, model, config, **kwargs)
    
    @classmethod
    def create_embeddings(cls, provider: str, model: str, config: dict, **kwargs):
        """Create an embeddings instance."""
        return EmbeddingFactory.create_embeddings(provider, model, config, **kwargs)
    
    @classmethod
    def get_available_providers(cls):
        """Get information about available providers."""
        return get_available_providers()


__all__ = [
    "ModelFactory",
    "LLMFactory", 
    "EmbeddingFactory",
    "get_available_providers",
]