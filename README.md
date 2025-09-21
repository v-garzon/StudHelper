# StudHelper User Guide

Complete setup and deployment guide for the StudHelper AI study assistant system.

## Table of Contents

- [Required External Services](#required-external-services)
- [Optional External Services](#optional-external-services)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Security Setup](#security-setup)
- [Cost Breakdown](#cost-breakdown)
- [Quick Start Guide](#quick-start-guide)
- [Troubleshooting](#troubleshooting)

## Required External Services

### 1. OpenAI API Account

**Sign up**: https://platform.openai.com/
**API Keys**: https://platform.openai.com/api-keys

**Pricing (as of 2024)**:
- **gpt-4o-mini**: $0.15/$0.60 per 1M tokens (input/output)
- **gpt-4o**: $2.50/$10.00 per 1M tokens 
- **text-embedding-3-large**: $0.13 per 1M tokens
- **whisper-1**: $0.006 per minute

**Expected monthly costs for personal use**: $15-50

**Setup**:
1. Create OpenAI account
2. Add payment method (required for API access)
3. Generate API key
4. Set usage limits to avoid unexpected charges

### 2. PostgreSQL Database

PostgreSQL is required for storing user data, documents, chat history, and usage analytics.

#### Option A: Local Development

**macOS**:
```bash
brew install postgresql
brew services start postgresql

# Create database
psql -U postgres
CREATE DATABASE studhelper;
CREATE USER studhelper_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE studhelper TO studhelper_user;
\q
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE studhelper;
CREATE USER studhelper_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE studhelper TO studhelper_user;
\q
```

**Windows**:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run installer and follow setup wizard
3. Use pgAdmin or command line to create database

#### Option B: Cloud Database (Recommended for Production)

**Neon (Recommended)**:
- Free tier: 512MB storage
- PostgreSQL-compatible
- Easy setup: https://neon.tech/

**Supabase**:
- Free tier: 500MB storage  
- Includes authentication features
- Setup: https://supabase.com/

**AWS RDS**:
- Pay-as-you-go pricing
- Managed PostgreSQL service
- More configuration required

**Google Cloud SQL**:
- Pay-as-you-go pricing
- Managed PostgreSQL service
- Good integration with other Google services

### 3. ChromaDB Vector Database

ChromaDB stores document embeddings for the RAG (Retrieval-Augmented Generation) system.

#### Option A: Embedded (Development)
ChromaDB runs as part of the backend application. No separate setup required.
Data is stored in the `./chroma_data` directory.

#### Option B: ChromaDB Server (Production)
```bash
# Install and run ChromaDB server
pip install chromadb
chroma run --host 0.0.0.0 --port 8000

# Or using Docker
docker run -p 8000:8000 chromadb/chroma:latest
```

## Optional External Services

### 4. Redis (Recommended for Production)

Redis provides caching and session storage for better performance.

**macOS**:
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker**:
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 5. FFmpeg (For YouTube Processing)

Required for YouTube video audio extraction and processing.

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt install ffmpeg
```

**Windows**:
1. Download from: https://ffmpeg.org/download.html
2. Add to system PATH

## Development Setup

### Local Development Environment

**1. Clone and Setup Backend**:
```bash
git clone <your-repo-url>
cd studhelper-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
```

**2. Environment Configuration**:
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

**Environment Variables (.env)**:
```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=your-super-secret-key-here-minimum-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://studhelper_user:your_password@localhost:5432/studhelper

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORG_ID=org-your-organization-id

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_HOST=localhost
CHROMA_PORT=8000

# File Upload
MAX_FILE_SIZE=100000000
UPLOAD_DIR=./uploads

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8501

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

**3. Database Setup**:
```bash
# Run setup script
python scripts/setup_dev.py

# Or manually run migrations
python scripts/migrate_db.py upgrade
```

**4. Start Backend**:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**5. Setup Frontend**:
```bash
cd ../StudHelper-Streamlit

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit BACKEND_URL if needed (default: http://localhost:8000)
```

**6. Start Frontend**:
```bash
streamlit run main.py
```

**Access the Application**:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**Demo Credentials**:
- Email: `default@studhelper.local`
- Password: `default_password_change_me`

## Production Setup

### Docker Deployment (Recommended)

**1. Prepare Environment**:
```bash
# Copy production environment
cp .env.example .env.prod

# Edit with production values
nano .env.prod
```

**Production Environment (.env.prod)**:
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key-32-chars-minimum
DATABASE_URL=postgresql://user:password@db:5432/studhelper
OPENAI_API_KEY=sk-your-production-openai-key
CORS_ORIGINS=https://yourdomain.com
```

**2. Deploy with Docker Compose**:
```bash
# Build and start services
docker-compose -f docker/docker-compose.prod.yml up -d

# Check status
docker-compose -f docker/docker-compose.prod.yml ps

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f
```

**3. Run Database Migrations**:
```bash
docker-compose -f docker/docker-compose.prod.yml exec api python scripts/migrate_db.py upgrade
```

### Manual Production Setup

**1. Server Requirements**:
- Ubuntu 20.04+ or similar Linux distribution
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ storage

**2. Install Dependencies**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server ffmpeg

# Install Node.js (for frontend build tools if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

**3. Setup Application**:
```bash
# Create application user
sudo adduser studhelper
sudo usermod -aG sudo studhelper

# Switch to application user
sudo su - studhelper

# Clone and setup application
git clone <your-repo-url>
cd studhelper-backend

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/prod.txt

# Setup environment
cp .env.example .env
# Edit with production values

# Run migrations
python scripts/migrate_db.py upgrade
```

**4. Setup Services**:
```bash
# Create systemd service file
sudo nano /etc/systemd/system/studhelper.service
```

**Service File Content**:
```ini
[Unit]
Description=StudHelper FastAPI Application
After=network.target

[Service]
User=studhelper
Group=studhelper
WorkingDirectory=/home/studhelper/studhelper-backend
Environment=PATH=/home/studhelper/studhelper-backend/venv/bin
ExecStart=/home/studhelper/studhelper-backend/venv/bin/gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**5. Configure Nginx**:
```bash
sudo nano /etc/nginx/sites-available/studhelper
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;  # Streamlit
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;  # FastAPI
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**6. Enable and Start Services**:
```bash
# Enable services
sudo systemctl enable studhelper
sudo systemctl start studhelper

# Enable nginx
sudo ln -s /etc/nginx/sites-available/studhelper /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Check status
sudo systemctl status studhelper
sudo systemctl status nginx
```

## Cloud Deployment Options

### Option 1: Simple Cloud Setup (Budget-Friendly)

**Backend**: Railway, Render, or Heroku
**Database**: Neon or Supabase (free tiers)
**Frontend**: Streamlit Cloud
**Total cost**: $0-20/month

**Steps**:
1. Deploy database on Neon/Supabase
2. Deploy backend on Railway/Render
3. Deploy frontend on Streamlit Cloud
4. Configure environment variables

### Option 2: AWS/GCP Setup (Scalable)

**AWS Components**:
- **Backend**: ECS Fargate or Elastic Beanstalk
- **Database**: RDS PostgreSQL
- **Vector DB**: EC2 instance with ChromaDB
- **Storage**: S3 for file uploads
- **CDN**: CloudFront

**GCP Components**:
- **Backend**: Cloud Run
- **Database**: Cloud SQL PostgreSQL
- **Vector DB**: Compute Engine with ChromaDB
- **Storage**: Cloud Storage
- **CDN**: Cloud CDN

**Total cost**: $30-100/month

### Option 3: VPS Setup (Balanced)

**Providers**: DigitalOcean, Linode, Vultr
**Size**: $20-40/month VPS (2-4 CPU, 4-8GB RAM)
**Setup**: All services on single server

**Recommended VPS Specs**:
- 2+ CPU cores
- 4GB+ RAM
- 50GB+ SSD storage
- Ubuntu 20.04+

## Security Setup

### Production Security Checklist

**1. Generate Secure Secret Key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**2. Setup SSL Certificate**:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**3. Configure Firewall**:
```bash
sudo ufw allow 22     # SSH
sudo ufw allow 80     # HTTP
sudo ufw allow 443    # HTTPS
sudo ufw enable
```

**4. Database Security**:
```bash
# Create dedicated database user
psql -U postgres
CREATE USER studhelper_prod WITH PASSWORD 'strong_random_password';
GRANT CONNECT ON DATABASE studhelper TO studhelper_prod;
GRANT USAGE ON SCHEMA public TO studhelper_prod;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO studhelper_prod;
```

**5. Environment Variables**:
```bash
# Set secure environment variables
export SECRET_KEY="your-32-character-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/studhelper"
export OPENAI_API_KEY="sk-your-production-key"
```

## Cost Breakdown

### Development (Local)
- **OpenAI API**: $10-30/month
- **Infrastructure**: $0 (local)
- **Total**: $10-30/month

### Production Options

#### Budget Setup
- **OpenAI API**: $15-50/month
- **Database**: $0 (Neon free tier)
- **Backend Hosting**: $5-10/month (Railway/Render)
- **Frontend Hosting**: $0 (Streamlit Cloud)
- **Total**: $20-70/month

#### Standard Setup
- **OpenAI API**: $20-60/month
- **Database**: $15-25/month (managed PostgreSQL)
- **VPS/Cloud**: $20-40/month
- **Storage**: $5-10/month
- **Total**: $60-135/month

#### Enterprise Setup
- **OpenAI API**: $50-200/month
- **Database**: $50-100/month (high-availability)
- **Compute**: $100-300/month (multiple instances)
- **Storage & CDN**: $20-50/month
- **Monitoring**: $20-50/month
- **Total**: $240-700/month

## Quick Start Guide

### Fastest Setup (5 minutes)

**Prerequisites**:
- OpenAI API key
- Local PostgreSQL installed

**Commands**:
```bash
# 1. Get OpenAI API key
echo "Get your API key from: https://platform.openai.com/api-keys"

# 2. Setup database
createdb studhelper

# 3. Clone and setup backend
git clone <repo-url>
cd studhelper-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and database URL

# 5. Initialize application
python scripts/setup_dev.py

# 6. Start backend
uvicorn src.main:app --reload &

# 7. Setup and start frontend
cd ../StudHelper-Streamlit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

**Access**: http://localhost:8501
**Login**: `default@studhelper.local` / `default_password_change_me`

### Production Deployment (Docker)

**Prerequisites**:
- Docker and Docker Compose installed
- Domain name (optional)
- OpenAI API key

**Commands**:
```bash
# 1. Clone repository
git clone <repo-url>
cd studhelper-backend

# 2. Configure production environment
cp .env.example .env.prod
# Edit .env.prod with production values

# 3. Deploy with Docker
docker-compose -f docker/docker-compose.prod.yml up -d

# 4. Run migrations
docker-compose -f docker/docker-compose.prod.yml exec api python scripts/migrate_db.py upgrade

# 5. Check status
docker-compose -f docker/docker-compose.prod.yml ps
```

## Troubleshooting

### Common Issues

#### OpenAI API Errors
```bash
# Check API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Common errors:
# - Invalid API key: Check key is correct and has billing set up
# - Rate limit: Upgrade your OpenAI plan or reduce usage
# - Quota exceeded: Add more credits to your OpenAI account
```

#### Database Connection Issues
```bash
# Test database connection
psql postgresql://user:password@localhost:5432/studhelper

# Common issues:
# - Database doesn't exist: CREATE DATABASE studhelper;
# - User permissions: GRANT ALL PRIVILEGES ON DATABASE studhelper TO user;
# - Wrong credentials: Check username/password in DATABASE_URL
```

#### ChromaDB Issues
```bash
# Check ChromaDB data directory
ls -la ./chroma_data/

# Reset ChromaDB (WARNING: deletes all vector data)
rm -rf ./chroma_data/

# Check ChromaDB server (if using server mode)
curl http://localhost:8000/api/v1/heartbeat
```

#### File Upload Issues
```bash
# Check upload directory permissions
ls -la ./uploads/

# Create upload directory
mkdir -p uploads
chmod 755 uploads

# Check file size limits in environment
echo $MAX_FILE_SIZE
```

#### Frontend Connection Issues
```bash
# Check backend is running
curl http://localhost:8000/health

# Check environment variables
echo $BACKEND_URL

# Check CORS settings in backend
grep CORS_ORIGINS .env
```

### Performance Optimization

#### Backend Optimization
- Use Redis for caching
- Enable database connection pooling
- Optimize vector search queries
- Use CDN for file uploads

#### Frontend Optimization
- Enable Streamlit caching
- Optimize file upload sizes
- Use session state efficiently
- Implement pagination for large datasets

### Monitoring and Logging

#### Enable Monitoring
```bash
# View application logs
docker-compose logs -f api

# Monitor resource usage
docker stats

# Check database performance
psql -c "SELECT * FROM pg_stat_activity;"
```

#### Set Up Alerts
- OpenAI usage alerts
- Database storage alerts
- Application error alerts
- Performance monitoring

---

## Support

For additional help:
1. Check the backend API documentation at `/docs`
2. Review error logs in the application
3. Check OpenAI API status at https://status.openai.com/
4. Verify all environment variables are set correctly

**Note**: Keep your OpenAI API key secure and never commit it to version control. Use environment variables or secure secret management systems in production.