#!/bin/bash

echo " OPS-X Dependency Installation"
echo "================================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo " WARNING: No virtual environment detected!"
    echo "   It's recommended to use a virtual environment."
    echo ""
    echo "   Create one with: python -m venv venv"
    echo "   Activate with:   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "🧪 Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "📦 Installing frontend dependencies..."
cd ../frontend
if command -v npm &> /dev/null; then
    npm install
else
    echo " npm not found. Please install Node.js to set up frontend."
fi

echo ""
echo " Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and add your API keys"
echo "2. Run 'make run-backend' to start the backend"
echo "3. Run 'make run-frontend' to start the frontend"
echo "4. Check out NEXT_STEPS.md for implementation guide"
