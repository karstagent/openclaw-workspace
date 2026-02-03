#!/usr/bin/env node

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Supabase configuration
const supabaseUrl = 'https://rjlrhzyiiurdjzmlgcyz.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqbHJoenlpaXVyZGp6bWxnY3l6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA4Mjk3MiwiZXhwIjoyMDg1NjU4OTcyfQ.7xr_CeyV73RHIPOQ4c-AwoP1dcDb3ryW3uo4BWOM-oE';

const supabase = createClient(supabaseUrl, serviceRoleKey);

async function runMigration() {
  console.log('🚀 Starting database migration...');
  
  // Read migration file
  const migrationPath = path.join(__dirname, 'migrations', '001_add_paid_messaging.sql');
  const sql = fs.readFileSync(migrationPath, 'utf-8');
  
  try {
    // Execute the migration using Supabase RPC
    const { data, error } = await supabase.rpc('exec_sql', { sql_query: sql });
    
    if (error) {
      console.error('❌ Migration failed:', error);
      
      // Try alternative method: execute SQL directly via REST API
      console.log('\n📝 Attempting alternative method via REST API...');
      const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': serviceRoleKey,
          'Authorization': `Bearer ${serviceRoleKey}`
        },
        body: JSON.stringify({ sql_query: sql })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Alternative method failed:', errorText);
        console.log('\n⚠️  Please run the migration manually in Supabase SQL Editor');
        console.log('\n📋 Migration file: migrations/001_add_paid_messaging.sql');
        process.exit(1);
      }
    }
    
    console.log('✅ Migration executed successfully!');
    
    // Verify the changes
    console.log('\n🔍 Verifying migration...');
    
    // Check agents table columns
    const { data: agentColumns, error: agentError } = await supabase
      .from('agents')
      .select('price_per_message, polling_interval_minutes, last_heartbeat_at')
      .limit(0);
    
    // Check messages table columns
    const { data: messageColumns, error: messageError } = await supabase
      .from('messages')
      .select('is_paid, payment_tx_hash')
      .limit(0);
    
    // Check payments table
    const { data: payments, error: paymentsError } = await supabase
      .from('payments')
      .select('*')
      .limit(0);
    
    if (!agentError && !messageError && !paymentsError) {
      console.log('✅ agents.price_per_message column exists');
      console.log('✅ messages.is_paid column exists');
      console.log('✅ payments table exists');
      console.log('\n🎉 Migration verified successfully!');
    } else {
      console.log('⚠️  Some verification checks failed, but migration may still be successful');
      if (agentError) console.log('  agents table:', agentError.message);
      if (messageError) console.log('  messages table:', messageError.message);
      if (paymentsError) console.log('  payments table:', paymentsError.message);
    }
    
  } catch (err) {
    console.error('❌ Error running migration:', err.message);
    console.log('\n⚠️  Please run the migration manually in Supabase SQL Editor');
    console.log('\n📋 Migration file: migrations/001_add_paid_messaging.sql');
    console.log('\n📖 Steps:');
    console.log('1. Go to https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql');
    console.log('2. Copy the contents of migrations/001_add_paid_messaging.sql');
    console.log('3. Paste and run the SQL');
    process.exit(1);
  }
}

runMigration();
