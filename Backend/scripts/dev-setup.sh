#!/bin/bash
set -e

echo "🚀 Setting up StudHelper Backend Development Environment"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version >= 3.11" | bc -l) != 1 ]]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL first."
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
# if [ ! -f .env ]; then
echo "⚙️  Creating environment file..."
cp .env.example .env
echo "✏️  Please edit .env with your actual values (especially OPENAI_API_KEY)"
# fi

# Create database
echo "🗄️  Setting up database..."
createdb studhelper 2>/dev/null || echo "Database already exists"

# Run migrations
echo "🔄 Running database migrations..."

alembic upgrade head

# Create upload directory
echo "📁 Creating upload directory..."
mkdir -p uploads logs

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Visit: http://localhost:8000/docs"

