text
# Getting Your Credentials - Step by Step

You need 5 credentials for your bot to work. This guide shows exactly how to get each one.

---

## Credential #1: Twilio Account SID

**What:** Unique identifier for your Twilio account

### **How to Get:**

1. Go to: https://twilio.com
2. Click: **Sign Up** (top right)
3. Enter email and password
4. Verify your email
5. Click: **Get Started** 
6. Select: **I'm building for myself** (or your preference)
7. Select: **Products → Messaging**
8. Complete signup

### **After Signup:**

1. You're in **Twilio Console**
2. Look at **top left** - you see:
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Auth Token: [show]

text
3. Copy the Account SID (long string starting with AC)
4. Save it somewhere safe

**Example:**
TWILIO_ACCOUNT_SID=AC1234567890abcdefghijklmnopqrst

text

---

## Credential #2: Twilio Auth Token

**What:** Password for accessing Twilio API

### **How to Get:**

1. Same Twilio Console (where you got Account SID)
2. You see: **Auth Token: [show]**
3. Click: **[show]** button
4. The hidden token appears
5. Copy it
6. Save it somewhere safe

**Example:**
TWILIO_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

text

**Important:** This is like your password. Keep it secret!

---

## Credential #3: Supabase Project URL

**You already have Supabase. Good!**

### **How to Get:**

1. Go to: https://supabase.com
2. Log in to your account
3. Click your project
4. Click: **Settings** (bottom left gear icon)
5. Click: **API**
6. Look for: **Project URL**
7. Copy it
8. Save it

**Example:**
SUPABASE_URL=https://abcdefghij.supabase.co

text

---

## Credential #4: Supabase Anon Key

**Also in Supabase**

### **How to Get:**

1. Same place as above (Settings → API)
2. Look for: **Anon Key**
3. Copy it
4. Save it

**Example:**
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

text

---

## Credential #5: Encryption Key

**What:** Secret key for encrypting sensitive data

### **How to Get:**

1. Open VS Code
2. Open Terminal: `Ctrl + `` (backtick key)
3. Paste this command:

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode()) text

4. Press Enter
5. You see output like:
-tZ8Z-5K9_H8w2z3Q4m5n6o7p8q9r0s1t2u3v4w5x6=

text
6. Copy this entire string
7. Save it

**Example:**
ENCRYPTION_KEY=-tZ8Z-5K9_H8w2z3Q4m5n6o7p8q9r0s1t2u3v4w5x6=

text

---

## Put Credentials in .env File

### **Your .env File Should Look Like:**

TWILIO_ACCOUNT_SID=AC1234567890abcdefghijklmnopqrst
TWILIO_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
SUPABASE_URL=https://abcdefghij.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ENCRYPTION_KEY=-tZ8Z-5K9_H8w2z3Q4m5n6o7p8q9r0s1t2u3v4w5x6=

text

**Replace examples with YOUR actual credentials!**

---

## Bonus: Enable WhatsApp on Twilio

1. Go to: https://twilio.com/console
2. Click: **Messaging** (left sidebar)
3. Click: **Try it Out → Send a WhatsApp Message**
4. Look for: **WhatsApp Sandbox**
5. You see a number: `+14155238886`
6. You see a code like: `join XXXXX`

**This is your testing number.**

Seniors will send messages to: `+14155238886`

Then follow the code to get started.

---

## Checklist

Before running your bot, confirm you have:

- [ ] Twilio Account SID (starts with AC)
- [ ] Twilio Auth Token (long string)
- [ ] Supabase Project URL (starts with https://)
- [ ] Supabase Anon Key (long JWT string)
- [ ] Encryption Key (generated from Python)
- [ ] .env file created with all 5 values
- [ ] .env file saved in your project folder

**All 5? You're ready to deploy!**

---

## Troubleshooting

### **"Can't find Account SID"**
Solution:

Make sure you're logged in to Twilio

Go to: twilio.com/console

Look at top left

You should see it there

text

### **"Can't find Auth Token"**
Solution:

Same place as Account SID

Click "show" to reveal it

It's just below Account SID

text

### **"Python command doesn't work"**
Solution:

Make sure Python is installed

In terminal, try: python --version

If not found, install Python from python.org

Then run the encryption key command again

text

### **"Supabase URL is missing"**
Solution:

Make sure you're in your Supabase project

Click "Settings" at bottom

Click "API" on left

First item is Project URL

Copy and paste exactly

text

---

## Security Reminder 🔒

**NEVER share your .env file!**

❌ DON'T:

Put .env on GitHub

Send .env to anyone

Share credentials

Put in code comments

✅ DO:

Keep .env locally only

Add to .gitignore

Regenerate if exposed

Keep secrets secret

text

---

## Ready to Deploy!

Once you have all 5 credentials in .env:

1. Open bot.py
2. Run: `python bot.py`
3. Bot starts locally
4. Test on Twilio Sandbox
5. Deploy to Railway
6. Connect Twilio webhook
7. Create database tables
8. BOT IS LIVE! 🎉

---

## Still Stuck?

**For Twilio issues:**
- Visit: twilio.com/docs
- Search your problem
- Twilio has great docs

**For Supabase issues:**
- Visit: supabase.com/docs
- Very well documented

**For Python issues:**
- Visit: python.org/docs
- Or search on Google

**For your specific bot:**
- Reread QUICK_START_DIRECT.md
- Check bot.py comments
- Check VS_CODE_SETUP_GUIDE.md

---

**You've got this!** 💪

Now go deploy your bot! 🚀