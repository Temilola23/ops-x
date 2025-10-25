# Resend Email Service Setup (5 minutes)

## What is Resend?

**Resend** is a modern email API for developers. We're using it to send OTP codes for authentication and team invitations.

**Free Tier**: 3,000 emails/month, 100 emails/day (perfect for hackathons!)

---

## Step 1: Create Resend Account

1. Go to: https://resend.com/signup
2. Sign up with GitHub or email
3. Verify your email

---

## Step 2: Get API Key

1. After login, go to: https://resend.com/api-keys
2. Click **"Create API Key"**
3. Name it: `ops-x-hackathon`
4. Permission: **Full Access**
5. Click **"Add"**
6. **COPY THE KEY** (starts with `re_...`) - you won't see it again!

Example: `re_123abc456def789ghi012jkl345mno678pqr`

---

## Step 3: Add to Environment

### Option A: Update scripts/.env manually
```bash
# Open scripts/.env
nano scripts/.env

# Add these lines:
RESEND_API_KEY=re_your_actual_key_here
RESEND_FROM_EMAIL=OPS-X <onboarding@resend.dev>
```

### Option B: Run create_env.py
```bash
cd scripts
python3 create_env.py
# Then manually edit scripts/.env to add your Resend key
```

---

## Step 4: Verify Domain (Optional - for production)

For hackathon, you can use Resend's test domain: **`onboarding@resend.dev`**

For production:
1. Go to: https://resend.com/domains
2. Click **"Add Domain"**
3. Follow DNS setup instructions

---

## Step 5: Test Email Service

```bash
cd /Users/temilolaolowolayemo/Documents/GitHub/ops-x
source venv/bin/activate
cd backend
python3 integrations/email_service.py
```

**Expected output:**
```
Testing email service...
RESEND_API_KEY configured: True
✅ OTP email sent to test@example.com (ID: abc123)
✅ Team invite email sent to team@example.com (ID: def456)
```

---

## Step 6: Restart Backend

```bash
cd /Users/temilolaolowolayemo/Documents/GitHub/ops-x
source venv/bin/activate
cd backend
python3 main.py
```

---

## Email Templates

### OTP Email
- Subject: `Your OPS-X Verification Code: 123456`
- Beautiful gradient design (purple/violet)
- Large OTP code display
- 10-minute expiry warning

### Team Invite Email
- Subject: `🎉 You're invited to join [Project Name] on OPS-X!`
- Pink/red gradient design
- Project info + role badge
- 30-minute expiry warning

---

## Troubleshooting

### "email-validator is not installed"
```bash
pip install "pydantic[email]"
```

### "RESEND_API_KEY not set"
- Check `scripts/.env` file exists
- Verify `RESEND_API_KEY=re_...` is present
- Restart backend after adding key

### "Email not received"
1. Check spam folder
2. Verify email address is correct
3. Check Resend logs: https://resend.com/emails
4. For hackathon: OTP will print to console as fallback

---

## Alternative: Test with Console OTP

If you don't want to set up Resend right now, the system has a fallback:

1. Don't set `RESEND_API_KEY`
2. OTPs will print to backend console
3. Copy OTP from console and use in frontend

**Backend log example:**
```
🔐 FALLBACK OTP for user@example.com: 123456
```

---

## Dashboard & Monitoring

View sent emails: https://resend.com/emails

Check:
- Email delivery status
- Open rates (if enabled)
- Bounces
- API errors

---

## Rate Limits

**Free tier limits:**
- 3,000 emails/month
- 100 emails/day
- No credit card required

**For hackathon:** More than enough!

**If you hit limits:** Emails will fail gracefully, OTPs will print to console.

---

## Production Considerations

For production deployment:

1. **Verify your domain** (better deliverability)
2. **Add SPF/DKIM records** (prevent spam)
3. **Monitor bounce rates** (clean your email list)
4. **Upgrade plan** if needed (>3K emails/month)
5. **Add unsubscribe links** (team invites)

---

## Quick Start Commands

```bash
# 1. Install dependencies
cd /Users/temilolaolowolayemo/Documents/GitHub/ops-x
source venv/bin/activate
pip install resend "pydantic[email]"

# 2. Add API key to scripts/.env
echo "RESEND_API_KEY=re_your_key_here" >> scripts/.env

# 3. Test
cd backend
python3 integrations/email_service.py

# 4. Start backend
python3 main.py
```

---

**Questions?** Check Resend docs: https://resend.com/docs

