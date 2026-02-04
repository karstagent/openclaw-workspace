import pg from 'pg';
const { Client } = pg;

const client = new Client({
  connectionString: 'postgresql://postgres.rjlrhzyiiurdjzmlgcyz:Fnb7u7M.g6Xcu83@aws-0-us-west-2.pooler.supabase.com:5432/postgres'
});

const policies = `
DROP POLICY IF EXISTS "Users can read their own data" ON users;
CREATE POLICY "Users can read their own data" ON users FOR SELECT USING (true);

DROP POLICY IF EXISTS "Anyone can insert verification tokens" ON verification_tokens;
CREATE POLICY "Anyone can insert verification tokens" ON verification_tokens FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Users can read their own tokens" ON verification_tokens;
CREATE POLICY "Users can read their own tokens" ON verification_tokens FOR SELECT USING (true);
`;

try {
  await client.connect();
  console.log('Adding RLS policies...');
  await client.query(policies);
  console.log('✅ RLS policies added successfully');
  await client.end();
} catch (error) {
  console.error('❌ Failed:', error.message);
  process.exit(1);
}
