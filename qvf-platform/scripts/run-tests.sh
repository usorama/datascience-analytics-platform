#!/bin/bash

# QVF Platform E2E Test Execution Script
# Usage: ./scripts/run-tests.sh [test_suite] [browser] [options]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_SUITE=${1:-"all"}
BROWSER=${2:-"chromium"}
HEADLESS=${3:-"true"}
DEBUG=${4:-"false"}

# Environment variables
export BASE_URL=${BASE_URL:-"http://localhost:3006"}
export API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
export NODE_ENV=${NODE_ENV:-"test"}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
API_DIR="$PROJECT_DIR/apps/api"
WEB_DIR="$PROJECT_DIR/apps/web"

echo -e "${BLUE}🚀 QVF Platform E2E Test Runner${NC}"
echo -e "${BLUE}================================${NC}"
echo "Test Suite: $TEST_SUITE"
echo "Browser: $BROWSER"
echo "Headless: $HEADLESS"
echo "Debug Mode: $DEBUG"
echo "Frontend URL: $BASE_URL"
echo "API URL: $API_BASE_URL"
echo ""

# Function to cleanup background processes
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up background processes...${NC}"
    
    # Stop API server
    if [ -f "$API_DIR/api.pid" ]; then
        kill $(cat "$API_DIR/api.pid") 2>/dev/null || true
        rm "$API_DIR/api.pid"
    fi
    
    # Stop web server
    if [ -f "$WEB_DIR/web.pid" ]; then
        kill $(cat "$WEB_DIR/web.pid") 2>/dev/null || true
        rm "$WEB_DIR/web.pid"
    fi
    
    # Kill any remaining processes on our ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3006 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set up trap to cleanup on exit
trap cleanup EXIT

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local timeout=${2:-30}
    local service_name=$3
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready at $url...${NC}"
    
    for i in $(seq 1 $timeout); do
        if curl -f -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready${NC}"
            return 0
        fi
        
        if [ $i -eq $timeout ]; then
            echo -e "${RED}❌ $service_name failed to start after ${timeout}s${NC}"
            return 1
        fi
        
        sleep 1
    done
}

# Validate prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command_exists pnpm; then
    echo -e "${RED}❌ pnpm is required but not installed${NC}"
    echo "Install with: npm install -g pnpm"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"

# Install dependencies if needed
if [ ! -d "$PROJECT_DIR/node_modules" ] || [ ! -d "$WEB_DIR/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    cd "$PROJECT_DIR"
    pnpm install
fi

if [ ! -d "$API_DIR/venv" ] && [ ! -f "$API_DIR/.requirements.installed" ]; then
    echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
    cd "$API_DIR"
    pip install -r requirements.txt
    touch .requirements.installed
fi

# Install Playwright browsers if needed
if [ "$BROWSER" = "all" ]; then
    BROWSERS="chromium firefox webkit"
else
    BROWSERS=$BROWSER
fi

echo -e "${YELLOW}🎭 Installing Playwright browsers: $BROWSERS${NC}"
cd "$PROJECT_DIR"
pnpm exec playwright install --with-deps $BROWSERS

# Setup test database
echo -e "${YELLOW}🗄️  Setting up test database...${NC}"
cd "$API_DIR"

python3 << 'EOF'
import sqlite3
import hashlib
import os

# Create test database
db_path = 'test.db'
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
conn.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.execute('''
    CREATE TABLE work_items (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        business_value INTEGER NOT NULL,
        technical_complexity INTEGER NOT NULL,
        story_points INTEGER NOT NULL,
        priority TEXT NOT NULL,
        risk_level INTEGER DEFAULT 3,
        state TEXT DEFAULT 'New',
        assigned_to TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert test users
users = [
    ('executive', 'executive123', 'executive', 'Executive User'),
    ('product_owner', 'po123', 'product_owner', 'Product Owner'),
    ('scrum_master', 'sm123', 'scrum_master', 'Scrum Master'),
    ('developer', 'dev123', 'developer', 'Developer User')
]

for username, password, role, full_name in users:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn.execute(
        'INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)',
        (username, password_hash, role, full_name)
    )

# Insert test work items
work_items = [
    ('WI-001', 'User Authentication Feature', 8, 6, 8, 'High', 3, 'New', 'developer'),
    ('WI-002', 'Dashboard Performance Optimization', 6, 8, 13, 'Medium', 5, 'Active', 'developer'),
    ('WI-003', 'QVF Algorithm Enhancement', 9, 9, 21, 'High', 7, 'New', 'developer'),
    ('WI-004', 'Mobile Responsive Design', 7, 5, 5, 'Medium', 2, 'New', 'developer'),
    ('WI-005', 'API Documentation', 4, 3, 3, 'Low', 1, 'Completed', 'developer')
]

for item in work_items:
    conn.execute(
        'INSERT INTO work_items (id, title, business_value, technical_complexity, story_points, priority, risk_level, state, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        item
    )

conn.commit()
conn.close()
print("✅ Test database created with sample data")
EOF

echo -e "${GREEN}✅ Test database setup complete${NC}"

# Start API server
echo -e "${YELLOW}🚀 Starting API server...${NC}"
cd "$API_DIR"
export PYTHONPATH=src
export DATABASE_URL=sqlite:///test.db
export JWT_SECRET_KEY=test-secret-key-for-e2e-tests
nohup python3 -m uvicorn qvf_api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
echo $! > api.pid

wait_for_service "http://localhost:8000/health" 30 "API server"

# Start web server
echo -e "${YELLOW}🌐 Starting web server...${NC}"
cd "$WEB_DIR"
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Build the application
echo -e "${YELLOW}🔨 Building web application...${NC}"
pnpm run build

# Start the server
nohup pnpm run start > web.log 2>&1 &
echo $! > web.pid

wait_for_service "http://localhost:3006" 60 "Web server"

# Prepare test command based on test suite
echo -e "${BLUE}🧪 Preparing test execution...${NC}"

case "$TEST_SUITE" in
    "all")
        TEST_PATTERN="tests/"
        ;;
    "smoke")
        TEST_PATTERN="tests/auth/authentication.spec.ts tests/dashboard/navigation.spec.ts"
        ;;
    "auth")
        TEST_PATTERN="tests/auth/"
        ;;
    "dashboard")
        TEST_PATTERN="tests/dashboard/"
        ;;
    "qvf")
        TEST_PATTERN="tests/qvf/"
        ;;
    "work-items")
        TEST_PATTERN="tests/work-items/"
        ;;
    "comparison")
        TEST_PATTERN="tests/comparison/"
        ;;
    "visual")
        TEST_PATTERN="tests/visual/"
        ;;
    "performance")
        TEST_PATTERN="tests/performance/"
        ;;
    "mobile")
        TEST_PATTERN="tests/mobile/"
        ;;
    "api")
        TEST_PATTERN="tests/api/"
        BROWSER="api"
        ;;
    *)
        echo -e "${RED}❌ Unknown test suite: $TEST_SUITE${NC}"
        echo "Available test suites: all, smoke, auth, dashboard, qvf, work-items, comparison, visual, performance, mobile, api"
        exit 1
        ;;
esac

# Build Playwright command
cd "$PROJECT_DIR"
PLAYWRIGHT_CMD="pnpm exec playwright test"

if [ "$BROWSER" != "all" ] && [ "$BROWSER" != "api" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --project=$BROWSER"
elif [ "$BROWSER" = "all" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --project=chromium --project=firefox --project=webkit"
fi

if [ "$HEADLESS" = "false" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --headed"
fi

if [ "$DEBUG" = "true" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --debug"
fi

# Add test pattern
PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD $TEST_PATTERN"

# Run tests
echo -e "${GREEN}🏃‍♂️ Running tests...${NC}"
echo "Command: $PLAYWRIGHT_CMD"
echo ""

# Create test results directory
mkdir -p test-results

# Execute tests
if eval $PLAYWRIGHT_CMD; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    EXIT_CODE=1
fi

# Generate summary report
echo -e "${BLUE}📊 Generating test summary...${NC}"

if [ -f "test-results/results.json" ]; then
    echo -e "${BLUE}Test Results Summary:${NC}"
    python3 << 'EOF'
import json
import os

if os.path.exists('test-results/results.json'):
    with open('test-results/results.json', 'r') as f:
        results = json.load(f)
    
    stats = results.get('stats', {})
    print(f"  • Total tests: {stats.get('total', 0)}")
    print(f"  • Passed: {stats.get('expected', 0)}")
    print(f"  • Failed: {stats.get('unexpected', 0)}")
    print(f"  • Skipped: {stats.get('skipped', 0)}")
    print(f"  • Flaky: {stats.get('flaky', 0)}")
    print(f"  • Duration: {stats.get('duration', 0)}ms")
else:
    print("  • No detailed results available")
EOF
fi

echo ""
echo -e "${BLUE}📁 Test artifacts:${NC}"
if [ -d "test-results" ]; then
    echo "  • Test results: test-results/"
    echo "  • HTML report: test-results/html-report/"
    echo "  • Screenshots: test-results/screenshots/"
    echo "  • Videos: test-results/videos/"
    echo "  • Traces: test-results/traces/"
else
    echo "  • No test artifacts generated"
fi

echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo "  • API logs: apps/api/api.log"
echo "  • Web logs: apps/web/web.log"

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 Test execution completed successfully!${NC}"
else
    echo -e "${RED}💥 Test execution completed with failures${NC}"
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo "  1. Check the HTML report: open test-results/html-report/index.html"
    echo "  2. Review failed test screenshots and videos"
    echo "  3. Check server logs for API errors"
    echo "  4. Run specific failed tests with --debug flag"
fi

exit $EXIT_CODE