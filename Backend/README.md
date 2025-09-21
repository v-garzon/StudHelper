# StudHelper Backend

AI-powered study assistant backend with document processing, RAG, and OpenAI integration.

## Features

- **Document Processing**: PDF, Word, PowerPoint, YouTube transcription
- **RAG System**: ChromaDB vector storage with intelligent retrieval
- **AI Integration**: OpenAI GPT-4o with three modes (Economic/Standard/Turbo)
- **Cost Tracking**: Real-time token usage and cost monitoring
- **Authentication**: JWT-based user authentication
- **Scalable**: Async FastAPI with proper database management

## Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd studhelper-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (32+ characters)

### 3. Database Setup

```bash
# Setup development environment
python scripts/setup_dev.py

# Run migrations
python scripts/migrate_db.py upgrade
```

### 4. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for API documentation.

## Architecture

### Core Components

- **FastAPI**: Async web framework
- **SQLAlchemy**: Database ORM with async support
- **ChromaDB**: Vector database for RAG
- **OpenAI**: GPT-4o integration with cost tracking
- **Alembic**: Database migrations

### Project Structure

```
src/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── auth/                # Authentication system
├── documents/           # Document processing
├── rag/                # RAG system
├── ai/                 # OpenAI integration
├── usage/              # Usage tracking
├── core/               # Core infrastructure
└── utils/              # Utilities
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/documents/youtube` - Add YouTube video
- `GET /api/v1/documents/` - List documents
- `DELETE /api/v1/documents/{id}` - Delete document

### AI Chat
- `POST /api/v1/ai/chat` - Send chat message
- `POST /api/v1/ai/chat/stream` - Stream chat response
- `GET /api/v1/ai/sessions` - List chat sessions

### RAG Search
- `POST /api/v1/rag/search` - Search documents
- `GET /api/v1/rag/context/{query}` - Get context

### Usage Tracking
- `GET /api/v1/usage/analytics` - Usage analytics
- `GET /api/v1/usage/limits` - Current limits

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_auth.py -v
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

### Database Migrations

```bash
# Create migration
python scripts/migrate_db.py migrate "add new table"

# Apply migrations
python scripts/migrate_db.py upgrade

# Rollback migration
python scripts/migrate_db.py downgrade
```

## Deployment

### Docker Development

```bash
# Start development environment
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose logs -f api
```

### Docker Production

```bash
# Build and start production environment
docker-compose -f docker/docker-compose.prod.yml up -d

# Scale API service
docker-compose -f docker/docker-compose.prod.yml up -d --scale api=3
```

### Environment Variables

Production settings:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `DATABASE_URL`: Production database
- `CORS_ORIGINS`: Allowed origins
- `OPENAI_API_KEY`: Production API key

## Cost Management

### Default Limits (Per Day)
- **Tokens**: 10,000
- **Cost**: $1.00
- **Requests**: 100

### Pricing per 1M tokens
- **Economic Mode**: $0.15 input, $0.60 output (gpt-4o-mini)
- **Standard Mode**: $2.50 input, $10.00 output (gpt-4o)
- **Turbo Mode**: $2.50 input, $10.00 output (gpt-4o + reasoning)

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check PostgreSQL is running
docker-compose ps db

# Reset database
docker-compose down -v
docker-compose up -d db
python scripts/migrate_db.py upgrade
```

**ChromaDB connection errors:**
```bash
# Check ChromaDB service
docker-compose ps chromadb

# Reset ChromaDB
docker-compose down chromadb
docker volume rm studhelper_chroma_data
docker-compose up -d chromadb
```

**OpenAI API errors:**
- Verify API key in .env
- Check account billing status
- Monitor rate limits

### Performance Optimization

**Database:**
- Add indexes for frequently queried columns
- Use connection pooling
- Optimize query patterns

**Vector Store:**
- Batch document uploads
- Use appropriate chunk sizes
- Monitor embedding costs

**API:**
- Enable response caching
- Use connection keep-alive
- Monitor memory usage

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

MIT License - see LICENSE file for details.
