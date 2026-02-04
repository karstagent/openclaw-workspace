# Email Authentication Implementation

## Overview
Implemented complete email-based authentication system for GlassWall, replacing the simple name field with secure email verification and magic link login.

## ✅ Completed Components

### 1. Database Schema (`migrations/add_email_auth.sql`)
- **users** table: Stores registered users with email and verification status
- **verification_tokens** table: Manages email verification and magic link tokens
- Added **user_id** column to messages table
- Row Level Security (RLS) policies configured
- Indexes for performance optimization

### 2. Backend Auth System
- **`/src/lib/auth.ts`** - JWT session management
  - Token creation and verification
  - Session cookie management (httpOnly, secure)
  - 30-day session duration

- **`/src/lib/email.ts`** - Resend email service
  - Verification email templates
  - Magic link email templates
  - Professional HTML email design

### 3. API Endpoints
- **POST `/api/auth/signup`** - Create account and send verification email
- **GET `/api/auth/verify`** - Verify email token and create session
- **POST `/api/auth/login`** - Request magic link for login
- **GET `/api/auth/magic-link`** - Verify magic link and create session
- **POST `/api/auth/logout`** - Clear session
- **GET `/api/auth/session`** - Check authentication status

### 4. Protected Messages API
- Updated **`/api/agents/[slug]/messages`** to require authentication
- Uses session user_id instead of arbitrary sender names
- Email address used as display name

### 5. Frontend UI
- **`AuthModal` component** - Signup/login modal with email input
- Updated **chat page** with:
  - Session management
  - Auth-required banner for logged-out users
  - Logout button in header
  - Automatic auth check on message send
  - Email display instead of name field

## 🔧 Setup Required

### 1. Run Database Migration

**Option A: Supabase SQL Editor (Recommended)**
1. Go to: https://supabase.com/dashboard/project/rjlrhzyiiurdjzmlgcyz/sql/new
2. Copy contents of `migrations/add_email_auth.sql`
3. Paste and click "Run"

**Option B: psql (if available)**
```bash
PGPASSWORD="Fnb7u7M.g6Xcu83" psql \
  "postgresql://postgres.rjlrhzyiiurdjzmlgcyz@aws-0-us-west-2.pooler.supabase.com:5432/postgres" \
  -f migrations/add_email_auth.sql
```

### 2. Get Resend API Key

1. Sign up at https://resend.com
2. Verify your domain (glasswall.xyz) or use test mode
3. Generate API key at https://resend.com/api-keys
4. Update `.env.local`:
   ```
   RESEND_API_KEY=re_your_actual_key_here
   ```

**Domain Verification (for production):**
- Add DNS records in your domain registrar
- From email will be `noreply@glasswall.xyz`
- Resend provides specific DNS records to add

### 3. Add Environment Variables to Vercel

Deploy command will need these environment variables:
```bash
vercel env add RESEND_API_KEY
vercel env add JWT_SECRET
vercel env add EMAIL_FROM
vercel env add NEXT_PUBLIC_BASE_URL
```

Or add via Vercel dashboard:
https://vercel.com/karstagent/glasswall/settings/environment-variables

## 🚀 Deployment Steps

1. **Run migration** (see above)
2. **Get Resend API key** and update .env.local
3. **Test locally:**
   ```bash
   cd app
   npm run dev
   # Visit http://localhost:3000/chat/glasswall
   # Try signup/login flow
   ```
4. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

## 🧪 Testing Checklist

### Email Verification Flow
- [ ] User enters email on signup
- [ ] Verification email received
- [ ] Click verification link
- [ ] Redirected to site with active session
- [ ] Can send messages

### Magic Link Login Flow
- [ ] User enters registered email on login
- [ ] Magic link email received
- [ ] Click magic link
- [ ] Redirected to site with active session
- [ ] Can send messages

### Protected Messaging
- [ ] Logged-out users see auth banner
- [ ] Cannot send messages without login
- [ ] After login, messages work normally
- [ ] Messages show email as sender name

### Session Persistence
- [ ] Session persists across page reloads
- [ ] Logout button clears session
- [ ] Session expires after 30 days

## 📝 Key Design Decisions

1. **Magic Link over Passwords**
   - Simpler UX (no password management)
   - More secure (no password storage/leaks)
   - Better for crypto-native users

2. **httpOnly Cookies for Sessions**
   - XSS-safe (JavaScript can't access)
   - CSRF protection via SameSite=lax
   - Automatic browser management

3. **Email as Display Name**
   - No additional username field needed
   - Familiar to users
   - Easy to identify message senders

4. **Backward Compatibility**
   - `user_id` column is nullable
   - Old messages without user_id still work
   - `sender_name` kept for display

## 🔐 Security Features

- JWT tokens with 30-day expiration
- Verification tokens expire (24h for signup, 15min for login)
- Tokens marked as "used" after redemption
- httpOnly, secure, SameSite cookies
- Rate limiting on signup endpoint (10/hour per IP)
- Email enumeration protection (always return success)
- Row Level Security policies on database

## 📊 Database Schema

### users
```sql
id UUID PRIMARY KEY
email TEXT UNIQUE NOT NULL
email_verified BOOLEAN DEFAULT FALSE
created_at TIMESTAMPTZ
last_login_at TIMESTAMPTZ
```

### verification_tokens
```sql
id UUID PRIMARY KEY
user_id UUID REFERENCES users
token TEXT UNIQUE NOT NULL
type TEXT ('verify_email' | 'magic_link')
expires_at TIMESTAMPTZ NOT NULL
used_at TIMESTAMPTZ
created_at TIMESTAMPTZ
```

### messages (updated)
```sql
-- Added column:
user_id UUID REFERENCES users
-- Existing columns remain unchanged
```

## 🎨 UI/UX Changes

### Before
- Simple "Your name" text input
- Anyone could send messages with any name
- No authentication required

### After
- "Sign Up" / "Log In" buttons when not authenticated
- Modal with email input for signup/login
- Auth banner prompts logged-out users
- Email displayed in header when logged in
- Logout button in header
- Professional email design with branded colors

## 📦 Dependencies Added

```json
{
  "resend": "^4.x",
  "jose": "^5.x",
  "cookie": "^0.6.x"
}
```

## 🔄 Migration Status

- [x] Database schema created
- [ ] Migration executed in Supabase
- [ ] Resend API key obtained
- [ ] Environment variables added to Vercel
- [ ] Deployed to production
- [ ] End-to-end testing completed

## Next Steps

1. **Execute the migration** in Supabase SQL Editor
2. **Sign up for Resend** and get API key
3. **Test locally** to verify email flow
4. **Deploy to Vercel** with environment variables
5. **Test in production** with real emails
6. **Monitor** for any issues

---

## Support & Troubleshooting

### Common Issues

**Email not sending:**
- Check RESEND_API_KEY is set correctly
- Verify domain in Resend dashboard
- Check Resend logs for errors

**Migration fails:**
- Check if tables already exist
- Verify Supabase connection
- Run statements individually if needed

**Session not persisting:**
- Check JWT_SECRET is set
- Verify cookies are enabled in browser
- Check HTTPS in production

**401 Unauthorized:**
- User needs to log in
- Session may have expired
- Check cookie configuration
