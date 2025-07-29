"""
Groq AI Provider for Monkey Coder
Supports Qwen and Kimi models via Groq API
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
import logging
from groq import AsyncGroq, Groq
from .base_provider import BaseAIProvider, AIModel, AIResponse, StreamingResponse

logger = logging.getLogger(__name__)

class GroqProvider(BaseAIProvider):
    """Groq AI provider for Qwen and Kimi models."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        self.client = AsyncGroq(api_key=self.api_key)
        self.sync_client = Groq(api_key=self.api_key)
        
        # Groq-available models
        self.models = {
            "llama-3.3-70b-versatile": AIModel(
                id="llama-3.3-70b-versatile",
                name="Llama 3.3 70B",
                provider="groq",
                context_window=131072,
                max_tokens=8192,
                supports_streaming=True,
                cost_per_1k_tokens=0.00059
            ),
            "qwen2.5-72b-instruct": AIModel(
                id="qwen2.5-72b-instruct",
                name="Qwen 2.5 72B Instruct",
                provider="groq",
                context_window=32768,
                max_tokens=8192,
                supports_streaming=True,
                cost_per_1k_tokens=0.0009
            ),
            "mixtral-8x7b-32768": AIModel(
                id="mixtral-8x7b-32768",
                name="Mixtral 8x7B",
                provider="groq",
                context_window=32768,
                max_tokens=32768,
                supports_streaming=True,
                cost_per_1k_tokens=0.0002
            )
        }
    
    def get_provider_name(self) -> str:
        return "groq"
    
    def get_available_models(self) -> List[AIModel]:
        return list(self.models.values())
    
    def validate_model(self, model_id: str) -> bool:
        return model_id in self.models
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "qwen2.5-72b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AIResponse:
        """Generate a response using Groq API."""
        
        if not self.validate_model(model_id):
            raise ValueError(f"Model {model_id} not supported by Groq provider")
        
        try:
            response = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=model_id,
                provider="groq",
                tokens_used=response.usage.total_tokens if response.usage else 0,
                cost_estimate=self._calculate_cost(model_id, response.usage.total_tokens if response.usage else 0),
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": response.usage.dict() if response.usage else None
                }
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "qwen2.5-72b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Generate a streaming response using Groq API."""
        
        if not self.validate_model(model_id):
            raise ValueError(f"Model {model_id} not supported by Groq provider")
        
        try:
            stream = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield StreamingResponse(
                        content=chunk.choices[0].delta.content,
                        model=model_id,
                        provider="groq",
                        is_complete=chunk.choices[0].finish_reason is not None,
                        metadata={
                            "finish_reason": chunk.choices[0].finish_reason
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Groq streaming API error: {e}")
            raise
    
    def _calculate_cost(self, model_id: str, tokens: int) -> float:
        """Calculate cost based on model and token usage."""
        if model_id in self.models:
            return (tokens / 1000) * self.models[model_id].cost_per_1k_tokens
        return 0.0
