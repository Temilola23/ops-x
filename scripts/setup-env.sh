#!/bin/bash

# OPS-X Environment Setup Script

echo "🔧 OPS-X Environment Setup"
echo "=========================="
echo ""

# Backend Environment
echo "📝 Setting up Backend environment..."
read -p "Enter your GitHub Personal Access Token: " github_token

cat > scripts/.env << EOF
# GitHub Integration (REQUIRED)
GITHUB_TOKEN=${github_token}

# Server Configuration
BACKEND_PORT=8000
EOF

echo "✅ Backend .env created at scripts/.env"
echo ""

# Frontend Environment
echo "📝 Setting up Frontend environment..."
read -p "Enter your V0.dev API Key: " v0_key

cat > frontend/.env.local << EOF
# V0.dev Integration (REQUIRED)
V0_API_KEY=${v0_key}

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo "✅ Frontend .env.local created"
echo ""

echo "🎉 Environment setup complete!"
echo ""
echo "To get your API keys:"
echo "  • GitHub Token: https://github.com/settings/tokens (scope: repo)"
echo "  • V0 API Key: https://v0.dev/settings"
echo ""
echo "Next steps:"
echo "  1. cd backend && python3 main.py"
echo "  2. cd frontend && npm run dev (in new terminal)"
echo "  3. Open http://localhost:3000"

