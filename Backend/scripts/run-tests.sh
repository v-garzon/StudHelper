#!/bin/bash
set -e

echo "🧪 Running StudHelper Backend Tests"

# Activate virtual environment
source venv/bin/activate

# Set test environment variables
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test-secret-key"
export OPENAI_API_KEY="test-key"

# Run tests with coverage
echo "🔍 Running tests with coverage..."
pytest --cov=app --cov-report=html --cov-report=term-missing tests/ -v

# Run linting
echo "🔧 Running code quality checks..."
black --check app tests
isort --check-only app tests
flake8 app tests

# Run security checks
echo "🔒 Running security checks..."
bandit -r app/
safety check

echo "✅ All tests and checks passed!"

