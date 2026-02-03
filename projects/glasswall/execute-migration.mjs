#!/usr/bin/env node

import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const supabaseUrl = 'https://rjlrhzyiiurdjzmlgcyz.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqbHJoenlpaXVyZGp6bWxnY3l6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA4Mjk3MiwiZXhwIjoyMDg1NjU4OTcyfQ.7xr_CeyV73RHIPOQ4c-AwoP1dcDb3ryW3uo4BWOM-oE';

const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

async function executeMigration() {
  console.log('🚀 Starting database migration...\n');
  
  // Read migration file
  const migrationPath = join(__dirname, 'migrations', '001_add_paid_messaging.sql');
  const sql = readFileSync(migrationPath, 'utf-8');
  
  console.log('📝 Executing SQL migration...');
  
  // Try to execute via Supabase Management API
  try {
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey,
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ query: sql })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    console.log('✅ Migration executed!\n');
  } catch (error) {
    console.error('⚠️  Direct execution not available:', error.message);
    console.log('\n📋 Please execute this SQL in Supabase SQL Editor:');
    console.log('   https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new\n');
  }
  
  // Verify the migration
  console.log('🔍 Verifying migration...\n');
  
  let allGood = true;
  
  try {
    // Check agents table
    const { error: agentError } = await supabase
      .from('agents')
      .select('price_per_message')
      .limit(1);
    
    if (!agentError) {
      console.log('✅ agents.price_per_message column exists');
    } else {
      console.log('❌ agents.price_per_message:', agentError.message);
      allGood = false;
    }
  } catch (e) {
    console.log('❌ agents table check failed:', e.message);
    allGood = false;
  }
  
  try {
    // Check messages table
    const { error: messageError } = await supabase
      .from('messages')
      .select('is_paid')
      .limit(1);
    
    if (!messageError) {
      console.log('✅ messages.is_paid column exists');
    } else {
      console.log('❌ messages.is_paid:', messageError.message);
      allGood = false;
    }
  } catch (e) {
    console.log('❌ messages table check failed:', e.message);
    allGood = false;
  }
  
  try {
    // Check payments table
    const { error: paymentsError } = await supabase
      .from('payments')
      .select('id')
      .limit(1);
    
    if (!paymentsError) {
      console.log('✅ payments table exists');
    } else {
      console.log('❌ payments table:', paymentsError.message);
      allGood = false;
    }
  } catch (e) {
    console.log('❌ payments table check failed:', e.message);
    allGood = false;
  }
  
  if (allGood) {
    console.log('\n🎉 Migration verified successfully!');
    return true;
  } else {
    console.log('\n⚠️  Migration may not be complete. Please run SQL manually in Supabase.');
    return false;
  }
}

executeMigration().then(success => {
  process.exit(success ? 0 : 1);
});
