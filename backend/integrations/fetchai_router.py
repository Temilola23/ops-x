"""
Fetch.ai Intelligent Model Router
Analyzes refinement requests and routes to the best AI model
"""

import os
from typing import Dict, Literal
import re

# Fetch.ai configuration
FETCHAI_API_KEY = os.getenv("FETCHAI_API_KEY")

# For now, using rule-based routing (can integrate actual Fetch.ai agent later)
print("Fetch.ai router initialized")


class FetchAIRouter:
    """Intelligent AI model selection based on request analysis"""
    
    def __init__(self):
        self.ui_keywords = [
            "ui", "design", "component", "button", "layout", "style", "color",
            "hero", "landing", "page", "modal", "dialog", "navbar", "footer",
            "responsive", "mobile", "gradient", "animation", "transition"
        ]
        
        self.backend_keywords = [
            "api", "endpoint", "database", "auth", "authentication", "jwt",
            "query", "schema", "model", "validation", "middleware", "route",
            "crud", "rest", "graphql", "sql", "postgres", "orm"
        ]
        
        self.general_keywords = [
            "refactor", "optimize", "improve", "fix", "update", "modify",
            "rename", "restructure", "clean", "organize"
        ]
    
    def route_refinement(
        self,
        request_text: str,
        stakeholder_role: str,
        ai_model_preference: str = "auto"
    ) -> Dict[str, any]:
        """
        Determine which AI model should handle the refinement
        
        Args:
            request_text: The refinement request
            stakeholder_role: User's role (Frontend, Backend, etc.)
            ai_model_preference: User's model preference or "auto"
        
        Returns:
            {
                "model": "v0" | "claude" | "gemini",
                "confidence": 0.0-1.0,
                "reasoning": str
            }
        """
        # If user specified a preference, honor it
        if ai_model_preference in ["v0", "claude", "gemini"]:
            return {
                "model": ai_model_preference,
                "confidence": 1.0,
                "reasoning": f"User explicitly selected {ai_model_preference}"
            }
        
        # Analyze request content
        request_lower = request_text.lower()
        
        # Count keyword matches
        ui_score = sum(1 for kw in self.ui_keywords if kw in request_lower)
        backend_score = sum(1 for kw in self.backend_keywords if kw in request_lower)
        general_score = sum(1 for kw in self.general_keywords if kw in request_lower)
        
        # Role-based defaults
        role_default = {
            "Frontend": "v0",
            "Backend": "claude",
            "Founder": "v0",  # UI-first
            "Investor": "gemini",  # General improvements
            "Facilitator": "gemini"
        }.get(stakeholder_role, "gemini")
        
        # Decision logic
        if ui_score > backend_score and ui_score > 0:
            # Clear UI request
            return {
                "model": "v0",
                "confidence": min(0.7 + (ui_score * 0.1), 1.0),
                "reasoning": f"UI-focused request (detected {ui_score} UI keywords)"
            }
        elif backend_score > ui_score and backend_score > 0:
            # Clear backend request
            return {
                "model": "claude",
                "confidence": min(0.7 + (backend_score * 0.1), 1.0),
                "reasoning": f"Backend-focused request (detected {backend_score} backend keywords)"
            }
        elif general_score > 0:
            # General improvement
            return {
                "model": "gemini",
                "confidence": 0.6,
                "reasoning": "General refactoring request, using Gemini for broad changes"
            }
        else:
            # Fall back to role default
            return {
                "model": role_default,
                "confidence": 0.5,
                "reasoning": f"Using role default ({role_default}) for {stakeholder_role}"
            }
    
    def should_use_document_analysis(self, has_documents: bool) -> bool:
        """
        Determine if Claude should be used for document analysis
        Claude excels at extracting requirements from docs
        """
        return has_documents  # Always use Claude for doc analysis


# Global instance
fetchai_router = FetchAIRouter()

