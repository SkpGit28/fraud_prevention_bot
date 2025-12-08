📖 DOCUMENT 4: VS_CODE_SETUP_GUIDE.md
text
# VS Code Setup Guide - Step by Step

## What is VS Code?

**VS Code** = A text editor for coding

Think of it like:
- Microsoft Word for writers
- But for programmers

You write code, run it, and deploy it.

---

## Step 1: Install VS Code (If Not Already)

### **Download:**
1. Go to: https://code.visualstudio.com
2. Click: "Download for Windows/Mac/Linux"
3. Install like any software
4. Open VS Code

---

## Step 2: Install Python Extensions

### **In VS Code:**

1. **Look at left sidebar** (icons on left)
2. Click **Extensions icon** (looks like 4 squares)
3. In search box, type: **Python**
4. Click on **Python (Microsoft)** (blue icon)
5. Click **Install**

**Do same for:**
- Search: **Pylance** → Install
- Search: **REST Client** → Install

Now your VS Code is ready for Python!

---

## Step 3: Create Project Folder

### **In VS Code:**

1. Click: **File → Open Folder**
2. Create new folder on your computer: `elder-fraud-bot`
3. Select that folder
4. Click: **Select Folder**

Now you should see empty folder in VS Code left sidebar.

---

## Step 4: Create Files

### **Method 1: Right-click**

Right-click in left sidebar (in empty space)

Click: "New File"

Type filename: bot.py

Press Enter

text

### **Method 2: Keyboard shortcut**

Ctrl + N → New file
Type code → Save as bot.py

text

---

## Step 5: Copy Code into Files

### **Create bot.py:**

1. **Right-click in sidebar → New File**
2. **Name it: bot.py**
3. Open it
4. Copy the bot.py code from QUICK_START_DIRECT.md
5. Paste into VS Code
6. Save: `Ctrl + S`

### **Create requirements.txt:**

1. **Right-click in sidebar → New File**
2. **Name it: requirements.txt**
3. Paste the 7 lines of dependencies
4. Save: `Ctrl + S`

### **Create .env:**

1. **Right-click in sidebar → New File**
2. **Name it: .env**
3. Paste template with your credentials
4. Save: `Ctrl + S`

### **Create Procfile:**

1. **Right-click in sidebar → New File**
2. **Name it: Procfile** (NO .txt)
3. Paste: `web: gunicorn bot:app`
4. Save: `Ctrl + S`

### **Create .gitignore:**

1. **Right-click in sidebar → New File**
2. **Name it: .gitignore**
3. Paste the ignore rules
4. Save: `Ctrl + S`

---

## Step 6: Folder Structure in VS Code

After creating files, you should see:

elder-fraud-bot/
├── bot.py ✅
├── requirements.txt ✅
├── .env ✅ (NEVER share!)
├── Procfile ✅
└── .gitignore ✅

text

If you see all 5 files, you're good! ✅

---

## Step 7: Open Terminal in VS Code

### **Open Terminal:**

Method 1: Ctrl + `
Method 2: View → Terminal

text

You should see bottom panel with terminal.

---

## Step 8: Create Virtual Environment

### **In Terminal:**

For Windows:
python -m venv venv
venv\Scripts\activate

For Mac/Linux:
python3 -m venv venv
source venv/bin/activate

text

After running, you should see `(venv)` at start of terminal line.

(venv) C:\Users\YourName\elder-fraud-bot>

text

---

## Step 9: Install Dependencies

### **In Terminal:**

pip install -r requirements.txt

text

This installs all Python packages your bot needs.

**Takes 2-3 minutes. Wait for "Successfully installed" message.**

---

## Step 10: Get Credentials

### **Twilio Credentials:**

1. Go to: https://twilio.com/console
2. Look for **Account SID** (copy it)
3. Look for **Auth Token** (copy it)
4. Paste in .env file

### **Supabase Credentials:**

1. Go to your Supabase project
2. Click: **Settings → API**
3. Copy: **Project URL**
4. Copy: **Anon Key**
5. Paste in .env file

### **Encryption Key:**

1. In VS Code terminal
2. Run this command:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

text
3. Copy the output
4. Paste in .env file under ENCRYPTION_KEY

---

## Step 11: Test Locally

### **In Terminal:**

python bot.py

text

You should see:

🚀 Elder Fraud Prevention Bot starting...
📍 Webhook: http://localhost:5000/whatsapp

text

✅ Bot is running!

---

## Step 12: Test with Twilio

1. Open separate browser window
2. Go to: https://twilio.com/console/sms/whatsapp/sandbox
3. Send WhatsApp message to: **+14155238886**
4. Message: `join [code]` (shown on page)
5. Then send: `help`
6. You should get bot response!

---

## Step 13: Stop Bot (When Done Testing)

In VS Code terminal:

Ctrl + C

text

Bot stops running.

---

## Step 14: Deploy to Railway

### **First time setup:**

1. In terminal, run:
git init
git add .
git commit -m "Initial commit"

text

2. Go to: https://railway.app
3. Click: "New Project"
4. Select: "Deploy from GitHub"
5. Follow Railway's instructions

6. Railway will auto-detect Python
7. Add environment variables (copy from .env)
8. Deploy!

### **After deploying:**

Railway gives you a public URL:
https://your-project-random.up.railway.app/whatsapp

text

**Copy this URL.**

---

## Step 15: Connect Twilio Webhook

1. Go to: https://twilio.com/console/sms/whatsapp/sandbox
2. Under "When a message comes in"
3. Paste Railway URL: `https://your-project.up.railway.app/whatsapp`
4. Save

**Now Twilio knows where to send messages!**

---

## Step 16: Create Database Tables

1. Go to your Supabase project
2. Click: **SQL Editor**
3. Click: **New Query**
4. Copy & paste the SQL from QUICK_START_DIRECT.md
5. Run

Tables are created! ✅

---

## Useful VS Code Shortcuts

Ctrl + S → Save file
Ctrl + / → Comment/uncomment code
Ctrl + ` → Open/close terminal
Ctrl + Shift + P → Command palette
F5 → Debug (if configured)
Ctrl + H → Find & replace
Ctrl + K + C → Comment code
Ctrl + K + U → Uncomment code

text

---

## Troubleshooting

### **Error: "python not found"**
Solution: Install Python from python.org
Make sure to check: "Add Python to PATH"

text

### **Error: "No module named 'flask'"**
Solution: Run: pip install -r requirements.txt
Make sure virtual environment is activated (see venv)

text

### **Error: "Module 'cryptography' not found"**
Solution: Run: pip install cryptography

text

### **Bot starts but doesn't respond**
Solution:

Check .env file has all 5 variables

Check Twilio credentials are correct

Check Twilio webhook URL is correct

Restart bot: Ctrl + C then python bot.py

text

### **Can't connect to Supabase**
Solution:

Check SUPABASE_URL in .env

Check SUPABASE_KEY in .env

Make sure Supabase project is active

Check internet connection

text

---

## File Checklist

Before deploying, confirm you have:

elder-fraud-bot/
✅ bot.py (480+ lines)
✅ requirements.txt (7 lines)
✅ .env (5 variables filled)
✅ Procfile (1 line)
✅ .gitignore (prevent .env upload)
✅ venv folder (virtual environment)
✅ .git folder (git initialized)

text

---

## Success Checklist

- [x] Installed VS Code
- [x] Installed Python extensions
- [x] Created project folder
- [x] Created 5 files (bot.py, requirements.txt, .env, Procfile, .gitignore)
- [x] Opened terminal
- [x] Created virtual environment
- [x] Installed dependencies
- [x] Got credentials (Twilio, Supabase, Encryption key)
- [x] Tested locally (python bot.py)
- [x] Tested with Twilio Sandbox
- [x] Initialized git
- [x] Deployed to Railway
- [x] Set Twilio webhook
- [x] Created database tables
- [x] BOT IS LIVE! ✅

---

## Your Bot is Now Live! 🎉

Next steps:

1. **Share bot number** with seniors (Twilio gives you a number)
2. **Tell them to add it on WhatsApp**
3. **They can use it 24/7**
4. **No download needed**
5. **Just messaging interface**

---

## Support Resources

**For VS Code questions:**
- Search: "VS Code tutorial"
- Official docs: https://code.visualstudio.com/docs

**For Python questions:**
- Search: "Python tutorial"
- Official docs: https://python.org/docs

**For deployment questions:**
- Railway docs: https://docs.railway.app
- Twilio docs: https://www.twilio.com/docs

**For your specific bot:**
- Check bot.py comments
- Reread QUICK_START_DIRECT.md
- Check Railway logs (click your project → Logs)

---

## You Did It! 🚀

You've successfully:
✅ Set up VS Code
✅ Written production Python code
✅ Created database
✅ Deployed to cloud
✅ Integrated with WhatsApp

**Your Elder Fraud Prevention Bot is LIVE!**

Seniors can now:
- Check suspicious numbers
- Get recovery guides if scammed
- Report scams to community
- Access help 24/7

**All from WhatsApp. All for free. All to protect them.**

🙏 Great work!