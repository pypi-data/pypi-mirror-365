"""
PersonaRouter module for SuperClaude slash-command & persona integration.

This module provides the interface between the main application and the 
AdvancedRouter system, focusing on persona-based routing decisions.
"""

import logging
from typing import Dict, Any

from .routing import AdvancedRouter, RoutingDecision
from ..models import ExecuteRequest, PersonaType

logger = logging.getLogger(__name__)


class PersonaRouter:
    """
    Persona-focused router interface for SuperClaude integration.
    
    This class wraps the AdvancedRouter to provide persona-specific 
    routing functionality with SuperClaude slash-command support.
    """
    
    def __init__(self):
        self.advanced_router = AdvancedRouter()
        logger.info("PersonaRouter initialized with AdvancedRouter")
    
    async def route_request(self, request: ExecuteRequest) -> Dict[str, Any]:
        """
        Route request through advanced routing system.
        
        Args:
            request: The execution request to route
            
        Returns:
            Dictionary containing persona context and routing information
        """
        logger.info(f"Routing request through persona system: {request.task_type}")
        
        # Use AdvancedRouter for sophisticated routing decision
        routing_decision = self.advanced_router.route_request(request)
        
        # Create persona context for downstream systems
        persona_context = {
            "selected_persona": routing_decision.persona,
            "provider": routing_decision.provider,
            "model": routing_decision.model,
            "confidence": routing_decision.confidence,
            "reasoning": routing_decision.reasoning,
            "complexity_analysis": {
                "complexity_score": routing_decision.complexity_score,
                "context_score": routing_decision.context_score,
                "capability_score": routing_decision.capability_score,
            },
            "routing_metadata": routing_decision.metadata,
        }
        
        logger.info(
            f"Persona routing complete: {routing_decision.persona.value} "
            f"via {routing_decision.provider.value}/{routing_decision.model}"
        )
        
        return persona_context
    
    def get_available_personas(self) -> Dict[str, Any]:
        """Get information about available personas."""
        return {
            "personas": [persona.value for persona in PersonaType],
            "slash_commands": self.advanced_router.slash_commands,
            "persona_mappings": self.advanced_router.persona_mappings,
        }
    
    def get_routing_debug_info(self, request: ExecuteRequest) -> Dict[str, Any]:
        """Get detailed debug information for routing decision."""
        return self.advanced_router.get_routing_debug_info(request)
