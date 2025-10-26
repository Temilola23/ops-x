"""
Claude API Integration - Backend code generation specialist
Using Anthropic's Claude for backend logic, APIs, and databases
"""

import os
import anthropic
from typing import Dict, List, Optional

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

if CLAUDE_API_KEY:
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    print("Claude API initialized successfully")
else:
    claude_client = None
    print("WARNING: CLAUDE_API_KEY not set, Claude agent disabled")


class ClaudeBackendAgent:
    """Claude-powered backend code generation"""
    
    def __init__(self):
        self.client = claude_client
        self.model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet
    
    def generate_backend_code(
        self,
        refinement_request: str,
        current_files: Dict[str, str],
        project_context: str,
        allowed_files: List[str]
    ) -> Dict[str, str]:
        """
        Generate backend code changes based on refinement request
        
        Args:
            refinement_request: What the user wants to change
            current_files: Dict of {file_path: content} of BACKEND files only
            project_context: Project description and requirements
            allowed_files: List of file paths this user can edit
        
        Returns:
            Dict of {file_path: new_content} with changes
        """
        if not self.client:
            raise ValueError("Claude API not configured")
        
        # Build the prompt
        system_prompt = """You are a senior backend engineer specializing in FastAPI, PostgreSQL, and API design.

You are helping refine an existing codebase. Your job is to:
1. Understand the refinement request
2. Only modify backend-related files (APIs, database, server config)
3. Generate COMPLETE file contents (not diffs)
4. Ensure all changes are production-ready
5. Maintain existing code style and structure

CRITICAL RULES:
- Only edit files in the allowed_files list
- Generate complete file contents, not partial changes
- Test your logic mentally - no placeholder code
- Preserve imports and existing functionality
- Add proper error handling
- Follow REST API best practices

Return your response in this exact format:
---FILE: path/to/file.py---
[complete file content here]
---END FILE---

---FILE: path/to/another_file.py---
[complete file content here]
---END FILE---
"""
        
        # Build context about current files
        files_context = "\n\n".join([
            f"---CURRENT FILE: {path}---\n{content}\n---END CURRENT FILE---"
            for path, content in current_files.items()
        ])
        
        user_prompt = f"""PROJECT CONTEXT:
{project_context}

CURRENT BACKEND FILES:
{files_context}

ALLOWED FILES TO EDIT:
{', '.join(allowed_files)}

REFINEMENT REQUEST:
{refinement_request}

Generate the modified backend code. Only include files that need changes.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse response
            content = response.content[0].text
            modified_files = self._parse_files(content)
            
            print(f"Claude generated {len(modified_files)} file(s)")
            return modified_files
            
        except Exception as e:
            print(f"Claude API error: {str(e)}")
            raise
    
    def _parse_files(self, content: str) -> Dict[str, str]:
        """Parse files from Claude's response"""
        files = {}
        
        # Split by file markers
        parts = content.split("---FILE: ")
        
        for part in parts[1:]:  # Skip first empty part
            if "---" in part:
                # Extract filename and content
                lines = part.split("\n", 1)
                if len(lines) == 2:
                    filename = lines[0].replace("---", "").strip()
                    file_content = lines[1].split("---END FILE---")[0].strip()
                    files[filename] = file_content
        
        return files


# Global instance
claude_agent = ClaudeBackendAgent() if CLAUDE_API_KEY else None

