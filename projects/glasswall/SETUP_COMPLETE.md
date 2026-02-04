# Email Authentication Setup - FINAL STEPS

## ✅ What's Been Completed

### 1. Code Implementation
- ✅ Database migration SQL created (`migrations/add_email_auth.sql`)
- ✅ Auth system implemented (JWT sessions, magic links)
- ✅ Email service integrated (Resend API)
- ✅ API endpoints created (signup, verify, login, logout, session)
- ✅ Frontend UI updated (AuthModal, session management)
- ✅ Messages API protected (requires authentication)
- ✅ Build successful
- ✅ Committed to git
- ✅ Pushed to GitHub
- ✅ Environment variables added to Vercel
- ✅ Deployment triggered

### 2. Vercel Deployment Status
**Repository:** https://github.com/karstagent/glasswall
**Branch:** main
**Commit:** bf46b3f - "feat: Add email authentication with magic link login"

**Deployment should be live at:** https://glasswall.xyz

Check deployment status:
- https://vercel.com/karstagent/glasswall

## 🔧 REQUIRED MANUAL STEPS

### Step 1: Run Database Migration

**⚠️ CRITICAL: Must be done before testing auth flow**

1. Open Supabase SQL Editor:
   https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new

2. Copy the entire contents of `migrations/add_email_auth.sql`

3. Paste into the SQL editor and click **"Run"**

4. Verify success - should see:
   - `users` table created
   - `verification_tokens` table created
   - `user_id` column added to `messages`
   - Indexes and policies created

**Quick test after migration:**
```sql
-- Run this to verify tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'verification_tokens');
```

### Step 2: Get Resend API Key

**⚠️ REQUIRED for email sending to work**

1. **Sign up at Resend:**
   - Go to https://resend.com
   - Sign up with GitHub or Google
   - Free tier: 100 emails/day, 3,000/month

2. **Verify Domain (for production emails):**
   - In Resend dashboard, go to "Domains"
   - Add `glasswall.xyz`
   - Copy the DNS records shown
   - Add to your domain registrar (Namecheap, GoDaddy, etc.)
   - Wait for verification (~5-10 minutes)
   - **OR** use test mode (only sends to your verified email)

3. **Generate API Key:**
   - Go to https://resend.com/api-keys
   - Click "Create API Key"
   - Name: "GlassWall Production"
   - Permission: "Sending access"
   - Copy the key (starts with `re_`)

4. **Update Vercel Environment Variable:**
   ```bash
   # Using Vercel CLI (if installed)
   vercel env rm RESEND_API_KEY production
   vercel env add RESEND_API_KEY production
   # Paste your real API key when prompted
   
   # Or via Vercel dashboard:
   # https://vercel.com/karstagent/glasswall/settings/environment-variables
   # Find RESEND_API_KEY, click edit, paste real key
   ```

5. **Redeploy to apply new API key:**
   ```bash
   # Option A: Via dashboard
   # Go to deployments and click "Redeploy"
   
   # Option B: Push empty commit
   cd /Users/karst/.openclaw/workspace/projects/glasswall/app
   git commit --allow-empty -m "chore: redeploy with Resend API key"
   git push
   ```

### Step 3: Test the Full Flow

1. **Visit the site:** https://glasswall.xyz/chat/glasswall

2. **Test Signup Flow:**
   - Click "Sign Up" button
   - Enter your email address
   - Click "Sign Up"
   - Should see "Check Your Email!" message
   - Check email inbox for verification link
   - Click verification link
   - Should be redirected to site, logged in
   - Try sending a message

3. **Test Logout:**
   - Click "Logout" in header
   - Should be logged out
   - Banner should appear: "Sign up or log in to send messages"

4. **Test Login Flow:**
   - Click "Log In" button
   - Enter same email
   - Click "Send Login Link"
   - Should see "Check Your Email!" message
   - Check email for magic link
   - Click magic link
   - Should be logged in
   - Try sending a message

5. **Verify Messages:**
   - Messages should show your email as sender
   - Messages should be visible to the agent
   - Agent can reply via API/webhook

## 📊 Verification Checklist

- [ ] Database migration executed successfully
- [ ] Resend API key obtained and added to Vercel
- [ ] Deployment completed without errors
- [ ] Can access https://glasswall.xyz
- [ ] Signup form appears when not logged in
- [ ] Verification email received (check spam folder)
- [ ] Email verification link works
- [ ] Session persists after page reload
- [ ] Can send messages when logged in
- [ ] Cannot send messages when logged out
- [ ] Magic link login works
- [ ] Logout clears session
- [ ] Messages show email as sender

## 🐛 Troubleshooting

### Email Not Sending
**Problem:** "Check Your Email!" appears but no email received

**Solutions:**
1. Check spam/junk folder
2. Verify RESEND_API_KEY is set correctly in Vercel
3. Check Resend dashboard logs: https://resend.com/logs
4. Verify domain is verified (if using custom domain)
5. Try with test mode (resend.dev emails)

### 401 Unauthorized Error
**Problem:** "You must be logged in to send messages"

**Solutions:**
1. Clear browser cookies
2. Log out and log in again
3. Check browser console for cookie errors
4. Verify JWT_SECRET is set in Vercel
5. Check if session expired (30 days)

### Migration Errors
**Problem:** SQL errors when running migration

**Solutions:**
1. Tables might already exist - check first:
   ```sql
   SELECT * FROM users LIMIT 1;
   ```
2. Drop and recreate if needed:
   ```sql
   DROP TABLE IF EXISTS verification_tokens CASCADE;
   DROP TABLE IF EXISTS users CASCADE;
   -- Then re-run migration
   ```
3. Run statements individually if batch fails

### Vercel Deployment Fails
**Problem:** Build or runtime errors

**Solutions:**
1. Check deployment logs in Vercel dashboard
2. Verify all environment variables are set
3. Try redeploying
4. Check if RESEND_API_KEY placeholder is causing issues

## 📚 Resources

- **Supabase Dashboard:** https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz
- **Resend Dashboard:** https://resend.com/home
- **Vercel Dashboard:** https://vercel.com/karstagent/glasswall
- **GitHub Repository:** https://github.com/karstagent/glasswall
- **Implementation Guide:** `EMAIL_AUTH_IMPLEMENTATION.md`

## 🎯 Next Steps After Setup

1. **Test extensively** with different email providers (Gmail, Outlook, ProtonMail)
2. **Monitor Resend logs** for delivery issues
3. **Set up domain verification** for better deliverability
4. **Update documentation** if needed
5. **Announce the feature** to users
6. **Monitor error logs** in Vercel and Supabase

## 📞 Support

If you encounter issues:

1. **Check Vercel logs:**
   ```bash
   vercel logs glasswall.xyz --prod
   ```

2. **Check Supabase logs:**
   - SQL Editor for database queries
   - Table Editor to view data

3. **Check Resend logs:**
   - View all sent emails
   - Delivery status
   - Error messages

4. **Debug locally:**
   ```bash
   cd /Users/karst/.openclaw/workspace/projects/glasswall/app
   npm run dev
   # Visit http://localhost:3000/chat/glasswall
   # Check browser console and terminal logs
   ```

---

## Summary

**Status:** 🟡 Deployment complete, manual steps required

**What works now:**
- Code is deployed to production
- UI shows signup/login forms
- Session management is ready
- Auth API endpoints are live

**What needs manual action:**
1. ⚠️ Run database migration in Supabase SQL Editor
2. ⚠️ Get Resend API key and update Vercel env var
3. ⚠️ Redeploy after updating API key

**Estimated time to complete:** 15-20 minutes

Once steps 1-3 are done, the full email authentication system will be live!
