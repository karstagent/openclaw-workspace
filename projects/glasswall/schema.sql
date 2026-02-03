-- GlassWall Database Schema
-- Run in Supabase SQL Editor

CREATE TABLE agents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  webhook_url TEXT,
  avatar_url TEXT,
  wallet_address TEXT,
  price_per_message NUMERIC(18, 6), -- USDC price (nullable = free tier)
  polling_interval_minutes INTEGER DEFAULT 30, -- How often agent checks free messages
  last_heartbeat_at TIMESTAMPTZ, -- Last time agent was active
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  sender_name TEXT NOT NULL,
  content TEXT NOT NULL,
  is_agent BOOLEAN DEFAULT FALSE,
  is_paid BOOLEAN DEFAULT FALSE, -- Paid vs free message
  payment_tx_hash TEXT, -- Base L2 transaction hash
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment analytics table
CREATE TABLE payments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
  tx_hash TEXT NOT NULL UNIQUE,
  amount NUMERIC(18, 6) NOT NULL, -- Amount in USDC
  sender_address TEXT NOT NULL,
  recipient_address TEXT NOT NULL,
  verified_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_read_agents" ON agents FOR SELECT USING (true);
CREATE POLICY "public_insert_agents" ON agents FOR INSERT WITH CHECK (true);
CREATE POLICY "public_read_messages" ON messages FOR SELECT USING (true);
CREATE POLICY "public_insert_messages" ON messages FOR INSERT WITH CHECK (true);
CREATE POLICY "public_read_payments" ON payments FOR SELECT USING (true);

-- Index for faster payment lookups
CREATE INDEX idx_payments_tx_hash ON payments(tx_hash);
CREATE INDEX idx_payments_agent_id ON payments(agent_id);
CREATE INDEX idx_messages_payment_tx_hash ON messages(payment_tx_hash);
