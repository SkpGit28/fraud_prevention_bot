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

# --- CONFIGURATION & SETUP ---
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

# --- HELPER FUNCTIONS ---

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

# --- UPDATED CONTENT WITH RBI RULES ---

MESSAGES = {
    'EN': {
        'greeting': '🛡️ ELDER FRAUD PREVENTION BOT\n\nChoose your language:\n1️⃣ English\n2️⃣ हिंदी (Hindi)',
        
        'menu': "\n🏡 MAIN MENU\nHow can I help you today?\n\n1️⃣ Check a Phone Number 📱\n(Find out if a caller is fake)\n\n2️⃣ HELP! I lost money 💸\n(I will guide you to get it back)\n\n3️⃣ Report a Bad Number 🚫\n(Protect others from scams)\n\n4️⃣ Know RBI Rules ⚖️\n(Recovery times, Refunds, & Rights)\n\n5️⃣ About Bot ℹ️\n\n6️⃣ Change Language 🌐\n\n0️⃣ Show this Menu again",
        
        'ask_number': '📱 Send number:\nExample: +91-9876543210\n\n0️⃣ Back',
        'checking': '🔍 Checking {number}...',
        'not_found': '✅ NO SCAM REPORTS FOUND (Yet)\n\nFor {number}.\n\n⚠️ CAUTION: Even if it looks safe, never share your OTP or PIN with anyone.\n\nIf you feel suspicious:\nPress 3️⃣ to Report it\nDial 1930 📞 for Police Help',
        
        'ask_recovery': '🚨 What happened?\n(Example: "₹50000 UPI" or "Bank Transfer")\n\n0️⃣ Back',
        'recovery_options': '💰 Choose method:\n\n1️⃣ UPI / GPay / Paytm\n2️⃣ Bank Transfer\n3️⃣ Crypto\n4️⃣ Loan Fraud\n5️⃣ Other\n\n0️⃣ Back',
        
        'recovery_upi': '🚨 UPI FRAUD DETECTED\n\nAmount: ₹{amount}\n\n📉 RBI RECOVERY CHANCE:\n• Report < 3 Days: 🟢 100% (Zero Liability)\n• Report 4-7 Days: 🟡 High (Limited Loss)\n• Report > 7 Days: 🔴 Low (Bank Policy)\n\n👇 FOLLOW THESE STEPS IN ORDER:\n\nSTEP 1️⃣: DIAL 1930 📞\nCall immediately. This is the "Golden Hour" to freeze money.\n\nSTEP 2️⃣: CALL YOUR BANK 🏦\nReport "Unauthorised Transaction". Ask for Complaint Number.\n\nSTEP 3️⃣: FILE COMPLAINT 🌐\nGo to cybercrime.gov.in within 24 hours.\n\n0️⃣ Menu',
        'recovery_bank': '🏦 BANK FRAUD DETECTED\n\nAmount: ₹{amount}\n\n📉 RBI RECOVERY CHANCE:\n• Report < 3 Days: 🟢 100% (Zero Liability)\n• Report 4-7 Days: 🟡 High (Limited Loss)\n• Report > 7 Days: 🔴 Low (Bank Policy)\n\n👇 FOLLOW THESE STEPS IN ORDER:\n\nSTEP 1️⃣: CALL 1930 📞\nAlert the Cyber Police immediately.\n\nSTEP 2️⃣: VISIT BRANCH 🏃\nSubmit a written application to "Freeze Account".\n\nSTEP 3️⃣: ONLINE REPORT 🌐\nRegister at cybercrime.gov.in for tracking.\n\n0️⃣ Menu',
        'recovery_crypto': '⚠️ CRYPTO FRAUD\n\nAmount: ₹{amount}\n\n❌ RBI STATUS: Hard to recover (Unregulated).\n\n👇 TRY THESE STEPS:\n\nSTEP 1️⃣: DIAL 1930 📞\nReport the bank transfer used to buy crypto.\n\nSTEP 2️⃣: CONTACT EXCHANGE 📉\nEmail the crypto app support immediately.\n\nSTEP 3️⃣: FILE FIR 👮\nGo to the nearest Cyber Police Station.\n\n0️⃣ Menu',
        'recovery_loan': '🚨 LOAN FRAUD\n\nAmount: ₹{amount}\n\n👇 STEPS TO PROTECT YOURSELF:\n\nSTEP 1️⃣: DO NOT PAY\nFake agents cannot arrest you. Ignore threats.\n\nSTEP 2️⃣: BLOCK & REPORT\nBlock the number. Report on WhatsApp.\n\nSTEP 3️⃣: CALL 1930 📞\nRegister a complaint against harassment.\n\n0️⃣ Menu',
        'recovery_other': '🆘 GENERAL HELP\n\nAmount: ₹{amount}\n\n👇 STEPS TO TAKE:\n\nSTEP 1️⃣: BLOCK SCAMMER\nCut off all contact immediately.\n\nSTEP 2️⃣: CALL 1930 📞\nReport the fraud number.\n\nSTEP 3️⃣: CONTACT BANK\nIf money was involved, alert your bank.\n\n0️⃣ Menu',

        'ask_report': '🚨 Tell us about scam:\n(Example: "Romance" or "Threats")\n\n0️⃣ Back',
        'report_received': '✅ REPORT RECEIVED!\n\nType: {scam_type}\n\nYour report protects others!\n\n📞 Also report to:\n🔗 cybercrime.gov.in\n☎️ 1930\n\n0️⃣ Menu',
        
        'about': '💡 ABOUT BOT\n\n🎯 Protect seniors from fraud\n👥 50L+ Indians scammed yearly\n✅ We help with recovery\n\n🛡️ All data encrypted\n\n📞 Resources:\n• 1930 (24/7)\n• cybercrime.gov.in\n\n0️⃣ Menu',

        # --- RBI SECTIONS (ENGLISH) ---
        'rbi_menu': "\n⚖️ RBI RULES & YOUR RIGHTS\nSelect a topic:\n\n1️⃣ Recovery Agent Rules 👮\n(When can they call?)\n\n2️⃣ Money Refund Rules 💰\n(Zero Liability & Time limits)\n\n3️⃣ Hidden Charges / Shadow Rules 📉\n(Penal charges vs Interest)\n\n0️⃣ Main Menu",

        'rbi_recovery': "\n👮 RECOVERY AGENT RULES\n\n1️⃣ TIME LIMITS:\nAgents can ONLY call between **8:00 AM and 7:00 PM**.\nCalls outside this time are HARASSMENT.\n\n2️⃣ NO THREATS:\nThey cannot threaten you or call your relatives.\n\n3️⃣ COMPLAIN:\nIf they break rules, complain to Bank. If ignored for 30 days, complain to RBI Ombudsman.\n\n0️⃣ Back",

        'rbi_refund': "\n💰 REFUND RULES (Zero Liability)\n\nIf money was stolen from account:\n\n1️⃣ REPORT FAST:\n• Within 3 Days: **100% Refund** (Zero Liability).\n• 4-7 Days: Loss limited to ₹5k-25k.\n\n2️⃣ SHADOW REVERSAL:\nBank must credit amount to your account within **10 working days** while investigating.\n\n0️⃣ Back",

        'rbi_shadow': "\n📉 HIDDEN CHARGES & RULES\n\n1️⃣ PENAL CHARGES:\nBanks CANNOT charge 'interest on interest'. Only fixed 'Penal Charges' allowed.\n\n2️⃣ KFS (Key Fact Statement):\nBefore loan, bank MUST give a sheet showing ALL costs. No hidden fees.\n\n3️⃣ COOLING OFF:\nDigital loans have 1-3 day period to return loan without penalty.\n\n0️⃣ Back",

        'invalid': "❌ I didn't understand.\n\nTry again:\n0️⃣ Menu",
        'error': '⚠️ Error!\n\nTry again:\n0️⃣ Menu'
    },
    'HI': {
        'greeting': '🛡️ वरिष्ठ नागरिक जालसाजी सुरक्षा\n\nभाषा चुनें:\n1️⃣ English\n2️⃣ हिंदी',
        
        'menu': "\n🏡 मुख्य मेनू\nबताइये मैं आपकी क्या मदद करूँ?\n\n1️⃣ नंबर की जांच करें 📱\n(क्या कॉल करने वाला चोर है?)\n\n2️⃣ मदद! मेरे पैसे चोरी हो गए 💸\n(पैसे वापस पाने का तरीका)\n\n3️⃣ ठग की शिकायत करें 🚫\n(दूसरों को बचाएं)\n\n4️⃣ RBI के नियम जानें ⚖️\n(रिकवरी और रिफंड के अधिकार)\n\n5️⃣ इस बॉट के बारे में ℹ️\n\n6️⃣ भाषा बदलें 🌐\n\n0️⃣ मेनू दोबारा देखें",
        
        'ask_number': '📱 नंबर भेजें:\nउदाहरण: +91-9876543210\n\n0️⃣ वापस',
        'checking': '🔍 जांच {number}...',
        'not_found': '✅ यह नंबर हमारी लिस्ट में नहीं है\n\nनंबर: {number}\n\n⚠️ सावधान: अगर कोई आपसे OTP या PIN मांगे, तो तुरंत फोन काट दें।\n\nअगर शक हो तो:\n3️⃣ दबाकर रिपोर्ट करें\n1930 📞 पर पुलिस को कॉल करें',
        
        'ask_recovery': '🚨 क्या हुआ?\n(उदाहरण: "₹50000 UPI")\n\n0️⃣ वापस',
        'recovery_options': '💰 तरीका चुनें:\n\n1️⃣ UPI / GPay / Paytm\n2️⃣ बैंक ट्रांसफर\n3️⃣ क्रिप्टो\n4️⃣ लोन फ्रॉड\n5️⃣ अन्य\n\n0️⃣ वापस',
        
        'recovery_upi': '🚨 UPI जालसाजी (Fraud)\n\nराशि: ₹{amount}\n\n📉 RBI रिकवरी चांस:\n• 3 दिन से कम: 🟢 100% (पूरे पैसे वापस)\n• 4-7 दिन: 🟡 उम्मीद है (नुकसान सीमित)\n• 7 दिन बाद: 🔴 कम उम्मीद (बैंक पर निर्भर)\n\n👇 ये स्टेप्स फॉलो करें:\n\nस्टेप 1️⃣: 1930 पर कॉल करें 📞\nतुरंत कॉल करें। पैसे फ्रीज करवाने का यह सबसे तेज तरीका है।\n\nस्टेप 2️⃣: बैंक को कॉल करें 🏦\n"Fraud" की रिपोर्ट करें और शिकायत नंबर लें।\n\nस्टेप 3️⃣: ऑनलाइन शिकायत 🌐\n24 घंटे के अंदर cybercrime.gov.in पर रिपोर्ट करें।\n\n0️⃣ मेनू',
        'recovery_bank': '🏦 बैंक जालसाजी (Bank Fraud)\n\nराशि: ₹{amount}\n\n📉 RBI रिकवरी चांस:\n• 3 दिन से कम: 🟢 100% (पूरे पैसे वापस)\n• 4-7 दिन: 🟡 उम्मीद है (नुकसान सीमित)\n• 7 दिन बाद: 🔴 कम उम्मीद (बैंक पर निर्भर)\n\n👇 ये स्टेप्स फॉलो करें:\n\nस्टेप 1️⃣: 1930 पर कॉल करें 📞\nसबसे पहले पुलिस को बताएं।\n\nस्टेप 2️⃣: बैंक शाखा (Branch) जाएं 🏃\nलिखित में शिकायत दें और खाता "Freeze" कराएं।\n\nस्टेप 3️⃣: ऑनलाइन रिपोर्ट 🌐\ncybercrime.gov.in पर शिकायत दर्ज करें।\n\n0️⃣ मेनू',
        'recovery_crypto': '⚠️ क्रिप्टो जालसाजी\n\nराशि: ₹{amount}\n\n❌ RBI स्थिति: रिकवरी मुश्किल है।\n\n👇 फिर भी यह कोशिश करें:\n\nस्टेप 1️⃣: 1930 पर कॉल करें 📞\nजिस बैंक से पैसे कटे थे, उसकी रिपोर्ट करें।\n\nस्टेप 2️⃣: ऐप सपोर्ट को लिखें 📉\nक्रिप्टो ऐप को तुरंत ईमेल करें।\n\nस्टेप 3️⃣: FIR दर्ज करें 👮\nनजदीकी साइबर पुलिस स्टेशन जाएं।\n\n0️⃣ मेनू',
        'recovery_loan': '🚨 लोन फ्रॉड सहायता\n\nराशि: ₹{amount}\n\n👇 बचने के उपाय:\n\nस्टेप 1️⃣: पैसे न दें\nफर्जी एजेंट आपको गिरफ्तार नहीं कर सकते। धमकी को इग्नोर करें।\n\nस्टेप 2️⃣: ब्लॉक और रिपोर्ट\nनंबर ब्लॉक करें और WhatsApp पर रिपोर्ट करें।\n\nस्टेप 3️⃣: 1930 कॉल करें 📞\nपरेशान करने वालों की शिकायत करें।\n\n0️⃣ मेनू',
        'recovery_other': '🆘 सामान्य सहायता\n\nराशि: ₹{amount}\n\n👇 ये कदम उठाएं:\n\nस्टेप 1️⃣: ठग को ब्लॉक करें\nसंपर्क तुरंत तोड़ दें।\n\nस्टेप 2️⃣: 1930 पर कॉल करें 📞\nपुलिस को सूचित करें।\n\nस्टेप 3️⃣: बैंक को बताएं\nअगर पैसे का लेनदेन हुआ है तो बैंक को बताएं।\n\n0️⃣ मेनू',

        'ask_report': '🚨 जालसाजी के बारे में बताएं:\n(उदाहरण: "प्रेम" या "धमकी")\n\n0️⃣ वापस',
        'report_received': '✅ रिपोर्ट प्राप्त!\n\nप्रकार: {scam_type}\n\nआपकी रिपोर्ट दूसरों को बचाएगी!\n\n📞 यह भी रिपोर्ट करें:\n🔗 cybercrime.gov.in\n☎️ 1930\n\n0️⃣ मेनू',
        
        'about': '💡 इस बॉट के बारे में\n\n🎯 बुजुर्गों को जालसाजी से बचाएं\n👥 50L+ भारतीय ठगे जाते हैं\n✅ हम रिकवरी में मदद करते हैं\n\n🛡️ सभी डेटा एन्क्रिप्ट किया\n\n📞 संसाधन:\n• 1930 (24/7)\n• cybercrime.gov.in\n\n0️⃣ मेनू',

        # --- RBI SECTIONS (HINDI) ---
        'rbi_menu': "\n⚖️ RBI के नियम और आपके अधिकार\nचुनें:\n\n1️⃣ रिकवरी एजेंट के नियम 👮\n(कॉल करने का समय)\n\n2️⃣ पैसे वापसी के नियम 💰\n(कब मिलेंगे पूरे पैसे?)\n\n3️⃣ गुप्त चार्ज / शैडो नियम 📉\n(पेनल्टी और ब्याज के नियम)\n\n0️⃣ मुख्य मेनू",

        'rbi_recovery': "\n👮 रिकवरी एजेंट के नियम\n\n1️⃣ समय सीमा:\nएजेंट केवल **सुबह 8:00 से शाम 7:00** के बीच कॉल कर सकते हैं।\nइसके बाद कॉल करना गैर-कानूनी है।\n\n2️⃣ कोई धमकी नहीं:\nवे आपको डरा नहीं सकते।\n\n3️⃣ शिकायत:\nअगर वे नियम तोड़ें, तो बैंक में शिकायत करें। 30 दिन में हल न मिले तो RBI लोकपाल को बताएं।\n\n0️⃣ वापस",

        'rbi_refund': "\n💰 रिफंड के नियम (जीरो लायबिलिटी)\n\n1️⃣ तुरंत रिपोर्ट करें:\n• 3 दिन के अंदर: **100% पैसे वापस** (Zero Liability)।\n• 4-7 दिन: नुकसान ₹5k-25k तक सीमित।\n\n2️⃣ शैडो रिवर्सल:\nजांच के दौरान बैंक को **10 दिन** में आपके खाते में पैसे (क्रेडिट) दिखाने होंगे।\n\n0️⃣ वापस",

        'rbi_shadow': "\n📉 गुप्त चार्ज और नियम\n\n1️⃣ पेनल्टी चार्ज:\nबैंक 'ब्याज पर ब्याज' नहीं लगा सकते। केवल फिक्स 'पेनल्टी' ले सकते हैं।\n\n2️⃣ KFS (की-फैक्ट स्टेटमेंट):\nलोन लेते समय, बैंक को **सारे खर्चे** लिखित में देने होंगे।\n\n3️⃣ कूलिंग ऑफ:\nडिजिटल लोन के 1-3 दिन के अंदर आप लोन वापस कर सकते हैं।\n\n0️⃣ वापस",

        'invalid': '❌ मुझे समझ नहीं आया।\n\nफिर से कोशिश करें:\n0️⃣ मेनू',
        'error': '⚠️ त्रुटि!\n\nफिर से कोशिश करें:\n0️⃣ मेनू'
    }
}

# --- ROUTES & LOGIC ---

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
    
    # --- LANGUAGE SELECTION ---
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
    
    # --- MAIN MENU ---
    elif state['step'] == 'main_menu':
        if any(w in msg_lower for w in ['1', 'check']):
            set_user_step(phone, 'check_number_input', flow='check_number')
            return MESSAGES[language]['ask_number']
        elif any(w in msg_lower for w in ['2', 'scammed', 'recovery']):
            set_user_step(phone, 'recovery_description', flow='recovery')
            return MESSAGES[language]['ask_recovery']
        elif any(w in msg_lower for w in ['3', 'report']):
            set_user_step(phone, 'report_description', flow='report')
            return MESSAGES[language]['ask_report']
        # NEW: RBI Menu Routing
        elif any(w in msg_lower for w in ['4', 'rbi', 'rules']):
            set_user_step(phone, 'rbi_rules_menu')
            return MESSAGES[language]['rbi_menu']
        elif any(w in msg_lower for w in ['5', 'about']):
            return MESSAGES[language]['about']
        elif any(w in msg_lower for w in ['6', 'change', 'language']):
            set_user_step(phone, 'language_selection')
            return MESSAGES['EN']['greeting']
        elif any(w in msg_lower for w in ['0', 'menu', 'help']):
            return MESSAGES[language]['menu']
        else:
            return MESSAGES[language]['invalid']
    
    # --- RBI RULES SUB-MENU ---
    elif state['step'] == 'rbi_rules_menu':
        if any(w in msg_lower for w in ['1', 'recovery', 'agent']):
            return MESSAGES[language]['rbi_recovery']
        elif any(w in msg_lower for w in ['2', 'refund', 'money']):
            return MESSAGES[language]['rbi_refund']
        elif any(w in msg_lower for w in ['3', 'hidden', 'shadow']):
            return MESSAGES[language]['rbi_shadow']
        elif any(w in msg_lower for w in ['0', 'back', 'menu']):
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        else:
            return MESSAGES[language]['invalid']
    
    # --- CHECK NUMBER ---
    elif state['step'] == 'check_number_input':
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        phone_pattern = r'\+91[-\s]?\d{4,}|\d{10}'
        match = re.search(phone_pattern, message)
        
        if match:
            number = match.group(0)
            set_user_step(phone, 'main_menu') # Reset to menu after showing result
            response = MESSAGES[language]['checking'].format(number=number)
            response += '\n\n' + MESSAGES[language]['not_found'].format(number=number)
            return response
        else:
            return MESSAGES[language]['invalid']
    
    # --- RECOVERY FLOW ---
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
        elif any(w in msg_lower for w in ['1', 'upi']):
            save_recovery_to_db(phone, amount, 'UPI')
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['recovery_upi'].format(amount=amount)
        elif any(w in msg_lower for w in ['2', 'bank']):
            save_recovery_to_db(phone, amount, 'Bank Transfer')
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['recovery_bank'].format(amount=amount)
        elif any(w in msg_lower for w in ['3', 'crypto']):
            save_recovery_to_db(phone, amount, 'Cryptocurrency')
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['recovery_crypto'].format(amount=amount)
        elif any(w in msg_lower for w in ['4', 'loan']):
            save_recovery_to_db(phone, amount, 'Loan Fraud')
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['recovery_loan'].format(amount=amount)
        elif any(w in msg_lower for w in ['5', 'other']):
            save_recovery_to_db(phone, amount, 'Other')
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['recovery_other'].format(amount=amount)
        else:
            return MESSAGES[language]['invalid']
    
    # --- REPORT FLOW ---
    elif state['step'] == 'report_description':
        if msg_lower in ['0', 'back']:
            set_user_step(phone, 'main_menu')
            return MESSAGES[language]['menu']
        
        scam_type = detect_scam_type(message, language)
        save_report_to_db(phone, scam_type, message)
        set_user_step(phone, 'main_menu')
        return MESSAGES[language]['report_received'].format(scam_type=scam_type)
    
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
    return jsonify({'bot': 'Elder Fraud Prevention', 'version': '2.1.0'}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("Bot starting...")
    app.run(debug=False, port=5000, host='0.0.0.0')