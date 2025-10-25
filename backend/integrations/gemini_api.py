"""
Google Gemini API Integration
Generates complete applications from prompts
"""

import os
import google.generativeai as genai
from typing import Dict, List

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiCodeGenerator:
    """Generate complete application code using Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def generate_app(self, prompt: str, project_name: str) -> Dict[str, str]:
        """
        Generate a complete Next.js application from a prompt
        
        Returns: Dict of filename -> content
        """
        
        system_prompt = f"""You are an expert full-stack developer. Generate a COMPLETE, FUNCTIONAL Next.js 14 application.

Project Name: {project_name}

CRITICAL REQUIREMENTS:
1. Build ACTUAL WORKING FEATURES - not just static placeholder text
2. Create interactive UI with state management (useState, React hooks)
3. Add actual functionality - forms, buttons that work, data that changes
4. Use Next.js 14 App Router with TypeScript
5. Beautiful styling with Tailwind CSS
6. Create separate components in /components folder
7. Add API routes in /app/api if needed for backend
8. Make it production-ready and impressive

RESPONSE FORMAT:
Return each file in this EXACT format:

---FILE: app/page.tsx---
[content here]
---END FILE---

---FILE: app/layout.tsx---
[content here]
---END FILE---

---FILE: components/Feature.tsx---
[content here]
---END FILE---

And so on for ALL files needed.

REQUIRED FILES:
- app/page.tsx (main interactive page)
- app/layout.tsx
- components/[FeatureComponents].tsx (actual working components)
- app/api/[endpoint]/route.ts (if backend needed)
- package.json
- tailwind.config.ts
- tsconfig.json
- README.md"""

        full_prompt = f"""{system_prompt}

USER REQUEST:
{prompt}

Generate a FULLY FUNCTIONAL app that actually WORKS with real features!"""
        
        try:
            generation_config = {
                "temperature": 0.7,
                "max_output_tokens": 8000,
            }
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Parse the response using FILE markers
            response_text = response.text.strip()
            
            import re
            
            # Extract files using ---FILE: filename--- markers
            files = {}
            pattern = r'---FILE:\s*([^\n]+?)---\n(.*?)\n---END FILE---'
            matches = re.findall(pattern, response_text, re.DOTALL)
            
            if matches:
                print(f"Found {len(matches)} files from Gemini")
                for filename, content in matches:
                    filename = filename.strip()
                    content = content.strip()
                    files[filename] = content
                    print(f"  - {filename}")
                return files
            else:
                print("No files found with FILE markers, trying fallback parsing")
                # Try alternative parsing methods
                return self._extract_files_from_text(response.text)
            
        except Exception as e:
            print(f"Gemini generation error: {str(e)}")
            # Fallback to minimal Next.js template
            return self._get_minimal_template(project_name, prompt)
    
    def _extract_files_from_text(self, text: str) -> Dict[str, str]:
        """
        Extract file contents from Gemini response even if JSON parsing fails
        Looks for file markers and extracts content
        """
        import re
        
        files = {}
        
        # Try to find file blocks in various formats
        # Format 1: "filename": "content"
        pattern1 = r'"([^"]+\.(?:tsx|ts|js|jsx|json|css|md))"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
        matches = re.findall(pattern1, text, re.DOTALL)
        
        for filename, content in matches:
            # Unescape the content
            content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            files[filename] = content
        
        # Format 2: File: filename\n```content```
        pattern2 = r'File:\s*([^\n]+)\n```(?:typescript|javascript|tsx|jsx|css|json)?\n(.*?)\n```'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        
        for filename, content in matches2:
            files[filename.strip()] = content.strip()
        
        return files if files else {}
    
    def _get_minimal_template(self, project_name: str, description: str) -> Dict[str, str]:
        """Fallback minimal Next.js template"""
        
        return {
            "package.json": f'''{{
  "name": "{project_name.lower().replace(' ', '-')}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }},
  "dependencies": {{
    "next": "14.0.4",
    "react": "^18",
    "react-dom": "^18"
  }},
  "devDependencies": {{
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }}
}}''',
            "app/layout.tsx": '''import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'OPS-X Generated App',
  description: 'Built with OPS-X Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}''',
            "app/page.tsx": f'''export default function Home() {{
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">{project_name}</h1>
        <p className="text-xl mb-8">{description}</p>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Welcome!</h2>
          <p>This is your MVP generated by OPS-X. Start collaborating with your team!</p>
        </div>
      </div>
    </main>
  )
}}''',
            "app/globals.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-start-rgb: 0, 0, 0;
    --background-end-rgb: 0, 0, 0;
  }
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}''',
            "tailwind.config.ts": '''import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
export default config''',
            "tsconfig.json": '''{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}''',
            "next.config.js": '''/** @type {import('next').NextConfig} */
const nextConfig = {}

module.exports = nextConfig''',
            "postcss.config.js": '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''',
            ".gitignore": '''# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts''',
            "README.md": f'''# {project_name}

{description}

## Generated by OPS-X

This project was generated using the OPS-X one-prompt startup platform.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.
''',
            ".env.example": '''# Add your environment variables here
NEXT_PUBLIC_API_URL=http://localhost:8000
'''
        }


# Singleton instance
gemini_generator = GeminiCodeGenerator() if GEMINI_API_KEY else None
