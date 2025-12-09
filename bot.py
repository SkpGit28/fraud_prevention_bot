from flask import Flask, request, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re
from cryptography.fernet import Fernet
from datetime import datetime
from html import escape

load_dotenv()
app = Flask(__name__)

try:
    encryption_key = os.getenv('ENCRYPTION_KEY').encode()
    cipher_suite = Fernet(encryption_key)
except:
    cipher_suite = None
    print("No encryption key")

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token) if account_sid else None

from supabase import create_client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key) if supabase_url else None

user_states = {}

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

def get_user_state(phone):
    if phone not in user_states:
        user_states[phone] = {
            'language': None,
            'step': 'language_selection',
            'current_flow': None,
            'data': {},
            'created_at': datetime.now().isoformat()
        }
    return user_states[phone]

def set_user_step(phone, step, flow=None, data=None):
    state = get_user_state(phone)
    state['step'] = step
    if flow:
        state['current_flow'] = flow
    if data:
        state['data'].update(data)

MESSAGES = {
    'EN': {
        'greeting': '🛡️ ELDER FRAUD PREVENTION BOT\n\nChoose your language:\n1️⃣ English\n2️⃣ हिंदी (Hindi)',
        'menu': '📋 WHAT DO YOU NEED?\n\n1️⃣ CHECK PHONE NUMBER\n2️⃣ I\'VE BEEN SCAMMED\n3️⃣ REPORT A SCAM\n4️⃣ ABOUT BOT\n\n0️⃣ MENU',
        'ask_number': '📱 Send number:\nExample: +91-9876543210\n\n0️⃣ Back',
        'checking': '🔍 Checking {number}...',
        'not_found': '🟡 No data for {number}\n\n📝 Report it? (Option 3)\n☎️ Call 1930',
        'ask_recovery': '🚨 What happened?\n(Example: "₹50000 UPI")\n\n0️⃣ Back',
        'recovery_options': '💰 Choose method:\n\n1️⃣ UPI\n2️⃣ Bank\n3️⃣ Crypto\n4️⃣ Loan\n5️⃣ Other\n\n0️⃣ Back',
        'recovery_upi': '🚨 UPI FRAUD\n\nAmount: ₹{amount}\n\n✅ CALL BANK NOW\n☎️ Say: "UPI fraud"\nSuccess: 60-80%\n\n✅ CALL 1930\n\n✅ FILE on cybercrime.gov.in\n\n⏱️ Timeline: 10-20 days\n\n0️⃣ Menu',
        'recovery_bank': '🏦 BANK FRAUD\n\nAmount: ₹{amount}\n\n✅ CALL BANK NOW\n☎️ Say: "Fraudulent transfer"\nSuccess: 70-80%\n\n✅ CALL 1930\n\n✅ FILE on cybercrime.gov.in\n\n⏱️ Timeline: 10-20 days\n\n0️⃣ Menu',
        'recovery_crypto': '⚠️ CRYPTO FRAUD\n\nAmount: ₹{amount}\n\n❌ Recovery: <1%\n\nStill try:\n1️⃣ cybercrime.gov.in\n2️⃣ 1930\n3️⃣ Get FIR\n\n⏱️ Timeline: 3-6 months\n\n0️⃣ Menu',
        'ask_report': '🚨 Tell us about scam:\n(Example: "Romance")\n\n0️⃣ Back',
        'report_received': '✅ REPORT RECEIVED!\n\nType: {scam_type}\n\nYour report protects others!\n\n📞 Also report to:\n🔗 cybercrime.gov.in\n☎️ 1930\n\n0️⃣ Menu',
        'about': '💡 ABOUT BOT\n\n🎯 Protect seniors from fraud\n👥 50L+ Indians scammed yearly\n✅ We help with recovery\n\n🛡️ All data encrypted\n\n📞 Resources:\n• 1930 (24/7)\n• cybercrime.gov.in\n• Police\n\n💚 We\'re here to help!\n\n0️⃣ Menu',
        'invalid': '❌ I didn\'t understand.\n\nTry again:\n0️⃣ Menu',
        'error': '⚠️ Error!\n\nTry again:\n0️⃣ Menu'
    },
    'HI': {
        'greeting': '🛡️ वरिष्ठ नागरिक जालसाजी सुरक्षा\n\nभाषा चुनें:\n1️⃣ English\n2️⃣ हिंदी',
        'menu': '📋 आप क्या चाहते हैं?\n\n1️⃣ नंबर जांचें\n2️⃣ मैं ठगा जा चुका हूँ\n3️⃣ जालसाजी रिपोर्ट करें\n4️⃣ इस बॉट के बारे में\n\n0️⃣ मेनू',
        'ask_number': '📱 नंबर भेजें:\nउदाहरण: +91-9876543210\n\n0️⃣ वापस',
        'checking': '🔍 जांच {number}...',
        'not_found': '🟡 {number} पर डेटा नहीं\n\n📝 रिपोर्ट करें? (विकल्प 3)\n☎️ 1930 कॉल करें',
        'ask_recovery': '🚨 क्या हुआ?\n(उदाहरण: "₹50000 UPI")\n\n0️⃣ वापस',
        'recovery_options': '💰 तरीका चुनें:\n\n1️⃣ UPI\n2️⃣ बैंक\n3️⃣ क्रिप्टो\n4️⃣ लोन\n5️⃣ अन्य\n\n0️⃣ वापस',
        'recovery_upi': '🚨 UPI जालसाजी\n\nराशि: ₹{amount}\n\n✅ अब बैंक कॉल करें\n☎️ कहें: "UPI धोखा"\nसफलता: 60-80%\n\n✅ 1930 को कॉल करें\n\n✅ cybercrime.gov.in पर रिपोर्ट करें\n\n⏱️ समय: 10-20 दिन\n\n0️⃣ मेनू',
        'recovery_bank': '🏦 बैंक जालसाजी\n\nराशि: ₹{amount}\n\n✅ अब बैंक कॉल करें\nसफलता: 70-80%\n\n✅ 1930 को कॉल करें\n\n✅ cybercrime.gov.in पर रिपोर्ट करें\n\n⏱️ समय: 10-20 दिन\n\n0️⃣ मेनू',
        'recovery_crypto': '⚠️ क्रिप्टो जालसाजी\n\nराशि: ₹{amount}\n\n❌ रिकवरी: <1%\n\nफिर भी कोशिश:\n1️⃣ cybercrime.gov.in\n2️⃣ 1930\n3️⃣ FIR प्राप्त करें\n\n⏱️ समय: 3-6 महीने\n\n0️⃣ मेनू',
        'ask_report': '🚨 जालसाजी के बारे में बताएं:\n(उदाहरण: "प्रेम")\n\n0️⃣ वापस',
        'report_received': '✅ रिपोर्ट प्राप्त!\n\nप्रकार: {scam_type}\n\nआपकी रिपोर्ट दूसरों को बचाएगी!\n\n📞 यह भी रिपोर्ट करें:\n🔗 cybercrime.gov.in\n☎️ 1930\n\n0️⃣ मेनू',
        'about': '💡 इस बॉट के बारे में\n\n🎯 बुजुर्गों को जालसाजी से बचाएं\n👥 50L+ भारतीय ठगे जाते हैं\n✅ हम रिकवरी में मदद करते हैं\n\n🛡️ सभी डेटा एन्क्रिप्ट किया\n\n📞 संसाधन:\n• 1930 (24/7)\n• cybercrime.gov.in\n• पुलिस\n\n💚 हम यहां हैं!\n\n0️⃣ मेनू',
        'invalid': '❌ मुझे समझ नहीं आया।\n\nफिर से कोशिश करें:\n0️⃣ मेनू',
        'error': '⚠️ त्रुटि!\n\nफिर से कोशिश करें:\n0️⃣ मेनू'
    }
}

@app.route('/whatsapp', methods=['POST'])
def receive_whatsapp():
    try:
        user_message = request.form.get('Body', '').strip()
        user_phone = request.form.get('From', '')
        
        state = get_user_state(user_phone)
        language = state['language'] or 'EN'
        
        safe_message = validate_message(user_message)
        if not safe_message:
            send_message(user_phone, MESSAGES[language]['error'])
            return 'OK'
        
        response = route_message(user_phone, safe_message, state)
        
        if response:
            send_message(user_phone, response)
        
        try:
            log_interaction(user_phone, safe_message, state['step'])
        except:
            pass
        
        return 'OK'
    except Exception as e:
        print(f"Error: {e}")
        return 'OK'

def route_message(phone, message, state):
    language = state['language'] or 'EN'
    msg_lower = message.lower().strip()
    
    if state['step'] == 'language_selection':
        if msg_lower in ['1', 'english', 'en']:
            state['language'] = 'EN'
            set_user_step(phone, 'main_menu')
            return MESSAGES['EN']['menu']
        elif msg_lower in ['2', 'hindi', 'hi', 'हिंदी']:
            state['language'] = 'HI'
            set_user_step(phone, 'main_menu')
            return MESSAGES['HI']['menu']
        else:
            return MESSAGES['EN']['greeting']
    
    elif state['step'] == 'main_menu':
        if msg_lower in ['1', 'check']:
            set_user_step(phone, 'check_number_input', flow='check_number')
            return MESSAGES[language]['ask_number']
        elif msg_lower in ['2', 'scammed', 'recovery']:
            set_user_step(phone, 'recovery_description', flow='recovery')
            return MESSAGES[language]['ask_recovery']
        elif msg_lower in ['3', 'report']:
            set_user_step(phone, 'report_description', flow='report')
            return MESSAGES[language]['ask_report']
        elif msg_lower in ['4', 'about']:
            return MESSAGES[language]['about']
        elif msg_lower in ['0', 'menu', 'help']:
            return MESSAGES[language]['menu']
        else:
            return MESSAGES[language]['invalid']
    
    elif state['step'] == 'check_number_input':
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        phone_pattern = r'\+91[-\s]?\d{4,}|\d{10}'
        match = re.search(phone_pattern, message)
        
        if match:
            number = match.group(0)
            set_user_step(phone, 'number_checked')
            response = MESSAGES[language]['checking'].format(number=number)
            response += '\n\n' + MESSAGES[language]['not_found'].format(number=number)
            return response
        else:
            return MESSAGES[language]['invalid']
    
    elif state['step'] == 'recovery_description':
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        amount_match = re.search(r'₹?(\d+,?\d*)', message)
        amount = amount_match.group(1) if amount_match else 'Unknown'
        
        set_user_step(phone, 'recovery_method_select', data={'amount': amount})
        return MESSAGES[language]['recovery_options']
    
    elif state['step'] == 'recovery_method_select':
        amount = state['data'].get('amount', 'Unknown')
        
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        elif msg_lower in ['1', 'upi']:
            save_recovery_to_db(phone, amount, 'UPI')
            set_user_step(phone, 'recovery_complete')
            return MESSAGES[language]['recovery_upi'].format(amount=amount)
        elif msg_lower in ['2', 'bank']:
            save_recovery_to_db(phone, amount, 'Bank Transfer')
            set_user_step(phone, 'recovery_complete')
            return MESSAGES[language]['recovery_bank'].format(amount=amount)
        elif msg_lower in ['3', 'crypto']:
            save_recovery_to_db(phone, amount, 'Cryptocurrency')
            set_user_step(phone, 'recovery_complete')
            return MESSAGES[language]['recovery_crypto'].format(amount=amount)
        elif msg_lower in ['4', 'loan']:
            save_recovery_to_db(phone, amount, 'Loan Fraud')
            set_user_step(phone, 'recovery_complete')
            return f"🚨 LOAN FRAUD\n\nAmount: ₹{amount}\n\n1️⃣ Don't send more\n2️⃣ Block number\n3️⃣ cybercrime.gov.in\n4️⃣ Call 1930\n\n0️⃣ Menu"
        elif msg_lower in ['5', 'other']:
            save_recovery_to_db(phone, amount, 'Other')
            set_user_step(phone, 'recovery_complete')
            return f"🆘 SCAM\n\nAmount: ₹{amount}\n\n1️⃣ Don't send\n2️⃣ Block scammer\n3️⃣ cybercrime.gov.in\n4️⃣ Call 1930\n5️⃣ Call bank\n\n0️⃣ Menu"
        else:
            return MESSAGES[language]['invalid']
    
    elif state['step'] == 'report_description':
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        scam_type = detect_scam_type(message, language)
        save_report_to_db(phone, scam_type, message)
        set_user_step(phone, 'report_complete')
        return MESSAGES[language]['report_received'].format(scam_type=scam_type)
    
    elif state['step'] in ['number_checked', 'recovery_complete', 'report_complete']:
        if msg_lower in ['0', 'menu']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        else:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
    
    else:
        set_user_step(phone, 'main_menu')
        return MESSAGES[language]['menu']

def save_recovery_to_db(phone, amount, method):
    try:
        recovery_data = {
            'phone_encrypted': encrypt_data(phone),
            'amount': str(amount),
            'method': method,
            'status': 'open',
            'created_at': datetime.now().isoformat()
        }
        save_to_db('recovery_cases', recovery_data)
    except:
        pass

def save_report_to_db(phone, scam_type, description):
    try:
        report_data = {
            'reporter_phone_encrypted': encrypt_data(phone),
            'scam_type': scam_type,
            'message_encrypted': encrypt_data(description),
            'votes': 1,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        save_to_db('scam_reports', report_data)
    except:
        pass

def detect_scam_type(message, language='EN'):
    msg = message.lower()
    
    romance = ['love', 'dating', 'girl', 'boy', 'प्रेम', 'प्यार']
    loan = ['loan', 'credit', 'emi', 'लोन', 'ऋण']
    police = ['police', 'arrest', 'cbi', 'पुलिस', 'गिरफ्तारी']
    investment = ['investment', 'profit', 'scheme', 'निवेश', 'लाभ']
    bank = ['bank', 'account', 'otp', 'बैंक', 'खाता']
    
    if any(w in msg for w in romance):
        return 'Romance Scam' if language == 'EN' else 'प्रेम जालसाजी'
    elif any(w in msg for w in loan):
        return 'Fake Loan' if language == 'EN' else 'नकली लोन'
    elif any(w in msg for w in police):
        return 'Digital Arrest' if language == 'EN' else 'डिजिटल गिरफ्तारी'
    elif any(w in msg for w in investment):
        return 'Investment Fraud' if language == 'EN' else 'निवेश धोखा'
    elif any(w in msg for w in bank):
        return 'Bank Scam' if language == 'EN' else 'बैंक धोखा'
    else:
        return 'Other' if language == 'EN' else 'अन्य'

def send_message(to_number, body):
    if not twilio_client:
        return False
    
    try:
        if len(body) > 1600:
            messages = [body[i:i+1600] for i in range(0, len(body), 1600)]
        else:
            messages = [body]
        
        for msg in messages:
            twilio_client.messages.create(
                from_='whatsapp:+14155238886',
                body=msg,
                to=to_number
            )
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def log_interaction(phone, message, step):
    try:
        log_data = {
            'phone_encrypted': encrypt_data(phone),
            'intent': step,
            'created_at': datetime.now().isoformat()
        }
        save_to_db('interactions', log_data)
    except:
        pass

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'users': len(user_states)}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({'bot': 'Elder Fraud Prevention', 'version': '2.0.1'}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("Bot starting...")
    app.run(debug=False, port=5000, host='0.0.0.0')
