#!/usr/bin/env python3
"""Create .env file with all API keys"""

env_content = """# OPS-X Environment Variables

# API Keys
CREAO_INVITATION_CODE=CALHAC
GITHUB_TOKEN=your_github_token_here
POSTMAN_API_KEY=your_postman_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Janitor AI
JANITOR_API_ENDPOINT=https://janitorai.com/hackathon/completions
JANITOR_API_KEY=calhacks2047

# Fetch.ai
FETCHAI_API_KEY=sk_f1565b8c1c934a7ab641446e5b1f4159fb14f45afe964224b90e7f6cfedd55a5
FETCHAI_ENDPOINT=https://agentverse.ai

# Database
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Server Config
BACKEND_PORT=8000
FRONTEND_PORT=3000
MCP_SERVER_PORT=8080

# Environment
NODE_ENV=development
DEBUG=true
"""

# Write to .env file
with open('.env', 'w') as f:
    f.write(env_content)

print("✅ Created .env file with all API keys!")
print("\n⚠️  Remember to add your GitHub personal access token!")
print("   Replace 'your_github_token_here' in .env")
