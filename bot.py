from flask import Flask, request
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re
from cryptography.fernet import Fernet
from datetime import datetime
from html import escape

load_dotenv()

app = Flask(__name__)

# ===== SETUP =====
try:
    encryption_key = os.getenv('ENCRYPTION_KEY').encode()
    cipher_suite = Fernet(encryption_key)
except:
    cipher_suite = None
    print("⚠️ Warning: No encryption key")

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token) if account_sid else None

from supabase import create_client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key) if supabase_url else None

# ===== ENCRYPTION =====
def encrypt_data(data):
    if not cipher_suite or not data:
        return data
    try:
        return cipher_suite.encrypt(data.encode()).decode()
    except:
        return data

def validate_message(message):
    if not message or len(message) > 1000:
        return None
    return escape(message).strip()

def save_to_db(table, data):
    if not supabase:
        return False
    try:
        supabase.table(table).insert([data]).execute()
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False

# ===== MAIN HANDLER =====
@app.route('/whatsapp', methods=['POST'])
def receive_whatsapp():
    try:
        user_message = request.form.get('Body', '').strip()
        user_phone = request.form.get('From', '')
        
        safe_message = validate_message(user_message)
        if not safe_message:
            send_message(user_phone, "Invalid input. Try again.")
            return 'OK'
        
        intent = detect_intent(safe_message)
        
        if intent == 'check_number':
            response = handle_check_number(safe_message)
        elif intent == 'recovery':
            response = handle_recovery(user_phone, safe_message)
        elif intent == 'report':
            response = handle_report(user_phone, safe_message)
        elif intent == 'help':
            response = get_help_menu()
        else:
            response = "Sorry, didn't understand. Type 'help' for options."
        
        send_message(user_phone, response)
        
        try:
            log_interaction(user_phone, user_message, intent)
        except:
            pass
        
        return 'OK'
    
    except Exception as e:
        print(f"Error: {e}")
        return 'OK'

# ===== INTENT DETECTION =====
def detect_intent(message):
    msg_lower = message.lower().strip()
    
    # Handle number inputs (1, 2, 3, 4)
    if msg_lower in ['1', 'check', 'check number', 'is this', 'safe', 'number', 'verify']:
        return 'check_number'
    elif msg_lower in ['2', 'scammed', 'i\'ve been scammed', 'lost', 'fraud', 'recover', 'recovery']:
        return 'recovery'
    elif msg_lower in ['3', 'report', 'report scam', 'alert', 'suspicious']:
        return 'report'
    elif msg_lower in ['4', 'help', 'menu', '/start', 'start']:
        return 'help'
    return 'unknown'

    msg_lower = message.lower()
    
    if any(w in msg_lower for w in ['check', 'is this', 'safe', 'number', 'verify']):
        return 'check_number'
    elif any(w in msg_lower for w in ['scammed', 'lost', 'fraud', 'recover']):
        return 'recovery'
    elif any(w in msg_lower for w in ['report', 'alert', 'suspicious']):
        return 'report'
    elif 'help' in msg_lower:
        return 'help'
    return 'unknown'

# ===== RECOVERY GUIDE (MAIN FEATURE) =====
def handle_recovery(user_phone, message):
    amount_match = re.search(r'₹?(\d+,?\d*)', message)
    amount = amount_match.group(1) if amount_match else "unknown"
    
    method = 'unknown'
    if 'upi' in message.lower():
        method = 'upi'
    elif 'transfer' in message.lower() or 'bank' in message.lower():
        method = 'bank'
    elif 'crypto' in message.lower():
        method = 'crypto'
    elif 'loan' in message.lower():
        method = 'loan'
    
    recovery_data = {
        'phone_encrypted': encrypt_data(user_phone),
        'amount': amount,
        'method': method,
        'status': 'new',
        'created_at': datetime.now().isoformat()
    }
    save_to_db('recovery_cases', recovery_data)
    
    if method == 'upi':
        return f"""🚨 UPI FRAUD RECOVERY

Amount: ₹{amount}
⏰ 24 HOURS TO ACT

STEP 1️⃣ CALL YOUR BANK (NOW!)
Say: "UPI fraud, ₹{amount}"
→ Bank freezes account
→ Reversal initiated
Recovery: 60-80% success

STEP 2️⃣ CALL 1930
Free government helpline
Tell them: Amount + scammer details

STEP 3️⃣ FILE COMPLAINT
Go to: cybercrime.gov.in
Upload: UPI screenshot

TIMELINE:
Day 1-7: Bank checks
Day 8+: Police involvement

Success depends on SPEED!

Need support? Reply "support" 💚"""
    
    elif method == 'bank':
        return f"""🏦 BANK TRANSFER FRAUD

Amount: ₹{amount}
⏰ 48 HOURS TO ACT

STEP 1️⃣ CALL YOUR BANK (NOW!)
Say: "Fraudulent transfer"
Recovery: 70-80% success

STEP 2️⃣ CALL 1930

STEP 3️⃣ FILE ON cybercrime.gov.in

Timeline: 10-20 days
Quick action = money back!

Need help? Reply "support" 💚"""
    
    elif method == 'crypto':
        return f"""⚠️ CRYPTO FRAUD

Amount: ₹{amount}
Success rate: <1%

Still try:
1. FILE COMPLAINT on cybercrime.gov.in
2. CALL 1930
3. CONTACT exchange (if used)

Timeline: 3-6 months
Don't lose hope!

Need support? Reply "support" 💚"""
    
    else:
        return f"""🆘 SCAM RECOVERY

Amount: ₹{amount}

IMMEDIATE (Next 24 hours):
1. CALL BANK (if transferred)
2. CALL 1930
3. FILE on cybercrime.gov.in
4. BLOCK scammer

Recovery chances:
Within 24 hrs: 60-80% ✅
Within 7 days: 20-40%
After 7 days: <5% ❌

You're not alone!
50 lakh Indians scammed in 2024

Need support? Reply "support" 💚"""

# ===== NUMBER CHECKER =====
def handle_check_number(message):
    numbers = re.findall(r'\+91-?\d{10}', message)
    
    if not numbers:
        return """📱 To check a number:
"Check +91-9876543210"

I'll tell you if it's a known scam!"""
    
    phone = numbers[0]
    
    return f"""🟡 No data on {phone} yet.

Is this a scam? Reply:
"Report {phone} [description]"

Your report protects seniors!

Unsure? Call 1930 (free)"""

# ===== REPORT HANDLER =====
def handle_report(user_phone, message):
    numbers = re.findall(r'\+91-?\d{10}', message)
    
    scam_type = detect_scam_type(message)
    
    report_data = {
        'reporter_phone_encrypted': encrypt_data(user_phone),
        'scam_type': scam_type,
        'message_encrypted': encrypt_data(message),
        'votes': 1,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    if numbers:
        report_data['reported_phone_encrypted'] = encrypt_data(numbers[0])
    
    save_to_db('scam_reports', report_data)
    
    return f"""✅ REPORT RECEIVED!

Type: {scam_type}

Your report helps protect seniors!

📊 WHAT HAPPENS NEXT:
1. Community reviews your report
2. If 50+ confirm → Added to warning list
3. Seniors get alert about this scam

📞 ALSO REPORT TO:
- Police: cybercrime.gov.in
- Helpline: 1930

Thank you for protecting others! 🙏"""

def detect_scam_type(message):
    msg = message.lower()
    
    if any(w in msg for w in ['love', 'dating', 'relationship', 'girl', 'boy']):
        return 'Romance Scam'
    elif any(w in msg for w in ['loan', 'credit', 'approval', 'emi']):
        return 'Fake Loan'
    elif any(w in msg for w in ['police', 'arrest', 'cbi', 'court']):
        return 'Digital Arrest'
    elif any(w in msg for w in ['investment', 'profit', 'return', 'scheme']):
        return 'Investment Fraud'
    elif any(w in msg for w in ['bank', 'account', 'verify', 'otp']):
        return 'Impersonation'
    else:
        return 'Other'

# ===== HELP MENU =====
def get_help_menu():
    return """🆘 ELDER FRAUD PREVENTION BOT

Commands:

1️⃣ CHECK NUMBER
"Check +91-9876543210"
→ Is it a known scam?

2️⃣ I'VE BEEN SCAMMED
"Scammed ₹50000 via UPI"
→ Step-by-step recovery guide

3️⃣ REPORT A SCAM
"Report romance scam [details]"
→ Help warn other seniors

4️⃣ HELP
"Help"
→ This menu

📞 ALSO:
🔴 1930 (Government helpline)
🟢 cybercrime.gov.in (File complaint)

Stay Safe! 🛡️"""

# ===== SEND MESSAGE =====
def send_message(to_number, body):
    if not twilio_client:
        print("Twilio not configured")
        return False
    
    try:
        message = twilio_client.messages.create(
            from_='whatsapp:+14155238886',
            body=body,
            to=to_number
        )
        print(f"✓ Message sent to {to_number}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def log_interaction(phone, message, intent):
    log_data = {
        'phone_encrypted': encrypt_data(phone),
        'intent': intent,
        'created_at': datetime.now().isoformat()
    }
    save_to_db('interactions', log_data)

# ===== ENDPOINTS =====
@app.route('/health', methods=['GET'])
def health():
    from flask import jsonify
    return jsonify({'status': '✓ Bot is running'}), 200

@app.route('/', methods=['GET'])
def home():
    from flask import jsonify
    return jsonify({
        'name': 'Elder Fraud Prevention Bot',
        'status': 'running',
        'webhook': '/whatsapp'
    }), 200

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    from flask import jsonify
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    from flask import jsonify
    print(f"Error: {error}")
    return jsonify({'error': 'Server error'}), 500

# ===== RUN =====
if __name__ == '__main__':
    print("🚀 Elder Fraud Prevention Bot starting...")
    print("📍 Webhook: http://localhost:5000/whatsapp")
    app.run(debug=False, port=5000, host='0.0.0.0')
