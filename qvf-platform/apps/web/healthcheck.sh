#!/bin/sh
# Health check script for Next.js frontend

set -e

# Check if the service is responding
if wget --no-verbose --tries=1 --spider http://localhost:3006/ 2>/dev/null; then
    echo "Frontend health check: PASS"
    exit 0
else
    echo "Frontend health check: FAIL"
    exit 1
fi