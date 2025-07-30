"""
Factory for creating LLM configurations based on environment parameters
"""
import os
from typing import Optional
from .llm_config import LLMConfig, OpenAIConfig, OllamaConfig, LiteLLMConfig


class LLMClientFactory:
    """Factory class for creating LLM configurations based on environment variables"""
    
    @staticmethod
    def create_from_env() -> LLMConfig:
        """
        Create LLM configuration from environment variables.
        
        Checks for the following patterns:
        1. LLM_PROVIDER environment variable (openai, ollama, litellm)
        2. Presence of specific environment variables
        3. Default to OpenAI if OPENAI_API_KEY is set
        
        Returns:
            LLMConfig: Appropriate configuration instance
            
        Raises:
            ValueError: If no valid configuration can be determined
        """
        # Check explicit provider setting
        provider = os.getenv("LLM_PROVIDER", "").lower()
        
        if provider == "litellm":
            return LLMClientFactory._create_litellm_config()
        elif provider == "ollama":
            return LLMClientFactory._create_ollama_config()
        elif provider == "openai":
            return LLMClientFactory._create_openai_config()
        
        # Auto-detect based on environment variables
        if os.getenv("LITELLM_BEARER_TOKEN"):
            return LLMClientFactory._create_litellm_config()
        elif os.getenv("OPENAI_API_KEY") == "ollama" or os.getenv("OLLAMA_BASE_URL"):
            return LLMClientFactory._create_ollama_config()
        elif os.getenv("OPENAI_API_KEY"):
            return LLMClientFactory._create_openai_config()
        
        raise ValueError(
            "No valid LLM configuration found. Set one of: "
            "OPENAI_API_KEY, OLLAMA_BASE_URL, or LITELLM_BEARER_TOKEN"
        )
    
    @staticmethod
    def _create_openai_config() -> OpenAIConfig:
        """Create OpenAI configuration from environment"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        return OpenAIConfig(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            organization=os.getenv("OPENAI_ORGANIZATION")
        )
    
    @staticmethod
    def _create_ollama_config() -> OllamaConfig:
        """Create Ollama configuration from environment"""
        model= os.getenv("OLLAMA_MODEL")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        if not model:
            raise ValueError("OLLAMA_MODEL environment variable is not set")

        return OllamaConfig(
            model=model,
            base_url=base_url
        )
    
    @staticmethod
    def _create_litellm_config() -> LiteLLMConfig:
        """Create LiteLLM configuration from environment"""
        bearer_token = os.getenv("LITELLM_BEARER_TOKEN")
        if not bearer_token:
            raise ValueError("LITELLM_BEARER_TOKEN environment variable is not set")
        
        base_url = os.getenv("LITELLM_BASE_URL", os.getenv("LLM_BASE_URL"))
        if not base_url:
            raise ValueError("LITELLM_BASE_URL or LLM_BASE_URL environment variable is not set")
        
        model = os.getenv("LITELLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o"))
        
        # Parse additional headers if provided
        additional_headers = None
        headers_str = os.getenv("LITELLM_ADDITIONAL_HEADERS")
        if headers_str:
            try:
                import json
                additional_headers = json.loads(headers_str)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse LITELLM_ADDITIONAL_HEADERS: {headers_str}")
        
        return LiteLLMConfig(
            bearer_token=bearer_token,
            model=model,
            base_url=base_url,
            additional_headers=additional_headers
        )
    
    @staticmethod
    def create_from_params(
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        provider: Optional[str] = None
    ) -> LLMConfig:
        """
        Create LLM configuration from explicit parameters.
        
        Args:
            api_key: API key for OpenAI or "ollama" for Ollama
            model: Model name to use
            base_url: Base URL for the API
            bearer_token: Bearer token for LiteLLM
            provider: Explicit provider name (openai, ollama, litellm)
            
        Returns:
            LLMConfig: Appropriate configuration instance
        """
        # Explicit provider
        if provider:
            if provider.lower() == "litellm" and bearer_token:
                return LiteLLMConfig(
                    bearer_token=bearer_token,
                    model=model or "gpt-4o",
                    base_url=base_url or os.getenv("LITELLM_BASE_URL", "")
                )
            elif provider.lower() == "ollama":
                return OllamaConfig(
                    model=model or "llama3.2:3b",
                    base_url=base_url or "http://localhost:11434/v1"
                )
            elif provider.lower() == "openai" and api_key:
                return OpenAIConfig(
                    api_key=api_key,
                    model=model or "gpt-4o",
                    base_url=base_url
                )
        
        # Auto-detect based on parameters
        if bearer_token and base_url:
            return LiteLLMConfig(
                bearer_token=bearer_token,
                model=model or "gpt-4o",
                base_url=base_url
            )
        elif api_key == "ollama":
            return OllamaConfig(
                model=model or "llama3.2:3b",
                base_url=base_url or "http://localhost:11434/v1"
            )
        elif api_key:
            return OpenAIConfig(
                api_key=api_key,
                model=model or "gpt-4o",
                base_url=base_url
            )
        
        # Fall back to environment variables
        return LLMClientFactory.create_from_env()