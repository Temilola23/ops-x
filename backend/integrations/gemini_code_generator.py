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
        
        # Be EXTREMELY specific about what we want
        prompt = f"""You are generating a PRODUCTION Next.js 14 application that will be deployed to a real server and demoed to judges.

PROJECT: {project_name}
USER WANTS: {user_requirements}

CRITICAL: This is for a LIVE DEMO. Everything must actually work. No placeholders, no TODOs, no example data.

Generate a complete, working Next.js 14 app with:

1. REAL FUNCTIONALITY - Every feature the user asked for must work
2. REAL STATE MANAGEMENT - Use React hooks properly (useState, useEffect)
3. REAL API ROUTES - Create working API endpoints with actual logic
4. REAL DATA - If it's a todo app, use UUIDs and real CRUD. If it's an ideas generator, use actual random generation with localStorage
5. BEAUTIFUL UI - Dark theme, modern design, fully responsive
6. ZERO PLACEHOLDERS - No "Example 1", "Sample Task", "Test Item"

REQUIRED FILES (output each one):
- package.json (all needed dependencies)
- app/page.tsx (main page with ALL requested features working)
- app/layout.tsx (root layout, metadata, fonts)
- app/globals.css (Tailwind + custom styles)
- app/api/[...]/route.ts (any API routes needed)
- components/*.tsx (any reusable components)
- tailwind.config.ts
- tsconfig.json
- next.config.js

OUTPUT FORMAT:
For each file, use EXACTLY this format:

===FILE: filename===
[file content here]
===END===

EXAMPLE OUTPUT:
===FILE: package.json===
{{
  "name": "my-app",
  "version": "0.1.0",
  ...
}}
===END===

===FILE: app/page.tsx===
'use client';
import {{ useState }} from 'react';
...
===END===

Now generate the COMPLETE, WORKING application for: {user_requirements}

Remember: This will be run in a LIVE DEMO. Make it impressive and functional, not a template."""

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

