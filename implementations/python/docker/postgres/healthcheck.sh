#!/bin/sh
# PostgreSQL Health Check Script for UPSS
# Performs comprehensive health checks on the database

set -e

# Configuration
TIMEOUT=5
DB_NAME="${POSTGRES_DB:-upss}"
DB_USER="${POSTGRES_USER:-upss}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo "${GREEN}✓${NC} $2"
    else
        echo "${RED}✗${NC} $2"
    fi
}

# Function to run SQL query with timeout
run_query() {
    timeout $TIMEOUT psql -U "$DB_USER" -d "$DB_NAME" -t -c "$1" 2>/dev/null
}

# Check 1: PostgreSQL is accepting connections
if ! pg_isready -U "$DB_USER" -d "$DB_NAME" -t $TIMEOUT >/dev/null 2>&1; then
    echo "${RED}UNHEALTHY:${NC} PostgreSQL is not accepting connections"
    exit 1
fi
print_status 0 "PostgreSQL is accepting connections"

# Check 2: Can execute queries
if ! run_query "SELECT 1" >/dev/null 2>&1; then
    echo "${RED}UNHEALTHY:${NC} Cannot execute queries"
    exit 1
fi
print_status 0 "Can execute queries"

# Check 3: UPSS schema exists
if ! run_query "SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'upss')" | grep -q 't'; then
    echo "${YELLOW}WARNING:${NC} UPSS schema not found (database may be initializing)"
    exit 0  # Don't fail during initialization
fi
print_status 0 "UPSS schema exists"

# Check 4: Required tables exist
REQUIRED_TABLES="prompts prompt_versions audit_logs user_roles role_permissions"
for table in $REQUIRED_TABLES; do
    if ! run_query "SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname = 'upss' AND tablename = '$table')" | grep -q 't'; then
        echo "${RED}UNHEALTHY:${NC} Required table 'upss.$table' not found"
        exit 1
    fi
done
print_status 0 "All required tables exist"

# Check 5: Database is not in recovery mode (not a standby)
if run_query "SELECT pg_is_in_recovery()" | grep -q 't'; then
    echo "${YELLOW}INFO:${NC} Database is in recovery mode (standby server)"
fi

# Check 6: Check for locks
LOCKS=$(run_query "SELECT COUNT(*) FROM pg_locks WHERE NOT GRANTED" | tr -d ' ')
if [ "$LOCKS" -gt 10 ]; then
    echo "${YELLOW}WARNING:${NC} High number of blocked queries: $LOCKS"
fi

# Check 7: Check for long-running transactions
LONG_TRANS=$(run_query "SELECT COUNT(*) FROM pg_stat_activity WHERE state != 'idle' AND NOW() - query_start > interval '5 minutes'" | tr -d ' ')
if [ "$LONG_TRANS" -gt 0 ]; then
    echo "${YELLOW}WARNING:${NC} Found $LONG_TRANS long-running transactions (>5 min)"
fi

# Check 8: Check connection count
CONN_COUNT=$(run_query "SELECT COUNT(*) FROM pg_stat_activity" | tr -d ' ')
MAX_CONN=$(run_query "SELECT setting FROM pg_settings WHERE name = 'max_connections'" | tr -d ' ')
CONN_PCT=$((CONN_COUNT * 100 / MAX_CONN))

if [ "$CONN_PCT" -gt 80 ]; then
    echo "${YELLOW}WARNING:${NC} Connection usage at ${CONN_PCT}% ($CONN_COUNT/$MAX_CONN)"
elif [ "$CONN_PCT" -gt 90 ]; then
    echo "${RED}CRITICAL:${NC} Connection usage at ${CONN_PCT}% ($CONN_COUNT/$MAX_CONN)"
fi

# Check 9: Check disk space for data directory
DISK_USAGE=$(df -h "$PGDATA" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "${RED}CRITICAL:${NC} Data directory disk usage at ${DISK_USAGE}%"
    exit 1
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo "${YELLOW}WARNING:${NC} Data directory disk usage at ${DISK_USAGE}%"
fi

# Check 10: Verify audit log is writable
if ! run_query "INSERT INTO upss.audit_logs (event_type, user_id, prompt_name, success) VALUES ('healthcheck', 'system', 'healthcheck', true)" >/dev/null 2>&1; then
    echo "${RED}UNHEALTHY:${NC} Cannot write to audit log"
    exit 1
fi
print_status 0 "Audit log is writable"

# All checks passed
echo "${GREEN}HEALTHY:${NC} All health checks passed"
exit 0
