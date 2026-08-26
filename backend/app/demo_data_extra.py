"""Two additional synthetic demo notices: a recruitment notification and a
scholarship notification.

These exist to demonstrate the *application* and *benefit* workflows, which
behave differently from a response notice: they have an application window,
eligibility criteria, a fee, a selection process and an official channel to
apply through.

The narrative fields below are curated so the demo reads well with no API key.
Everything else — dates, eligibility, fees, documents, the procedure — is left
for ``services/extractors.py`` to pull out of ``raw_text`` at runtime. That is
deliberate: it means the demo exercises the same extraction code that runs on a
notice the app has never seen.

EVERYTHING HERE IS FICTIONAL. The "Demo State Public Service Commission" and
"Demo Directorate of Higher Education" do not exist. Reference numbers, portal
names, amounts and contact details are invented for demonstration only.
"""

from __future__ import annotations

DISCLAIMER_LINE = (
    "*** SYNTHETIC DEMONSTRATION NOTICE — NOT AN OFFICIAL GOVERNMENT DOCUMENT ***"
)


RECRUITMENT_DEMO: dict = {
    "id": "recruit-jr-assistant",
    "title": "Recruitment — Junior Assistant (Demo PSC)",
    "category": "Recruitment",
    "icon": "clipboard",
    "mode": "application",
    "authority": "Demo State Public Service Commission [SYNTHETIC]",
    "blurb": (
        "An application window is open for 42 Junior Assistant posts. Has eligibility "
        "rules, a fee, and a document checklist."
    ),
    "raw_text": f"""{DISCLAIMER_LINE}

DEMO STATE PUBLIC SERVICE COMMISSION (SYNTHETIC)
Recruitment Cell, Demo Secretariat, Demo City

ADVERTISEMENT NO. DEMO-PSC/2026/JA-07

Notification Number: NM-DEMO-PSC-2026-000742
Date of Notification: 18 August 2026

Subject: Recruitment to the post of Junior Assistant (Group C) in the Demo
State Secretariat — online applications invited from eligible candidates.

Number of vacancies: 42 (Unreserved 21, OBC 9, SC 7, ST 3, EWS 2)
Pay level: Demo Pay Level 4 (illustrative)

IMPORTANT DATES

  Application opens                 : 01 September 2026
  Last date for submission          : 30 September 2026
  Last date for fee payment         : 02 October 2026
  Correction window                 : 05 October 2026 to 08 October 2026
  Written examination date          : 15 November 2026
  Admit card available              : 01 November 2026
  Document verification date        : To be announced

ELIGIBILITY CONDITIONS

  1. Age limit: Candidates must have attained 18 years and must not have
     exceeded 32 years of age as on 01 September 2026.
  2. Age relaxation of 5 years is available for SC/ST candidates and 3 years
     for OBC candidates, as per Demo State rules.
  3. Educational qualification: Candidates must have passed a Bachelor's
     degree from a recognised university.
  4. Candidates must possess a typing speed of 30 words per minute in English.
  5. Residency: Only candidates who are a resident of Demo State are eligible
     to apply against the reserved vacancies.
  6. Nationality: The candidate must be a citizen of India.

APPLICATION FEE

  Application fee for Unreserved and OBC candidates : Rs. 500
  Application fee for SC/ST/EWS candidates          : Rs. 250
  Female candidates and persons with benchmark disability are exempt from
  payment of the application fee.
  Fee once paid shall not be refunded under any circumstances.

DOCUMENTS REQUIRED AT THE TIME OF APPLICATION:
  1. Recent passport-size photograph (JPEG, maximum 100 KB)
  2. Scanned signature (JPEG, maximum 50 KB)
  3. Matriculation certificate as proof of date of birth (PDF)
  4. Bachelor's degree certificate or provisional certificate (PDF)
  5. Typing certificate issued by a recognised institute (PDF)
  6. Category certificate in the prescribed format, if applicable
  7. Domicile certificate of Demo State, if applying against reserved posts

HOW TO APPLY:
  1. Visit the Demo State PSC recruitment portal at demopsc.example.gov.
  2. Register using a valid email address and mobile number.
  3. Complete the online application form and select your category.
  4. Upload the scanned documents in the prescribed format and size.
  5. Pay the applicable application fee online.
  6. Review all entries carefully before final submission.
  7. Submit the application and download the confirmation page.
  8. Retain the application number for all future correspondence.

SELECTION PROCESS
  Selection shall be made on the basis of a written examination followed by a
  typing skill test and document verification. Merely applying does not confer
  any right to selection.

For queries, contact the Demo PSC helpdesk at helpdesk@demopsc.example.gov or
telephone 1800-000-0000 (illustrative number, not a real helpline).

Candidates are advised to read the full advertisement before applying.
Incomplete applications shall be summarily rejected.

{DISCLAIMER_LINE}
""",
    "analysis": {
        "notice_type": "Recruitment notification (synthetic demonstration)",
        "category": "recruitment",
        "category_confident": True,
        "mode": "application",
        "title": "Junior Assistant (Group C) recruitment — Advertisement DEMO-PSC/2026/JA-07",
        "authority": "Demo State Public Service Commission [SYNTHETIC]",
        "department": "Recruitment Cell, Demo State Secretariat",
        "organization": "Demo State Public Service Commission",
        "notice_date": "18 August 2026",
        "deadline": "30 September 2026",
        "reference_number": "NM-DEMO-PSC-2026-000742",
        "subject": "Recruitment to 42 Junior Assistant (Group C) posts — online applications invited.",
        "one_sentence": (
            "This is a job advertisement: 42 Junior Assistant posts are open, and you "
            "can apply online between 1 and 30 September 2026."
        ),
        "summary": (
            "The Demo State Public Service Commission is hiring 42 Junior Assistants. "
            "Applications are accepted online only, from 1 September to 30 September "
            "2026, with fee payment allowed until 2 October. You need to be between 18 "
            "and 32 years old on 1 September 2026, hold a Bachelor's degree, and have a "
            "typing speed of 30 words per minute. The fee is Rs. 500 (Rs. 250 for "
            "SC/ST/EWS), and female candidates and persons with benchmark disability pay "
            "nothing. Selection is by written examination on 15 November 2026, then a "
            "typing test and document verification."
        ),
        "why_received": (
            "This is a public advertisement rather than a notice addressed to you "
            "personally. It was published so that anyone who meets the conditions can "
            "apply."
        ),
        "required_action": (
            "Check that you meet the age, education and typing requirements, get your "
            "documents scanned in the exact formats and sizes listed, then complete the "
            "online application and pay the fee before the deadline."
        ),
        "what_happens_next": (
            "After the window closes you can correct mistakes between 5 and 8 October. "
            "Admit cards are released on 1 November and the written examination is on 15 "
            "November 2026. Document verification has not been scheduled yet."
        ),
        "consequences": (
            "The notice says incomplete applications will be rejected outright, and that "
            "the fee is not refundable. It does not describe any penalty for simply not "
            "applying — if you miss the deadline you would need to wait for a future "
            "advertisement."
        ),
        "selection_process": [
            "Written examination on 15 November 2026",
            "Typing skill test",
            "Document verification (date to be announced)",
        ],
        "vacancies": {
            "total": "42",
            "unreserved": "21",
            "obc": "9",
            "sc": "7",
            "st": "3",
            "ews": "2",
        },
        "glossary": [
            {
                "term": "Group C",
                "meaning": "A category of government post. Junior Assistant roles are clerical/administrative.",
            },
            {
                "term": "Correction window",
                "meaning": "A short period after the deadline when you can fix mistakes in a submitted application.",
            },
            {
                "term": "Benchmark disability",
                "meaning": "A disability of 40% or more as certified under Indian disability law. Here it means no application fee.",
            },
            {
                "term": "Domicile certificate",
                "meaning": "An official document proving you are a permanent resident of a particular state.",
            },
        ],
        "warnings": [
            "Incomplete applications will be rejected outright, according to the notice.",
            "The application fee is not refundable once paid.",
            "Photograph and signature have strict size limits (100 KB and 50 KB). Prepare these before you start.",
        ],
        "important_notes": [
            "Applying does not guarantee selection — the notice states this explicitly.",
            "The reserved-vacancy route additionally requires a Demo State domicile certificate.",
        ],
        "source_spans": {
            "deadline": "Important dates block, line 2",
            "reference_number": "Header, notification number line",
            "notice_date": "Header, date of notification",
            "fees": "Application fee section",
            "eligibility": "Eligibility conditions, items 1-6",
        },
        "uncertainties": [
            "The document verification date is listed as 'to be announced', so it is not yet known.",
            "The exact typing test format is not described in this notice.",
        ],
        "unknown_information": [
            "Document verification date",
            "Examination centre / city",
            "Syllabus details for the written examination",
        ],
        "next_steps": [
            "Confirm your age against the 1 September 2026 cut-off",
            "Check your degree and typing certificate are available",
            "Scan the photograph and signature to the exact sizes given",
            "Complete the online application between 1 and 30 September",
            "Pay the fee by 2 October and save the confirmation page",
        ],
        "confidence": 0.93,
        "translations": {
            "hi": {
                "one_sentence": "यह एक नौकरी का विज्ञापन है: जूनियर असिस्टेंट के 42 पद खुले हैं, और आप 1 से 30 सितंबर 2026 के बीच ऑनलाइन आवेदन कर सकते हैं।",
                "summary": (
                    "डेमो स्टेट पब्लिक सर्विस कमीशन 42 जूनियर असिस्टेंट भर्ती कर रहा है। आवेदन "
                    "केवल ऑनलाइन, 1 सितंबर से 30 सितंबर 2026 तक स्वीकार किए जाएंगे; शुल्क 2 "
                    "अक्टूबर तक जमा किया जा सकता है। 1 सितंबर 2026 को आपकी आयु 18 से 32 वर्ष के "
                    "बीच होनी चाहिए, स्नातक डिग्री होनी चाहिए, और टाइपिंग गति 30 शब्द प्रति मिनट "
                    "होनी चाहिए। शुल्क Rs. 500 है (SC/ST/EWS के लिए Rs. 250); महिला उम्मीदवारों "
                    "और बेंचमार्क दिव्यांगजनों के लिए कोई शुल्क नहीं। चयन 15 नवंबर 2026 की लिखित "
                    "परीक्षा, फिर टाइपिंग टेस्ट और दस्तावेज़ सत्यापन से होगा।"
                ),
                "why_received": "यह किसी व्यक्ति को भेजा गया नोटिस नहीं, बल्कि एक सार्वजनिक विज्ञापन है, ताकि शर्तें पूरी करने वाला कोई भी आवेदन कर सके।",
                "required_action": "जाँचें कि आप आयु, शिक्षा और टाइपिंग की शर्तें पूरी करते हैं, दस्तावेज़ों को बताए गए प्रारूप और आकार में स्कैन करें, फिर समय सीमा से पहले ऑनलाइन आवेदन पूरा करें और शुल्क जमा करें।",
                "what_happens_next": "आवेदन बंद होने के बाद 5 से 8 अक्टूबर के बीच आप गलतियाँ सुधार सकते हैं। एडमिट कार्ड 1 नवंबर को और लिखित परीक्षा 15 नवंबर 2026 को है। दस्तावेज़ सत्यापन की तारीख अभी तय नहीं है।",
                "consequences": "नोटिस के अनुसार अपूर्ण आवेदन सीधे अस्वीकार कर दिए जाएंगे और शुल्क वापस नहीं होगा। आवेदन न करने पर किसी दंड का उल्लेख नहीं है — समय सीमा चूकने पर आपको अगले विज्ञापन की प्रतीक्षा करनी होगी।",
            },
            "te": {
                "one_sentence": "ఇది ఒక ఉద్యోగ ప్రకటన: జూనియర్ అసిస్టెంట్ 42 పోస్టులు ఖాళీగా ఉన్నాయి, మీరు 2026 సెప్టెంబర్ 1 నుండి 30 వరకు ఆన్‌లైన్‌లో దరఖాస్తు చేసుకోవచ్చు.",
                "summary": (
                    "డెమో స్టేట్ పబ్లిక్ సర్వీస్ కమిషన్ 42 జూనియర్ అసిస్టెంట్లను నియమిస్తోంది. "
                    "దరఖాస్తులు ఆన్‌లైన్‌లో మాత్రమే, 2026 సెప్టెంబర్ 1 నుండి 30 వరకు స్వీకరిస్తారు; "
                    "ఫీజు అక్టోబర్ 2 వరకు చెల్లించవచ్చు. 2026 సెప్టెంబర్ 1 నాటికి మీ వయస్సు 18 నుండి "
                    "32 సంవత్సరాల మధ్య ఉండాలి, డిగ్రీ ఉండాలి, టైపింగ్ వేగం నిమిషానికి 30 పదాలు "
                    "ఉండాలి. ఫీజు Rs. 500 (SC/ST/EWS కు Rs. 250); మహిళా అభ్యర్థులు మరియు బెంచ్‌మార్క్ "
                    "వికలాంగులకు ఫీజు లేదు. ఎంపిక 2026 నవంబర్ 15 వ్రాత పరీక్ష, తర్వాత టైపింగ్ టెస్ట్ "
                    "మరియు పత్రాల ధృవీకరణ ద్వారా జరుగుతుంది."
                ),
                "why_received": "ఇది మీకు వ్యక్తిగతంగా పంపిన నోటీసు కాదు, ఒక బహిరంగ ప్రకటన. షరతులు తీర్చే ఎవరైనా దరఖాస్తు చేసుకోవచ్చు.",
                "required_action": "వయస్సు, విద్య, టైపింగ్ షరతులు మీరు తీర్చుతున్నారో చూసుకోండి, పత్రాలను చెప్పిన ఫార్మాట్ మరియు సైజులో స్కాన్ చేయండి, గడువుకు ముందు ఆన్‌లైన్ దరఖాస్తు పూర్తి చేసి ఫీజు చెల్లించండి.",
                "what_happens_next": "దరఖాస్తు గడువు ముగిసిన తర్వాత అక్టోబర్ 5 నుండి 8 వరకు తప్పులు సరిదిద్దుకోవచ్చు. అడ్మిట్ కార్డ్ నవంబర్ 1న, వ్రాత పరీక్ష 2026 నవంబర్ 15న. పత్రాల ధృవీకరణ తేదీ ఇంకా ప్రకటించలేదు.",
                "consequences": "నోటీసు ప్రకారం అసంపూర్ణ దరఖాస్తులు తిరస్కరించబడతాయి, ఫీజు తిరిగి ఇవ్వరు. దరఖాస్తు చేయకపోతే జరిమానా గురించి ప్రస్తావన లేదు — గడువు తప్పితే తదుపరి ప్రకటన కోసం వేచి ఉండాలి.",
            },
        },
    },
    "response_template": None,
}


SCHOLARSHIP_DEMO: dict = {
    "id": "scholarship-merit",
    "title": "Scholarship — Merit-cum-Means (Demo Higher Education)",
    "category": "Scholarship",
    "icon": "certificate",
    "mode": "benefit",
    "authority": "Demo Directorate of Higher Education [SYNTHETIC]",
    "blurb": (
        "A tuition scholarship with an income ceiling and a renewal condition. Shows "
        "the benefit workflow end to end."
    ),
    "raw_text": f"""{DISCLAIMER_LINE}

DEMO DIRECTORATE OF HIGHER EDUCATION (SYNTHETIC)
Scholarship Section, Demo Bhavan, Demo City

PUBLIC NOTICE — MERIT-CUM-MEANS SCHOLARSHIP 2026-27

Notification Number: NM-DEMO-DHE-2026-001185
Date of Publication: 21 August 2026

Subject: Invitation of online applications for the Demo Merit-cum-Means
Scholarship for undergraduate students for the academic year 2026-27.

The Demo Directorate of Higher Education invites applications from eligible
undergraduate students studying in recognised institutions within Demo State
for award of the Merit-cum-Means Scholarship for the academic year 2026-27.

SCHEME BENEFIT
  Tuition assistance of Rs. 25,000 per academic year, paid directly to the
  student's bank account in two instalments.
  A one-time book grant of Rs. 3,000 is additionally payable to selected
  first-year students.
  Total number of scholarships available: 1,500

IMPORTANT DATES
  Application opens                 : 05 September 2026
  Last date for submission          : 10 October 2026
  Institutional verification by     : 25 October 2026
  Provisional list published on     : 12 November 2026
  Disbursement of first instalment  : To be announced

ELIGIBILITY CONDITIONS
  1. The applicant must be a resident of Demo State.
  2. Educational qualification: the applicant must have passed the 10+2
     examination with not less than 60 percent aggregate marks.
  3. The applicant must be enrolled in the first, second or third year of a
     recognised full-time undergraduate programme.
  4. Annual family income should not exceed Rs. 2,50,000 from all sources.
  5. Age limit: the applicant must not have exceeded 25 years of age as on
     01 September 2026.
  6. Applicants already receiving any other government scholarship for the
     same academic year are not eligible.

APPLICATION FEE
  No fee is charged for this scholarship. Applicants are cautioned against
  paying any amount to any agent or intermediary.

DOCUMENTS REQUIRED:
  1. 10+2 marksheet showing aggregate percentage (PDF, maximum 500 KB)
  2. Current year bonafide certificate issued by the institution (PDF)
  3. Income certificate issued by the competent revenue authority (PDF)
  4. Domicile certificate of Demo State (PDF)
  5. Bank passbook first page showing account number and IFSC (PDF)
  6. Recent passport-size photograph (JPEG, maximum 200 KB)
  7. Caste certificate, if applicable

HOW TO APPLY:
  1. Register on the Demo scholarship portal at demoscholarship.example.gov.
  2. Complete the application form with your academic and income details.
  3. Upload the required documents in the prescribed formats.
  4. Submit the application before the last date.
  5. Request your institution to complete the institutional verification.
  6. Download and retain the application acknowledgement.

APPROVAL AND DISBURSEMENT
  Applications will be verified by the institution and then by the Directorate.
  A provisional list will be published on the portal. Scholarship amounts will
  be credited directly to the verified bank account of the selected student.
  Renewal in the following year is subject to the student securing not less
  than 50 percent marks in the current academic year.

For queries write to scholarship@demodhe.example.gov or contact the Demo
Scholarship Helpline at 1800-000-0001 (illustrative number, not a real
helpline).

{DISCLAIMER_LINE}
""",
    "analysis": {
        "notice_type": "Scholarship notification (synthetic demonstration)",
        "category": "scholarship",
        "category_confident": True,
        "mode": "benefit",
        "title": "Demo Merit-cum-Means Scholarship 2026-27",
        "authority": "Demo Directorate of Higher Education [SYNTHETIC]",
        "department": "Scholarship Section, Demo Directorate of Higher Education",
        "organization": "Demo Directorate of Higher Education",
        "scheme_name": "Demo Merit-cum-Means Scholarship 2026-27",
        "notice_date": "21 August 2026",
        "deadline": "10 October 2026",
        "reference_number": "NM-DEMO-DHE-2026-001185",
        "subject": "Online applications invited for the Merit-cum-Means Scholarship for 2026-27.",
        "one_sentence": (
            "This is a scholarship you can apply for: Rs. 25,000 a year towards tuition, "
            "with applications open from 5 September to 10 October 2026."
        ),
        "summary": (
            "The Demo Directorate of Higher Education is offering 1,500 Merit-cum-Means "
            "Scholarships to undergraduate students in Demo State. The award is Rs. 25,000 "
            "per year paid into your bank account in two instalments, plus a one-time Rs. "
            "3,000 book grant for first-year students. To qualify you must live in Demo "
            "State, have scored at least 60% in 10+2, be enrolled in a recognised "
            "full-time undergraduate course, have annual family income of Rs. 2,50,000 or "
            "less, and be 25 or younger on 1 September 2026. There is no application fee. "
            "Your college must complete an institutional verification by 25 October."
        ),
        "why_received": (
            "This is a public scholarship announcement, not a notice addressed to you "
            "personally. It is published so that every eligible student can apply."
        ),
        "required_action": (
            "Check the income, marks, age and residency conditions, collect the income and "
            "domicile certificates (these often take time to obtain), apply on the portal "
            "before 10 October, and then ask your college to complete its verification."
        ),
        "what_happens_next": (
            "Your college verifies your application by 25 October, the Directorate then "
            "checks it, and a provisional list is published on 12 November 2026. The date "
            "the money is actually paid has not been announced yet."
        ),
        "consequences": (
            "The notice does not describe a penalty — this is an opportunity rather than an "
            "obligation. If you miss the 10 October date, or your college does not verify "
            "in time, you simply would not be considered this year."
        ),
        "glossary": [
            {
                "term": "Merit-cum-means",
                "meaning": "Awarded on both academic performance and financial need — you must satisfy the marks condition and the income ceiling.",
            },
            {
                "term": "Bonafide certificate",
                "meaning": "A letter from your college confirming you are genuinely enrolled there this year.",
            },
            {
                "term": "Institutional verification",
                "meaning": "A step where your college confirms your details to the department. You cannot do it yourself.",
            },
            {
                "term": "Disbursement",
                "meaning": "The actual payment of the money into your bank account.",
            },
        ],
        "warnings": [
            "The notice warns against paying any agent or intermediary — this scholarship has no fee at all.",
            "You cannot hold another government scholarship for the same year.",
            "Renewal next year requires at least 50% marks this year.",
        ],
        "important_notes": [
            "Institutional verification is done by your college, not by you. Ask them early — the window closes 25 October.",
            "Income and domicile certificates are issued by the revenue authority and can take time. Start with those.",
        ],
        "source_spans": {
            "deadline": "Important dates block, line 2",
            "reference_number": "Header, notification number line",
            "fees": "Application fee section",
            "eligibility": "Eligibility conditions, items 1-6",
            "benefit": "Scheme benefit section",
        },
        "uncertainties": [
            "The disbursement date is listed as 'to be announced', so when the money arrives is not yet known.",
            "The notice does not say how the 1,500 scholarships are distributed between categories or districts.",
        ],
        "unknown_information": [
            "Disbursement date for the first instalment",
            "How applications are ranked when more than 1,500 students qualify",
            "Whether the book grant is paid with the first instalment",
        ],
        "next_steps": [
            "Check your 10+2 percentage against the 60% condition",
            "Confirm your family income is within Rs. 2,50,000",
            "Apply for the income and domicile certificates now if you do not have them",
            "Submit the online application before 10 October",
            "Ask your college to complete institutional verification before 25 October",
        ],
        "confidence": 0.92,
        "translations": {
            "hi": {
                "one_sentence": "यह एक छात्रवृत्ति है जिसके लिए आप आवेदन कर सकते हैं: ट्यूशन हेतु प्रति वर्ष Rs. 25,000, आवेदन 5 सितंबर से 10 अक्टूबर 2026 तक खुले हैं।",
                "summary": (
                    "डेमो निदेशालय उच्च शिक्षा, डेमो राज्य के स्नातक विद्यार्थियों को 1,500 "
                    "मेरिट-कम-मीन्स छात्रवृत्तियाँ दे रहा है। राशि Rs. 25,000 प्रति वर्ष, दो किस्तों "
                    "में सीधे आपके बैंक खाते में; प्रथम वर्ष के विद्यार्थियों को Rs. 3,000 की "
                    "एकमुश्त पुस्तक सहायता भी। पात्रता: डेमो राज्य का निवासी होना, 10+2 में कम से "
                    "कम 60% अंक, मान्यता प्राप्त पूर्णकालिक स्नातक पाठ्यक्रम में नामांकन, वार्षिक "
                    "पारिवारिक आय Rs. 2,50,000 या कम, और 1 सितंबर 2026 को आयु 25 वर्ष या कम। कोई "
                    "आवेदन शुल्क नहीं है। आपके कॉलेज को 25 अक्टूबर तक संस्थागत सत्यापन पूरा करना होगा।"
                ),
                "why_received": "यह किसी व्यक्ति को भेजा गया नोटिस नहीं, बल्कि एक सार्वजनिक छात्रवृत्ति घोषणा है, ताकि हर पात्र विद्यार्थी आवेदन कर सके।",
                "required_action": "आय, अंक, आयु और निवास की शर्तें जाँचें, आय और निवास प्रमाणपत्र इकट्ठा करें (इनमें समय लगता है), 10 अक्टूबर से पहले पोर्टल पर आवेदन करें, और फिर कॉलेज से सत्यापन पूरा कराएँ।",
                "what_happens_next": "आपका कॉलेज 25 अक्टूबर तक आवेदन सत्यापित करेगा, निदेशालय जाँच करेगा, और 12 नवंबर 2026 को अनंतिम सूची प्रकाशित होगी। भुगतान की तारीख अभी घोषित नहीं हुई है।",
                "consequences": "नोटिस में किसी दंड का उल्लेख नहीं है — यह एक अवसर है, बाध्यता नहीं। यदि आप 10 अक्टूबर की तारीख चूक जाते हैं, या कॉलेज समय पर सत्यापन नहीं करता, तो इस वर्ष आप पर विचार नहीं होगा।",
            },
            "te": {
                "one_sentence": "ఇది మీరు దరఖాస్తు చేసుకోగల స్కాలర్‌షిప్: ట్యూషన్ కోసం సంవత్సరానికి Rs. 25,000, దరఖాస్తులు 2026 సెప్టెంబర్ 5 నుండి అక్టోబర్ 10 వరకు తెరిచి ఉన్నాయి.",
                "summary": (
                    "డెమో డైరెక్టరేట్ ఆఫ్ హయ్యర్ ఎడ్యుకేషన్ డెమో స్టేట్‌లోని అండర్‌గ్రాడ్యుయేట్ "
                    "విద్యార్థులకు 1,500 మెరిట్-కమ్-మీన్స్ స్కాలర్‌షిప్‌లు అందిస్తోంది. మొత్తం "
                    "సంవత్సరానికి Rs. 25,000, రెండు వాయిదాలలో నేరుగా మీ బ్యాంక్ ఖాతాకు; మొదటి "
                    "సంవత్సరం విద్యార్థులకు అదనంగా Rs. 3,000 పుస్తక గ్రాంట్. అర్హత: డెమో స్టేట్ "
                    "నివాసి, 10+2లో కనీసం 60% మార్కులు, గుర్తింపు పొందిన పూర్తికాల డిగ్రీ కోర్సులో "
                    "చేరిక, వార్షిక కుటుంబ ఆదాయం Rs. 2,50,000 లోపు, 2026 సెప్టెంబర్ 1 నాటికి వయస్సు "
                    "25 లోపు. దరఖాస్తు ఫీజు లేదు. మీ కళాశాల అక్టోబర్ 25 లోపు ధృవీకరణ పూర్తి చేయాలి."
                ),
                "why_received": "ఇది మీకు వ్యక్తిగతంగా పంపిన నోటీసు కాదు, బహిరంగ స్కాలర్‌షిప్ ప్రకటన. అర్హులైన ప్రతి విద్యార్థి దరఖాస్తు చేసుకోవచ్చు.",
                "required_action": "ఆదాయం, మార్కులు, వయస్సు, నివాస షరతులు తనిఖీ చేయండి, ఆదాయ మరియు నివాస ధృవీకరణ పత్రాలు సేకరించండి (వీటికి సమయం పడుతుంది), అక్టోబర్ 10 లోపు పోర్టల్‌లో దరఖాస్తు చేయండి, తర్వాత కళాశాల ధృవీకరణ పూర్తి చేయమని కోరండి.",
                "what_happens_next": "మీ కళాశాల అక్టోబర్ 25 లోపు ధృవీకరిస్తుంది, డైరెక్టరేట్ తనిఖీ చేస్తుంది, 2026 నవంబర్ 12న తాత్కాలిక జాబితా ప్రచురిస్తారు. డబ్బు చెల్లించే తేదీ ఇంకా ప్రకటించలేదు.",
                "consequences": "నోటీసులో జరిమానా గురించి ప్రస్తావన లేదు — ఇది ఒక అవకాశం, బాధ్యత కాదు. అక్టోబర్ 10 తేదీ తప్పితే, లేదా కళాశాల సమయానికి ధృవీకరించకపోతే, ఈ సంవత్సరం మీరు పరిగణించబడరు.",
            },
        },
    },
    "response_template": None,
}


EXTRA_DEMOS: list[dict] = [RECRUITMENT_DEMO, SCHOLARSHIP_DEMO]
