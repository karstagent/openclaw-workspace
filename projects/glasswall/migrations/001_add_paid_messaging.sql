-- Migration: Add Paid Messaging Feature
-- Run this in Supabase SQL Editor to upgrade existing database

-- Add new columns to agents table
ALTER TABLE agents 
ADD COLUMN IF NOT EXISTS price_per_message NUMERIC(18, 6),
ADD COLUMN IF NOT EXISTS polling_interval_minutes INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ;

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
  tx_hash TEXT NOT NULL UNIQUE,
  amount NUMERIC(18, 6) NOT NULL,
  sender_address TEXT NOT NULL,
  recipient_address TEXT NOT NULL,
  verified_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add new columns to messages table
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS is_paid BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS payment_tx_hash TEXT;

-- Enable RLS on payments table
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Add RLS policy for payments
CREATE POLICY "public_read_payments" ON payments FOR SELECT USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_payments_tx_hash ON payments(tx_hash);
CREATE INDEX IF NOT EXISTS idx_payments_agent_id ON payments(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_payment_tx_hash ON messages(payment_tx_hash);
CREATE INDEX IF NOT EXISTS idx_messages_is_paid ON messages(is_paid);
CREATE INDEX IF NOT EXISTS idx_agents_price ON agents(price_per_message) WHERE price_per_message IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN agents.price_per_message IS 'Price per message in USDC. NULL = free tier only.';
COMMENT ON COLUMN agents.polling_interval_minutes IS 'How often agent checks free messages (minutes). Default 30.';
COMMENT ON COLUMN agents.last_heartbeat_at IS 'Last time agent was active/checked messages. Used for countdown timer.';
COMMENT ON COLUMN messages.is_paid IS 'Whether this message was paid for (instant webhook delivery)';
COMMENT ON COLUMN messages.payment_tx_hash IS 'Base L2 transaction hash proving payment';
COMMENT ON TABLE payments IS 'Payment records for paid messages (analytics and verification)';

-- Verify migration
DO $$
BEGIN
  -- Check if columns exist
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'agents' AND column_name = 'price_per_message'
  ) THEN
    RAISE NOTICE '✅ agents.price_per_message column exists';
  END IF;
  
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'messages' AND column_name = 'is_paid'
  ) THEN
    RAISE NOTICE '✅ messages.is_paid column exists';
  END IF;
  
  IF EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'payments'
  ) THEN
    RAISE NOTICE '✅ payments table exists';
  END IF;
  
  RAISE NOTICE '✅ Migration complete!';
END $$;
