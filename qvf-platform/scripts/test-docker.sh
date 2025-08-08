#!/bin/bash

# QVF Platform E2E Tests in Docker Environment
# Usage: ./scripts/test-docker.sh [test_suite] [browser]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_SUITE=${1:-"smoke"}
BROWSER=${2:-"chromium"}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🐳 QVF Platform Docker E2E Test Runner${NC}"
echo -e "${BLUE}=====================================${NC}"
echo "Test Suite: $TEST_SUITE"
echo "Browser: $BROWSER"
echo ""

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up Docker containers...${NC}"
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.yml -f docker-compose.test.yml down --remove-orphans
    docker volume prune -f
}

# Set up trap to cleanup on exit
trap cleanup EXIT

# Check if docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is required but not installed${NC}"
    exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is required but not installed${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Create test-specific docker-compose override
cat > docker-compose.test.yml << EOF
version: '3.8'

services:
  api:
    environment:
      - NODE_ENV=test
      - DATABASE_URL=sqlite:///test.db
      - JWT_SECRET_KEY=test-secret-key-for-e2e-tests
    volumes:
      - ./test-data:/app/test-data

  web:
    environment:
      - NODE_ENV=test
      - NEXT_PUBLIC_API_URL=http://api:8000

  playwright:
    build:
      context: .
      dockerfile: Dockerfile.playwright
    depends_on:
      - api
      - web
    environment:
      - BASE_URL=http://web:3006
      - API_BASE_URL=http://api:8000
      - CI=true
    volumes:
      - ./tests:/app/tests
      - ./test-results:/app/test-results
      - ./playwright.config.ts:/app/playwright.config.ts
    command: ["./scripts/run-tests-in-container.sh", "${TEST_SUITE}", "${BROWSER}"]
EOF

# Create Playwright Dockerfile
cat > Dockerfile.playwright << EOF
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8

# Copy package files
COPY package*.json pnpm*.yaml ./
COPY apps/web/package*.json ./apps/web/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy test files and configuration
COPY tests/ ./tests/
COPY playwright.config.ts ./
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x ./scripts/*.sh

CMD ["pnpm", "exec", "playwright", "test"]
EOF

# Create in-container test script
cat > scripts/run-tests-in-container.sh << 'EOF'
#!/bin/bash

TEST_SUITE=${1:-"smoke"}
BROWSER=${2:-"chromium"}

echo "🐳 Running tests inside Docker container"
echo "Test Suite: $TEST_SUITE"
echo "Browser: $BROWSER"

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
timeout 60 bash -c 'until curl -f http://web:3006; do sleep 2; done'
timeout 30 bash -c 'until curl -f http://api:8000/health; do sleep 2; done'

echo "✅ Services are ready, starting tests..."

# Run tests based on suite
case "$TEST_SUITE" in
    "smoke")
        pnpm exec playwright test --project=$BROWSER tests/auth/authentication.spec.ts tests/dashboard/navigation.spec.ts
        ;;
    "auth")
        pnpm exec playwright test --project=$BROWSER tests/auth/
        ;;
    "dashboard")
        pnpm exec playwright test --project=$BROWSER tests/dashboard/
        ;;
    "qvf")
        pnpm exec playwright test --project=$BROWSER tests/qvf/
        ;;
    "work-items")
        pnpm exec playwright test --project=$BROWSER tests/work-items/
        ;;
    "comparison")
        pnpm exec playwright test --project=$BROWSER tests/comparison/
        ;;
    "api")
        pnpm exec playwright test --project=api tests/api/
        ;;
    *)
        pnpm exec playwright test --project=$BROWSER tests/
        ;;
esac
EOF

chmod +x scripts/run-tests-in-container.sh

# Build and start services
echo -e "${YELLOW}🚀 Building and starting Docker services...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.test.yml build

echo -e "${YELLOW}🌐 Starting application services...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d api web

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.test.yml exec -T api sh -c 'timeout 30 bash -c "until curl -f http://localhost:8000/health; do sleep 2; done"'
docker-compose -f docker-compose.yml -f docker-compose.test.yml exec -T web sh -c 'timeout 60 bash -c "until curl -f http://localhost:3006; do sleep 2; done"'

echo -e "${GREEN}✅ Services are ready${NC}"

# Run tests
echo -e "${GREEN}🏃‍♂️ Running E2E tests...${NC}"
mkdir -p test-results

if docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm playwright; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    EXIT_CODE=1
fi

# Copy test results from container
echo -e "${BLUE}📊 Copying test results...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm -v $(pwd)/test-results:/host-results playwright sh -c "cp -r /app/test-results/* /host-results/ 2>/dev/null || true"

# Show results summary
echo -e "${BLUE}📋 Test Results Summary:${NC}"
if [ -f "test-results/results.json" ]; then
    echo "  • Detailed results available in test-results/"
    echo "  • HTML report: test-results/html-report/index.html"
    echo "  • Screenshots and videos in test-results/"
else
    echo "  • Test results may be available in test-results/ directory"
fi

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 Docker E2E tests completed successfully!${NC}"
else
    echo -e "${RED}💥 Docker E2E tests completed with failures${NC}"
    echo -e "${YELLOW}💡 Check test-results/ for detailed failure information${NC}"
fi

# Cleanup temporary files
rm -f docker-compose.test.yml Dockerfile.playwright

exit $EXIT_CODE