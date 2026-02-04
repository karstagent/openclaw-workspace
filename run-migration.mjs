import pg from 'pg';
const { Client } = pg;

const client = new Client({
  connectionString: 'postgresql://postgres.rjlrhzyiiurdjzmlgcyz:Fnb7u7M.g6Xcu83@aws-0-us-west-2.pooler.supabase.com:5432/postgres'
});

const migration = `
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS verification_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  token TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE messages ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_token ON verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_email ON verification_tokens(email);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_tokens ENABLE ROW LEVEL SECURITY;
`;

try {
  await client.connect();
  console.log('Connected to database...');
  await client.query(migration);
  console.log('✅ Migration completed successfully');
  await client.end();
} catch (error) {
  console.error('❌ Migration failed:', error.message);
  process.exit(1);
}
