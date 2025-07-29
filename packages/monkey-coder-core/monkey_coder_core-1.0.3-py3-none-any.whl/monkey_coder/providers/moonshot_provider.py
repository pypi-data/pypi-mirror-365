"""
Moonshot AI Provider for Monkey Coder
Supports Kimi K2 models via Moonshot API
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
import logging
import aiohttp
import json
from .base_provider import BaseAIProvider, AIModel, AIResponse, StreamingResponse

logger = logging.getLogger(__name__)

class MoonshotProvider(BaseAIProvider):
    """Moonshot AI provider for Kimi K2 models."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        if not self.api_key:
            raise ValueError("MOONSHOT_API_KEY is required")
        
        self.base_url = "https://api.moonshot.cn/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Moonshot-available models  
        self.models = {
            "moonshot-v1-8k": AIModel(
                id="moonshot-v1-8k",
                name="Kimi K2 8K",
                provider="moonshot",
                context_window=8192,
                max_tokens=4096,
                supports_streaming=True,
                cost_per_1k_tokens=0.012
            ),
            "moonshot-v1-32k": AIModel(
                id="moonshot-v1-32k", 
                name="Kimi K2 32K",
                provider="moonshot",
                context_window=32768,
                max_tokens=16384,
                supports_streaming=True,
                cost_per_1k_tokens=0.024
            ),
            "moonshot-v1-128k": AIModel(
                id="moonshot-v1-128k",
                name="Kimi K2 128K",
                provider="moonshot",
                context_window=131072,
                max_tokens=65536,
                supports_streaming=True,
                cost_per_1k_tokens=0.06
            )
        }
    
    def get_provider_name(self) -> str:
        return "moonshot"
    
    def get_available_models(self) -> List[AIModel]:
        return list(self.models.values())
    
    def validate_model(self, model_id: str) -> bool:
        return model_id in self.models
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "moonshot-v1-8k",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AIResponse:
        """Generate a response using Moonshot API."""
        
        if not self.validate_model(model_id):
            raise ValueError(f"Model {model_id} not supported by Moonshot provider")
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    return AIResponse(
                        content=data["choices"][0]["message"]["content"],
                        model=model_id,
                        provider="moonshot",
                        tokens_used=data.get("usage", {}).get("total_tokens", 0),
                        cost_estimate=self._calculate_cost(model_id, data.get("usage", {}).get("total_tokens", 0)),
                        metadata={
                            "finish_reason": data["choices"][0]["finish_reason"],
                            "usage": data.get("usage", {})
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Moonshot API error: {e}")
            raise
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "moonshot-v1-8k",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Generate a streaming response using Moonshot API."""
        
        if not self.validate_model(model_id):
            raise ValueError(f"Model {model_id} not supported by Moonshot provider")
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            if data_str == '[DONE]':
                                break
                            
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0]["delta"]
                                if "content" in delta and delta["content"]:
                                    yield StreamingResponse(
                                        content=delta["content"],
                                        model=model_id,
                                        provider="moonshot",
                                        is_complete=data["choices"][0].get("finish_reason") is not None,
                                        metadata={
                                            "finish_reason": data["choices"][0].get("finish_reason")
                                        }
                                    )
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Moonshot streaming API error: {e}")
            raise
    
    def _calculate_cost(self, model_id: str, tokens: int) -> float:
        """Calculate cost based on model and token usage."""
        if model_id in self.models:
            return (tokens / 1000) * self.models[model_id].cost_per_1k_tokens
        return 0.0
