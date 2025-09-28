# StudHelper Backend Development Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- OpenAI API Key
- Git

## Development Setup

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd studhelper-backend
```

2. **Run setup script**
```bash
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

3. **Configure environment**
```bash
# Edit .env with your actual values
nano .env
```

Required environment variables:
```bash
DATABASE_URL=postgresql://postgres:password@localhost/studhelper
SECRET_KEY=your-super-secret-key-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key
```

4. **Start the application**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Development

1. **Quick start with Docker**
```bash
chmod +x scripts/docker-dev.sh
./scripts/docker-dev.sh
```

This will:
- Build the Docker image
- Start PostgreSQL database
- Run database migrations
- Start the API server

## Testing

```bash
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh
```

```bash
# Activate virtual environment
source venv/bin/activate

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_login_success -v

# Run with coverage
pytest --cov=app tests/
```

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test API endpoints end-to-end
- **Service tests**: Test business logic in service layer

## Database Management

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

```bash
# Create demo data for development
python seed_data.py
```

This creates:
- Demo teacher account: `teacher@studhelper.com` / `teacher123`
- Demo student account: `student@studhelper.com` / `student123`
- Demo class with code: `PHYS101`

## API Development

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


1. **Create route in `app/routes/`**
```python
from fastapi import APIRouter, Depends
from app.schemas import YourSchema
from app.services.your_service import YourService

router = APIRouter()

@router.post("/your-endpoint", response_model=YourSchema)
async def your_endpoint(data: YourSchema):
    # Implementation
    pass
```

2. **Add service logic in `app/services/`**
```python
class YourService:
    async def your_method(self, db: Session, data: YourSchema):
        # Business logic
        pass
```

3. **Include router in `app/main.py`**
```python
from app.routes import your_routes
app.include_router(your_routes.router, prefix="/api/v1/your-prefix", tags=["Your Tag"])
```

## Code Quality

```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint code
flake8 app tests

# Type checking
mypy app
```

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Debugging

Application logs are written to:
- Console (INFO level)
- `logs/app.log` (detailed logs)
- `logs/error.log` (errors only)
- `logs/access.log` (HTTP access logs)

```bash
# Connect to database
psql postgresql://postgres:password@localhost/studhelper

# View tables
\dt

# View specific table
\d users
```

```bash
# Profile API endpoints
pip install py-spy
py-spy top --pid <uvicorn-pid>
```

## Environment Configuration

```bash
DEBUG=true
DATABASE_URL=postgresql://postgres:password@localhost/studhelper
SECRET_KEY=development-secret-key
OPENAI_API_KEY=sk-your-api-key
```

```bash
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key
OPENAI_API_KEY=test-key
```

## Monitoring

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
python monitoring/healthcheck.py --url http://localhost:8000
```

```bash
# Collect application metrics
python monitoring/metrics.py
```

## Common Development Tasks

1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Generate migration: `alembic revision --autogenerate -m "Add new model"`
4. Apply migration: `alembic upgrade head`

```python
from app.utils.security import get_current_user
from app.schemas import UserResponse

@router.get("/protected")
async def protected_endpoint(current_user: UserResponse = Depends(get_current_user)):
    return {"user": current_user.username}
```

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate file type and size
    # Save file to storage
    # Process file content
    pass
```

## Troubleshooting


1. **Database connection failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Check firewall settings

2. **OpenAI API errors**
   - Verify OPENAI_API_KEY is set
   - Check API key validity
   - Monitor rate limits

3. **Import errors**
   - Ensure virtual environment is activated
   - Check all `__init__.py` files exist
   - Verify PYTHONPATH includes app directory

4. **Test failures**
   - Check test database is clean
   - Verify test fixtures are working
   - Check for test data conflicts


1. Check the logs in `logs/` directory
2. Review the API documentation at `/docs`
3. Run health checks with `monitoring/healthcheck.py`
4. Check GitHub issues for known problems

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run test suite: `./scripts/run-tests.sh`
4. Commit changes: `git commit -m "Add your feature"`
5. Push branch: `git push origin feature/your-feature`
6. Create pull request

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for public methods
- Maintain test coverage above 80%
- Add integration tests for new endpoints

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(auth): add password reset functionality

Add password reset endpoint and email notification service.
Includes rate limiting and security validation.

Closes #123
```

