"""
Model pricing data and management.

This module handles pricing information for different AI models,
including fetching updated pricing data and calculating costs.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelPricing(BaseModel):
    """
    Pricing information for an AI model.
    """
    model_id: str = Field(..., description="Model identifier")
    provider: str = Field(..., description="Provider name")
    
    # Pricing per token (in USD)
    input_cost_per_token: float = Field(..., description="Cost per input token")
    output_cost_per_token: float = Field(..., description="Cost per output token")
    
    # Additional pricing info
    context_length: int = Field(default=4096, description="Maximum context length")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Tuple[float, float, float]:
        """
        Calculate costs for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Tuple[float, float, float]: (input_cost, output_cost, total_cost)
        """
        input_cost = input_tokens * self.input_cost_per_token
        output_cost = output_tokens * self.output_cost_per_token
        total_cost = input_cost + output_cost
        
        return input_cost, output_cost, total_cost


# Current pricing data (updated nightly)
# Prices are per 1 token (not per 1K tokens) for easier calculation
MODEL_PRICING_DATA: Dict[str, ModelPricing] = {
    # OpenAI Models
    "gpt-4o": ModelPricing(
        model_id="gpt-4o",
        provider="openai",
        input_cost_per_token=0.0000025,   # $2.50 per 1M input tokens
        output_cost_per_token=0.00001,    # $10.00 per 1M output tokens
        context_length=128000
    ),
    "gpt-4o-mini": ModelPricing(
        model_id="gpt-4o-mini", 
        provider="openai",
        input_cost_per_token=0.00000015,  # $0.15 per 1M input tokens
        output_cost_per_token=0.0000006,  # $0.60 per 1M output tokens
        context_length=128000
    ),
    "gpt-4-turbo": ModelPricing(
        model_id="gpt-4-turbo",
        provider="openai", 
        input_cost_per_token=0.00001,     # $10.00 per 1M input tokens
        output_cost_per_token=0.00003,    # $30.00 per 1M output tokens
        context_length=128000
    ),
    "gpt-4": ModelPricing(
        model_id="gpt-4",
        provider="openai",
        input_cost_per_token=0.00003,     # $30.00 per 1M input tokens
        output_cost_per_token=0.00006,    # $60.00 per 1M output tokens
        context_length=8192
    ),
    "gpt-3.5-turbo": ModelPricing(
        model_id="gpt-3.5-turbo",
        provider="openai",
        input_cost_per_token=0.0000005,   # $0.50 per 1M input tokens
        output_cost_per_token=0.0000015,  # $1.50 per 1M output tokens
        context_length=16385
    ),
    "o1-preview": ModelPricing(
        model_id="o1-preview",
        provider="openai",
        input_cost_per_token=0.000015,    # $15.00 per 1M input tokens  
        output_cost_per_token=0.00006,    # $60.00 per 1M output tokens
        context_length=128000
    ),
    "o1-mini": ModelPricing(
        model_id="o1-mini",
        provider="openai",
        input_cost_per_token=0.000003,    # $3.00 per 1M input tokens
        output_cost_per_token=0.000012,   # $12.00 per 1M output tokens
        context_length=128000
    ),
    
    # Anthropic Models
    "claude-3-5-sonnet-20241022": ModelPricing(
        model_id="claude-3-5-sonnet-20241022",
        provider="anthropic",
        input_cost_per_token=0.000003,    # $3.00 per 1M input tokens
        output_cost_per_token=0.000015,   # $15.00 per 1M output tokens
        context_length=200000
    ),
    "claude-3-5-haiku-20241022": ModelPricing(
        model_id="claude-3-5-haiku-20241022",
        provider="anthropic",
        input_cost_per_token=0.0000008,   # $0.80 per 1M input tokens
        output_cost_per_token=0.000004,   # $4.00 per 1M output tokens
        context_length=200000
    ),
    "claude-3-opus-20240229": ModelPricing(
        model_id="claude-3-opus-20240229",
        provider="anthropic",
        input_cost_per_token=0.000015,    # $15.00 per 1M input tokens
        output_cost_per_token=0.000075,   # $75.00 per 1M output tokens
        context_length=200000
    ),
    "claude-3-sonnet-20240229": ModelPricing(
        model_id="claude-3-sonnet-20240229",
        provider="anthropic",
        input_cost_per_token=0.000003,    # $3.00 per 1M input tokens
        output_cost_per_token=0.000015,   # $15.00 per 1M output tokens
        context_length=200000
    ),
    "claude-3-haiku-20240307": ModelPricing(
        model_id="claude-3-haiku-20240307",
        provider="anthropic",
        input_cost_per_token=0.00000025,  # $0.25 per 1M input tokens
        output_cost_per_token=0.00000125, # $1.25 per 1M output tokens
        context_length=200000
    ),
    
    # Google Models
    "gemini-2.0-flash-exp": ModelPricing(
        model_id="gemini-2.0-flash-exp",
        provider="google",
        input_cost_per_token=0.0000000375,  # $0.0375 per 1M input tokens (experimental pricing)
        output_cost_per_token=0.00000015,   # $0.15 per 1M output tokens
        context_length=1048576
    ),
    "gemini-1.5-pro": ModelPricing(
        model_id="gemini-1.5-pro",
        provider="google",
        input_cost_per_token=0.00000125,  # $1.25 per 1M input tokens
        output_cost_per_token=0.000005,   # $5.00 per 1M output tokens
        context_length=2097152
    ),
    "gemini-1.5-flash": ModelPricing(
        model_id="gemini-1.5-flash",
        provider="google",
        input_cost_per_token=0.000000075, # $0.075 per 1M input tokens
        output_cost_per_token=0.0000003,  # $0.30 per 1M output tokens
        context_length=1048576
    ),
    "gemini-1.0-pro": ModelPricing(
        model_id="gemini-1.0-pro",
        provider="google",
        input_cost_per_token=0.0000005,   # $0.50 per 1M input tokens
        output_cost_per_token=0.0000015,  # $1.50 per 1M output tokens
        context_length=32768
    ),
    
    # Qwen Models (estimated pricing - adjust based on actual costs)
    "qwen2.5-coder-32b-instruct": ModelPricing(
        model_id="qwen2.5-coder-32b-instruct",
        provider="qwen",
        input_cost_per_token=0.000002,    # Estimated $2.00 per 1M input tokens
        output_cost_per_token=0.000008,   # Estimated $8.00 per 1M output tokens
        context_length=32768
    ),
    "qwen2.5-coder-14b-instruct": ModelPricing(
        model_id="qwen2.5-coder-14b-instruct",
        provider="qwen",
        input_cost_per_token=0.0000015,   # Estimated $1.50 per 1M input tokens
        output_cost_per_token=0.000006,   # Estimated $6.00 per 1M output tokens
        context_length=32768
    ),
    "qwen2.5-coder-7b-instruct": ModelPricing(
        model_id="qwen2.5-coder-7b-instruct",
        provider="qwen",
        input_cost_per_token=0.000001,    # Estimated $1.00 per 1M input tokens
        output_cost_per_token=0.000004,   # Estimated $4.00 per 1M output tokens
        context_length=32768
    ),
    "qwen2.5-coder-1.5b-instruct": ModelPricing(
        model_id="qwen2.5-coder-1.5b-instruct",
        provider="qwen",
        input_cost_per_token=0.0000005,   # Estimated $0.50 per 1M input tokens
        output_cost_per_token=0.000002,   # Estimated $2.00 per 1M output tokens
        context_length=32768
    ),
    "qwen2.5-coder-0.5b-instruct": ModelPricing(
        model_id="qwen2.5-coder-0.5b-instruct",
        provider="qwen",
        input_cost_per_token=0.0000002,   # Estimated $0.20 per 1M input tokens
        output_cost_per_token=0.0000008,  # Estimated $0.80 per 1M output tokens
        context_length=32768
    ),
}


def get_model_pricing(model_id: str) -> Optional[ModelPricing]:
    """
    Get pricing information for a model.
    
    Args:
        model_id: Model identifier
        
    Returns:
        Optional[ModelPricing]: Pricing info if available
    """
    return MODEL_PRICING_DATA.get(model_id)


async def update_pricing_data(force_update: bool = False) -> bool:
    """
    Update pricing data from external sources.
    
    This function fetches updated pricing information and updates
    the in-memory pricing data. It's designed to be called nightly
    via a cron job.
    
    Args:
        force_update: Force update even if data is recent
        
    Returns:
        bool: True if update was successful
    """
    try:
        # Check if we need to update
        pricing_file = "pricing_data.json"
        should_update = force_update
        
        if not should_update:
            try:
                stat = os.stat(pricing_file)
                last_update = datetime.fromtimestamp(stat.st_mtime)
                should_update = datetime.now() - last_update > timedelta(hours=12)
            except (OSError, FileNotFoundError):
                should_update = True
        
        if not should_update:
            logger.debug("Pricing data is recent, skipping update") 
            return True
        
        logger.info("Updating pricing data from external sources")
        
        # In a real implementation, you would fetch from APIs like:
        # - OpenAI pricing API
        # - Anthropic pricing information
        # - Google Cloud Vertex AI pricing
        # For now, we'll use static data but demonstrate the structure
        
        updated_pricing = {}
        
        # Example: Fetch OpenAI pricing (pseudo-code)
        try:
            # This would be a real API call in production
            openai_pricing = await _fetch_openai_pricing()
            updated_pricing.update(openai_pricing)
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAI pricing: {e}")
        
        # Example: Fetch Anthropic pricing
        try:
            anthropic_pricing = await _fetch_anthropic_pricing()
            updated_pricing.update(anthropic_pricing)  
        except Exception as e:
            logger.warning(f"Failed to fetch Anthropic pricing: {e}")
        
        # Example: Fetch Google pricing
        try:
            google_pricing = await _fetch_google_pricing()
            updated_pricing.update(google_pricing)
        except Exception as e:
            logger.warning(f"Failed to fetch Google pricing: {e}")
        
        # Save updated pricing to file
        if updated_pricing:
            with open(pricing_file, 'w') as f:
                pricing_dict = {}
                for model_id, pricing in updated_pricing.items():
                    pricing_dict[model_id] = pricing.dict()
                json.dump(pricing_dict, f, indent=2, default=str)
            
            # Update in-memory data
            MODEL_PRICING_DATA.update(updated_pricing)
            logger.info(f"Updated pricing for {len(updated_pricing)} models")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update pricing data: {e}")
        return False


async def _fetch_openai_pricing() -> Dict[str, ModelPricing]:
    """
    Fetch OpenAI pricing information.
    
    In production, this would call OpenAI's pricing API or scrape
    their pricing page for the latest rates.
    """
    # This is a placeholder implementation
    # In reality, you'd fetch from OpenAI's API or pricing page
    
    # For now, return empty dict to keep existing pricing
    return {}


async def _fetch_anthropic_pricing() -> Dict[str, ModelPricing]:
    """
    Fetch Anthropic pricing information.
    
    In production, this would fetch from Anthropic's pricing information.
    """
    # Placeholder implementation
    return {}


async def _fetch_google_pricing() -> Dict[str, ModelPricing]:
    """
    Fetch Google Cloud Vertex AI pricing information.
    
    In production, this would fetch from Google Cloud's pricing API.
    """
    # Placeholder implementation
    return {}


def load_pricing_from_file() -> None:
    """
    Load pricing data from file if available.
    
    This is called on startup to load any updated pricing data
    that was fetched by the nightly cron job.
    """
    try:
        with open("pricing_data.json", 'r') as f:
            pricing_dict = json.load(f)
            
        for model_id, pricing_data in pricing_dict.items():
            if isinstance(pricing_data.get('last_updated'), str):
                pricing_data['last_updated'] = datetime.fromisoformat(pricing_data['last_updated'])
            
            MODEL_PRICING_DATA[model_id] = ModelPricing(**pricing_data)
        
        logger.info(f"Loaded pricing data for {len(pricing_dict)} models from file")
        
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        logger.debug(f"Could not load pricing from file: {e}")
        # Use default pricing data
