.PHONY: help setup install-backend install-frontend run-backend run-frontend run-all test clean demo

help:
	@echo "OPS-X Development Commands:"
	@echo "  make setup          - Set up the entire development environment"
	@echo "  make install-backend - Install Python dependencies"
	@echo "  make install-frontend - Install Node dependencies"
	@echo "  make run-backend    - Run the backend server"
	@echo "  make run-frontend   - Run the frontend server"
	@echo "  make run-all        - Run all services with docker-compose"
	@echo "  make test           - Run all tests"
	@echo "  make demo           - Run the demo flow"
	@echo "  make clean          - Clean up generated files"

setup:
	@echo "Setting up OPS-X development environment..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@cd backend && pip install -r requirements-dev.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

run-backend:
	@echo "Starting backend server..."
	@cd backend && python main.py

run-frontend:
	@echo "Starting frontend server..."
	@cd frontend && npm run dev

run-all:
	@echo "Starting all services..."
	@docker-compose up

test:
	@echo "Running backend tests..."
	@cd backend && pytest tests/
	@echo "Running frontend tests..."
	@cd frontend && npm test

demo:
	@echo "Running demo flow..."
	@python scripts/demo_flow.py

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf backend/.pytest_cache
	@rm -rf frontend/node_modules
	@rm -rf data/cache/*
