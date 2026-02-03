#!/usr/bin/env node

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://rjlrhzyiiurdjzmlgcyz.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqbHJoenlpaXVyZGp6bWxnY3l6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA4Mjk3MiwiZXhwIjoyMDg1NjU4OTcyfQ.7xr_CeyV73RHIPOQ4c-AwoP1dcDb3ryW3uo4BWOM-oE';

const supabase = createClient(supabaseUrl, serviceRoleKey);

async function verifyMigration() {
  console.log('🔍 Verifying migration...\n');
  
  try {
    // Check agents table columns
    const { error: agentError } = await supabase
      .from('agents')
      .select('price_per_message, polling_interval_minutes, last_heartbeat_at')
      .limit(1);
    
    if (!agentError) {
      console.log('✅ agents table: price_per_message, polling_interval_minutes, last_heartbeat_at');
    } else {
      console.log('❌ agents table:', agentError.message);
    }
    
    // Check messages table columns
    const { error: messageError } = await supabase
      .from('messages')
      .select('is_paid, payment_tx_hash')
      .limit(1);
    
    if (!messageError) {
      console.log('✅ messages table: is_paid, payment_tx_hash');
    } else {
      console.log('❌ messages table:', messageError.message);
    }
    
    // Check payments table
    const { error: paymentsError } = await supabase
      .from('payments')
      .select('*')
      .limit(1);
    
    if (!paymentsError) {
      console.log('✅ payments table exists');
    } else {
      console.log('❌ payments table:', paymentsError.message);
    }
    
    if (!agentError && !messageError && !paymentsError) {
      console.log('\n🎉 Migration verified successfully!');
      process.exit(0);
    } else {
      console.log('\n⚠️  Some checks failed - please review migration');
      process.exit(1);
    }
    
  } catch (err) {
    console.error('❌ Error verifying migration:', err.message);
    process.exit(1);
  }
}

verifyMigration();
