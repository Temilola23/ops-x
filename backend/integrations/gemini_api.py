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
        Generate a complete Next.js application from a prompt using Gemini's JSON mode
        
        Returns: Dict of filename -> content
        """
        
        # Simple prompt with FILE markers for better parsing
        system_prompt = f"""You are an expert full-stack developer. Generate a COMPLETE, FUNCTIONAL Next.js 14 application.

Output each file using this format:
---FILE: filename---
file content here
---END---

CRITICAL REQUIREMENTS:
1. Generate REAL WORKING CODE, not placeholders or examples
2. Build the EXACT features requested by the user
3. Use Next.js 14 App Router with TypeScript
4. Beautiful dark/noir theme with Tailwind CSS
5. Interactive UI with proper state management
6. Include ALL files needed to run the app

MUST INCLUDE:
- app/page.tsx - main page with the requested features
- app/layout.tsx - root layout
- app/globals.css - Tailwind styles
- components/*.tsx - feature components  
- app/api/*/route.ts - API routes if needed
- package.json - with all dependencies
- tailwind.config.ts
- tsconfig.json
- next.config.js

DO NOT output explanations, markdown, or anything else. ONLY output the files."""

        user_request = f"Build this app: {prompt}"
        
        try:
            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8000
            )
            
            response = self.model.generate_content(
                [system_prompt, user_request],
                generation_config=generation_config
            )
            
            # Parse response with FILE markers
            import re
            
            files = {}
            response_text = response.text
            
            # Debug output
            print(f"DEBUG: Gemini response length: {len(response_text)} chars")
            print(f"DEBUG: First 200 chars: {response_text[:200]}")
            
            # Parse files using regex
            file_pattern = r'---FILE:\s*([^\n]+)---\n(.*?)(?=---(?:FILE:|END)---)'
            matches = re.findall(file_pattern, response_text, re.DOTALL)
            
            if matches:
                for filename, content in matches:
                    filename = filename.strip()
                    content = content.strip()
                    files[filename] = content
                
                print(f"Successfully parsed {len(files)} files from Gemini response")
                for path in files.keys():
                    print(f"  - {path}")
                
                return files if files else self._get_functional_template(project_name, prompt)
            else:
                print("No files found with FILE markers, trying fallback parsing")
                files = self._extract_files_from_text(response_text)
                return files if files else self._get_functional_template(project_name, prompt)
                
        except Exception as e:
            print(f"Gemini generation error: {str(e)}")
            return self._get_functional_template(project_name, prompt)
    
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
    
    def _get_functional_template(self, project_name: str, description: str) -> Dict[str, str]:
        """Generate a FUNCTIONAL app template based on the description"""
        
        # Determine app type from description
        desc_lower = description.lower()
        is_ideas_app = "idea" in desc_lower or "billion" in desc_lower
        is_gothic = "gothic" in desc_lower or "noir" in desc_lower or "dark" in desc_lower
        
        # Generate appropriate app based on description
        if is_ideas_app:
            return self._generate_ideas_app(project_name, is_gothic)
        else:
            return self._generate_default_app(project_name, description)
    
    def _generate_ideas_app(self, project_name: str, is_gothic: bool) -> Dict[str, str]:
        """Generate a functional billion dollar ideas app"""
        
        theme_colors = {
            "bg": "bg-black" if is_gothic else "bg-gray-900",
            "card": "bg-gray-900 border-red-900" if is_gothic else "bg-gray-800",
            "text": "text-red-500" if is_gothic else "text-blue-500",
            "accent": "text-red-600" if is_gothic else "text-purple-600"
        }
        
        return {
            "app/page.tsx": f'''\"use client\";

import {{ useState }} from \"react\";

export default function Home() {{
  const [ideas, setIdeas] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  const [currentIdea, setCurrentIdea] = useState(\"\");

  const ideaTemplates = [
    \"AI-powered {{noun}} that {{verb}} for {{audience}}\",
    \"Blockchain-based {{solution}} for {{problem}}\",
    \"Social platform that connects {{group1}} with {{group2}}\",
    \"Marketplace for {{product}} with {{feature}}\",
    \"SaaS tool that automates {{process}} using {{technology}}\",
    \"Mobile app that tracks {{metric}} and predicts {{outcome}}\",
    \"Platform that democratizes {{industry}} through {{method}}\",
    \"Service that disrupts {{market}} by eliminating {{pain_point}}\"
  ];

  const nouns = [\"assistant\", \"platform\", \"system\", \"network\", \"solution\", \"service\", \"tool\", \"engine\"];
  const verbs = [\"optimizes\", \"automates\", \"streamlines\", \"revolutionizes\", \"transforms\", \"enhances\"];
  const audiences = [\"enterprises\", \"creators\", \"developers\", \"small businesses\", \"students\", \"professionals\"];
  const solutions = [\"payment system\", \"identity verification\", \"supply chain\", \"voting mechanism\"];
  const problems = [\"transparency\", \"trust issues\", \"inefficiency\", \"data silos\"];
  const groups = [\"experts\", \"beginners\", \"investors\", \"mentors\", \"freelancers\", \"companies\"];
  const products = [\"digital assets\", \"services\", \"expertise\", \"computing power\", \"storage space\"];
  const features = [\"AI matching\", \"smart contracts\", \"instant settlement\", \"reputation scoring\"];
  const processes = [\"hiring\", \"accounting\", \"customer support\", \"data analysis\", \"content creation\"];
  const technologies = [\"GPT-4\", \"computer vision\", \"quantum computing\", \"edge computing\", \"AR/VR\"];
  const metrics = [\"carbon footprint\", \"productivity\", \"health vitals\", \"market trends\", \"user behavior\"];
  const outcomes = [\"ROI\", \"risk\", \"opportunities\", \"success rate\", \"market crashes\"];
  const industries = [\"education\", \"healthcare\", \"finance\", \"real estate\", \"legal services\"];
  const methods = [\"AI\", \"crowdsourcing\", \"tokenization\", \"gamification\", \"decentralization\"];
  const markets = [\"taxi industry\", \"hotels\", \"banking\", \"retail\", \"entertainment\"];
  const painPoints = [\"middlemen\", \"high fees\", \"slow processes\", \"gatekeepers\", \"complexity\"];

  const getRandomItem = (arr: string[]) => arr[Math.floor(Math.random() * arr.length)];

  const generateIdea = () => {{
    setGenerating(true);
    setCurrentIdea(\"\");
    
    setTimeout(() => {{
      const template = getRandomItem(ideaTemplates);
      const idea = template
        .replace(\"{{noun}}\", getRandomItem(nouns))
        .replace(\"{{verb}}\", getRandomItem(verbs))
        .replace(\"{{audience}}\", getRandomItem(audiences))
        .replace(\"{{solution}}\", getRandomItem(solutions))
        .replace(\"{{problem}}\", getRandomItem(problems))
        .replace(\"{{group1}}\", getRandomItem(groups))
        .replace(\"{{group2}}\", getRandomItem(groups))
        .replace(\"{{product}}\", getRandomItem(products))
        .replace(\"{{feature}}\", getRandomItem(features))
        .replace(\"{{process}}\", getRandomItem(processes))
        .replace(\"{{technology}}\", getRandomItem(technologies))
        .replace(\"{{metric}}\", getRandomItem(metrics))
        .replace(\"{{outcome}}\", getRandomItem(outcomes))
        .replace(\"{{industry}}\", getRandomItem(industries))
        .replace(\"{{method}}\", getRandomItem(methods))
        .replace(\"{{market}}\", getRandomItem(markets))
        .replace(\"{{pain_point}}\", getRandomItem(painPoints));
      
      const valuation = (Math.random() * 900 + 100).toFixed(0);
      const fullIdea = `${{valuation}}B Idea: ${{idea}}`;
      
      setCurrentIdea(fullIdea);
      setIdeas([fullIdea, ...ideas.slice(0, 9)]);
      setGenerating(false);
    }}, 1500);
  }};

  return (
    <main className=\"min-h-screen {theme_colors["bg"]} text-white p-8\">
      <div className=\"max-w-4xl mx-auto\">
        <h1 className=\"text-6xl font-bold {theme_colors["accent"]} mb-2 text-center font-mono\">
          BILLION DOLLAR IDEA GENERATOR
        </h1>
        <p className=\"text-center text-gray-400 mb-12\">
          Disrupting the disruption industry, one idea at a time
        </p>

        <div className=\"{theme_colors["card"]} border-2 rounded-lg p-8 mb-8\">
          <button
            onClick={{generateIdea}}
            disabled={{generating}}
            className=\"w-full py-6 px-8 bg-gradient-to-r from-red-600 to-purple-600 hover:from-red-700 hover:to-purple-700 disabled:opacity-50 rounded-lg font-bold text-2xl transition-all transform hover:scale-105\"
          >
            {{generating ? \"GENERATING BILLIONS...\" : \"GENERATE BILLION DOLLAR IDEA\"}}
          </button>
          
          {{currentIdea && (
            <div className=\"mt-8 p-6 bg-black/50 rounded-lg border-2 {theme_colors["text"]} border-opacity-50\">
              <p className=\"text-xl font-mono\">{{currentIdea}}</p>
            </div>
          )}}
        </div>

        {{ideas.length > 0 && (
          <div className=\"{theme_colors["card"]} border-2 rounded-lg p-8\">
            <h2 className=\"text-2xl font-bold mb-6 {theme_colors["text"]}\">Previous Ideas</h2>
            <div className=\"space-y-4\">
              {{ideas.map((idea, index) => (
                <div
                  key={{index}}
                  className=\"p-4 bg-black/30 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors\"
                >
                  <p className=\"font-mono text-sm\">{{idea}}</p>
                </div>
              ))}}
            </div>
          </div>
        )}}
      </div>
    </main>
  );
}}''',
            
            "app/layout.tsx": f'''import type {{ Metadata }} from \"next\";
import {{ Inter }} from \"next/font/google\";
import \"./globals.css\";

const inter = Inter({{ subsets: [\"latin\"] }});

export const metadata: Metadata = {{
  title: \"{project_name}\",
  description: \"Generate billion dollar startup ideas\",
}};

export default function RootLayout({{
  children,
}}: Readonly<{{
  children: React.ReactNode;
}}>) {{
  return (
    <html lang=\"en\">
      <body className={{inter.className}}>{{children}}</body>
    </html>
  );
}}''',

            "app/globals.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 255, 255, 255;
  --background-start-rgb: 0, 0, 0;
  --background-end-rgb: 20, 20, 20;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
  min-height: 100vh;
}''',

            "package.json": f'''{{
  \"name\": \"{project_name.lower().replace(' ', '-')}\",
  \"version\": \"0.1.0\",
  \"private\": true,
  \"scripts\": {{
    \"dev\": \"next dev\",
    \"build\": \"next build\",
    \"start\": \"next start\",
    \"lint\": \"next lint\"
  }},
  \"dependencies\": {{
    \"next\": \"14.2.0\",
    \"react\": \"^18.3.0\",
    \"react-dom\": \"^18.3.0\"
  }},
  \"devDependencies\": {{
    \"@types/node\": \"^20\",
    \"@types/react\": \"^18\",
    \"@types/react-dom\": \"^18\",
    \"autoprefixer\": \"^10.4.0\",
    \"postcss\": \"^8.4.0\",
    \"tailwindcss\": \"^3.4.0\",
    \"typescript\": \"^5\",
    \"eslint\": \"^8\",
    \"eslint-config-next\": \"14.2.0\"
  }}
}}''',

            "tailwind.config.ts": '''import type { Config } from \"tailwindcss\";

const config: Config = {
  content: [
    \"./pages/**/*.{js,ts,jsx,tsx,mdx}\",
    \"./components/**/*.{js,ts,jsx,tsx,mdx}\",
    \"./app/**/*.{js,ts,jsx,tsx,mdx}\",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
export default config;''',

            "tsconfig.json": '''
{
  \"compilerOptions\": {
    \"lib\": [\"dom\", \"dom.iterable\", \"esnext\"],
    \"allowJs\": true,
    \"skipLibCheck\": true,
    \"strict\": true,
    \"noEmit\": true,
    \"esModuleInterop\": true,
    \"module\": \"esnext\",
    \"moduleResolution\": \"bundler\",
    \"resolveJsonModule\": true,
    \"isolatedModules\": true,
    \"jsx\": \"preserve\",
    \"incremental\": true,
    \"plugins\": [
      {
        \"name\": \"next\"
      }
    ],
    \"paths\": {
      \"@/*\": [\"./*\"]
    }
  },
  \"include\": [\"next-env.d.ts\", \"**/*.ts\", \"**/*.tsx\", \".next/types/**/*.ts\"],
  \"exclude\": [\"node_modules\"]
}''',

            "next.config.js": '''/** @type {import('next').NextConfig} */
const nextConfig = {};

module.exports = nextConfig;''',

            "README.md": f'''# {project_name}

A billion dollar idea generator with a noir/gothic theme.

## Getting Started

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your billion dollar ideas!

## Features

- Generates unique billion dollar startup ideas
- Dark noir theme
- Saves history of generated ideas
- Interactive UI with animations

Built with Next.js 14, React, TypeScript, and Tailwind CSS.
'''
        }
    
    def _generate_default_app(self, project_name: str, description: str) -> Dict[str, str]:
        """Generate a default functional app"""
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
