# QVF Platform Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (optional, but recommended)

### One-Command Deployment
```bash
make quickstart
```

This will:
1. Set up directories and environment files
2. Build all Docker images
3. Start the platform in production mode
4. Perform health checks

## Manual Deployment

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your configurations
nano .env
```

### 2. Build and Start Services
```bash
# Development mode (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Production mode
docker-compose up --build -d

# Production with nginx reverse proxy
docker-compose --profile production up --build -d
```

## Service Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  Nginx (Port 80/443) │────│  QVF Web (3006) │
│  Reverse Proxy   │    │  Next.js Frontend│
└─────────────────┘    └─────────────────┘
         │                       │
         │               ┌─────────────────┐
         └───────────────│ QVF API (8000)  │
                         │ FastAPI Backend │
                         └─────────────────┘
                                 │
                         ┌─────────────────┐
                         │ Redis (6379)    │
                         │ Cache & Sessions│
                         └─────────────────┘
```

## Available Services

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| qvf-web | 3006 | Next.js Frontend | http://localhost:3006/ |
| qvf-api | 8000 | FastAPI Backend | http://localhost:8000/health |
| redis | 6379 | Cache & Sessions | docker-compose exec redis redis-cli ping |
| nginx | 80/443 | Reverse Proxy | Only in production profile |

## Make Commands

### Development
```bash
make dev              # Start development environment
make dev-detached     # Start development in background
make logs             # View all logs
make logs-api         # View API logs only
make logs-web         # View frontend logs only
```

### Production
```bash
make prod             # Start production environment
make prod-with-nginx  # Start with nginx reverse proxy
make health           # Check service health
make status           # Show service status
```

### Management
```bash
make build            # Build all images
make up               # Start without rebuild
make down             # Stop all services
make restart          # Restart all services
```

### Database
```bash
make db-init          # Initialize with sample data
make db-backup        # Backup database
```

### Utilities
```bash
make shell-api        # Shell access to API container
make shell-web        # Shell access to Web container
make clean            # Remove containers and volumes
make ssl-cert         # Generate self-signed SSL certificates
```

## Environment Configuration

### Critical Security Settings
```env
# Change these in production!
SECRET_KEY=your-super-secret-key-256-bits
REDIS_PASSWORD=strong-redis-password
```

### API Configuration
```env
QVF_API_URL=http://qvf-api:8000          # Internal container communication
NEXT_PUBLIC_API_URL=http://localhost:8000 # External browser access
DATABASE_URL=sqlite:///./data/qvf.db     # Database location
```

### Azure DevOps Integration (Optional)
```env
ADO_ORGANIZATION=your-org
ADO_PROJECT=your-project
ADO_PAT_TOKEN=your-token
```

## Data Persistence

### Volume Mapping
- `qvf_data`: SQLite database and user uploads
- `qvf_logs`: Application logs
- `redis_data`: Redis persistence

### Backup Strategy
```bash
# Automated backup
make db-backup

# Manual backup
docker-compose exec qvf-api cp /app/data/qvf.db /app/data/backup.db
```

## Production Deployment

### 1. SSL Configuration
```bash
# Generate self-signed certificates (development)
make ssl-cert

# Or use your own certificates
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem
```

### 2. Production Environment
```bash
# Set production variables
echo "NODE_ENV=production" >> .env
echo "DEBUG=false" >> .env

# Start with nginx
make prod-with-nginx
```

### 3. Performance Tuning
```env
# In .env file
UVICORN_WORKERS=4
MAX_CONNECTIONS=1000
```

## Monitoring and Logging

### Health Checks
```bash
# Overall health
make health

# Individual services
curl http://localhost:8000/health  # API health
curl http://localhost:3006/        # Frontend health
```

### Log Management
```bash
# Follow all logs
make logs

# Service-specific logs
make logs-api
make logs-web
make logs-redis
```

### Metrics
- API metrics: http://localhost:8000/health
- Container metrics: `docker stats`
- Nginx metrics: Access logs in nginx container

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tlnp | grep :3006
   netstat -tlnp | grep :8000
   
   # Change ports in docker-compose.yml if needed
   ```

2. **Permission Issues**
   ```bash
   # Fix data directory permissions
   sudo chown -R 1001:1001 data logs
   ```

3. **Database Issues**
   ```bash
   # Reset database
   make clean-data
   make db-init
   ```

4. **Memory Issues**
   ```bash
   # Increase Docker memory limits
   # Docker Desktop: Settings > Resources > Memory
   ```

### Debug Mode
```bash
# Enable debug logging
echo "DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env

# Restart services
make restart
```

## Security Considerations

### Production Checklist
- [ ] Change default SECRET_KEY
- [ ] Set strong REDIS_PASSWORD  
- [ ] Use HTTPS with valid SSL certificates
- [ ] Configure firewall rules
- [ ] Enable log monitoring
- [ ] Set up automated backups
- [ ] Configure CORS origins properly
- [ ] Use secrets management for sensitive data

### Network Security
```bash
# Default network: 172.20.0.0/16
# Services communicate internally via service names
# Only necessary ports exposed to host
```

## Performance Optimization

### Image Optimization
- Multi-stage builds minimize image size
- Alpine Linux base images
- Layer caching for faster builds

### Runtime Optimization
- Uvicorn workers: 4 (adjust based on CPU cores)
- Keep-alive connections in nginx
- Redis caching for session storage
- Gzip compression for static assets

### Resource Limits
Add to docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

## Scaling

### Horizontal Scaling
```yaml
# Scale web instances
docker-compose up --scale qvf-web=3

# Scale API instances  
docker-compose up --scale qvf-api=2
```

### Load Balancer Configuration
Update nginx.conf for multiple instances:
```nginx
upstream qvf_web {
    server qvf-web_1:3006;
    server qvf-web_2:3006;
    server qvf-web_3:3006;
}
```

## Support

### Getting Help
1. Check logs: `make logs`
2. Verify health: `make health`
3. Check configuration: `make status`
4. Review documentation: This file

### Reporting Issues
Include in bug reports:
- Docker version: `docker --version`
- Compose version: `docker-compose --version`
- Service logs: `make logs`
- System resources: `docker stats`