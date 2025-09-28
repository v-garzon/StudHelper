# StudHelper Backend

A class-based AI learning platform with flexible permissions and granular usage tracking.

## Features

- **User Management**: Registration, authentication, profile management
- **Class System**: Create/join classes with unique codes
- **Permission Management**: Granular class-based permissions
- **Dual-Document System**: Class-wide + chat-specific documents
- **AI Chat**: Context-aware conversations with document integration
- **Usage Tracking**: Per-class, per-user token limits and monitoring

## Quick Start


- Python 3.11+
- PostgreSQL 12+
- OpenAI API Key


1. **Clone the repository**
```bash
git clone <repository-url>
cd studhelper-backend
```

2. **Set up environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb studhelper

# Run migrations
alembic upgrade head
```

5. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


1. **Using Docker Compose**
```bash
# Copy environment file
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Start services
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative docs**: `http://localhost:8000/redoc`

## Project Structure

```
app/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── config.py           # Settings and configuration
├── models/             # Database models
├── schemas/            # Pydantic schemas
├── routes/             # API endpoints
├── services/           # Business logic
├── utils/              # Helper functions
└── migrations/         # Database migrations
```

## Testing

Run the test suite:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Environment Variables

Required environment variables:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-at-least-32-characters
OPENAI_API_KEY=your-openai-api-key
```

Optional variables:
```bash
DEBUG=false
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
CORS_ORIGINS=http://localhost:3000
```

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- File type and size validation
- SQL injection protection via SQLAlchemy ORM

## Usage Tracking

The system tracks token usage per user per class with:
- Daily, weekly, and monthly limits
- Automatic reset at 00:00 Madrid time
- Sponsorship support (managers can pay for students)
- Overflow billing detection

## Document Processing

Supports multiple file types:
- PDF files (text extraction)
- TXT files (plain text)
- DOCX files (Microsoft Word)

Documents are:
- Chunked for efficient processing
- Available at class or chat session level
- Processed asynchronously
- Used for context-aware AI responses

## Production Deployment

1. **Use production environment variables**
2. **Set up SSL/TLS termination**
3. **Configure proper database connection pooling**
4. **Set up logging and monitoring**
5. **Use a production WSGI server** (included: uvicorn)


```bash
docker-compose -f docker-compose.production.yml up -d
```

## Architecture

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: ORM with PostgreSQL
- **Alembic**: Database migrations
- **JWT**: Stateless authentication
- **OpenAI GPT-4o-mini**: AI responses with cost optimization
- **Pydantic**: Data validation and serialization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Add your license here]
