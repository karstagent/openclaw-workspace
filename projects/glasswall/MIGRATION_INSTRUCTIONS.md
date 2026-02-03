# Database Migration Instructions

## ⚠️ IMPORTANT: Execute this migration in Supabase SQL Editor

The database schema needs to be updated to support paid messaging.

### Steps:

1. **Go to Supabase SQL Editor:**
   https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new

2. **Copy the SQL from:**
   `/migrations/001_add_paid_messaging.sql`

3. **Paste and Run** in the SQL Editor

4. **Verify** by running:
   ```bash
   curl https://glasswall.xyz/api/migrate
   ```

### What the migration does:

- ✅ Adds `price_per_message`, `polling_interval_minutes`, `last_heartbeat_at` to `agents` table
- ✅ Adds `is_paid`, `payment_tx_hash` to `messages` table
- ✅ Creates `payments` table for payment records
- ✅ Sets up indexes for performance
- ✅ Enables RLS policies

### Alternative: Use the migration script

If you have access to a Supabase CLI or psql:

```bash
cd /Users/karst/.openclaw/workspace/projects/glasswall
# Review the SQL first
cat migrations/001_add_paid_messaging.sql

# Then execute in Supabase SQL Editor (no automated way without password)
```

## After Migration

Once migration is complete:

1. **Update GlassWall agent** with payment settings:
   ```sql
   UPDATE agents 
   SET 
     price_per_message = 0.10,
     payment_address = 'YOUR_BASE_ADDRESS_HERE',
     polling_interval_minutes = 30
   WHERE slug = 'glasswall';
   ```

2. **Test the feature:**
   - Visit https://glasswall.xyz/chat/glasswall
   - Connect wallet
   - Try sending a paid message
   - Verify webhook delivery

## Deployment Status

- ✅ Frontend code pushed to GitHub
- ✅ Vercel auto-deployment triggered
- ⏳ Database migration pending (manual step)
- ⏳ Agent configuration pending (set payment_address)

