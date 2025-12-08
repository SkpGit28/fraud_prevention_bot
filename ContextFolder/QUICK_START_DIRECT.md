# QUICK START – Direct Instructions (1 Hour to Live)

## What Is a “Bot”?

A **WhatsApp bot is not an app or a website.**  
It is a **backend service** (Python code) that:

- Listens for incoming WhatsApp messages  
- Processes those messages  
- Sends automated responses back  

It behaves like a **chatbot inside WhatsApp** – seniors send it messages, and it replies with guidance.

---

## How WhatsApp Integration Works

Conceptual flow:

- **Senior’s Phone (WhatsApp app)**  
  ↕ (sends and receives messages)  
- **Twilio Servers (WhatsApp API gateway)**  
  ↕ (forwards and returns messages)  
- **Your Python Bot (hosted on Railway)**  

Message lifecycle:

1. Senior sends a message in WhatsApp.  
2. Twilio forwards the message to your bot endpoint.  
3. Your bot processes the message and prepares a response.  
4. Twilio delivers that response back to the senior in WhatsApp.

---

## What You Actually Need to Build

You **do not need to create a separate app or website** for the bot itself.

**Your bot consists of:**

- Backend Python code running on Railway  
- Incoming messages handled through the Twilio API  
- Outgoing replies sent back via the Twilio API  
- Data stored in Supabase (with encryption where needed)  

**Optional extras you can add:**

- A **dashboard** (for example, React app on Vercel) to:
  - View scam reports  
  - Track recovery cases  
  - See statistics and trends  

---

## Step 1: Install VS Code Extensions (≈5 min)

Open VS Code and install these extensions:

1. **Python (by Microsoft)**  
   - Open the Extensions panel (left sidebar)  
   - Search for “Python”  
   - Install the official extension by Microsoft  

2. **REST Client (by Humao)**  
   - Search for “REST Client”  
   - Install it (used to test your API directly from VS Code)  

3. **Pylance (by Microsoft)**  
   - Search for “Pylance”  
   - Install it to get better Python language support  

---

## Step 2: Create Project Folder in VS Code

1. Open VS Code.  
2. Go to **File → Open Folder**.  
3. Create a new folder named: `elder-fraud-bot`.  
4. Open that folder in VS Code.  

You should now see an empty project folder in the left sidebar.

---

## Step 3: Create Files in VS Code

### Create `bot.py`

1. In the left sidebar, right‑click inside the project.  
2. Click **New File**.  
3. Name the file: `bot.py`.  
4. Paste your bot logic (provided separately) into this file.  
5. Save with **Ctrl + S**.

---

### Create `requirements.txt`

1. Right‑click in the left sidebar.  
2. Click **New File**.  
3. Name it: `requirements.txt`.  
4. Add the following dependencies:

Flask==2.3.0
python-dotenv==1.0.0
twilio==8.10.0
supabase==2.0.0
cryptography==41.0.0
requests==2.31.0
gunicorn==21.2.0


---

### Create `.env`

1. Right‑click in the left sidebar.  
2. Click **New File**.  
3. Name it: `.env`.  
4. Add the following and replace the placeholders with your real credentials:

TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
ENCRYPTION_KEY=your_encryption_key_here


#### How to obtain these values

**Twilio:**

1. Log in to the Twilio console (`twilio.com/console`). [web:1]  
2. Copy your **Account SID**.  
3. Copy your **Auth Token**.  

**Supabase:**

1. Open your Supabase project.  
2. Go to **Settings → API**.  
3. Copy the **Project URL**.  
4. Copy the **Anon (public) Key**.  

**Encryption key:**

1. Open the terminal in VS Code (**Ctrl + `**).  
2. Run:

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"


3. Copy the printed key and paste it as `ENCRYPTION_KEY`.

---

### Create `Procfile`

1. Right‑click in the left sidebar.  
2. Click **New File**.  
3. Name it: `Procfile` (no `.txt` extension).  
4. Add:

web: gunicorn bot:app


---

### Create `.gitignore`

1. Right‑click in the left sidebar.  
2. Click **New File**.  
3. Name it: `.gitignore`.  
4. Add:

.env
pycache/
venv/
*.pyc
.DS_Store
node_modules/
.idea/
.vscode/


---

## Step 4: Test Locally in VS Code

1. Open the terminal in VS Code (**Ctrl + `**).  
2. Create a virtual environment:

python -m venv venv


3. Activate the environment:  

- **Windows:**

  ```
  venv\Scripts\activate
  ```

- **macOS / Linux:**

  ```
  source venv/bin/activate
  ```

4. Install dependencies:

pip install -r requirements.txt


5. Run the bot:

python bot.py


You should see logs indicating the bot has started, including a webhook like:

🚀 Elder Fraud Prevention Bot starting...
📍 Webhook: http://localhost:5000/whatsapp
---

## Step 5: Test with Twilio Sandbox (WhatsApp)

1. Go to the WhatsApp sandbox page in your Twilio console:  
   `https://www.twilio.com/console/sms/whatsapp/sandbox`. [web:1]  
2. From your phone, send a WhatsApp message to the sandbox number: `+14155238886`.  
3. First send the **join code** shown on the sandbox page (for example, `join xxxx`).  
4. Then send: `help`.  

If everything is wired correctly, the bot should respond in WhatsApp with its help menu.

---

## Step 6: Deploy to Railway

1. In the VS Code terminal, initialize Git:

git init
git add .
git commit -m "Initial commit: Elder fraud bot"

2. Push this repository to GitHub (or another supported Git provider).  
3. Go to `railway.app` in your browser.  
4. Click **New Project**.  
5. Choose **Deploy from GitHub** and select your repo.  
6. Railway will detect the Python project automatically.  
7. Add environment variables in Railway:

- `TWILIO_ACCOUNT_SID`  
- `TWILIO_AUTH_TOKEN`  
- `SUPABASE_URL`  
- `SUPABASE_KEY`  
- `ENCRYPTION_KEY`  

8. After deployment, Railway will give you a public URL for your app, for example:

https://your-project.up.railway.app/whatsapp

---

## Step 7: Connect Railway to Twilio

1. Go again to the Twilio WhatsApp sandbox page:  
`https://www.twilio.com/console/sms/whatsapp/sandbox`. [web:1]  
2. Find the field **“When a message comes in”**.  
3. Paste your Railway webhook URL, such as:

https://your-project.up.railway.app/whatsapp


4. Save the configuration.

At this point, **your bot is live** and Twilio will forward incoming WhatsApp messages to your Railway endpoint.

---

## Step 8: Create Database Tables in Supabase

1. Open your Supabase project.  
2. Go to **SQL Editor**.  
3. Click **New Query**.  
4. Paste and run the following SQL to create your tables:

CREATE TABLE scam_reports (
id BIGSERIAL PRIMARY KEY,
reporter_phone_encrypted TEXT,
reported_phone_encrypted TEXT,
scam_type VARCHAR(100),
message_encrypted TEXT,
votes INT DEFAULT 1,
status VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW(),
expires_at TIMESTAMP
);

CREATE TABLE recovery_cases (
id BIGSERIAL PRIMARY KEY,
phone_encrypted TEXT,
amount VARCHAR(50),
method VARCHAR(50),
status VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interactions (
id BIGSERIAL PRIMARY KEY,
phone_encrypted TEXT,
intent VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW()
);

These tables store scam reports, recovery case details, and interaction logs.

---

## Step 9: Test on Real WhatsApp

Your bot is now fully wired up.

From your own WhatsApp (connected to the Twilio number), try sending:

- `help`  
- `Check +91-9876543210`  
- `Scammed ₹50000 via UPI`  
- `Report romance scam details`  

The bot should respond appropriately for each message.

---

## DONE! Your Bot Is Live 🎉

You now have:

- ✅ Code set up in VS Code  
- ✅ Bot running on Railway  
- ✅ Database configured on Supabase  
- ✅ WhatsApp integration through Twilio  
- ✅ Recovery‑guide behavior working  
- ✅ Infrastructure cost effectively at ₹0 (using free tiers where available)  

**Users (especially seniors) can now:**

1. Check suspicious phone numbers.  
2. Get step‑by‑step recovery guidance after a scam.  
3. Report scams to help protect others.  
4. Access government helpline and portal information.

---

## Next Steps

**Share your bot:**

1. Give the Twilio WhatsApp number to family and trusted contacts.  
2. Ask them to save and message it in WhatsApp.  

**Promote:**

1. Share in relevant WhatsApp groups.  
2. Inform NGOs and community organizations.  
3. Reach out to government bodies (such as I4C) to collaborate.  
4. Create case studies showing successful recoveries or prevented scams.  

**Scale:**

1. Collect user feedback and logs to improve responses.  
2. Add and refine features in the bot flow.  
3. Engage with banks and fintech partners.  
4. Explore government or institutional contracts to grow impact.

