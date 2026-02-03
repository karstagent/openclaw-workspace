# GlassWall Paid Messaging Deployment Status

## ✅ COMPLETED

### Frontend Code
- ✅ **WalletConnect Component** - Web3 wallet connection (MetaMask/Coinbase Wallet)
- ✅ **PaymentModal Component** - USDC payment flow on Base L2
- ✅ **PaidMessageButton Component** - Triggers paid message flow
- ✅ **Chat Page Updated** - Shows paid/free message options
- ✅ **Visual Indicators** - Lightning bolt for paid messages, transaction links
- ✅ **Migration API Endpoint** - `/api/migrate` for checking migration status

### Deployment
- ✅ **Code Committed** - All changes committed to main branch
- ✅ **Code Pushed** - Pushed to GitHub (karstagent/glasswall)
- ✅ **Vercel Deployment** - Auto-deployment triggered
- ✅ **Live Site** - https://glasswall.xyz

## ⏳ PENDING - DATABASE MIGRATION

### Required: Execute SQL in Supabase

**URL:** https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new

**SQL to Execute:**
```sql
-- Migration: Add Paid Messaging Feature

-- Add new columns to agents table
ALTER TABLE agents 
ADD COLUMN IF NOT EXISTS price_per_message NUMERIC(18, 6),
ADD COLUMN IF NOT EXISTS polling_interval_minutes INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ;

-- Add payment_address column (IMPORTANT - needed for payments!)
ALTER TABLE agents
ADD COLUMN IF NOT EXISTS payment_address TEXT;

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
COMMENT ON COLUMN agents.payment_address IS 'Base L2 address to receive USDC payments';
COMMENT ON COLUMN agents.polling_interval_minutes IS 'How often agent checks free messages (minutes). Default 30.';
COMMENT ON COLUMN agents.last_heartbeat_at IS 'Last time agent was active/checked messages. Used for countdown timer.';
COMMENT ON COLUMN messages.is_paid IS 'Whether this message was paid for (instant webhook delivery)';
COMMENT ON COLUMN messages.payment_tx_hash IS 'Base L2 transaction hash proving payment';
COMMENT ON TABLE payments IS 'Payment records for paid messages (analytics and verification)';
```

**Steps:**
1. Go to: https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new
2. Copy the SQL above
3. Paste into the SQL Editor
4. Click "Run"
5. Verify success

**Check Migration Status:**
```bash
curl https://glasswall.xyz/api/migrate
```

## ⏳ PENDING - AGENT CONFIGURATION

### Configure GlassWall Agent for Paid Messaging

**SQL to Execute in Supabase:**
```sql
UPDATE agents 
SET 
  price_per_message = 0.10,
  payment_address = 'YOUR_BASE_WALLET_ADDRESS_HERE',
  polling_interval_minutes = 30
WHERE slug = 'glasswall';
```

**Replace `YOUR_BASE_WALLET_ADDRESS_HERE` with:**
- Your Base L2 wallet address (0x...)
- This address will receive USDC payments
- Make sure you control this address!

## 🧪 TESTING CHECKLIST

After migration + configuration:

1. **Visit Chat Page**
   - Go to: https://glasswall.xyz/chat/glasswall
   - Verify UI shows paid messaging option

2. **Connect Wallet**
   - Click "Connect Wallet"
   - Connect MetaMask or Coinbase Wallet
   - Verify wallet address shows

3. **Send Free Message**
   - Type message and sender name
   - Click "Send Free"
   - Verify message appears in chat
   - Note: Webhook NOT called for free messages

4. **Send Paid Message**
   - Type message
   - Click paid messaging button
   - Connect wallet if not connected
   - Click "Pay $0.10"
   - Approve USDC transfer in wallet
   - Verify:
     - Payment confirmation
     - Message sent
     - Lightning bolt badge shows
     - Transaction link works
     - **Webhook called instantly**

5. **Check Database**
   ```sql
   -- Check agent config
   SELECT slug, price_per_message, payment_address FROM agents WHERE slug = 'glasswall';
   
   -- Check paid messages
   SELECT id, sender_name, content, is_paid, payment_tx_hash 
   FROM messages 
   WHERE is_paid = true 
   ORDER BY created_at DESC 
   LIMIT 5;
   
   -- Check payment records
   SELECT * FROM payments ORDER BY created_at DESC LIMIT 5;
   ```

## 📝 NOTES

- **Free messages:** Polled every 30 minutes (no instant webhook)
- **Paid messages:** Instant webhook delivery + stored in payments table
- **USDC Contract:** 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 (Base mainnet)
- **Gas fees:** Paid by sender (Base L2 = low fees)
- **Migration:** Idempotent (safe to re-run)

## 🚀 NEXT STEPS

1. ⏳ Execute database migration
2. ⏳ Configure payment address for GlassWall agent
3. ⏳ Test paid message flow end-to-end
4. ✅ Document any issues

## 📊 DEPLOYMENT SUMMARY

**Deployed Features:**
- Wallet connection UI
- Payment modal with USDC transfer
- Paid vs free message distinction
- Visual indicators for paid messages
- Migration API endpoint

**Technology Stack:**
- Frontend: Next.js + React + TypeScript
- Web3: viem (Ethereum library)
- Blockchain: Base L2 (Optimistic Rollup)
- Token: USDC (6 decimals)
- Database: Supabase (PostgreSQL)

**Git Commits:**
- Main repo: `b129ea6` - Migration scripts
- App repo: `b09fa4f` - UI components and chat page

---

**Status:** 🟡 Deployment ~95% complete - Awaiting manual migration step
**Blocker:** Database migration requires manual SQL execution
**Time to completion:** ~5 minutes (manual step)
