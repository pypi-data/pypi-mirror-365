"""Base classes and protocols for LLM and embedding providers.

This module defines the base abstractions and protocols that all provider
implementations must follow, ensuring consistency across different providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class LLMProviderProtocol(Protocol):
    """Protocol defining the interface for LLM providers.
    
    All LLM providers must implement these methods to ensure
    compatibility with the factory system.
    """

    def invoke(self, messages: list[Any]) -> Any:
        """Invoke the LLM with messages.
        
        Args:
            messages: List of message objects to send to the LLM
            
        Returns:
            The LLM's response
        """
        ...

    def stream(self, messages: list[Any]) -> Any:
        """Stream responses from the LLM.
        
        Args:
            messages: List of message objects to send to the LLM
            
        Returns:
            An iterator of response chunks
        """
        ...


class EmbeddingProviderProtocol(Protocol):
    """Protocol defining the interface for embedding providers.
    
    All embedding providers must implement these methods to ensure
    compatibility with the factory system.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents.
        
        Args:
            texts: List of text documents to embed
            
        Returns:
            List of embedding vectors
        """
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector for the query
        """
        ...


class BaseProvider(ABC):
    """Base class for all provider implementations.
    
    This class provides common functionality for all providers including
    lazy loading of models and configuration management.
    """

    def __init__(self, config: Any):
        """Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration object
        """
        self.config = config
        self._model = None

    @abstractmethod
    def _create_model(self) -> Any:
        """Create the actual model instance.
        
        This method must be implemented by all concrete providers
        to instantiate their specific model.
        
        Returns:
            The configured model instance
        """
        pass

    @property
    def model(self) -> Any:
        """Get or create the model instance using lazy loading.
        
        The model is created on first access to avoid unnecessary
        initialization overhead.
        
        Returns:
            The model instance
        """
        if self._model is None:
            self._model = self._create_model()
        return self._model

    def is_available(self) -> bool:
        """Check if the provider is available.
        
        Can be overridden by specific providers to implement
        custom availability checks.
        
        Returns:
            True if the provider is available
        """
        return True
    
    async def is_available_async(self) -> bool:
        """Async version of availability check for real API testing.
        
        Can be overridden by specific providers to implement
        real connectivity checks.
        
        Returns:
            True if the provider is available and responsive
        """
        return self.is_available()
