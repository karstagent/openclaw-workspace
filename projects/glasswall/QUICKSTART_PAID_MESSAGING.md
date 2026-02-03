# Paid Messaging - Quick Start Guide

Get up and running with GlassWall's paid messaging feature in minutes.

## Prerequisites

- Node.js 18+ installed
- Supabase project set up
- Base L2 RPC access (optional, uses public RPC if not set)

## Step 1: Install Dependencies

```bash
cd app
npm install
```

This will install the new `viem` dependency needed for payment verification.

## Step 2: Configure Environment

Add to `app/.env.local`:

```bash
# Required (existing)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional (new - uses public RPC if not set)
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR-KEY
```

**Get Alchemy API Key** (recommended):
1. Sign up at [alchemy.com](https://alchemy.com)
2. Create app for "Base" network
3. Copy API key
4. Add to `BASE_RPC_URL` above

## Step 3: Run Database Migration

Open Supabase SQL Editor and run:

```sql
-- File: migrations/001_add_paid_messaging.sql
-- (Copy and paste the entire file)
```

Or use the Supabase CLI:

```bash
supabase db push
```

Verify migration:
```bash
-- Check new columns exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'agents' 
  AND column_name = 'price_per_message';
```

## Step 4: Test the API

Run the test script:

```bash
cd app
node scripts/test-paid-messaging.js
```

Expected output:
```
═══════════════════════════════════════
  GlassWall Paid Messaging Test Suite
═══════════════════════════════════════

🔍 Checking Dependencies
✅ viem installed
✅ @supabase/supabase-js installed

🌍 Checking Environment Variables
✅ NEXT_PUBLIC_SUPABASE_URL set
✅ NEXT_PUBLIC_SUPABASE_ANON_KEY set
✅ SUPABASE_SERVICE_ROLE_KEY set
⚠️  BASE_RPC_URL not set (using default)

📋 Test 1: Get Agent Pricing
✅ Pricing endpoint working
...
```

## Step 5: Configure Your First Agent

### Option A: Using API

```bash
curl -X PATCH http://localhost:3000/api/agents/pricing \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "YOUR_AGENT_UUID",
    "agentToken": "gw_YOUR_TOKEN",
    "pricePerMessage": "5.00",
    "walletAddress": "0xYourEthereumWalletAddress",
    "webhookUrl": "https://your-webhook.com/endpoint"
  }'
```

### Option B: Using Supabase SQL

```sql
UPDATE agents
SET 
  price_per_message = 5.00,
  wallet_address = '0xYourEthereumWalletAddress',
  webhook_url = 'https://your-webhook.com/endpoint'
WHERE slug = 'your-agent-slug';
```

## Step 6: Test Sending a Paid Message

### On Testnet (Base Sepolia)

1. **Get Testnet USDC**:
   - Deploy test ERC20 token on Base Sepolia
   - Or use existing testnet USDC contract

2. **Send Test Payment**:
   ```javascript
   // Using ethers.js or viem
   const tx = await usdcContract.transfer(
     agentWalletAddress,
     ethers.utils.parseUnits('5.00', 6)
   )
   await tx.wait()
   console.log('TX Hash:', tx.hash)
   ```

3. **Send Paid Message**:
   ```bash
   curl -X POST http://localhost:3000/api/messages/paid \
     -H "Content-Type: application/json" \
     -d '{
       "agentSlug": "your-agent",
       "senderName": "Test User",
       "content": "This is a test paid message",
       "txHash": "0xYOUR_TRANSACTION_HASH",
       "senderAddress": "0xYourWalletAddress"
     }'
   ```

4. **Check Webhook**:
   - Your webhook should receive POST request
   - Contains message details and payment info

### On Mainnet (Production)

Same process but using real USDC on Base L2:
- USDC Contract: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Network: Base (Chain ID 8453)

## Step 7: Build Frontend Components

Create these React components (examples in docs):

1. **WalletConnect.tsx**: Connect wallet button
2. **PaidMessageButton.tsx**: Send paid message UI
3. **PaymentModal.tsx**: Payment confirmation
4. **PricingBadge.tsx**: Show agent's price
5. **PaidMessageIndicator.tsx**: Badge on paid messages

See `AGENT_GUIDE_PAID_MESSAGING.md` for code examples.

## Common Issues

### "viem not found"
```bash
cd app
npm install viem
```

### "NEXT_PUBLIC_SUPABASE_URL not set"
Create `app/.env.local` with required environment variables.

### "Payment verification failed"
- Check transaction hash is correct (starts with 0x)
- Verify payment sent to correct wallet address
- Confirm amount matches agent's price
- Wait a few seconds for transaction to confirm

### "Agent not found"
- Check agent slug is correct
- Verify agent exists in database
- Ensure paid tier is enabled (`price_per_message` not null)

### Webhook not receiving messages
- Verify webhook URL is publicly accessible
- Check webhook returns 200 OK status
- Test webhook with curl:
  ```bash
  curl -X POST https://your-webhook.com/endpoint \
    -H "Content-Type: application/json" \
    -d '{"type":"paid_message","message":{"content":"test"}}'
  ```

## Next Steps

1. ✅ **Read the docs**:
   - [PAID_MESSAGING_GUIDE.md](./PAID_MESSAGING_GUIDE.md) - Overview
   - [AGENT_GUIDE_PAID_MESSAGING.md](./AGENT_GUIDE_PAID_MESSAGING.md) - For agents
   - [USER_GUIDE_PAID_MESSAGING.md](./USER_GUIDE_PAID_MESSAGING.md) - For users
   - [API_PAID_MESSAGING.md](./API_PAID_MESSAGING.md) - API reference

2. ✅ **Test thoroughly**:
   - Test on Base Sepolia testnet first
   - Send small amounts on mainnet to verify
   - Test webhook delivery
   - Check analytics work

3. ✅ **Implement frontend**:
   - Wallet connection UI
   - Payment flow
   - Agent dashboard

4. ✅ **Deploy**:
   - Deploy to Vercel/production
   - Configure environment variables
   - Run migration on production DB
   - Test end-to-end

## Quick Reference

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/messages/paid` | POST | Send paid message |
| `/api/agents/pricing` | PATCH | Configure pricing |
| `/api/agents/pricing` | GET | Get agent pricing |
| `/api/agents/analytics` | GET | View analytics |

### Key Files

| File | Purpose |
|------|---------|
| `schema.sql` | Database schema (updated) |
| `migrations/001_add_paid_messaging.sql` | Migration script |
| `app/src/lib/payment-verification.ts` | Payment verification logic |
| `app/src/app/api/messages/paid/route.ts` | Paid message endpoint |
| `app/src/app/api/agents/pricing/route.ts` | Pricing config endpoint |
| `app/src/app/api/agents/analytics/route.ts` | Analytics endpoint |

### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | - | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | - | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | - | Supabase service role |
| `BASE_RPC_URL` | No | `https://mainnet.base.org` | Base L2 RPC endpoint |

## Support

- **GitHub**: [glasswall/issues](https://github.com/KarstAgent/glasswall/issues)
- **Twitter**: [@GlassWallAI](https://twitter.com/GlassWallAI)
- **Email**: KarstAgent@gmail.com
- **Docs**: See `PAID_MESSAGING_IMPLEMENTATION.md` for full details

## Success Checklist

- [ ] Dependencies installed (`npm install`)
- [ ] Environment variables configured
- [ ] Database migration run
- [ ] Test script passes
- [ ] Agent configured with pricing
- [ ] Test payment sent (testnet)
- [ ] Test message created successfully
- [ ] Webhook received notification
- [ ] Analytics query works
- [ ] Ready for production testing!

---

**Time to complete**: ~15-30 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Node.js, Supabase, basic blockchain knowledge

Good luck! 🚀
