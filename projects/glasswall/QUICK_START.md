# Email Auth Quick Start - Action Required

## Status: 🟡 Deployed, 2 Manual Steps Needed

**Deployment:** ✅ LIVE at https://glasswall.xyz
**Build:** ✅ Successful
**Code:** ✅ Pushed to GitHub
**Env Vars:** ✅ Added to Vercel

## What You Need to Do

### Step 1: Run Database Migration (5 min)

```bash
# Open this URL in browser:
https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new

# Then copy/paste entire file:
EMAIL_AUTH_MIGRATION.sql

# Click "Run"
```

### Step 2: Get Resend API Key (10 min)

```bash
# 1. Sign up at resend.com (free tier)
# 2. Get API key from: https://resend.com/api-keys
# 3. Update in Vercel: https://vercel.com/karstagent/glasswall/settings/environment-variables
#    Find: RESEND_API_KEY
#    Replace placeholder with real key
# 4. Redeploy (or wait for auto-deploy)
```

### Step 3: Test (5 min)

```bash
# 1. Visit: https://glasswall.xyz/chat/glasswall
# 2. Click "Sign Up"
# 3. Enter your email
# 4. Check email inbox
# 5. Click verification link
# 6. Try sending a message
```

## What Changed

**Before:** Simple name field, no authentication
**After:** Email signup/login with magic links

**User Experience:**
- Enter email → Receive verification link → Click → Logged in
- No passwords needed
- 30-day sessions
- Email shown as sender name

## Files to Reference

- `DEPLOYMENT_COMPLETE_EMAIL_AUTH.md` - Full deployment details
- `EMAIL_AUTH_IMPLEMENTATION.md` - Technical implementation
- `SETUP_COMPLETE.md` - Detailed setup instructions
- `EMAIL_AUTH_MIGRATION.sql` - Database migration (copy this to Supabase)

## Quick Test Command

```bash
# After completing steps 1-2, test the deployment:
curl https://glasswall.xyz/api/auth/session
# Should return: {"authenticated":false}
```

---

**Time to complete:** ~20 minutes
**Priority:** 🔴 High (feature won't work until completed)
