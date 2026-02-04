const fs = require('fs')
const https = require('https')

const SUPABASE_URL = 'https://rjlrhzyiiurdjzmlgcyz.supabase.co'
const SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqbHJoenlpaXVyZGp6bWxnY3l6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA4Mjk3MiwiZXhwIjoyMDg1NjU4OTcyfQ.7xr_CeyV73RHIPOQ4c-AwoP1dcDb3ryW3uo4BWOM-oE'

// Read the migration file
const sql = fs.readFileSync('migrations/add_email_auth.sql', 'utf8')

console.log('🔄 Running email auth migration...\n')
console.log('Migration SQL:')
console.log('----------------------------------------')
console.log(sql.substring(0, 500) + '...')
console.log('----------------------------------------\n')

// Split SQL into individual statements
const statements = sql
  .split(';')
  .map(s => s.trim())
  .filter(s => s.length > 0 && !s.startsWith('--'))

console.log(`Executing ${statements.length} SQL statements...\n`)

async function executeSQL(statement) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query: statement })
    
    const options = {
      hostname: SUPABASE_URL.replace('https://', ''),
      path: '/rest/v1/rpc/exec_sql',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
      },
    }

    const req = https.request(options, (res) => {
      let responseData = ''
      
      res.on('data', (chunk) => {
        responseData += chunk
      })
      
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ success: true, data: responseData })
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${responseData}`))
        }
      })
    })

    req.on('error', (error) => {
      reject(error)
    })

    req.write(data)
    req.end()
  })
}

// Alternative: Use Supabase REST API directly
async function runMigration() {
  console.log('📝 Note: This script may fail if exec_sql RPC is not available.')
  console.log('   Please run the migration manually in the Supabase SQL Editor:')
  console.log('   https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new\n')
  console.log('✅ Migration file ready at: migrations/add_email_auth.sql')
  console.log('\nCopy and paste the SQL into the Supabase SQL Editor and run it.')
}

runMigration()
