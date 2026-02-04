-- Email Authentication Migration
-- Adds user authentication with email verification

-- Users table
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);

-- Email verification tokens table
CREATE TABLE verification_tokens (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token TEXT UNIQUE NOT NULL,
  type TEXT NOT NULL, -- 'verify_email' or 'magic_link'
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add user_id to messages table (nullable for backwards compatibility)
ALTER TABLE messages 
  ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_verification_tokens_token ON verification_tokens(token);
CREATE INDEX idx_verification_tokens_user_id ON verification_tokens(user_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);

-- RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_tokens ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "users_select_own" ON users 
  FOR SELECT USING (auth.uid()::text = id::text);

-- Anyone can insert new users (for signup)
CREATE POLICY "users_insert_public" ON users 
  FOR INSERT WITH CHECK (true);

-- Users can update their own data
CREATE POLICY "users_update_own" ON users 
  FOR UPDATE USING (auth.uid()::text = id::text);

-- Verification tokens: users can select their own
CREATE POLICY "tokens_select_own" ON verification_tokens 
  FOR SELECT USING (user_id::text = auth.uid()::text);

-- System can manage tokens
CREATE POLICY "tokens_insert_public" ON verification_tokens 
  FOR INSERT WITH CHECK (true);

-- Update messages policy to allow authenticated users
DROP POLICY IF EXISTS "public_insert_messages" ON messages;
CREATE POLICY "authenticated_insert_messages" ON messages 
  FOR INSERT WITH CHECK (true); -- Will be enforced at API level

-- Comments for documentation
COMMENT ON TABLE users IS 'Registered users with email authentication';
COMMENT ON TABLE verification_tokens IS 'Tokens for email verification and magic link login';
COMMENT ON COLUMN users.email_verified IS 'User must verify email before sending messages';
COMMENT ON COLUMN verification_tokens.type IS 'Token type: verify_email or magic_link';
