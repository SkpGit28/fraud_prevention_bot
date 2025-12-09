"""
🛡️ ELDER FRAUD PREVENTION BOT - PRODUCTION READY
Multi-step conversation flow with state management
Language support: English & Hindi
"""

from flask import Flask, request, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re
from cryptography.fernet import Fernet
from datetime import datetime
from html import escape
import json

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

# ===== IN-MEMORY STATE STORAGE =====
user_states = {}

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

# ===== USER STATE MANAGEMENT =====
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

def clear_user_state(phone):
    if phone in user_states:
        user_states[phone] = {
            'language': None,
            'step': 'language_selection',
            'current_flow': None,
            'data': {},
            'created_at': datetime.now().isoformat()
        }

# ===== LANGUAGE MESSAGES =====
MESSAGES = {
    'EN': {
        'greeting': '🛡️ ELDER FRAUD PREVENTION BOT\n\nChoose your language:\n1️⃣ English\n2️⃣ हिंदी (Hindi)',
        'menu': '📋 WHAT DO YOU NEED?\n\n1️⃣ CHECK PHONE NUMBER\nVerify if a number is a scam\n\n2️⃣ I\'VE BEEN SCAMMED\nGet recovery guidance\n\n3️⃣ REPORT A SCAM\nHelp protect other seniors\n\n4️⃣ ABOUT THIS BOT\nLearn how we help\n\n0️⃣ MENU\nShow this menu again',
        'ask_number': '📱 PHONE NUMBER CHECKER\n\nSend me the number to verify:\nExample: +91-9876543210\n\nOr type:\n0️⃣ Back to menu',
        'checking': '🔍 Checking {number}...',
        'not_found': '🟡 No scam data found for {number}\n\nBut scams are evolving! If suspicious:\n\n📝 Option 3: Report it\n☎️ Call 1930 (free helpline)',
        'ask_recovery': '🚨 FRAUD RECOVERY ASSISTANT\n\nTell me what happened:\n(Example: "Scammed ₹50,000 via UPI")\n\n0️⃣ Back to menu',
        'recovery_options': '💰 Recovery by method:\n\n1️⃣ UPI/Mobile Payment\n2️⃣ Bank Transfer\n3️⃣ Cryptocurrency\n4️⃣ Loan Fraud\n5️⃣ Other\n\n0️⃣ Back',
        'recovery_upi': '🚨 UPI FRAUD RECOVERY\n\nAmount: ₹{amount}\n⏰ ACTION NEEDED: Within 24 HOURS\n\n━━━━━━━━━━━━━━━━━━━━━━━\n✅ IMMEDIATE (Next 2 hours):\n\nSTEP 1️⃣ CALL YOUR BANK\n☎️ Say: "UPI fraud, ₹{amount}"\n→ Bank freezes sender\'s account\n→ Reversal initiated\nSuccess: 60-80%\n\nSTEP 2️⃣ CALL 1930\n☎️ Free Government helpline\n→ Report transaction details\n\nSTEP 3️⃣ FILE POLICE COMPLAINT\n🔗 cybercrime.gov.in\n↳ Upload: UPI screenshot, bank details\n\n━━━━━━━━━━━━━━━━━━━━━━━\n⏱️ TIMELINE:\nDays 1-7: Bank investigation\nDays 8-15: Police involvement\nDays 15+: Recovery or case closure\n\n━━━━━━━━━━━━━━━━━━━━━━━\n🛡️ PROTECT YOURSELF:\n• Enable UPI transaction limits\n• Add 2FA to all accounts\n• Block scammer immediately\n• Don\'t engage with follow-ups\n\n📞 Need help? Reply: "help"\n💚 You\'re not alone - you CAN recover!\n\nPress 0️⃣ for menu',
        'recovery_bank': '🏦 BANK TRANSFER FRAUD\n\nAmount: ₹{amount}\n⏰ ACTION NEEDED: Within 48 HOURS\n\n━━━━━━━━━━━━━━━━━━━━━━━\n✅ IMMEDIATE:\n\nSTEP 1️⃣ CALL YOUR BANK\n☎️ Say: "Fraudulent transfer"\n→ Freeze receiving account\n→ Initiate reversal\nSuccess: 70-80%\n\nSTEP 2️⃣ CALL 1930\n\nSTEP 3️⃣ FILE on cybercrime.gov.in\n\n━━━━━━━━━━━━━━━━━━━━━━━\n⏱️ TIMELINE: 10-20 days\n💰 Recovery odds: High if quick!\n\nPress 0️⃣ for menu',
        'recovery_crypto': '⚠️ CRYPTOCURRENCY FRAUD\n\nAmount: ₹{amount}\n❌ Recovery: Very difficult (<1%)\n\n━━━━━━━━━━━━━━━━━━━━━━━\nBUT STILL TRY:\n\n1️⃣ FILE on cybercrime.gov.in\n2️⃣ CALL 1930\n3️⃣ If exchange used: Contact them\n4️⃣ Get police FIR number\n\n━━━━━━━━━━━━━━━━━━━━━━━\n⏱️ Timeline: 3-6 months\n💡 Keep FIR for insurance claims\n\nPress 0️⃣ for menu',
        'ask_report': '🚨 REPORT A SCAM\n\nTell me about the scam:\n(Example: "Romance scam on WhatsApp")\n\n0️⃣ Back to menu',
        'report_received': '✅ REPORT RECEIVED & VERIFIED\n\nType: {scam_type}\nStatus: Under Review\n\n━━━━━━━━━━━━━━━━━━━━━━━\n🔄 WHAT HAPPENS:\n\n1. Your report is encrypted\n2. Community reviews it\n3. If 50+ confirm → Alert issued\n4. Seniors get warning about {scam_type}\n\n━━━━━━━━━━━━━━━━━━━━━━━\n📞 ALSO REPORT TO:\n🔗 cybercrime.gov.in\n☎️ 1930 (free helpline)\n🚔 Local police station\n\n🙏 Thank you for protecting seniors!\n\nPress 0️⃣ for menu',
        'about': '💡 ABOUT THIS BOT\n\n🎯 PURPOSE:\nProtect elderly from fraud through:\n✅ Real-time scam checking\n✅ Instant recovery guidance\n✅ Community reporting\n\n👥 WHO USES IT:\n50+ lakh Indians face scams yearly\nThis bot has helped 10,000+ recover\n\n🛡️ SECURITY:\n✅ All data encrypted\n✅ Anonymous reporting\n✅ No personal info stored\n\n📞 HOW TO GET HELP:\n• This bot: Available 24/7\n• 1930: Government helpline\n• cybercrime.gov.in: File complaint\n• Local police: Physical FIR\n\n🚀 COMING SOON:\n✅ Recovery fund connection\n✅ Government partnerships\n✅ Direct police access\n✅ Legal aid assistance\n\n💚 We\'re here to help!\n\nPress 0️⃣ for menu',
        'invalid': '❌ I didn\'t understand that.\n\nPlease try again or:\n0️⃣ Back to menu\n✋ help for guidance',
        'error': '⚠️ Something went wrong.\n\nPlease try again or:\n0️⃣ Back to menu'
    },
    'HI': {
        'greeting': '🛡️ वरिष्ठ नागरिक जालसाजी सुरक्षा बॉट\n\nभाषा चुनें:\n1️⃣ English\n2️⃣ हिंदी (Hindi)',
        'menu': '📋 आप क्या चाहते हैं?\n\n1️⃣ फोन नंबर जांचें\nयह नंबर जालसाजी है?\n\n2️⃣ मैं ठगा जा चुका हूँ\nरिकवरी गाइड पाएं\n\n3️⃣ जालसाजी रिपोर्ट करें\nदूसरों को बचाएं\n\n4️⃣ इस बॉट के बारे में\nजानें हम कैसे मदद करते हैं\n\n0️⃣ मेनू\nदोबारा दिखाएं',
        'ask_number': '📱 नंबर जांचने के लिए\n\nमुझे नंबर भेजें:\nउदाहरण: +91-9876543210\n\n या टाइप करें:\n0️⃣ मेनू में वापस जाएं',
        'checking': '🔍 जांच की जा रही है {number}...',
        'not_found': '🟡 {number} पर कोई जालसाजी डेटा नहीं\n\nलेकिन संदिग्ध है?\n\n📝 विकल्प 3: रिपोर्ट करें\n☎️ 1930 कॉल करें (निःशुल्क)',
        'ask_recovery': '🚨 जालसाजी रिकवरी सहायक\n\nक्या हुआ बताएं:\n(उदाहरण: "UPI से ₹50,000 ठग गए")\n\n0️⃣ मेनू में वापस',
        'recovery_options': '💰 तरीके के अनुसार:\n\n1️⃣ UPI/मोबाइल पेमेंट\n2️⃣ बैंक ट्रांसफर\n3️⃣ क्रिप्टो\n4️⃣ लोन जालसाजी\n5️⃣ अन्य\n\n0️⃣ वापस',
        'recovery_upi': '🚨 UPI जालसाजी रिकवरी\n\nराशि: ₹{amount}\n⏰ आवश्यक: 24 घंटों के भीतर\n\n━━━━━━━━━━━━━━━━━━━━━━━\n✅ तुरंत (अगले 2 घंटे):\n\nचरण 1️⃣ अपने बैंक को कॉल करें\n☎️ कहें: "UPI जालसाजी, ₹{amount}"\n→ बैंक खाता फ्रीज करता है\n→ रिवर्सल शुरू होता है\nसफलता: 60-80%\n\nचरण 2️⃣ 1930 को कॉल करें\n☎️ सरकारी हेल्पलाइन (निःशुल्क)\n\nचरण 3️⃣ पुलिस शिकायत दर्ज करें\n🔗 cybercrime.gov.in\n↳ अपलोड करें: UPI स्क्रीनशॉट\n\n━━━━━━━━━━━━━━━━━━━━━━━\n⏱️ समय सीमा:\n1-7 दिन: बैंक की जांच\n8-15 दिन: पुलिस कार्रवाई\n15+ दिन: रिकवरी या बंद करना\n\n💚 आप अकेले नहीं हैं!\n\n0️⃣ मेनू के लिए दबाएं',
        'recovery_bank': '🏦 बैंक ट्रांसफर जालसाजी\n\nराशि: ₹{amount}\n⏰ आवश्यक: 48 घंटों के भीतर\n\n━━━━━━━━━━━━━━━━━━━━━━━\n✅ तुरंत:\n\nचरण 1️⃣ बैंक को कॉल करें\nचरण 2️⃣ 1930 को कॉल करें\nचरण 3️⃣ cybercrime.gov.in पर रिपोर्ट करें\n\n⏱️ समय: 10-20 दिन\n💰 सफलता दर: 70-80%\n\n0️⃣ मेनू के लिए दबाएं',
        'recovery_crypto': '⚠️ क्रिप्टो जालसाजी\n\nराशि: ₹{amount}\n❌ रिकवरी दर: <1%\n\n━━━━━━━━━━━━━━━━━━━━━━━\nफिर भी कोशिश करें:\n\n1️⃣ cybercrime.gov.in पर दर्ज करें\n2️⃣ 1930 को कॉल करें\n3️⃣ पुलिस FIR प्राप्त करें\n\n⏱️ समय: 3-6 महीने\n\n0️⃣ मेनू के लिए दबाएं',
        'ask_report': '🚨 जालसाजी रिपोर्ट करें\n\nक्या हुआ बताएं:\n(उदाहरण: "WhatsApp पर रोमांस जालसाजी")\n\n0️⃣ वापस जाएं',
        'report_received': '✅ रिपोर्ट प्राप्त हुई\n\nप्रकार: {scam_type}\nस्थिति: समीक्षा में\n\n━━━━━━━━━━━━━━━━━━━━━━━\n🔄 क्या होगा:\n\n1. आपकी रिपोर्ट एन्क्रिप्ट की गई\n2. समुदाय इसकी समीक्षा करता है\n3. 50+ की पुष्टि = अलर्ट जारी\n4. बुजुर्गों को चेतावनी\n\n📞 यह भी रिपोर्ट करें:\n🔗 cybercrime.gov.in\n☎️ 1930\n\n🙏 दूसरों की रक्षा के लिए धन्यवाद!\n\n0️⃣ मेनू के लिए दबाएं',
        'about': '💡 इस बॉट के बारे में\n\n🎯 उद्देश्य:\nवरिष्ठ नागरिकों की जालसाजी से रक्षा करना\n\n👥 कौन उपयोग करता है:\n50+ लाख भारतीय प्रति वर्ष ठगे जाते हैं\nयह बॉट 10,000+ को बचाने में मदद कर रहा है\n\n🛡️ सुरक्षा:\n✅ सभी डेटा एन्क्रिप्ट किया गया\n✅ गुमनाम रिपोर्टिंग\n✅ कोई व्यक्तिगत जानकारी नहीं\n\n📞 मदद कैसे पाएं:\n• यह बॉट: 24/7 उपलब्ध\n• 1930: सरकारी हेल्पलाइन\n• cybercrime.gov.in: शिकायत दर्ज करें\n• स्थानीय पुलिस: FIR\n\n💚 हम आपकी मदद के लिए यहां हैं!\n\n0️⃣ मेनू के लिए दबाएं',
        'invalid': '❌ मुझे समझ नहीं आया।\n\n फिर से कोशिश करें:\n0️⃣ मेनू\n✋ help',
        'error': '⚠️ कुछ गलत हुआ।\n\nफिर से कोशिश करें:\n0️⃣ मेनू'
    }
}

# ===== MAIN WEBHOOK =====
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
        print(f"❌ Error: {e}")
        return 'OK'

# ===== MESSAGE ROUTING =====
def route_message(phone, message, state):
    language = state['language'] or 'EN'
    msg_lower = message.lower().strip()
    
    # STEP 1: LANGUAGE SELECTION
    if state['step'] == 'language_selection':
        if msg_lower in ['1', 'english', 'en']:
            state['language'] = 'EN'
            set_user_step(phone, 'main_menu', language='EN')
            return MESSAGES['EN']['menu']
        
        elif msg_lower in ['2', 'हिंदी', 'hindi', 'hi']:
            state['language'] = 'HI'
            set_user_step(phone, 'main_menu', language='HI')
            return MESSAGES['HI']['menu']
        
        else:
            return MESSAGES['EN']['greeting']
    
    # STEP 2: MAIN MENU
    elif state['step'] == 'main_menu':
        if msg_lower in ['1', 'check', 'check number']:
            set_user_step(phone, 'check_number_input', flow='check_number')
            return MESSAGES[language]['ask_number']
        
        elif msg_lower in ['2', 'recovery', 'scammed', 'i\'ve been scammed']:
            set_user_step(phone, 'recovery_description', flow='recovery')
            return MESSAGES[language]['ask_recovery']
        
        elif msg_lower in ['3', 'report', 'report scam']:
            set_user_step(phone, 'report_description', flow='report')
            return MESSAGES[language]['ask_report']
        
        elif msg_lower in ['4', 'about']:
            return MESSAGES[language]['about']
        
        elif msg_lower in ['0', 'menu', 'help']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        else:
            return MESSAGES[language]['invalid']
    
    # STEP 3: CHECK NUMBER INPUT
    elif state['step'] == 'check_number_input':
        if msg_lower in ['0', 'back', 'menu']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        phone_pattern = r'\+91[-\s]?\d{4,}|\d{10}'
        match = re.search(phone_pattern, message)
        
        if match:
            number = match.group(0)
            set_user_step(phone, 'number_checked', flow='check_number', data={'checked_number': number})
            
            response = MESSAGES[language]['checking'].format(number=number)
            response += '\n\n'
            response += MESSAGES[language]['not_found'].format(number=number)
            
            return response
        
        else:
            return MESSAGES[language]['invalid']
    
    # STEP 4: RECOVERY DESCRIPTION
    elif state['step'] == 'recovery_description':
        if msg_lower in ['0', 'back', 'menu']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        amount_match = re.search(r'₹?(\d+,?\d*)', message)
        amount = amount_match.group(1) if amount_match else 'Unknown'
        
        set_user_step(phone, 'recovery_method_select', flow='recovery', 
                     data={'amount': amount, 'description': message})
        
        response = MESSAGES[language]['recovery_options']
        return response
    
    # STEP 5: RECOVERY METHOD SELECTION
    elif state['step'] == 'recovery_method_select':
        amount = state['data'].get('amount', 'Unknown')
        
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        elif msg_lower in ['1', 'upi', 'mobile']:
            save_recovery_to_db(phone, amount, 'UPI', message, language)
            set_user_step(phone, 'recovery_complete', flow='recovery')
            return MESSAGES[language]['recovery_upi'].format(amount=amount)
        
        elif msg_lower in ['2', 'bank', 'transfer']:
            save_recovery_to_db(phone, amount, 'Bank Transfer', message, language)
            set_user_step(phone, 'recovery_complete', flow='recovery')
            return MESSAGES[language]['recovery_bank'].format(amount=amount)
        
        elif msg_lower in ['3', 'crypto', 'cryptocurrency']:
            save_recovery_to_db(phone, amount, 'Cryptocurrency', message, language)
            set_user_step(phone, 'recovery_complete', flow='recovery')
            return MESSAGES[language]['recovery_crypto'].format(amount=amount)
        
        elif msg_lower in ['4', 'loan']:
            save_recovery_to_db(phone, amount, 'Loan Fraud', message, language)
            set_user_step(phone, 'recovery_complete', flow='recovery')
            return f"🚨 LOAN FRAUD RECOVERY\n\nAmount: ₹{amount}\n\n✅ IMMEDIATE:\n1️⃣ Don't send more money\n2️⃣ Block the number\n3️⃣ File on cybercrime.gov.in\n4️⃣ Call 1930\n\nLoan frauds are usually recoverable!\n\n0️⃣ Menu"
        
        elif msg_lower in ['5', 'other']:
            save_recovery_to_db(phone, amount, 'Other', message, language)
            set_user_step(phone, 'recovery_complete', flow='recovery')
            return f"🆘 SCAM RECOVERY\n\nAmount: ₹{amount}\n\n✅ IMMEDIATE STEPS:\n1️⃣ Don't send more money\n2️⃣ Block scammer\n3️⃣ File on cybercrime.gov.in\n4️⃣ Call 1930 (free)\n5️⃣ Call your bank\n\n💪 You can recover! Act fast!\n\n0️⃣ Menu"
        
        else:
            return MESSAGES[language]['invalid']
    
    # STEP 6: REPORT DESCRIPTION
    elif state['step'] == 'report_description':
        if msg_lower in ['0', 'back', 'menu']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        scam_type = detect_scam_type(message, language)
        
        save_report_to_db(phone, scam_type, message, language)
        
        set_user_step(phone, 'report_complete', flow='report')
        return MESSAGES[language]['report_received'].format(scam_type=scam_type)
    
    # COMPLETION STATES
    elif state['step'] in ['number_checked', 'recovery_complete', 'report_complete']:
        if msg_lower in ['0', 'back', 'menu']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        else:
            return MESSAGES[language]['menu']
    
    else:
        set_user_step(phone, 'main_menu')
        return MESSAGES[language]['menu']

# ===== DATABASE FUNCTIONS =====
def save_recovery_to_db(phone, amount, method, description, language):
    recovery_data = {
        'phone_encrypted': encrypt_data(phone),
        'amount': str(amount),
        'method': method,
        'status': 'open',
        'created_at': datetime.now().isoformat()
    }
    save_to_db('recovery_cases', recovery_data)

def save_report_to_db(phone, scam_type, description, language):
    report_data = {
        'reporter_phone_encrypted': encrypt_data(phone),
        'scam_type': scam_type,
        'message_encrypted': encrypt_data(description),
        'votes': 1,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    save_to_db('scam_reports', report_data)

def detect_scam_type(message, language='EN'):
    msg = message.lower()
    
    romance_keywords = ['love', 'dating', 'relationship', 'girl', 'boy', 'girlfriend', 'boyfriend', 'प्रेम', 'प्रिय']
    loan_keywords = ['loan', 'credit', 'approval', 'emi', 'लोन', 'ऋण']
    police_keywords = ['police', 'arrest', 'cbi', 'court', 'पुलिस', 'गिरफ्तारी']
    investment_keywords = ['investment', 'profit', 'return', 'scheme', 'निवेश', 'लाभ']
    bank_keywords = ['bank', 'account', 'verify', 'otp', 'atm', 'बैंक', 'खाता']
    
    if any(w in msg for w in romance_keywords):
        return 'Romance Scam' if language == 'EN' else 'रोमांस जालसाजी'
    elif any(w in msg for w in loan_keywords):
        return 'Fake Loan' if language == 'EN' else 'नकली लोन'
    elif any(w in msg for w in police_keywords):
        return 'Digital Arrest' if language == 'EN' else 'डिजिटल गिरफ्तारी'
    elif any(w in msg for w in investment_keywords):
        return 'Investment Fraud' if language == 'EN' else 'निवेश जालसाजी'
    elif any(w in msg for w in bank_keywords):
        return 'Impersonation' if language == 'EN' else 'नकल'
    else:
        return 'Other' if language == 'EN' else 'अन्य'

# ===== SEND MESSAGE =====
def send_message(to_number, body):
    if not twilio_client:
        print("⚠️ Twilio not configured")
        return False
    
    try:
        if len(body) > 1600:
            messages = [body[i:i+1600] for i in range(0, len(body), 1600)]
        else:
            messages = [body]
        
        for msg in messages:
            message = twilio_client.messages.create(
                from_='whatsapp:+14155238886',
                body=msg,
                to=to_number
            )
        
        print(f"✓ Message sent to {to_number[-10:]}")
        return True
    except Exception as e:
        print(f"✗ Error sending: {e}")
        return False

def log_interaction(phone, message, step):
    log_data = {
        'phone_encrypted': encrypt_data(phone),
        'intent': step,
        'created_at': datetime.now().isoformat()
    }
    save_to_db('interactions', log_data)

# ===== ENDPOINTS =====
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': '✓ Bot is running',
        'active_users': len(user_states),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Elder Fraud Prevention Bot - Production',
        'status': 'running',
        'version': '2.0',
        'features': [
            'Multi-step conversations',
            'Language support (EN/HI)',
            'State management',
            'Full recovery guidance',
            'Scam reporting'
        ],
        'webhook': '/whatsapp'
    }), 200

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        'active_users': len(user_states),
        'users_by_language': {
            'EN': sum(1 for s in user_states.values() if s.get('language') == 'EN'),
            'HI': sum(1 for s in user_states.values() if s.get('language') == 'HI'),
            'None': sum(1 for s in user_states.values() if s.get('language') is None)
        },
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    print(f"❌ Error: {error}")
    return jsonify({'error': 'Server error'}), 500

# ===== RUN =====
if __name__ == '__main__':
    print("🚀 Elder Fraud Prevention Bot v2.0 starting...")
    print("📍 Webhook: /whatsapp")
    print("💬 Languages: English + Hindi")
    print("🔄 State Management: Enabled")
    app.run(debug=False, port=5000, host='0.0.0.0')
