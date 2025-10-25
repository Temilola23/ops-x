"""
Gemini Code Generator - Clean implementation from scratch
Based on official Gemini API docs: https://ai.google.dev/gemini-api/docs/quickstart
"""

import os
import google.generativeai as genai
from typing import Dict, List
import re
import json


class GeminiCodeGenerator:
    """Generate production-ready code using Gemini 2.5 with thinking mode"""
    
    def __init__(self):
        """Initialize Gemini with API key from environment"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash with thinking mode for better reasoning
        # https://ai.google.dev/gemini-api/docs/thinking
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        
        print(f"Initialized Gemini Code Generator with thinking mode")
    
    def generate_nextjs_app(self, project_name: str, user_requirements: str) -> Dict[str, str]:
        """
        Generate a complete, functional Next.js application
        
        Args:
            project_name: Name of the project
            user_requirements: What the user wants to build
            
        Returns:
            Dictionary mapping filename -> file content
        """
        
        # Ultra-specific prompt based on Gemini best practices
        prompt = f"""<ROLE>
You are an expert full-stack developer generating a PRODUCTION Next.js 14 application for immediate deployment and live demo at a hackathon.
</ROLE>

<PROJECT_DETAILS>
Project Name: {project_name}
Requirements: {user_requirements}
</PROJECT_DETAILS>

<CRITICAL_RULES>
This code will be:
1. Git pushed to GitHub in 60 seconds
2. Auto-deployed to Vercel production
3. Demoed LIVE to hackathon judges
4. Used in front of a real audience

THEREFORE:
- NO database setup required (use in-memory arrays or localStorage)
- NO external APIs (unless it's the core feature)
- NO Prisma, no .env files, no Docker
- NO placeholder text like "Example 1", "Sample Task", "Test Data"
- NO comments like "TODO: Add logic here"
- EVERY function must be 100% implemented
- EVERY feature requested must actually work
</CRITICAL_RULES>

<ARCHITECTURE>
Use Next.js 14 App Router with:
- Client components ('use client') for interactivity
- In-memory state or localStorage for data persistence
- API routes ONLY if needed for the specific feature
- Tailwind CSS for styling
- Zero external dependencies beyond: next, react, react-dom, typescript, tailwindcss

Keep it SIMPLE and FUNCTIONAL.
</ARCHITECTURE>

<WHAT_TO_BUILD>
{user_requirements}

If user wants a todo app: Build real CRUD with UUID generation, actual state management
If user wants an idea generator: Build real random generation with clever algorithms
If user wants a dashboard: Build real charts with mock but realistic data
If user wants a game: Build actual game logic that works

Match the vibe they request (dark/gothic/modern/minimal) in the Tailwind classes.
</WHAT_TO_BUILD>

<OUTPUT_FORMAT>
Output ONLY the files, nothing else. Use this EXACT format:

===FILE: filename===
[complete file content - no truncation, no "..."]
===END===

REQUIRED FILES:
1. package.json
2. app/page.tsx (main UI with ALL features working)
3. app/layout.tsx
4. app/globals.css
5. tailwind.config.ts
6. tsconfig.json
7. next.config.js
8. components/[ComponentName].tsx (if needed for organization)
9. app/api/[endpoint]/route.ts (ONLY if needed for the feature)

DO NOT include: .env, prisma/schema.prisma, docker-compose.yml, README.md
</OUTPUT_FORMAT>

<EXAMPLE_GOOD>
For a "gothic noir todo app":

===FILE: app/page.tsx===
'use client';
import {{ useState, useEffect }} from 'react';

interface Todo {{
  id: string;
  text: string;
  done: boolean;
  createdAt: number;
}}

export default function Home() {{
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState('');
  
  useEffect(() => {{
    const saved = localStorage.getItem('todos');
    if (saved) setTodos(JSON.parse(saved));
  }}, []);
  
  const addTodo = () => {{
    if (!input.trim()) return;
    const newTodo = {{
      id: crypto.randomUUID(),
      text: input,
      done: false,
      createdAt: Date.now()
    }};
    const updated = [newTodo, ...todos];
    setTodos(updated);
    localStorage.setItem('todos', JSON.stringify(updated));
    setInput('');
  }};
  
  // ... rest of REAL implementation
}}
===END===
</EXAMPLE_GOOD>

<EXAMPLE_BAD>
DON'T DO THIS:
- const todos = ['Example 1', 'Example 2'];  ❌ HARDCODED
- // TODO: Implement save logic  ❌ NOT IMPLEMENTED
- <div>Placeholder content</div>  ❌ PLACEHOLDER
- Using Prisma without setup  ❌ WON'T WORK
</EXAMPLE_BAD>

Now generate the COMPLETE, WORKING, PRODUCTION-READY app for: {project_name}

Remember: Real demo in 60 seconds. Make it work."""

        try:
            print(f"Generating code for '{project_name}'...")
            print(f"Requirements: {user_requirements[:100]}...")
            
            # Generate content - Gemini will use its thinking mode internally
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Gemini returned empty response")
            
            response_text = response.text
            print(f"Received response: {len(response_text)} characters")
            
            # Parse the files from the response
            files = self._parse_files(response_text)
            
            if not files:
                print("ERROR: No files were parsed from Gemini response")
                print("Response preview:", response_text[:500])
                raise ValueError("Failed to parse any files from Gemini response")
            
            print(f"Successfully parsed {len(files)} files:")
            for filename in files.keys():
                print(f"  - {filename}")
            
            return files
            
        except Exception as e:
            print(f"ERROR generating with Gemini: {e}")
            raise
    
    def _parse_files(self, response_text: str) -> Dict[str, str]:
        """
        Parse files from Gemini response using our specific format
        
        Expected format:
        ===FILE: filename===
        content
        ===END===
        """
        files = {}
        
        # Pattern to match our file format
        pattern = r'===FILE:\s*([^\n]+)\s*===\n(.*?)\n===END==='
        matches = re.findall(pattern, response_text, re.DOTALL)
        
        if matches:
            for filename, content in matches:
                filename = filename.strip()
                content = content.strip()
                files[filename] = content
            return files
        
        # Fallback: Try to find code blocks
        print("Primary parsing failed, trying fallback...")
        
        # Look for markdown code blocks
        code_block_pattern = r'```(?:\w+)?\n(.*?)```'
        code_blocks = re.findall(code_block_pattern, response_text, re.DOTALL)
        
        # Look for common Next.js files in the text
        common_files = [
            'package.json',
            'app/page.tsx',
            'app/layout.tsx',
            'app/globals.css',
            'tailwind.config.ts',
            'tsconfig.json',
            'next.config.js'
        ]
        
        for filename in common_files:
            # Try to find content for this file
            file_pattern = rf'{filename}.*?```(?:\w+)?\n(.*?)```'
            match = re.search(file_pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                files[filename] = match.group(1).strip()
        
        return files


# Singleton instance - will be initialized when API key is available
try:
    gemini_code_generator = GeminiCodeGenerator()
except ValueError:
    # API key not set yet - will be initialized on first use
    gemini_code_generator = None

