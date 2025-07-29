"""
Mock pricing module for development.
"""
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class PricingMiddleware(BaseHTTPMiddleware):
    """Mock pricing middleware."""
    
    def __init__(self, app, enabled=True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response

def load_pricing_from_file():
    """Mock pricing loader."""
    logger.info("Pricing data loading skipped for development")
    return None
