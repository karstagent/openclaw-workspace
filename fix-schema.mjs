import pg from 'pg';
const { Client } = pg;

const client = new Client({
  connectionString: 'postgresql://postgres.rjlrhzyiiurdjzmlgcyz:Fnb7u7M.g6Xcu83@aws-0-us-west-2.pooler.supabase.com:5432/postgres'
});

const fix = `
-- Add missing columns to verification_tokens
ALTER TABLE verification_tokens ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);
ALTER TABLE verification_tokens ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'verify_email';

-- Create index on user_id
CREATE INDEX IF NOT EXISTS idx_verification_tokens_user_id ON verification_tokens(user_id);
`;

try {
  await client.connect();
  console.log('Fixing schema...');
  await client.query(fix);
  console.log('✅ Schema fixed successfully');
  await client.end();
} catch (error) {
  console.error('❌ Failed:', error.message);
  process.exit(1);
}
