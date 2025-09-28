#!/bin/bash
set -e

echo "🚀 Deploying StudHelper Backend to Production"

# Check required environment variables
required_vars=("DATABASE_URL" "SECRET_KEY" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

# Build production image
echo "🏗️  Building production image..."
docker build -t studhelper-backend:latest .

# Create production directories
echo "📁 Creating production directories..."
sudo mkdir -p /opt/studhelper/{uploads,logs,backups}
sudo chown -R $(id -u):$(id -g) /opt/studhelper

# Backup database (if exists)
if [ -n "$BACKUP_DATABASE" ]; then
    echo "💾 Creating database backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    pg_dump $DATABASE_URL > /opt/studhelper/backups/backup_$timestamp.sql
fi

# Run database migrations
echo "🔄 Running database migrations..."
docker run --rm \
    -e DATABASE_URL="$DATABASE_URL" \
    studhelper-backend:latest \
    alembic upgrade head

# Start production services
echo "🚀 Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Health check
echo "🏥 Running health check..."
sleep 10
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed"
    exit 1
fi

echo "🎉 StudHelper Backend deployed successfully!"

