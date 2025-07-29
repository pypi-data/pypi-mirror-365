"""OpenAI LLM provider implementation.

This module provides the OpenAI-specific implementation for language models,
supporting all OpenAI chat models including GPT-4 and GPT-3.5 variants.
"""

from typing import TYPE_CHECKING, Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAILLMProvider(BaseProvider):
    """OpenAI LLM provider implementation.
    
    Supports all OpenAI chat models with customizable parameters
    including temperature, max tokens, and organization settings.
    """

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the OpenAI provider.
        
        Args:
            provider_config: OpenAI-specific configuration
            model_name: Name of the OpenAI model to use (e.g., 'gpt-4')
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> "ChatOpenAI":
        """Create the OpenAI chat model instance.
        
        Returns:
            Configured ChatOpenAI instance
            
        Raises:
            ConfigurationError: If OpenAI provider is not available
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationError(
                "OpenAI provider not available. Install: uv add langchain-openai"
            )

        # Extract common parameters with defaults from config
        temperature = self.kwargs.get('temperature', self.config.temperature)
        max_tokens = self.kwargs.get('max_tokens', self.config.max_tokens)

        # Build model configuration (exact same as main branch)
        model_config = {
            'model': self.model_name,
            'api_key': self.config.api_key,
            'base_url': self.config.base_url,
            'organization': self.config.organization,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'timeout': self.config.timeout,
        }

        # Add additional kwargs, excluding already handled ones (same pattern as main branch)
        additional_kwargs = {k: v for k, v in self.kwargs.items() if k not in ['temperature', 'max_tokens']}
        model_config.update(additional_kwargs)

        return ChatOpenAI(**model_config)
    
    def is_available(self) -> bool:
        """Check if OpenAI provider is available (module installed + API key).
        
        Returns:
            True if OpenAI is available and has API key
        """
        return OPENAI_AVAILABLE and bool(self.config.api_key)
    
    async def is_available_async(self) -> bool:
        """Test real OpenAI API connectivity using configured model.
        
        Tests the actual configured model to detect when models are deprecated.
        
        Returns:
            True if OpenAI API is reachable with configured model
        """
        if not self.is_available():
            return False
            
        try:
            # Test with the actual configured model
            test_model = ChatOpenAI(
                model=self.model_name,  # Use configured model
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                organization=self.config.organization,
                timeout=5,  # Short timeout for health check
                max_tokens=1
            )
            
            # Send minimal test message
            response = await test_model.ainvoke([{"role": "user", "content": "hi"}])
            return bool(response and response.content)
            
        except Exception:
            return False
