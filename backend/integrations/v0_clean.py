"""
PURE V0 Integration - Clean implementation based on official docs
https://v0.app/docs/api/model

V0 is framework-aware, has auto-fix, and generates production-ready Next.js code.
NO Gemini. NO Prisma. JUST V0.
"""

import os
import httpx
from typing import Dict, List, Optional
import json
import re


class V0CleanGenerator:
    """Pure V0 code generator using official V0 Model API"""
    
    def __init__(self):
        self.api_key = os.getenv("V0_API_KEY", "")
        self.base_url = "https://api.v0.dev/v1"
        
        # Use v0-1.5-md for everyday UI generation (as per docs)
        self.model = "v0-1.5-md"
        
        if not self.api_key:
            raise ValueError("V0_API_KEY not found in environment")
        
        print(f"Initialized V0 Clean Generator with model: {self.model}")
    
    async def generate_full_app(
        self,
        project_name: str,
        user_requirements: str,
        pages: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate a complete Next.js app using ONLY V0
        
        Args:
            project_name: Name of the project
            user_requirements: What the user wants to build
            pages: Optional list of pages to generate
            
        Returns:
            Dictionary mapping filename -> file content
        """
        
        if pages is None:
            pages = ["Home", "Dashboard"]
        
        # Craft V0-specific prompt based on their docs
        # V0 is framework-aware and optimized for Next.js
        prompt = f"""Create a complete, SELF-CONTAINED, production-ready Next.js 14 application called "{project_name}".

USER REQUIREMENTS: {user_requirements}

PAGES TO INCLUDE: {", ".join(pages)}

CRITICAL RULES:
- ALL code must be COMPLETE and SELF-CONTAINED in each file
- NO references to components that don't exist in the response
- If you need an additional component, DEFINE IT in the same file
- Use ONLY standard Tailwind classes
- Include ALL imports at the top of each file
- EVERY component must be fully functional standalone

TECHNICAL REQUIREMENTS:
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS for styling
- shadcn/ui components if needed
- Fully responsive design
- NO database setup (use localStorage or in-memory state)
- NO external APIs unless explicitly requested
- ZERO placeholders or dummy data

WHAT I NEED:
Generate ALL necessary files for a working Next.js app:
1. package.json with dependencies
2. app/page.tsx - Main page with full functionality
3. app/layout.tsx - Root layout
4. app/globals.css - Tailwind styles
5. components/*.tsx - Any reusable components
6. tailwind.config.ts
7. tsconfig.json
8. next.config.js
9. Any additional pages for: {", ".join(pages)}

Make it beautiful, functional, and ready to deploy immediately to Vercel.

Output the complete code for each file."""

        try:
            print(f"Generating full app with V0 for '{project_name}'...")
            print(f"Using model: {self.model}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "stream": False,  # Non-streaming for simplicity
                        "max_completion_tokens": 16000  # Plenty for a full app
                    }
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    print(f"V0 API error ({response.status_code}): {error_text}")
                    raise Exception(f"V0 API error: {error_text}")
                
                result = response.json()
                
                # Extract content from OpenAI-compatible response
                content = result["choices"][0]["message"]["content"]
                
                print(f"V0 response length: {len(content)} characters")
                
                # Parse files from V0's response
                files = self._parse_v0_response(content)
                
                if not files:
                    print("WARNING: No files parsed from V0 response")
                    print("Response preview:", content[:500])
                    raise Exception("Failed to parse files from V0 response")
                
                print(f"Successfully parsed {len(files)} files from V0:")
                for filename in files.keys():
                    print(f"  ✓ {filename}")
                
                return files
        
        except httpx.TimeoutException:
            print("V0 request timed out")
            raise Exception("V0 request timed out after 120 seconds")
        except Exception as e:
            print(f"V0 generation error: {e}")
            raise
    
    def _parse_v0_response(self, content: str) -> Dict[str, str]:
        """
        Parse files from V0's response
        
        V0 typically returns code in markdown blocks with filenames
        """
        files = {}
        
        # Method 1: Look for ```language file="path/to/file.ext"
        file_pattern = r'```[\w]+\s+file="([^"]+)"\n(.*?)```'
        matches = re.findall(file_pattern, content, re.DOTALL)
        
        for filename, code in matches:
            files[filename] = code.strip()
        
        # Method 2: Look for standard markdown blocks with filename comments
        # ```typescript
        # // app/page.tsx
        if not files:
            blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
            for block in blocks:
                # Try to extract filename from comment
                filename_match = re.search(r'^(?://|#)\s*([^\n]+\.(?:tsx?|jsx?|json|css|js|ts))', block, re.MULTILINE)
                if filename_match:
                    filename = filename_match.group(1).strip()
                    files[filename] = block.strip()
        
        # Method 3: If V0 structured it differently, look for common Next.js files
        if not files or len(files) < 3:
            # Ensure we have at least the core files
            files.update(self._extract_core_nextjs_files(content))
        
        return files
    
    def _extract_core_nextjs_files(self, content: str) -> Dict[str, str]:
        """
        Extract core Next.js files from V0 response using pattern matching
        """
        files = {}
        
        # Common Next.js files to look for
        patterns = {
            "package.json": r'{\s*"name":\s*"[^"]+",\s*"version":\s*"[^"]+"[^}]*"dependencies"[^}]*}',
            "app/page.tsx": r"export default function (?:Home|Page)\(\)[^{]*{[\s\S]+?^}",
            "app/layout.tsx": r"export default function (?:RootLayout|Layout)\([^)]*\)[^{]*{[\s\S]+?^}",
            "tailwind.config.ts": r"(?:export default|module\.exports\s*=)\s*{[^}]*content:[^}]*}",
            "tsconfig.json": r'{\s*"compilerOptions":[^}]*}',
        }
        
        for filename, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                files[filename] = match.group(0).strip()
        
        return files
    
    async def generate_streaming(
        self,
        project_name: str,
        user_requirements: str,
        stream_callback
    ):
        """
        Generate app with streaming progress updates
        
        Yields chunks of generated code as they arrive
        """
        
        prompt = f"""Create a production-ready Next.js 14 app called "{project_name}".

Requirements: {user_requirements}

Generate a complete, working app with:
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- Full functionality (no placeholders)
- Beautiful, responsive UI

Output all necessary files."""

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True
                    }
                ) as response:
                    accumulated = ""
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    accumulated += content
                                    # Call callback with progress
                                    await stream_callback(content, accumulated)
                            
                            except json.JSONDecodeError:
                                continue
                    
                    # Parse final result
                    return self._parse_v0_response(accumulated)
        
        except Exception as e:
            print(f"V0 streaming error: {e}")
            raise


# Singleton instance
try:
    v0_clean_generator = V0CleanGenerator()
except ValueError as e:
    print(f"V0 initialization skipped: {e}")
    v0_clean_generator = None

