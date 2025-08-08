.PHONY: help build up down logs shell-api shell-web clean dev prod health

# Default target
help: ## Show this help message
	@echo 'Usage: make [TARGET]'
	@echo 'Targets:'
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Environment setup
setup: ## Create necessary directories and copy environment file
	@echo "Setting up QVF Platform..."
	@mkdir -p data logs nginx/ssl
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env file from .env.example"; fi
	@echo "Setup complete! Please edit .env file with your configurations."

# Development commands
dev: setup ## Start development environment
	@echo "Starting QVF Platform in development mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-detached: setup ## Start development environment in background
	@echo "Starting QVF Platform in development mode (detached)..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# Production commands
prod: setup ## Start production environment
	@echo "Starting QVF Platform in production mode..."
	docker-compose up --build -d

prod-with-nginx: setup ## Start production environment with nginx reverse proxy
	@echo "Starting QVF Platform in production mode with nginx..."
	docker-compose --profile production up --build -d

# Build commands
build: ## Build all Docker images
	@echo "Building QVF Platform images..."
	docker-compose build

build-api: ## Build API Docker image only
	@echo "Building QVF API image..."
	docker-compose build qvf-api

build-web: ## Build Web Docker image only
	@echo "Building QVF Web image..."
	docker-compose build qvf-web

# Management commands
up: ## Start services (without rebuild)
	docker-compose up -d

down: ## Stop all services
	@echo "Stopping QVF Platform..."
	docker-compose down

restart: ## Restart all services
	@echo "Restarting QVF Platform..."
	docker-compose restart

# Monitoring commands
logs: ## Show logs from all services
	docker-compose logs -f

logs-api: ## Show API logs only
	docker-compose logs -f qvf-api

logs-web: ## Show Web logs only
	docker-compose logs -f qvf-web

logs-redis: ## Show Redis logs only
	docker-compose logs -f redis

status: ## Show status of all services
	@echo "QVF Platform Service Status:"
	@docker-compose ps

health: ## Check health of all services
	@echo "Checking QVF Platform health..."
	@echo "API Health:"
	@curl -s http://localhost:8000/health | jq '.' || echo "API not responding"
	@echo "Web Health:"
	@curl -s http://localhost:3006/ > /dev/null && echo "Frontend: Healthy" || echo "Frontend: Unhealthy"
	@echo "Redis Health:"
	@docker-compose exec redis redis-cli ping || echo "Redis: Unhealthy"

# Shell access
shell-api: ## Get shell access to API container
	docker-compose exec qvf-api /bin/sh

shell-web: ## Get shell access to Web container
	docker-compose exec qvf-web /bin/sh

shell-redis: ## Get shell access to Redis container
	docker-compose exec redis /bin/sh

# Database management
db-init: ## Initialize database with sample data
	docker-compose exec qvf-api python -c "from qvf_api.init_db import create_test_users, create_sample_qvf_session; from qvf_api.database import SessionLocal; db = SessionLocal(); create_test_users(db); create_sample_qvf_session(db); db.close()"

db-backup: ## Backup database
	@echo "Creating database backup..."
	@mkdir -p backups
	docker-compose exec qvf-api cp /app/data/qvf.db /app/data/qvf_backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "Database backed up successfully"

# Cleanup commands
clean: ## Stop services and remove containers, networks, volumes
	@echo "Cleaning up QVF Platform..."
	docker-compose down -v --remove-orphans

clean-all: ## Remove everything including images
	@echo "Removing all QVF Platform Docker resources..."
	docker-compose down -v --remove-orphans --rmi all

clean-data: ## Remove persistent data (WARNING: This will delete your database!)
	@echo "WARNING: This will delete all persistent data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data logs; \
		echo "Data cleaned"; \
	else \
		echo "Cancelled"; \
	fi

# SSL certificate generation for production
ssl-cert: ## Generate self-signed SSL certificates for nginx
	@echo "Generating self-signed SSL certificates..."
	@mkdir -p nginx/ssl
	@openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/key.pem \
		-out nginx/ssl/cert.pem \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=qvf-platform.local"
	@echo "SSL certificates generated in nginx/ssl/"

# Testing
test: ## Run tests in containers
	@echo "Running tests..."
	docker-compose exec qvf-api python -m pytest tests/ -v
	docker-compose exec qvf-web pnpm test

# Quick start
quickstart: setup build prod ## Quick start for first-time users
	@echo "QVF Platform is starting up..."
	@echo "Please wait for services to be ready..."
	@sleep 30
	@make health
	@echo ""
	@echo "QVF Platform is ready!"
	@echo "Frontend: http://localhost:3006"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "API Health: http://localhost:8000/health"