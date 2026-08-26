"""Synthetic demo dataset.

Three clearly-synthetic Indian government notices with fully curated analysis,
document checklists, action plans and response templates (English + Hindi +
Telugu). This lets the entire demo run deterministically with NO API key.

EVERYTHING HERE IS FICTIONAL. Departments, reference numbers and identifiers
are invented for demonstration only and do not correspond to any real person,
document, or government system. No real Aadhaar/PAN/bank data is used.
"""

from __future__ import annotations

from .demo_data_extra import EXTRA_DEMOS

DISCLAIMER_LINE = (
    "*** SYNTHETIC DEMONSTRATION NOTICE — NOT AN OFFICIAL GOVERNMENT DOCUMENT ***"
)


DEMO_NOTICES: list[dict] = [
    # ---------------------------------------------------------------- 1. TAX
    {
        "id": "tax-143-1",
        "title": "Income Tax — Preliminary Assessment (Sec. 143(1))",
        "category": "Income Tax",
        "icon": "tax",
        "authority": "Office of the Assessing Officer, Demo Income Tax Ward 7(3) [SYNTHETIC]",
        "blurb": "A mismatch was found between reported and recorded interest income. A response is requested.",
        "raw_text": f"""{DISCLAIMER_LINE}

DEMO INCOME TAX DEPARTMENT (SYNTHETIC)
Office of the Assessing Officer, Ward 7(3), Demo City

Intimation under Section 143(1) of the Demo Income Tax Act (Illustrative)

Reference Number: NM-DEMO-IT-2026-000481
PAN on record: (demo) ABCDE0000F
Date of Notice: 12 August 2026
Response Due By: 11 September 2026

Subject: Proposed adjustment to your return of income for Assessment Year 2026-27.

Sir/Madam,

A preliminary processing of your income tax return for AY 2026-27 has been
carried out. The following mismatch was observed between the income reported
in your return and the information available with this office:

  - Interest income reported by you        : Rs. 4,000
  - Interest income as per records (demo)   : Rs. 21,500
  - Proposed addition                       : Rs. 17,500

You are requested to respond to this intimation within 30 days, either by
agreeing to the proposed adjustment or by submitting a written explanation
along with supporting evidence. If no response is received by the due date,
the proposed adjustment may be processed as indicated above.

Documents that may support your response:
  1. Form 16 / salary statement (demo)
  2. Bank interest certificate for the relevant year
  3. A signed response letter stating your agreement or explanation

For assistance you may contact the Demo Helpdesk at 1800-DEMO-000 (not a real
number) or visit the illustrative e-filing portal referenced in this demo.

This is a computer-generated synthetic notice for demonstration only.
{DISCLAIMER_LINE}
""",
        "analysis": {
            "notice_type": "Income Tax preliminary assessment intimation (Section 143(1))",
            "authority": "Demo Income Tax Department, Ward 7(3) [SYNTHETIC]",
            "notice_date": "12 August 2026",
            "deadline": "11 September 2026",
            "reference_number": "NM-DEMO-IT-2026-000481",
            "subject": "Proposed adjustment to your income tax return for AY 2026-27",
            "summary": (
                "The tax office processed your return and found a difference between "
                "the interest income you reported (Rs. 4,000) and what their records "
                "show (Rs. 21,500). They plan to add Rs. 17,500 to your income unless "
                "you respond by 11 September 2026."
            ),
            "why_received": (
                "You received this because the interest income in your return did not "
                "match the figure in the department's records for AY 2026-27."
            ),
            "required_action": (
                "Within 30 days, either agree to the adjustment online or send a "
                "written explanation with supporting documents (like a bank interest "
                "certificate)."
            ),
            "consequences": (
                "The notice states that if you do not respond by 11 September 2026, "
                "the proposed addition of Rs. 17,500 may be processed as indicated."
            ),
            "required_documents": [
                {"name": "Form 16 / salary statement", "reason": "Shows your reported income for the year.", "required": True},
                {"name": "Bank interest certificate", "reason": "Confirms the actual interest income you earned.", "required": True},
                {"name": "Signed response letter", "reason": "States whether you agree or your explanation.", "required": True},
            ],
            "next_steps": [
                "Check your bank interest certificate for the year",
                "Compare it with the Rs. 21,500 figure in the notice",
                "Collect Form 16 and the interest certificate",
                "Prepare a response letter agreeing or explaining",
                "Submit before 11 September 2026",
            ],
            "uncertainties": [
                "The notice does not specify which bank account the interest relates to — verify with the issuing authority if unsure.",
            ],
            "confidence": 0.9,
            "translations": {
                "hi": {
                    "summary": "आयकर कार्यालय ने आपका रिटर्न जाँचा और पाया कि आपने जो ब्याज आय बताई (रु. 4,000) और उनके रिकॉर्ड में दर्ज राशि (रु. 21,500) में अंतर है। यदि आप 11 सितंबर 2026 तक जवाब नहीं देते, तो वे आपकी आय में रु. 17,500 जोड़ सकते हैं।",
                    "why_received": "यह नोटिस इसलिए आया क्योंकि आपके रिटर्न में दर्ज ब्याज आय, विभाग के रिकॉर्ड से मेल नहीं खाती (आकलन वर्ष 2026-27)।",
                    "required_action": "30 दिनों के भीतर या तो समायोजन से ऑनलाइन सहमति दें, या सहायक दस्तावेज़ों (जैसे बैंक ब्याज प्रमाणपत्र) के साथ लिखित स्पष्टीकरण भेजें।",
                    "consequences": "नोटिस के अनुसार, यदि आप 11 सितंबर 2026 तक जवाब नहीं देते, तो रु. 17,500 का प्रस्तावित जोड़ लागू किया जा सकता है।",
                },
                "te": {
                    "summary": "ఆదాయపు పన్ను కార్యాలయం మీ రిటర్న్‌ను పరిశీలించి, మీరు తెలిపిన వడ్డీ ఆదాయం (రూ. 4,000) వారి రికార్డులలోని మొత్తం (రూ. 21,500) మధ్య తేడాను గుర్తించింది. మీరు 11 సెప్టెంబర్ 2026 లోపు స్పందించకపోతే, వారు మీ ఆదాయానికి రూ. 17,500 జోడించవచ్చు.",
                    "why_received": "మీ రిటర్న్‌లో తెలిపిన వడ్డీ ఆదాయం, శాఖ రికార్డులతో సరిపోలకపోవడం వల్ల (అసెస్‌మెంట్ సంవత్సరం 2026-27) ఈ నోటీసు వచ్చింది.",
                    "required_action": "30 రోజుల్లోపు, సర్దుబాటుకు ఆన్‌లైన్‌లో అంగీకరించండి లేదా సహాయక పత్రాలతో (బ్యాంకు వడ్డీ ధృవీకరణ పత్రం వంటివి) లిఖితపూర్వక వివరణ పంపండి.",
                    "consequences": "నోటీసు ప్రకారం, మీరు 11 సెప్టెంబర్ 2026 లోపు స్పందించకపోతే, ప్రతిపాదిత రూ. 17,500 జోడింపు అమలు కావచ్చు.",
                },
            },
        },
        "response_template": {
            "en": (
                "To,\nThe Assessing Officer, Demo Income Tax Ward 7(3)\n\n"
                "Subject: Response to intimation NM-DEMO-IT-2026-000481 (AY 2026-27)\n\n"
                "Respected Sir/Madam,\n\n"
                "With reference to the above intimation dated 12 August 2026, I am "
                "submitting my response regarding the proposed adjustment of Rs. 17,500 "
                "to my interest income. I am enclosing my bank interest certificate and "
                "Form 16 for your kind verification. [State here whether you AGREE with "
                "the adjustment, or EXPLAIN the difference.]\n\n"
                "I request you to kindly consider the enclosed documents. Please let me "
                "know if any further information is required.\n\n"
                "Thanking you,\n[Your Name]\nPAN: [Your PAN]\nDate: [Date]"
            ),
            "hi": (
                "सेवा में,\nआकलन अधिकारी, डेमो आयकर वार्ड 7(3)\n\n"
                "विषय: सूचना NM-DEMO-IT-2026-000481 का उत्तर (आ.व. 2026-27)\n\n"
                "महोदय/महोदया,\n\n"
                "दिनांक 12 अगस्त 2026 की उपरोक्त सूचना के संदर्भ में, मैं रु. 17,500 के "
                "प्रस्तावित समायोजन के संबंध में अपना उत्तर प्रस्तुत कर रहा/रही हूँ। सत्यापन हेतु "
                "मैं अपना बैंक ब्याज प्रमाणपत्र और फॉर्म 16 संलग्न कर रहा/रही हूँ। [यहाँ लिखें कि "
                "आप समायोजन से सहमत हैं या अंतर का स्पष्टीकरण दें।]\n\n"
                "कृपया संलग्न दस्तावेज़ों पर विचार करें।\n\nधन्यवाद,\n[आपका नाम]\nपैन: [आपका पैन]\nदिनांक: [दिनांक]"
            ),
            "te": (
                "గౌరవనీయులైన,\nఅసెస్సింగ్ ఆఫీసర్, డెమో ఆదాయపు పన్ను వార్డ్ 7(3)\n\n"
                "విషయం: నోటీసు NM-DEMO-IT-2026-000481 కు స్పందన (అసెస్‌మెంట్ సం. 2026-27)\n\n"
                "అయ్యా/అమ్మా,\n\n"
                "12 ఆగస్టు 2026 నాటి పై నోటీసు సందర్భంగా, నా వడ్డీ ఆదాయానికి ప్రతిపాదించిన రూ. 17,500 "
                "సర్దుబాటుపై నా స్పందనను సమర్పిస్తున్నాను. పరిశీలన కోసం నా బ్యాంకు వడ్డీ ధృవీకరణ పత్రం "
                "మరియు ఫారం 16 జతచేస్తున్నాను. [మీరు సర్దుబాటుకు అంగీకరిస్తున్నారా లేదా తేడాను వివరించండి.]\n\n"
                "జతచేసిన పత్రాలను దయచేసి పరిగణించగలరు.\n\nధన్యవాదాలు,\n[మీ పేరు]\nPAN: [మీ PAN]\nతేదీ: [తేదీ]"
            ),
        },
    },
    # ------------------------------------------------------------ 2. PENSION
    {
        "id": "epf-kyc",
        "title": "Provident Fund — KYC & Contribution Verification",
        "category": "Pension / EPF",
        "icon": "pension",
        "authority": "Demo Regional Provident Fund Office, Zone II [SYNTHETIC]",
        "blurb": "Your EPF account needs KYC completion and contribution verification to avoid a hold.",
        "raw_text": f"""{DISCLAIMER_LINE}

DEMO EMPLOYEES' PROVIDENT FUND ORGANISATION (SYNTHETIC)
Regional Provident Fund Office, Zone II, Demo City

Notice: KYC Completion & Contribution Verification

Reference Number: NM-DEMO-EPF-2026-002217
Demo UAN: 1000-DEMO-2217 (illustrative)
Date of Notice: 20 August 2026
Action Required By: 04 September 2026

Dear Member,

Our records indicate that the Know Your Customer (KYC) details for your
provident fund account are incomplete, and a recent monthly contribution could
not be matched to your account. To keep your account active and ensure your
contributions are correctly credited, please complete the following:

  1. Complete/verify your KYC (bank account and ID linkage).
  2. Verify the contribution for the month of July 2026.

Documents to keep ready:
  - Demo UAN details / passbook copy
  - A cancelled cheque or bank passbook copy showing your account number
  - Identity proof (demo)
  - A signed declaration confirming your details are correct

If action is not completed by 04 September 2026, crediting of future
contributions may be delayed until KYC is completed. This will not cause any
loss of your existing balance.

For help, contact the Demo Member Helpdesk (not a real number).

This is a synthetic notice generated for a demonstration.
{DISCLAIMER_LINE}
""",
        "analysis": {
            "notice_type": "Provident Fund KYC completion and contribution verification notice",
            "authority": "Demo Regional Provident Fund Office, Zone II [SYNTHETIC]",
            "notice_date": "20 August 2026",
            "deadline": "04 September 2026",
            "reference_number": "NM-DEMO-EPF-2026-002217",
            "subject": "Complete KYC and verify your July 2026 EPF contribution",
            "summary": (
                "Your provident fund (EPF) account is missing some KYC details, and one "
                "recent monthly contribution could not be matched to your account. You "
                "need to complete KYC and verify the July 2026 contribution by "
                "04 September 2026 so future contributions are credited on time."
            ),
            "why_received": (
                "You received this because your EPF KYC (bank/ID linkage) is incomplete "
                "and the July 2026 contribution could not be automatically matched."
            ),
            "required_action": (
                "Complete or verify your KYC and confirm the July 2026 contribution "
                "before 04 September 2026."
            ),
            "consequences": (
                "The notice states that if KYC is not completed by the deadline, "
                "crediting of future contributions may be delayed. It explicitly says "
                "your existing balance will not be lost."
            ),
            "required_documents": [
                {"name": "Demo UAN details / passbook copy", "reason": "Identifies your EPF account.", "required": True},
                {"name": "Cancelled cheque or bank passbook copy", "reason": "Links the correct bank account for KYC.", "required": True},
                {"name": "Identity proof", "reason": "Verifies your identity for KYC.", "required": True},
                {"name": "Signed declaration", "reason": "Confirms your details are correct.", "required": False},
            ],
            "next_steps": [
                "Locate your UAN / passbook details",
                "Keep a cancelled cheque or passbook copy ready",
                "Keep an identity proof ready",
                "Complete KYC and confirm the July 2026 contribution",
                "Finish before 04 September 2026",
            ],
            "uncertainties": [
                "The notice does not say exactly which KYC field is missing — confirm with the issuing office if unclear.",
            ],
            "confidence": 0.88,
            "translations": {
                "hi": {
                    "summary": "आपके भविष्य निधि (EPF) खाते में कुछ KYC जानकारी अधूरी है, और हाल के एक मासिक अंशदान का मिलान आपके खाते से नहीं हो पाया। भविष्य के अंशदान समय पर जमा हों, इसके लिए 04 सितंबर 2026 तक KYC पूरा करें और जुलाई 2026 के अंशदान की पुष्टि करें।",
                    "why_received": "यह नोटिस इसलिए आया क्योंकि आपका EPF KYC (बैंक/पहचान लिंकिंग) अधूरा है और जुलाई 2026 का अंशदान स्वतः मिलान नहीं हो सका।",
                    "required_action": "04 सितंबर 2026 से पहले अपना KYC पूरा/सत्यापित करें और जुलाई 2026 के अंशदान की पुष्टि करें।",
                    "consequences": "नोटिस के अनुसार, यदि समय पर KYC पूरा नहीं होता, तो भविष्य के अंशदान जमा होने में देरी हो सकती है। यह स्पष्ट रूप से कहता है कि आपका मौजूदा बैलेंस समाप्त नहीं होगा।",
                },
                "te": {
                    "summary": "మీ ప్రావిడెంట్ ఫండ్ (EPF) ఖాతాలో కొన్ని KYC వివరాలు అసంపూర్తిగా ఉన్నాయి, ఇటీవలి ఒక నెల చందా మీ ఖాతాతో సరిపోలలేదు. భవిష్యత్ చందాలు సకాలంలో జమ అయ్యేలా 04 సెప్టెంబర్ 2026 లోపు KYC పూర్తిచేసి, జూలై 2026 చందాను ధృవీకరించండి.",
                    "why_received": "మీ EPF KYC (బ్యాంకు/గుర్తింపు అనుసంధానం) అసంపూర్తిగా ఉండటం, జూలై 2026 చందా ఆటోమేటిక్‌గా సరిపోలకపోవడం వల్ల ఈ నోటీసు వచ్చింది.",
                    "required_action": "04 సెప్టెంబర్ 2026 లోపు మీ KYC పూర్తిచేసి/ధృవీకరించి, జూలై 2026 చందాను నిర్ధారించండి.",
                    "consequences": "నోటీసు ప్రకారం, గడువులోగా KYC పూర్తికాకపోతే భవిష్యత్ చందాల జమలో ఆలస్యం కావచ్చు. మీ ప్రస్తుత నిల్వ నష్టపోదని స్పష్టంగా తెలిపింది.",
                },
            },
        },
        "response_template": {
            "en": (
                "To,\nThe Regional Provident Fund Officer, Demo RPFO Zone II\n\n"
                "Subject: KYC completion & contribution verification — Ref "
                "NM-DEMO-EPF-2026-002217\n\n"
                "Respected Sir/Madam,\n\n"
                "With reference to the above notice dated 20 August 2026, I confirm that "
                "I have completed/verified my KYC details and I am enclosing a cancelled "
                "cheque and identity proof for verification. I request you to kindly "
                "match my contribution for July 2026 and update my account.\n\n"
                "I declare that the details provided are correct to the best of my "
                "knowledge.\n\nThanking you,\n[Your Name]\nUAN: [Your UAN]\nDate: [Date]"
            ),
            "hi": (
                "सेवा में,\nक्षेत्रीय भविष्य निधि अधिकारी, डेमो RPFO ज़ोन II\n\n"
                "विषय: KYC पूर्णता एवं अंशदान सत्यापन — संदर्भ NM-DEMO-EPF-2026-002217\n\n"
                "महोदय/महोदया,\n\n"
                "दिनांक 20 अगस्त 2026 के उपरोक्त नोटिस के संदर्भ में, मैं पुष्टि करता/करती हूँ कि "
                "मैंने अपना KYC पूरा/सत्यापित कर लिया है और सत्यापन हेतु रद्द किया गया चेक एवं पहचान "
                "प्रमाण संलग्न कर रहा/रही हूँ। कृपया जुलाई 2026 के मेरे अंशदान का मिलान कर मेरा खाता "
                "अद्यतन करें।\n\nमैं घोषणा करता/करती हूँ कि दी गई जानकारी सही है।\n\nधन्यवाद,\n[आपका नाम]\nUAN: [आपका UAN]\nदिनांक: [दिनांक]"
            ),
            "te": (
                "గౌరవనీయులైన,\nప్రాంతీయ ప్రావిడెంట్ ఫండ్ అధికారి, డెమో RPFO జోన్ II\n\n"
                "విషయం: KYC పూర్తి & చందా ధృవీకరణ — రిఫ NM-DEMO-EPF-2026-002217\n\n"
                "అయ్యా/అమ్మా,\n\n"
                "20 ఆగస్టు 2026 నాటి పై నోటీసు సందర్భంగా, నేను నా KYC వివరాలను పూర్తిచేసాను/ధృవీకరించానని "
                "తెలియజేస్తున్నాను. పరిశీలన కోసం రద్దుచేసిన చెక్కు మరియు గుర్తింపు పత్రం జతచేస్తున్నాను. "
                "దయచేసి జూలై 2026 నా చందాను సరిపోల్చి నా ఖాతాను నవీకరించగలరు.\n\n"
                "అందించిన వివరాలు సరైనవని ప్రకటిస్తున్నాను.\n\nధన్యవాదాలు,\n[మీ పేరు]\nUAN: [మీ UAN]\nతేదీ: [తేదీ]"
            ),
        },
    },
    # -------------------------------------------------------- 3. CERTIFICATE
    {
        "id": "muni-address",
        "title": "Municipal — Address Verification for Certificate",
        "category": "Certificate / Municipal",
        "icon": "certificate",
        "authority": "Demo Municipal Corporation, Citizen Services Dept [SYNTHETIC]",
        "blurb": "Your certificate request is on hold pending address verification. Documents are requested.",
        "raw_text": f"""{DISCLAIMER_LINE}

DEMO MUNICIPAL CORPORATION (SYNTHETIC)
Citizen Services Department, Demo City

Notice: Address Verification for Pending Certificate Application

Reference Number: NM-DEMO-MUN-2026-004590
Application ID: APP-DEMO-77821 (illustrative)
Date of Notice: 22 August 2026
Please Respond By: 12 September 2026

Dear Applicant,

Your application for a Residence Certificate (Application ID APP-DEMO-77821) is
currently on hold. Before the certificate can be issued, the address you
provided needs to be verified. Please submit the documents listed below so that
processing can continue.

Required Documents:
  1. Proof of current address (e.g., a recent electricity or water bill) [demo]
  2. Latest property tax receipt OR rent agreement [demo]
  3. Completed address verification form (attached in the demo pack)

If the requested documents are not received by 12 September 2026, your
application may be marked inactive and you may need to re-apply. Submitting the
documents will allow verification to proceed.

For questions, contact the Demo Citizen Services counter (not a real contact).

This synthetic notice is provided only for demonstration purposes.
{DISCLAIMER_LINE}
""",
        "analysis": {
            "notice_type": "Municipal address-verification notice for a certificate application",
            "authority": "Demo Municipal Corporation, Citizen Services Dept [SYNTHETIC]",
            "notice_date": "22 August 2026",
            "deadline": "12 September 2026",
            "reference_number": "NM-DEMO-MUN-2026-004590",
            "subject": "Address verification needed for your Residence Certificate application",
            "summary": (
                "Your Residence Certificate application is on hold because your address "
                "needs to be verified. Submit proof of address, a property tax receipt "
                "or rent agreement, and the verification form by 12 September 2026 so "
                "the certificate can be issued."
            ),
            "why_received": (
                "You received this because the municipal office needs to verify the "
                "address on your pending Residence Certificate application."
            ),
            "required_action": (
                "Submit the requested address-proof documents before 12 September 2026 "
                "so verification can continue."
            ),
            "consequences": (
                "The notice states that if the documents are not received by the "
                "deadline, your application may be marked inactive and you may need to "
                "re-apply."
            ),
            "required_documents": [
                {"name": "Proof of current address", "reason": "Confirms where you currently live (e.g., a utility bill).", "required": True},
                {"name": "Property tax receipt or rent agreement", "reason": "Supports your claim to the address.", "required": True},
                {"name": "Address verification form", "reason": "Standard form the office needs to process the request.", "required": True},
            ],
            "next_steps": [
                "Find a recent utility bill in your name",
                "Locate your property tax receipt or rent agreement",
                "Fill in the address verification form",
                "Submit all documents together",
                "Complete before 12 September 2026",
            ],
            "uncertainties": [
                "The notice does not state whether digital copies are accepted — confirm with the issuing office.",
            ],
            "confidence": 0.9,
            "translations": {
                "hi": {
                    "summary": "आपका निवास प्रमाणपत्र आवेदन इसलिए रुका है क्योंकि आपके पते का सत्यापन आवश्यक है। प्रमाणपत्र जारी होने के लिए 12 सितंबर 2026 तक पते का प्रमाण, संपत्ति कर रसीद या किरायानामा, और सत्यापन फॉर्म जमा करें।",
                    "why_received": "यह नोटिस इसलिए आया क्योंकि नगरपालिका को आपके लंबित निवास प्रमाणपत्र आवेदन में दर्ज पते का सत्यापन करना है।",
                    "required_action": "12 सितंबर 2026 से पहले माँगे गए पते के प्रमाण दस्तावेज़ जमा करें ताकि सत्यापन जारी रह सके।",
                    "consequences": "नोटिस के अनुसार, यदि समय-सीमा तक दस्तावेज़ प्राप्त नहीं होते, तो आपका आवेदन निष्क्रिय किया जा सकता है और आपको दोबारा आवेदन करना पड़ सकता है।",
                },
                "te": {
                    "summary": "మీ నివాస ధృవీకరణ పత్రం దరఖాస్తు, మీ చిరునామా ధృవీకరణ అవసరమైనందున నిలిపివేయబడింది. పత్రం జారీ కావాలంటే 12 సెప్టెంబర్ 2026 లోపు చిరునామా రుజువు, ఆస్తి పన్ను రసీదు లేదా అద్దె ఒప్పందం, మరియు ధృవీకరణ ఫారం సమర్పించండి.",
                    "why_received": "మీ పెండింగ్ నివాస ధృవీకరణ పత్రం దరఖాస్తులోని చిరునామాను మునిసిపల్ కార్యాలయం ధృవీకరించవలసి ఉన్నందున ఈ నోటీసు వచ్చింది.",
                    "required_action": "ధృవీకరణ కొనసాగేలా 12 సెప్టెంబర్ 2026 లోపు కోరిన చిరునామా రుజువు పత్రాలను సమర్పించండి.",
                    "consequences": "నోటీసు ప్రకారం, గడువులోగా పత్రాలు అందకపోతే మీ దరఖాస్తు నిష్క్రియంగా గుర్తించబడవచ్చు, మీరు మళ్లీ దరఖాస్తు చేయవలసి రావచ్చు.",
                },
            },
        },
        "response_template": {
            "en": (
                "To,\nThe Citizen Services Officer, Demo Municipal Corporation\n\n"
                "Subject: Address verification for application APP-DEMO-77821 — Ref "
                "NM-DEMO-MUN-2026-004590\n\n"
                "Respected Sir/Madam,\n\n"
                "With reference to the above notice dated 22 August 2026, I am submitting "
                "the requested documents for verification of my address: a recent utility "
                "bill and my property tax receipt, along with the completed address "
                "verification form. I request you to kindly proceed with verification and "
                "issue my Residence Certificate.\n\n"
                "Thanking you,\n[Your Name]\nApplication ID: APP-DEMO-77821\nDate: [Date]"
            ),
            "hi": (
                "सेवा में,\nनागरिक सेवा अधिकारी, डेमो नगर निगम\n\n"
                "विषय: आवेदन APP-DEMO-77821 हेतु पता सत्यापन — संदर्भ NM-DEMO-MUN-2026-004590\n\n"
                "महोदय/महोदया,\n\n"
                "दिनांक 22 अगस्त 2026 के उपरोक्त नोटिस के संदर्भ में, मैं अपने पते के सत्यापन हेतु "
                "माँगे गए दस्तावेज़ जमा कर रहा/रही हूँ: एक हालिया उपयोगिता बिल, संपत्ति कर रसीद, और "
                "भरा हुआ पता सत्यापन फॉर्म। कृपया सत्यापन आगे बढ़ाकर मेरा निवास प्रमाणपत्र जारी करें।\n\n"
                "धन्यवाद,\n[आपका नाम]\nआवेदन आईडी: APP-DEMO-77821\nदिनांक: [दिनांक]"
            ),
            "te": (
                "గౌరవనీయులైన,\nసిటిజన్ సర్వీసెస్ ఆఫీసర్, డెమో మునిసిపల్ కార్పొరేషన్\n\n"
                "విషయం: దరఖాస్తు APP-DEMO-77821 కోసం చిరునామా ధృవీకరణ — రిఫ NM-DEMO-MUN-2026-004590\n\n"
                "అయ్యా/అమ్మా,\n\n"
                "22 ఆగస్టు 2026 నాటి పై నోటీసు సందర్భంగా, నా చిరునామా ధృవీకరణ కోసం కోరిన పత్రాలను "
                "సమర్పిస్తున్నాను: ఇటీవలి యుటిలిటీ బిల్లు, ఆస్తి పన్ను రసీదు, మరియు పూర్తిచేసిన చిరునామా "
                "ధృవీకరణ ఫారం. దయచేసి ధృవీకరణను కొనసాగించి నా నివాస ధృవీకరణ పత్రాన్ని జారీ చేయగలరు.\n\n"
                "ధన్యవాదాలు,\n[మీ పేరు]\nదరఖాస్తు ID: APP-DEMO-77821\nతేదీ: [తేదీ]"
            ),
        },
    },
]


# The recruitment and scholarship notices live in their own module to keep this
# file readable. They demonstrate the application/benefit workflows.
DEMO_NOTICES.extend(EXTRA_DEMOS)


def get_demo(demo_id: str) -> dict | None:
    for n in DEMO_NOTICES:
        if n["id"] == demo_id:
            return n
    return None


def demo_summaries() -> list[dict]:
    return [
        {
            "id": n["id"],
            "title": n["title"],
            "category": n["category"],
            "icon": n["icon"],
            "authority": n["authority"],
            "blurb": n["blurb"],
            "mode": n.get("mode", "response"),
        }
        for n in DEMO_NOTICES
    ]

