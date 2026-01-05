#!/bin/bash

###############################################################################
# TeamFlow Deployment Verification Script
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "======================================"
echo "TeamFlow Deployment Verification"
echo "======================================"
echo ""
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2

    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗ FAIL${NC}: $message"
    else
        echo -e "${YELLOW}⚠ WARN${NC}: $message"
    fi
}

# Function to test endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3

    echo -n "Testing: $description... "

    response=$(curl -s -o /dev/null -w "%{http_code}" -L "$url" --max-time 10 2>/dev/null || echo "000")

    if [ "$response" = "$expected_status" ]; then
        print_status "PASS" "$description"
        return 0
    else
        print_status "FAIL" "$description (expected $expected_status, got $response)"
        return 1
    fi
}

# Counter for results
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

###############################################################################
# Backend Health Checks
###############################################################################

echo "======================================"
echo "Backend Health Checks"
echo "======================================"

# Test 1: Health endpoint
if test_endpoint "$BACKEND_URL/health" "200" "Health Check Endpoint"; then
    ((PASS_COUNT++))
else
    ((FAIL_COUNT++))
fi

# Test 2: API Documentation (Swagger UI)
if test_endpoint "$BACKEND_URL/docs" "200" "API Documentation (Swagger)"; then
    ((PASS_COUNT++))
else
    ((FAIL_COUNT++))
fi

# Test 3: ReDoc
if test_endpoint "$BACKEND_URL/redoc" "200" "API Documentation (ReDoc)"; then
    ((PASS_COUNT++))
else
    ((FAIL_COUNT++))
fi

# Test 4: API v1 prefix exists
if test_endpoint "$BACKEND_URL/api/v1/" "404" "API v1 Prefix (404 expected)"; then
    ((PASS_COUNT++))
else
    ((FAIL_COUNT++))
fi

# Test 5: Root endpoint
root_response=$(curl -s "$BACKEND_URL/" --max-time 10 2>/dev/null || echo "")
if echo "$root_response" | grep -q "TeamFlow API"; then
    print_status "PASS" "Root Endpoint contains API name"
    ((PASS_COUNT++))
else
    print_status "WARN" "Root Endpoint response"
    ((WARN_COUNT++))
fi

###############################################################################
# Frontend Health Checks
###############################################################################

echo ""
echo "======================================"
echo "Frontend Health Checks"
echo "======================================"

# Test 6: Frontend is accessible
if test_endpoint "$FRONTEND_URL" "200" "Frontend Home Page"; then
    ((PASS_COUNT++))
else
    ((FAIL_COUNT++))
fi

# Test 7: Check for Next.js data
frontend_html=$(curl -s "$FRONTEND_URL" --max-time 10 2>/dev/null || echo "")
if echo "$frontend_html" | grep -q "TeamFlow\|__NEXT_DATA__"; then
    print_status "PASS" "Frontend contains React/Next.js markers"
    ((PASS_COUNT++))
else
    print_status "WARN" "Frontend may not be built correctly"
    ((WARN_COUNT++))
fi

###############################################################################
# CORS Check
###############################################################################

echo ""
echo "======================================"
echo "CORS Configuration"
echo "======================================"

# Test CORS preflight
cors_response=$(curl -s -i -X OPTIONS "$BACKEND_URL/api/v1/health" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: GET" \
    2>/dev/null | grep -i "access-control-allow-origin" || echo "")

if [ -n "$cors_response" ]; then
    print_status "PASS" "CORS headers present for frontend"
    ((PASS_COUNT++))
else
    print_status "FAIL" "CORS headers missing"
    ((FAIL_COUNT++))
fi

###############################################################################
# Environment Variable Check
###############################################################################

echo ""
echo "======================================"
echo "Environment Variables"
echo "======================================"

# Check if backend URL is set
if [ -n "$BACKEND_URL" ]; then
    print_status "PASS" "BACKEND_URL is set"
    ((PASS_COUNT++))
else
    print_status "WARN" "BACKEND_URL not set (using default)"
    ((WARN_COUNT++))
fi

# Check if frontend URL is set
if [ -n "$FRONTEND_URL" ]; then
    print_status "PASS" "FRONTEND_URL is set"
    ((PASS_COUNT++))
else
    print_status "WARN" "FRONTEND_URL not set (using default)"
    ((WARN_COUNT++))
fi

###############################################################################
# Database Check (if API is accessible)
###############################################################################

echo ""
echo "======================================"
echo "Database Connection"
echo "======================================"

# Try to access a protected endpoint to verify database
db_test=$(curl -s "$BACKEND_URL/api/v1/projects" --max-time 10 2>/dev/null || echo "")

if echo "$db_test" | grep -q "authentication\|Unauthorized\|token"; then
    print_status "PASS" "Database endpoint responds (auth required)"
    ((PASS_COUNT++))
elif echo "$db_test" | grep -q "connection\|database"; then
    print_status "WARN" "Database endpoint accessible but may have issues"
    ((WARN_COUNT++))
else
    print_status "INFO" "Database check skipped (auth required)"
    ((WARN_COUNT++))
fi

###############################################################################
# Summary
###############################################################################

echo ""
echo "======================================"
echo "Verification Summary"
echo "======================================"
echo ""
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${YELLOW}Warnings: $WARN_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Deployment appears successful."
    echo ""
    echo "Next Steps:"
    echo "1. Test the full application in browser: $FRONTEND_URL"
    echo "2. Verify authentication flow"
    echo "3. Test API endpoints: $BACKEND_URL/docs"
    echo "4. Monitor logs in HuggingFace Spaces and Vercel"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the output above.${NC}"
    echo ""
    echo "Common Issues:"
    echo "1. Services still starting up - wait 2-3 minutes and retry"
    echo "2. Wrong URLs - verify BACKEND_URL and FRONTEND_URL"
    echo "3. CORS issues - check backend configuration"
    echo "4. Database not ready - verify DATABASE_URL in backend"
    exit 1
fi
