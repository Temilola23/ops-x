"""
JLLM (Janitor AI) Integration
Role-aware AI assistant for team chat rooms
"""

import os
import httpx
from typing import List, Dict, Optional

# JLLM Configuration
JLLM_ENDPOINT = os.getenv("JLLM_API_ENDPOINT", "https://janitorai.com/hackathon/completions")
JLLM_API_KEY = os.getenv("JLLM_API_KEY", "calhacks2047")

class JLLMAgent:
    """JLLM AI assistant for team collaboration"""
    
    def __init__(self):
        self.endpoint = JLLM_ENDPOINT
        self.api_key = JLLM_API_KEY
        self.model = "jllm-v1"  # 25k context
        print(f"JLLM initialized: {self.endpoint}")
    
    async def get_response(
        self,
        message: str,
        chat_history: List[Dict[str, str]] = None,
        project_context: Optional[str] = None,
        team_members: Optional[List[Dict]] = None
    ) -> str:
        """
        Get JLLM response to a message
        
        Args:
            message: User's message
            chat_history: Previous messages [{"role": "user", "content": "..."}]
            project_context: Project description
            team_members: List of team members with roles
        
        Returns:
            JLLM's response text
        """
        # Build context-aware system message
        system_context = self._build_system_context(project_context, team_members)
        
        # Build messages array
        messages = []
        
        # Add system context as first user message (if JLLM doesn't support system role)
        if system_context:
            messages.append({
                "role": "user",
                "content": f"[CONTEXT]\n{system_context}\n[END CONTEXT]"
            })
            messages.append({
                "role": "assistant",
                "content": "I understand the project context and team structure. How can I help?"
            })
        
        # Add chat history
        if chat_history:
            messages.extend(chat_history)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers={
                        "Authorization": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": messages,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"JLLM API error: {response.status_code} - {response.text}")
                    return "I'm having trouble responding right now. Please try again."
                    
        except Exception as e:
            print(f"JLLM error: {str(e)}")
            return "Sorry, I encountered an error. Please try again."
    
    def _build_system_context(
        self,
        project_context: Optional[str],
        team_members: Optional[List[Dict]]
    ) -> str:
        """Build context string for JLLM"""
        context_parts = []
        
        context_parts.append("You are JLLM, an AI assistant helping a software development team collaborate on a startup MVP.")
        context_parts.append("You are role-aware and understand each team member's expertise.")
        
        if project_context:
            context_parts.append(f"\nPROJECT: {project_context}")
        
        if team_members:
            members_str = "\n".join([
                f"- {m['name']} ({m['role']}): {m['email']}"
                for m in team_members
            ])
            context_parts.append(f"\nTEAM MEMBERS:\n{members_str}")
        
        context_parts.append("\nYour job is to:")
        context_parts.append("- Answer questions about the project")
        context_parts.append("- Suggest task assignments based on roles")
        context_parts.append("- Help resolve technical discussions")
        context_parts.append("- Provide guidance on best practices")
        context_parts.append("- Be concise and actionable")
        
        return "\n".join(context_parts)


# Global instance
jllm_agent = JLLMAgent()

