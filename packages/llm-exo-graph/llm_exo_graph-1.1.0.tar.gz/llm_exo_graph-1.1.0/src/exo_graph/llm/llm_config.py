"""
LLM Configuration classes for Knowledge Graph Engine v2
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from openai import OpenAI


class LLMConfig(ABC):
    @property
    def provider(self) -> str:
        return "unknown"
    """Abstract base class for LLM configurations"""
    
    @abstractmethod
    def create_client(self) -> OpenAI:
        """Create and return the OpenAI-compatible client"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name to use"""
        pass
    

@dataclass
class OpenAIConfig(LLMConfig):
    """Configuration for OpenAI API"""
    api_key: str
    model: str = "gpt-4o"
    base_url: Optional[str] = None
    organization: Optional[str] = None

    @property
    def provider(self) -> str:
        return "openai"

    def create_client(self) -> OpenAI:
        """Create OpenAI client with standard API key authentication"""
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.organization:
            kwargs["organization"] = self.organization
        return OpenAI(**kwargs)
    
    def get_model_name(self) -> str:
        return self.model
    

@dataclass
class OllamaConfig(LLMConfig):
    """Configuration for Ollama local LLM"""
    model: str = "phi3:3.8b"
    base_url: str = "http://localhost:11434/v1"

    @property
    def provider(self) -> str:
        return "ollama"

    def create_client(self) -> OpenAI:
        """Create OpenAI-compatible client for Ollama"""
        return OpenAI(
            api_key="ollama",  # Ollama doesn't need a real API key
            base_url=self.base_url
        )
    
    def get_model_name(self) -> str:
        return self.model
    


@dataclass
class LiteLLMConfig(LLMConfig):
    """Configuration for LiteLLM with bearer token authentication"""
    bearer_token: str
    model: str
    base_url: str
    additional_headers: Optional[Dict[str, str]] = None

    @property
    def provider(self) -> str:
        return "litellm"

    def create_client(self) -> OpenAI:
        """Create OpenAI-compatible client with bearer token authentication"""
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        if self.additional_headers:
            headers.update(self.additional_headers)
        
        return OpenAI(
            api_key="dummy",  # LiteLLM uses bearer token instead
            base_url=self.base_url,
            default_headers=headers
        )
    
    def get_model_name(self) -> str:
        return self.model
