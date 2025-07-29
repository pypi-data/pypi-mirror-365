"""
OpenAI Provider Adapter for Monkey Coder Core.

This adapter provides integration with OpenAI's API, including GPT models.
All model names are validated against official OpenAI documentation to ensure
accuracy and compliance.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI  # type: ignore
except ImportError:
    AsyncOpenAI = None
    logging.warning("OpenAI package not installed. Install it with: pip install openai")

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider adapter implementing the BaseProvider interface.
    
    Provides access to OpenAI's latest GPT models including GPT-4.1 and GPT-4.1-mini.
    Validates all model names against the official OpenAI API.
    """
    
    # Official OpenAI model names validated against API documentation
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        # GPT-4.1 Models (latest generation)
        "gpt-4.1": {
            "name": "gpt-4.1",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 2.00,  # per 1M tokens
            "output_cost": 8.00,  # per 1M tokens
            "description": "GPT-4.1 - Latest flagship model with extended context",
            "capabilities": ["text", "vision", "function_calling", "reasoning"],
            "version": "4.1",
            "release_date": datetime(2025, 1, 1),
        },
        "gpt-4.1-mini": {
            "name": "gpt-4.1-mini",
            "type": "chat", 
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.12,
            "output_cost": 0.48,
            "description": "GPT-4.1 Mini - Efficient model for fast, lightweight tasks",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "4.1-mini",
            "release_date": datetime(2025, 1, 1),
        },
    }
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url")
        self.organization = kwargs.get("organization")
        self.project = kwargs.get("project")
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        if AsyncOpenAI is None:
            raise ProviderError(
                "OpenAI package not installed. Install it with: pip install openai",
                provider="OpenAI",
                error_code="PACKAGE_NOT_INSTALLED"
            )
        
        try:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
                project=self.project,
            )
            
            # Test the connection
            await self._test_connection()
            logger.info("OpenAI provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise ProviderError(
                f"OpenAI initialization failed: {e}",
                provider="OpenAI",
                error_code="INIT_FAILED"
            )
    
    async def cleanup(self) -> None:
        """Cleanup OpenAI client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("OpenAI provider cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the OpenAI API connection."""
        if not self.client:
            raise ProviderError(
                "OpenAI client not available for testing",
                provider="OpenAI",
                error_code="CLIENT_NOT_INITIALIZED"
            )
        
        try:
            # Simple API call to test connection
            models = await self.client.models.list()  # type: ignore
            if not models.data:
                raise ProviderError(
                    "No models returned from OpenAI API",
                    provider="OpenAI",
                    error_code="NO_MODELS"
                )
        except Exception as e:
            raise ProviderError(
                f"OpenAI API connection test failed: {e}",
                provider="OpenAI", 
                error_code="CONNECTION_FAILED"
            )
    
    async def validate_model(self, model_name: str) -> bool:
        """
        Validate model name against official OpenAI documentation.
        
        This method checks the model name against our curated list of
        officially supported OpenAI models, ensuring accuracy and compliance.
        """
        # Check against our validated models list
        if model_name in self.VALIDATED_MODELS:
            return True
        
        # If client not initialized, we can only check validated models
        if not self.client:
            return False
        
        # For dynamic validation, query the API
        try:
            models = await self.client.models.list()
            api_models = {model.id for model in models.data}
            
            if model_name in api_models:
                logger.info(f"Model {model_name} validated via OpenAI API")
                return True
            
            logger.warning(f"Model {model_name} not found in OpenAI API")
            return False
            
        except Exception as e:
            logger.error(f"Model validation failed for {model_name}: {e}")
            return False
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from OpenAI."""
        models = []
        
        # Use our validated models as the primary source
        for model_name, info in self.VALIDATED_MODELS.items():
            model_info = ModelInfo(
                name=info["name"],
                provider=self.provider_type,
                type=info["type"],
                context_length=info["context_length"],
                input_cost=info["input_cost"] / 1_000_000,  # Convert to per-token cost
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
            )
            models.append(model_info)
        
        return models
    
    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model."""
        if model_name in self.VALIDATED_MODELS:
            info = self.VALIDATED_MODELS[model_name]
            return ModelInfo(
                name=info["name"],
                provider=self.provider_type,
                type=info["type"],
                context_length=info["context_length"],
                input_cost=info["input_cost"] / 1_000_000,
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
            )
        
        # Try to get from API
        if not self.client:
            raise ProviderError(
                "OpenAI client not initialized",
                provider="OpenAI",
                error_code="CLIENT_NOT_INITIALIZED"
            )
        
        try:
            model = await self.client.models.retrieve(model_name)
            return ModelInfo(
                name=model.id,
                provider=self.provider_type,
                type="unknown",
                context_length=0,  # Not provided by API
                input_cost=0.0,    # Not provided by API
                output_cost=0.0,   # Not provided by API
                capabilities=[],
                description=f"OpenAI model {model.id}",
                version=None,
                release_date=None,
            )
        except Exception as e:
            raise ProviderError(
                f"Model {model_name} not found: {e}",
                provider="OpenAI",
                error_code="MODEL_NOT_FOUND"
            )
    
    async def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI's API."""
        if not self.client:
            raise ProviderError(
                "OpenAI client not initialized",
                provider="OpenAI",
                error_code="CLIENT_NOT_INITIALIZED"
            )
        
        try:
            # Validate model first
            if not await self.validate_model(model):
                raise ProviderError(
                    f"Invalid model: {model}",
                    provider="OpenAI",
                    error_code="INVALID_MODEL"
                )
            
            # Prepare parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            # Add tools if provided
            if tools := kwargs.get("tools"):
                params["tools"] = tools
            
            # Add response format if provided  
            if response_format := kwargs.get("response_format"):
                params["response_format"] = response_format
            
            # Make the API call
            start_time = datetime.utcnow()
            response = await self.client.chat.completions.create(**params)
            end_time = datetime.utcnow()
            
            # Calculate metrics
            usage = response.usage
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "openai",
            }
            
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="OpenAI",
                error_code="COMPLETION_FAILED"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on OpenAI provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "OpenAI client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }
        
        try:
            # Test API connectivity
            models = await self.client.models.list()
            
            # Test a simple completion
            test_response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "model_count": len(models.data),
                "test_completion": test_response.choices[0].message.content,
                "last_updated": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
