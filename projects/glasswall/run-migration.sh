#!/bin/bash

echo "🚀 Executing database migration via Supabase SQL Editor..."
echo ""
echo "⚠️  Note: Direct SQL execution via API is limited."
echo "    Best approach: Run migration in Supabase SQL Editor"
echo ""
echo "📋 Migration file: migrations/001_add_paid_messaging.sql"
echo "🌐 Supabase SQL Editor: https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new"
echo ""
echo "Migration SQL:"
echo "----------------------------------------"
cat migrations/001_add_paid_messaging.sql
echo "----------------------------------------"
echo ""
echo "Please:"
echo "1. Go to: https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new"
echo "2. Copy the SQL above"
echo "3. Paste and run it"
echo ""
read -p "Have you completed the migration in Supabase? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "✅ Great! Proceeding with verification..."
    # Run verification using Node.js in app directory
    cd app && node ../verify-migration.js
else
    echo "⚠️  Please complete the migration before continuing."
    exit 1
fi
