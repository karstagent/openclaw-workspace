#!/bin/bash

SUPABASE_URL="https://rjlrhzyiiurdjzmlgcyz.supabase.co"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqbHJoenlpaXVyZGp6bWxnY3l6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA4Mjk3MiwiZXhwIjoyMDg1NjU4OTcyfQ.7xr_CeyV73RHIPOQ4c-AwoP1dcDb3ryW3uo4BWOM-oE"

echo "🚀 Executing migration via direct SQL..."
echo ""

# Execute each statement separately
echo "Adding columns to agents table..."
curl -X POST "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
  -H "apikey: ${SERVICE_KEY}" \
  -H "Authorization: Bearer ${SERVICE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query": "ALTER TABLE agents ADD COLUMN IF NOT EXISTS price_per_message NUMERIC(18, 6), ADD COLUMN IF NOT EXISTS polling_interval_minutes INTEGER DEFAULT 30, ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ;"}' 2>&1

echo ""
echo "Running full migration script..."

# Read and execute the full migration
SQL_CONTENT=$(cat migrations/001_add_paid_messaging.sql)

# Try via PostgREST stored procedure approach
curl -X POST "${SUPABASE_URL}/rest/v1/rpc/exec" \
  -H "apikey: ${SERVICE_KEY}" \
  -H "Authorization: Bearer ${SERVICE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"sql\": $(echo "$SQL_CONTENT" | jq -Rs .)}" 2>&1

echo ""
echo "Migration attempted. Verifying..."
