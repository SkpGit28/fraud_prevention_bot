import time
import re
import sys

# ==========================================
# 1. DATA & CONTENT
# ==========================================

MESSAGES = {
    'EN': {
        'greeting': '👋 Hello! I am your Elder Fraud Protector.\n\nI am here to keep you safe from scams.\n\nPlease choose your language:\n\n1️⃣ English\n2️⃣ हिंदी (Hindi)',
        
        'menu': "\n🏡 MAIN MENU\nHow can I help you today?\n\n1️⃣ Check a Phone Number 📱\n(Find out if a caller is fake)\n\n2️⃣ HELP! I lost money 💸\n(I will guide you to get it back)\n\n3️⃣ Report a Bad Number 🚫\n(Protect others from scams)\n\n4️⃣ Know RBI Rules ⚖️\n(Recovery times, Refunds, & Rights)\n\n5️⃣ Who are we? ℹ️\n\n6️⃣ Change Language / भाषा 🌐\n\n0️⃣ Show this Menu again",
        
        'ask_number': '\n📱 CHECK A NUMBER\n\nPlease type the phone number that called you.\n\nExample: 9876543210\n\n(Or press 0️⃣ to go back)',
        
        'checking': '⏳ Just a moment, checking that number...',
        
        'not_found': '✅ NO SCAM REPORTS FOUND (Yet)\n\nFor {number}.\n\n⚠️ CAUTION: Even if it looks safe, never share your OTP or PIN with anyone.\n\nIf you feel suspicious:\nPress 3️⃣ to Report it\nDial 1930 📞 for Police Help',
        
        'ask_recovery': '\n😌 TAKE A DEEP BREATH.\nDo not panic. We can help you fix this.\n\nTell me roughly what happened?\n(Example: "Sent 5000 on Paytm" or "Bank transfer")\n\n0️⃣ Go Back',
        
        'recovery_options': '\n🤝 WE ARE WITH YOU.\nSelect how the money was taken:\n\n1️⃣ UPI / GPay / Paytm 📱\n2️⃣ Bank Transfer 🏦\n3️⃣ Crypto / Bitcoin 🪙\n4️⃣ Loan App Fraud 📝\n5️⃣ Other\n\n0️⃣ Back',
        
        'recovery_upi': '\n🚨 UPI RECOVERY STEPS\n\nAmount: ₹{amount}\n\n👇 DO THIS IMMEDIATELY:\n\n1️⃣ Call 1930 📞 (Police Helpline)\nIt is Free. Call them now.\n\n2️⃣ Call Your Bank 🏦\nTell them: "Fraud Transaction"\n\n3️⃣ Do NOT delete SMS/Messages 📱\nYou will need them for proof.\n\n💪 You are strong. Act fast.\n\nPress 0️⃣ for Main Menu',
        
        'recovery_bank': '\n🏦 BANK RECOVERY STEPS\n\nAmount: ₹{amount}\n\n👇 ACT NOW (Within 24 hours):\n\n1️⃣ Call 1930 📞\nThis is the Cyber Crime Helpline.\n\n2️⃣ Visit Your Bank Branch 🏃\nAsk them to "Freeze" the receiver\'s account.\n\n3️⃣ File Complaint Online 🌐\nIf you can, go to cybercrime.gov.in\n\nPress 0️⃣ for Main Menu',
        
        'recovery_crypto': '\n⚠️ CRYPTO FRAUD DETECTED\n\nThis is a bit harder, but don\'t give up.\n\n1️⃣ Call 1930 📞 immediately.\n2️⃣ Do NOT pay any "fees" to get money back.\n3️⃣ Go to the Police Station to file an FIR.\n\nPress 0️⃣ for Main Menu',
        
        'recovery_loan': '\n🚨 LOAN FRAUD HELP\n\nAmount: ₹{amount}\n\n1️⃣ Do NOT pay any more money.\n2️⃣ Block the number immediately.\n3️⃣ Call 1930 for help.\n\nDon\'t worry, fake loans cannot arrest you.\n\nPress 0️⃣ for Menu',
        
        'recovery_other': '\n🆘 GENERAL HELP\n\nAmount: ₹{amount}\n\n1️⃣ Block the scammer.\n2️⃣ Call 1930 (Police Helpline).\n3️⃣ Call your Bank immediately.\n\nYou can fix this. Stay strong.\n\nPress 0️⃣ for Menu',
        
        'ask_report': '\n🛡️ REPORT A SCAMMER\n\nThank you for protecting others.\n\nWhat did the scammer say or do?\n(Example: "Promised a free gift" or "Threatened arrest")\n\n0️⃣ Go Back',
        
        'report_received': '✅ REPORT SAVED.\n\nWe have noted this scam: "{scam_type}"\n\n👮 We will alert other seniors about this trick.\n\nThank you for being a hero today! 🌟\n\nPress 0️⃣ for Main Menu',
        
        'about': '\nℹ️ WHO ARE WE?\n\nWe are a digital friend for senior citizens.\n\n🎯 Our Job: To stop you from losing hard-earned money.\n\n📞 Important Numbers:\n• 1930 (Cyber Police)\n• 100 (Police)\n\nRemember: No bank will ever ask for your PIN or OTP over the phone.\n\nPress 0️⃣ for Main Menu',
        
        # --- RBI SECTIONS ---
        'rbi_menu': "\n⚖️ RBI RULES & YOUR RIGHTS\nSelect a topic to learn more:\n\n1️⃣ Recovery Agent Rules 👮\n(When can they call?)\n\n2️⃣ Money Refund Rules 💰\n(Zero Liability & Time limits)\n\n3️⃣ Hidden Charges / Shadow Rules 📉\n(Penal charges vs Interest)\n\n0️⃣ Back to Main Menu",

        'rbi_recovery': "\n👮 RECOVERY AGENT RULES\n\n1️⃣ TIME LIMITS:\nAgents can ONLY call between **8:00 AM and 7:00 PM**.\nCalls outside this time are HARASSMENT.\n\n2️⃣ NO THREATS:\nThey cannot threaten you or call your relatives.\n\n3️⃣ COMPLAIN:\nIf they break these rules, complain to your Bank immediately. If the Bank ignores you for 30 days, complain to the RBI Ombudsman.\n\n0️⃣ Back",

        'rbi_refund': "\n💰 REFUND RULES (Zero Liability)\n\nIf money was stolen from your account:\n\n1️⃣ REPORT FAST (Golden Rule):\n• Within 3 Days: You get **100% money back** (Zero Liability).\n• 4 to 7 Days: You lose a maximum of ₹5,000 to ₹25,000 (Limited Liability).\n\n2️⃣ SHADOW REVERSAL:\nOnce you report, the Bank must credit the amount to your account within **10 working days** while they investigate.\n\n3️⃣ 1930 HELPLINE:\nCall 1930 immediately to freeze the scammer's account.\n\n0️⃣ Back",

        'rbi_shadow': "\n📉 HIDDEN CHARGES & SHADOW RULES\n\n1️⃣ PENAL CHARGES:\nBanks CANNOT charge 'interest on interest' for late payments. They can only charge a fixed 'Penal Charge'.\n\n2️⃣ KEY FACT STATEMENT (KFS):\nBefore you take a loan, the bank MUST give you a simple sheet showing ALL costs. No hidden fees allowed.\n\n3️⃣ COOLING OFF PERIOD:\nFor digital loans, you have a 1-3 day 'Cooling Off' period to return the loan without penalty.\n\n0️⃣ Back",

        'invalid': "❌ I didn't catch that.\n\nPlease type the number options (1, 2, 3...)\n\nOr press 0️⃣ for the Menu.",
        'error': '⚠️ A small error occurred.\nPress 0️⃣ to start over.'
    },
    'HI': {
        'greeting': '👋 नमस्ते! मैं आपका सुरक्षा साथी हूँ।\n\nमैं आपको ऑनलाइन ठगी से बचाने के लिए यहाँ हूँ।\n\nअपनी भाषा चुनें:\n\n1️⃣ English\n2️⃣ हिंदी (Hindi)',
        
        'menu': "\n🏡 मुख्य मेनू\nबताइये मैं आपकी क्या मदद करूँ?\n\n1️⃣ नंबर की जांच करें 📱\n(क्या कॉल करने वाला चोर है?)\n\n2️⃣ मदद! मेरे पैसे चोरी हो गए 💸\n(पैसे वापस पाने का तरीका)\n\n3️⃣ ठग की शिकायत करें 🚫\n(दूसरों को बचाएं)\n\n4️⃣ RBI के नियम जानें ⚖️\n(रिकवरी और रिफंड के अधिकार)\n\n5️⃣ हम कौन हैं? ℹ️\n\n6️⃣ Change Language / भाषा बदलें 🌐\n\n0️⃣ मेनू दोबारा देखें",
        
        'ask_number': '\n📱 नंबर जांचें\n\nवह फोन नंबर लिखें जिससे कॉल आया था।\n\nउदाहरण: 9876543210\n\n(या वापस जाने के लिए 0️⃣ दबाएं)',
        
        'checking': '⏳ बस एक मिनट, नंबर चेक कर रहा हूँ...',
        
        'not_found': '✅ यह नंबर हमारी लिस्ट में नहीं है\n\nनंबर: {number}\n\n⚠️ सावधान: अगर कोई आपसे OTP या PIN मांगे, तो तुरंत फोन काट दें।\n\nअगर शक हो तो:\n3️⃣ दबाकर रिपोर्ट करें\n1930 📞 पर पुलिस को कॉल करें',
        
        'ask_recovery': '\n😌 घबराएं नहीं। लंबी सांस लें।\nहम सब ठीक कर सकते हैं।\n\nक्या हुआ था? थोड़ा बताएं:\n(जैसे: "Paytm से 5000 गए" या "बैंक फ्रॉड")',
        
        'recovery_options': '\n🤝 हम आपके साथ हैं।\nपैसे कैसे कटे?\n\n1️⃣ UPI / PhonePe / Paytm 📱\n2️⃣ बैंक ट्रांसफर 🏦\n3️⃣ क्रिप्टो / Bitcoin 🪙\n4️⃣ लोन ऐप फ्रॉड 📝\n5️⃣ अन्य\n\n0️⃣ वापस',
        
        'recovery_upi': '\n🚨 UPI रिकवरी (बचाव)\n\nराशि: ₹{amount}\n\n👇 यह तुरंत करें:\n\n1️⃣ 1930 पर कॉल करें 📞\nयह पुलिस का नंबर है। अभी कॉल करें।\n\n2️⃣ अपने बैंक को कॉल करें 🏦\nउन्हें बताएं "फ्रॉड हुआ है"।\n\n3️⃣ मैसेज डिलीट न करें 📱\nये सबूत हैं।\n\n💪 हिम्मत रखें। अभी कार्यवाही करें।\n\n0️⃣ मुख्य मेनू',
        
        'recovery_bank': '\n🏦 बैंक फ्रॉड बचाव\n\nराशि: ₹{amount}\n\n👇 अगले 24 घंटे बहुत जरूरी हैं:\n\n1️⃣ 1930 पर कॉल करें 📞\n\n2️⃣ अपनी बैंक शाखा (Branch) जाएं 🏃\nउनसे कहें कि चोर का खाता "Freeze" करें।\n\n3️⃣ शिकायत दर्ज करें 🌐\nअगर हो सके तो cybercrime.gov.in पर जाएं।\n\n0️⃣ मुख्य मेनू',
        
        'recovery_crypto': '\n⚠️ क्रिप्टो फ्रॉड\n\nयह थोड़ा कठिन है, लेकिन हार न मानें।\n\n1️⃣ तुरंत 1930 📞 पर कॉल करें।\n2️⃣ पैसे वापस पाने के लिए किसी को और पैसे न दें।\n3️⃣ पुलिस स्टेशन जाकर FIR दर्ज कराएं।\n\n0️⃣ मुख्य मेनू',

        'recovery_loan': '\n🚨 लोन फ्रॉड सहायता\n\nराशि: ₹{amount}\n\n1️⃣ और पैसे बिल्कुल न दें।\n2️⃣ नंबर को तुरंत ब्लॉक करें।\n3️⃣ 1930 पर कॉल करें।\n\nचिंता न करें, फर्जी लोन वाले आपको गिरफ्तार नहीं कर सकते।\n\n0️⃣ मेनू',

        'recovery_other': '\n🆘 सामान्य सहायता\n\nराशि: ₹{amount}\n\n1️⃣ ठग को ब्लॉक करें।\n2️⃣ 1930 (पुलिस) पर कॉल करें।\n3️⃣ अपने बैंक को अभी फोन करें।\n\nहिम्मत रखें।\n\n0️⃣ मेनू',
        
        'ask_report': '\n🛡️ ठग की शिकायत\n\nदूसरों को बचाने के लिए शुक्रिया।\n\nठग ने क्या कहा या किया?\n(जैसे: "लॉटरी का लालच दिया" या "पुलिस बनकर डराया")',
        
        'report_received': '✅ शिकायत दर्ज हो गई।\n\nहमने नोट कर लिया है: "{scam_type}"\n\n👮 हम दूसरे बुजुर्गों को इसके बारे में सावधान करेंगे।\n\nआज आपने एक अच्छा काम किया है! 🌟\n\n0️⃣ मुख्य मेनू',
        
        'about': '\nℹ️ हम कौन हैं?\n\nहम वरिष्ठ नागरिकों के लिए एक डिजिटल दोस्त हैं।\n\n🎯 हमारा काम: आपकी मेहनत की कमाई को सुरक्षित रखना।\n\n📞 जरूरी नंबर:\n• 1930 (साइबर पुलिस)\n• 100 (पुलिस)\n\nयाद रखें: कोई भी बैंक फोन पर आपसे पिन (PIN) या ओटीपी (OTP) नहीं मांगता।\n\n0️⃣ मुख्य मेनू',

        # --- RBI SECTIONS HINDI ---
        'rbi_menu': "\n⚖️ RBI के नियम और आपके अधिकार\nजानकारी के लिए चुनें:\n\n1️⃣ रिकवरी एजेंट के नियम 👮\n(कॉल करने का समय)\n\n2️⃣ पैसे वापसी के नियम 💰\n(कब मिलेंगे पूरे पैसे?)\n\n3️⃣ गुप्त चार्ज / शैडो नियम 📉\n(पेनल्टी और ब्याज के नियम)\n\n0️⃣ मुख्य मेनू",

        'rbi_recovery': "\n👮 रिकवरी एजेंट के नियम\n\n1️⃣ समय सीमा (Time Limits):\nएजेंट केवल **सुबह 8:00 से शाम 7:00** के बीच कॉल कर सकते हैं।\nइसके बाद कॉल करना गैर-कानूनी है।\n\n2️⃣ कोई धमकी नहीं:\nवे आपको डरा नहीं सकते और न ही रिश्तेदारों को फोन कर सकते हैं।\n\n3️⃣ शिकायत:\nअगर वे नियम तोड़ें, तो बैंक में शिकायत करें। अगर 30 दिन में हल न मिले, तो RBI लोकपाल (Ombudsman) को बताएं।\n\n0️⃣ वापस",

        'rbi_refund': "\n💰 रिफंड के नियम (जीरो लायबिलिटी)\n\nअगर आपके खाते से पैसे चोरी हुए हैं:\n\n1️⃣ तुरंत रिपोर्ट करें (सुनहरा नियम):\n• 3 दिन के अंदर: आपको **100% पैसे वापस** मिलेंगे (Zero Liability)।\n• 4 से 7 दिन: आपका नुकसान ₹5,000 से ₹25,000 तक सीमित रहेगा।\n\n2️⃣ शैडो रिवर्सल (Shadow Reversal):\nरिपोर्ट करने पर, जांच के दौरान बैंक को **10 दिन** के भीतर आपके खाते में पैसे (क्रेडिट) दिखाने होंगे।\n\n3️⃣ 1930 हेल्पलाइन:\nतुरंत 1930 पर कॉल करें।\n\n0️⃣ वापस",

        'rbi_shadow': "\n📉 गुप्त चार्ज और शैडो नियम\n\n1️⃣ पेनल्टी चार्ज:\nबैंक लेट पेमेंट पर 'ब्याज पर ब्याज' नहीं लगा सकते। वे केवल एक फिक्स 'पेनल्टी चार्ज' ले सकते हैं।\n\n2️⃣ की-फैक्ट स्टेटमेंट (KFS):\nलोन लेते समय, बैंक को एक साफ पर्चे पर **सारे खर्चे** लिखकर देने होंगे। कोई गुप्त फीस नहीं हो सकती।\n\n3️⃣ कूलिंग ऑफ पीरियड:\nडिजिटल लोन लेने के 1-3 दिन के अंदर आप लोन वापस कर सकते हैं, बिना किसी पेनल्टी के।\n\n0️⃣ वापस",
        
        'invalid': '❌ मुझे समझ नहीं आया।\n\nकृपया विकल्पों के नंबर लिखें (1, 2, 3...)\n\nया 0️⃣ दबाकर मेनू देखें।',
        'error': '⚠️ कुछ गड़बड़ हुई।\n0️⃣ दबाकर शुरू करें.'
    }
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def detect_scam_type(message, language='EN'):
    msg = message.lower()
    
    keywords = {
        'romance': ['love', 'dating', 'relationship', 'girl', 'boy', 'girlfriend', 'boyfriend', 'प्रेम', 'दोस्ती'],
        'loan': ['loan', 'credit', 'approval', 'emi', 'लोन', 'कर्ज', 'उधार'],
        'police': ['police', 'arrest', 'cbi', 'court', 'jail', 'पुलिस', 'गिरफ्तारी', 'जेल'],
        'investment': ['investment', 'profit', 'return', 'scheme', 'double', 'निवेश', 'फायदा', 'मुनाफा'],
        'bank': ['bank', 'account', 'verify', 'otp', 'atm', 'kyc', 'pan', 'बैंक', 'खाता', 'केवाईसी']
    }

    if any(w in msg for w in keywords['romance']):
        return 'Romance/Friendship Scam' if language == 'EN' else 'दोस्ती/रोमांस फ्रॉड'
    if any(w in msg for w in keywords['loan']):
        return 'Fake Loan App' if language == 'EN' else 'नकली लोन ऐप'
    if any(w in msg for w in keywords['police']):
        return 'Digital Arrest Threat' if language == 'EN' else 'पुलिस/गिरफ्तारी की धमकी'
    if any(w in msg for w in keywords['investment']):
        return 'Investment Scheme' if language == 'EN' else 'निवेश योजना'
    if any(w in msg for w in keywords['bank']):
        return 'Bank Impersonation' if language == 'EN' else 'फर्जी बैंक कॉल'
    
    return 'General Suspicious Activity' if language == 'EN' else 'अन्य संदिग्ध गतिविधि'

def print_slow(text, delay=0.01):
    """Simulates typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def simulate_processing(seconds=1.5):
    """Simulates processing delay"""
    time.sleep(seconds)

# ==========================================
# 3. MAIN APPLICATION LOGIC
# ==========================================

def main():
    # Initial State
    state = {
        'language': 'EN',
        'step': 'language_selection',
        'data': {}
    }

    # Clear screen (simple newline method)
    print("\n" * 50)
    
    # Show Initial Greeting
    print(MESSAGES['EN']['greeting'])

    while True:
        try:
            # Get User Input
            user_input = input("\n> ").strip().lower()
            
            current_lang = state['language']
            
            # --- STEP 1: LANGUAGE SELECTION ---
            if state['step'] == 'language_selection':
                if user_input in ['1', 'english', 'en']:
                    state['language'] = 'EN'
                    state['step'] = 'main_menu'
                    print_slow(MESSAGES['EN']['menu'])
                elif user_input in ['2', 'हिंदी', 'hindi', 'hi']:
                    state['language'] = 'HI'
                    state['step'] = 'main_menu'
                    print_slow(MESSAGES['HI']['menu'])
                else:
                    print(MESSAGES['EN']['greeting'])
            
            # --- STEP 2: MAIN MENU ---
            elif state['step'] == 'main_menu':
                if any(w in user_input for w in ['1', 'check', 'check number']):
                    state['step'] = 'check_number_input'
                    print(MESSAGES[current_lang]['ask_number'])
                
                elif any(w in user_input for w in ['2', 'help', 'lost money', 'scammed']):
                    state['step'] = 'recovery_description'
                    print(MESSAGES[current_lang]['ask_recovery'])
                
                elif any(w in user_input for w in ['3', 'report', 'bad number']):
                    state['step'] = 'report_description'
                    print(MESSAGES[current_lang]['ask_report'])

                # NEW: RBI Rules
                elif any(w in user_input for w in ['4', 'rbi', 'rules']):
                    state['step'] = 'rbi_rules_menu'
                    print(MESSAGES[current_lang]['rbi_menu'])
                
                elif any(w in user_input for w in ['5', 'about', 'who']):
                    print(MESSAGES[current_lang]['about'])
                    # Stay in menu, prompts user implicitly
                    
                elif any(w in user_input for w in ['6', 'change', 'language', 'भाषा']):
                    state['step'] = 'language_selection'
                    print(MESSAGES['EN']['greeting'])
                    
                elif user_input in ['0', 'menu', 'back']:
                    print(MESSAGES[current_lang]['menu'])
                    
                else:
                    print(MESSAGES[current_lang]['invalid'])

            # --- STEP 3: RBI RULES SUB-MENU ---
            elif state['step'] == 'rbi_rules_menu':
                if any(w in user_input for w in ['1', 'recovery', 'agent']):
                    print(MESSAGES[current_lang]['rbi_recovery'])
                elif any(w in user_input for w in ['2', 'refund', 'money']):
                    print(MESSAGES[current_lang]['rbi_refund'])
                elif any(w in user_input for w in ['3', 'hidden', 'shadow', 'charges']):
                    print(MESSAGES[current_lang]['rbi_shadow'])
                elif any(w in user_input for w in ['0', 'back', 'menu']):
                    state['step'] = 'main_menu'
                    print(MESSAGES[current_lang]['menu'])
                else:
                    print(MESSAGES[current_lang]['invalid'])

            # --- STEP 4: CHECK NUMBER ---
            elif state['step'] == 'check_number_input':
                if user_input in ['0', 'back', 'menu']:
                    state['step'] = 'main_menu'
                    print(MESSAGES[current_lang]['menu'])
                else:
                    # Regex for phone number (simple validation)
                    phone_pattern = r'\+91[-\s]?\d{4,}|\d{10}'
                    match = re.search(phone_pattern, user_input)
                    
                    if match:
                        number = match.group(0)
                        print(MESSAGES[current_lang]['checking'])
                        simulate_processing(1.5)
                        print(MESSAGES[current_lang]['not_found'].replace('{number}', number))
                        # We stay in this state or go back to menu? React stays, let's offer menu
                    else:
                        error_msg = "⚠️ That doesn't look like a phone number. Try entering 10 digits." if current_lang == 'EN' else "⚠️ यह फोन नंबर जैसा नहीं लग रहा। कृपया 10 अंक लिखें।"
                        print(error_msg)

            # --- STEP 5: RECOVERY DESCRIPTION ---
            elif state['step'] == 'recovery_description':
                if user_input in ['0', 'back', 'menu']:
                    state['step'] = 'main_menu'
                    print(MESSAGES[current_lang]['menu'])
                else:
                    # Extract amount using regex
                    amount_match = re.search(r'₹?(\d+,?\d*)', user_input)
                    amount = amount_match.group(1) if amount_match else 'Unknown'
                    
                    state['data']['amount'] = amount
                    state['step'] = 'recovery_method_select'
                    print(MESSAGES[current_lang]['recovery_options'])

            # --- STEP 6: RECOVERY METHOD ---
            elif state['step'] == 'recovery_method_select':
                amount = state['data'].get('amount', 'Unknown')
                
                if user_input in ['0', 'back']:
                    state['step'] = 'main_menu'
                    print(MESSAGES[current_lang]['menu'])
                
                elif any(w in user_input for w in ['1', 'upi', 'phonepe', 'gpay', 'paytm']):
                    print(MESSAGES[current_lang]['recovery_upi'].replace('{amount}', amount))
                    state['step'] = 'main_menu' # Reset after showing advice
                    
                elif any(w in user_input for w in ['2', 'bank', 'transfer']):
                    print(MESSAGES[current_lang]['recovery_bank'].replace('{amount}', amount))
                    state['step'] = 'main_menu'
                    
                elif any(w in user_input for w in ['3', 'crypto', 'bitcoin']):
                    print(MESSAGES[current_lang]['recovery_crypto'].replace('{amount}', amount))
                    state['step'] = 'main_menu'
                    
                elif any(w in user_input for w in ['4', 'loan']):
                    print(MESSAGES[current_lang]['recovery_loan'].replace('{amount}', amount))
                    state['step'] = 'main_menu'

                elif any(w in user_input for w in ['5', 'other']):
                    print(MESSAGES[current_lang]['recovery_other'].replace('{amount}', amount))
                    state['step'] = 'main_menu'
                    
                else:
                    print(MESSAGES[current_lang]['invalid'])

            # --- STEP 7: REPORT SCAM ---
            elif state['step'] == 'report_description':
                if user_input in ['0', 'back', 'menu']:
                    state['step'] = 'main_menu'
                    print(MESSAGES[current_lang]['menu'])
                else:
                    scam_type = detect_scam_type(user_input, current_lang)
                    print(MESSAGES[current_lang]['report_received'].replace('{scam_type}', scam_type))
                    state['step'] = 'main_menu'

        except KeyboardInterrupt:
            print("\n👋 Goodbye! Stay safe.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            state['step'] = 'main_menu'

if __name__ == "__main__":
    main()