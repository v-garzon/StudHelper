# StudHelper Backend Production Deployment Guide

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database (managed service recommended)
- OpenAI API key

## Production Environment Setup


```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install required tools
sudo apt install -y nginx certbot python3-certbot-nginx
```


```bash
# Clone repository
git clone <repository-url> /opt/studhelper
cd /opt/studhelper

# Copy and configure environment
cp .env.example .env
nano .env
```


Create production `.env` file:
```bash
# Database (use managed PostgreSQL service)
DATABASE_URL=postgresql://username:password@db-host:5432/studhelper

# Security (generate strong keys)
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-your-production-openai-api-key

# File Upload
UPLOAD_DIR=/opt/studhelper/uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,txt,docx

# CORS (add your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Application
DEBUG=false
```


```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```


```bash
# Run deployment script
chmod +x scripts/production-deploy.sh

# Set required environment variables
export DATABASE_URL="postgresql://username:password@db-host:5432/studhelper"
export SECRET_KEY="your-super-secure-secret-key"
export OPENAI_API_KEY="sk-your-production-openai-api-key"

# Deploy
./scripts/production-deploy.sh
```

## Manual Deployment Steps

If you prefer manual deployment:


```bash
# Build Docker image
docker build -t studhelper-backend:latest .

# Create production directories
sudo mkdir -p /opt/studhelper/{uploads,logs,backups}
sudo chown -R $(id -u):$(id -g) /opt/studhelper

# Run database migrations
docker run --rm \
    -e DATABASE_URL="$DATABASE_URL" \
    studhelper-backend:latest \
    alembic upgrade head

# Start services
docker-compose -f docker-compose.production.yml up -d
```


```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/studhelper
sudo ln -s /etc/nginx/sites-available/studhelper /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Database Setup


Use a managed PostgreSQL service like:
- AWS RDS
- Google Cloud SQL
- Digital Ocean Managed Databases
- Azure Database for PostgreSQL

Benefits:
- Automated backups
- High availability
- Automatic security updates
- Monitoring and alerting


If you must self-host:

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createuser --createdb studhelper
sudo -u postgres createdb studhelper -O studhelper
sudo -u postgres psql -c "ALTER USER studhelper PASSWORD 'secure_password';"

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
# Update: shared_buffers, effective_cache_size, work_mem, maintenance_work_mem

sudo nano /etc/postgresql/13/main/pg_hba.conf
# Configure authentication methods

sudo systemctl restart postgresql
```

## Monitoring and Logging


```bash
# Set up log rotation
sudo nano /etc/logrotate.d/studhelper
```

Add:
```
/opt/studhelper/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 studhelper studhelper
    postrotate
        docker-compose -f /opt/studhelper/docker-compose.production.yml restart backend
    endscript
}
```


```bash
# Set up health check cron job
crontab -e
```

Add:
```bash
# Health check every 5 minutes
*/5 * * * * /usr/bin/python3 /opt/studhelper/monitoring/healthcheck.py --url https://your-domain.com >> /var/log/studhelper-health.log 2>&1
```


Install monitoring tools:
```bash
# Install system monitoring
sudo apt install htop iotop nethogs

# Optional: Install Prometheus node exporter
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*-linux-amd64.tar.gz
tar xvfz node_exporter-*-linux-amd64.tar.gz
sudo cp node_exporter-*/node_exporter /usr/local/bin/
```

## Backup Strategy


```bash
# Create backup script
sudo nano /opt/studhelper/backup-db.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/opt/studhelper/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE_URL="your-database-url"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/backup_$TIMESTAMP.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz s3://your-backup-bucket/
```

```bash
# Make executable and schedule
chmod +x /opt/studhelper/backup-db.sh
crontab -e
```

Add:
```bash
# Backup database daily at 2 AM
0 2 * * * /opt/studhelper/backup-db.sh
```


```bash
# Backup uploaded files
rsync -av /opt/studhelper/uploads/ /backup/uploads/

# Or use cloud sync
# aws s3 sync /opt/studhelper/uploads/ s3://your-files-bucket/
```

## Security Hardening


```bash
# Enable UFW
sudo ufw enable

# Allow SSH (adjust port if needed)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```


```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
```


- Use strong, unique SECRET_KEY
- Regularly rotate API keys
- Enable HTTPS only
- Set up proper CORS origins
- Monitor for security vulnerabilities
- Keep Docker images updated

## Performance Optimization


```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_chat_sessions_user_class ON chat_sessions(user_id, class_id);
CREATE INDEX CONCURRENTLY idx_usage_records_user_timestamp ON usage_records(user_id, timestamp);
CREATE INDEX CONCURRENTLY idx_documents_class_scope ON documents(class_id, scope);
```


```bash
# Tune Docker container resources
docker-compose -f docker-compose.production.yml up -d
```

Update `docker-compose.production.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```


Consider adding Redis for caching:
```yaml
# Add to docker-compose.production.yml
redis:
  image: redis:alpine
  restart: unless-stopped
  volumes:
    - redis_data:/data
```

## SSL/TLS Configuration


Update `nginx.conf` for better security:
```nginx
# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```


```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Check renewal service
sudo systemctl status certbot.timer
```

## Troubleshooting


1. **Application won't start**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Check database connectivity
   docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
   ```

2. **High memory usage**
   ```bash
   # Monitor resources
   docker stats
   
   # Check application metrics
   python monitoring/metrics.py
   ```

3. **Slow database queries**
   ```sql
   -- Enable query logging
   ALTER SYSTEM SET log_statement = 'all';
   SELECT pg_reload_conf();
   
   -- Check slow queries
   SELECT query, total_time, calls 
   FROM pg_stat_statements 
   ORDER BY total_time DESC 
   LIMIT 10;
   ```


1. **Application Rollback**
   ```bash
   # Rollback to previous image
   docker tag studhelper-backend:previous studhelper-backend:latest
   docker-compose -f docker-compose.production.yml up -d
   ```

2. **Database Recovery**
   ```bash
   # Restore from backup
   gunzip -c /opt/studhelper/backups/backup_TIMESTAMP.sql.gz | psql $DATABASE_URL
   ```

3. **Service Restart**
   ```bash
   # Restart all services
   docker-compose -f docker-compose.production.yml restart
   
   # Restart nginx
   sudo systemctl restart nginx
   ```

## Scaling Considerations


1. **Load Balancer Setup**
   - Use nginx or cloud load balancer
   - Configure session affinity if needed
   - Health check endpoints

2. **Database Scaling**
   - Read replicas for queries
   - Connection pooling
   - Database sharding (if needed)

3. **File Storage**
   - Use object storage (S3, GCS)
   - CDN for static content
   - Distributed file systems


1. **Resource Monitoring**
   ```bash
   # Monitor resource usage
   htop
   iotop
   docker stats
   ```

2. **Database Tuning**
   - Increase shared_buffers
   - Tune work_mem and maintenance_work_mem
   - Optimize queries and indexes

3. **Application Tuning**
   - Increase worker processes
   - Optimize Docker resource limits
   - Enable application-level caching

## Maintenance Schedule

- Check application health
- Monitor error logs
- Verify backup completion

- Review performance metrics
- Check security updates
- Rotate log files

- Update dependencies
- Review and test backup recovery
- Security audit
- Performance optimization review

- Comprehensive security review
- Disaster recovery testing
- Capacity planning review
- Documentation updates
