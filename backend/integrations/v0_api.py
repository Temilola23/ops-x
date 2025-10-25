"""
V0 API Integration - Beautiful UI Generation
Uses V0's Model API for React/Next.js component generation
"""

import os
import httpx
from typing import Dict, List, Optional
import json


class V0Generator:
    """V0 API client for generating React/Next.js UI components"""
    
    def __init__(self):
        self.api_key = os.getenv("V0_API_KEY", "")
        self.base_url = "https://api.v0.dev/v1"
        
        if not self.api_key:
            print(" V0_API_KEY not found - V0 features disabled")
    
    async def generate_ui_component(
        self,
        prompt: str,
        component_name: str = "Component",
        framework: str = "nextjs"
    ) -> Optional[Dict[str, str]]:
        """
        Generate a single UI component with V0 using the Model API
        
        Based on V0 API docs: https://v0.app/docs/api/model
        """
        if not self.api_key:
            return None
        
        try:
            # V0 Model API endpoint - correct path
            url = f"{self.base_url}/chat/completions"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "v0",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 4096
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # V0 uses OpenAI format - extract from choices
                    choices = data.get("choices", [])
                    if choices and len(choices) > 0:
                        content = choices[0].get("message", {}).get("content", "")
                        if content:
                            # Remove thinking tags if present
                            import re
                            # Remove <Thinking>...</Thinking> blocks
                            content = re.sub(r'<Thinking>.*?</Thinking>', '', content, flags=re.DOTALL)
                            # Extract code from markdown blocks if present
                            code_match = re.search(r'```(?:tsx|typescript|jsx|javascript)?\n(.*?)```', content, re.DOTALL)
                            if code_match:
                                content = code_match.group(1).strip()
                            
                            return {
                                "filename": f"components/{component_name}.tsx",
                                "content": content,
                                "preview_url": "",  # V0 doesn't return preview URL in this format
                            }
                    print("V0 API returned no content")
                    return None
                else:
                    print(f"V0 API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"V0 API exception: {e}")
            return None
    
    async def generate_full_app(
        self,
        prompt: str,
        project_name: str,
        pages: List[str]
    ) -> Dict[str, str]:
        """
        Generate a complete Next.js app with multiple pages
        
        Args:
            prompt: Full app description
            project_name: Name of the project
            pages: List of page names to generate
        
        Returns:
            Dict mapping filenames to code content
        """
        if not self.api_key:
            return {}
        
        files = {}
        
        # Generate main page
        main_page_prompt = f"""
        Create the main landing page for {project_name}.
        Requirements: {prompt}
        Use shadcn/ui components, Tailwind CSS, and Lucide icons.
        Make it modern, responsive, and visually appealing.
        """
        
        main_page = await self.generate_ui_component(
            prompt=main_page_prompt,
            component_name="page",
        )
        
        if main_page:
            files["src/app/page.tsx"] = main_page["content"]
        
        # Generate additional pages
        for page_name in pages:
            if page_name.lower() != "home":
                page_prompt = f"""
                Create the {page_name} page for {project_name}.
                Requirements: {prompt}
                Use shadcn/ui components, Tailwind CSS, and Lucide icons.
                """
                
                page_component = await self.generate_ui_component(
                    prompt=page_prompt,
                    component_name=page_name.lower(),
                )
                
                if page_component:
                    files[f"src/app/{page_name.lower()}/page.tsx"] = page_component["content"]
        
        # Add standard Next.js files
        files.update(self._generate_standard_files(project_name))
        
        return files
    
    def _generate_standard_files(self, project_name: str) -> Dict[str, str]:
        """Generate standard Next.js configuration files"""
        
        return {
            "package.json": json.dumps({
                "name": project_name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint"
                },
                "dependencies": {
                    "react": "^18.3.0",
                    "react-dom": "^18.3.0",
                    "next": "^14.2.0",
                    "@radix-ui/react-slot": "^1.0.2",
                    "class-variance-authority": "^0.7.0",
                    "clsx": "^2.1.0",
                    "lucide-react": "^0.344.0",
                    "tailwind-merge": "^2.2.0",
                    "tailwindcss-animate": "^1.0.7"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "@types/node": "^20.0.0",
                    "@types/react": "^18.3.0",
                    "@types/react-dom": "^18.3.0",
                    "autoprefixer": "^10.4.0",
                    "postcss": "^8.4.0",
                    "tailwindcss": "^3.4.0",
                    "eslint": "^8.0.0",
                    "eslint-config-next": "^14.2.0"
                }
            }, indent=2),
            
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2017",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "paths": {
                        "@/*": ["./src/*"]
                    }
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"]
            }, indent=2),
            
            "tailwind.config.ts": """
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
""",
            
            "src/app/globals.css": """
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
""",
            
            "src/app/layout.tsx": f"""
import type {{ Metadata }} from "next";
import {{ Inter }} from "next/font/google";
import "./globals.css";

const inter = Inter({{ subsets: ["latin"] }});

export const metadata: Metadata = {{
  title: "{project_name}",
  description: "Generated by OPS-X",
}};

export default function RootLayout({{
  children,
}}: Readonly<{{
  children: React.ReactNode;
}}>) {{
  return (
    <html lang="en">
      <body className={{inter.className}}>{{children}}</body>
    </html>
  );
}}
""",
            
            ".gitignore": """
# dependencies
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
next-env.d.ts
""",
            
            "README.md": f"""# {project_name}

Generated by OPS-X - One-Prompt Startup Platform

## Getting Started

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your app.

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components

## Generated with AI

This project was generated using:
- V0 (UI components)
- Google Gemini (backend logic)
- GitHub (version control)
- Vercel (deployment)
"""
        }


# Global instance
v0_generator = V0Generator() if os.getenv("V0_API_KEY") else None

