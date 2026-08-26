/**
 * UI translations for English, Hindi and Telugu.
 *
 * Long-form *content* (the plain-language explanation of a notice) is
 * translated on the backend and travels with the analysis payload — this file
 * only covers the interface chrome so the two never disagree.
 */

export const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
];

const en = {
  'demo.banner': 'DEMO PROTOTYPE — NOT AN OFFICIAL GOVERNMENT SERVICE',
  'footer.disclaimer':
    'NoticeMate is a hackathon prototype and is not an official government service. All notices and data shown are synthetic.',
  'footer.privacy':
    'Your information stays on this demo. No data is sent to any government system.',

  'common.back': 'Back',
  'common.continue': 'Continue',
  'common.next': 'Next',
  'common.cancel': 'Cancel',
  'common.retry': 'Try again',
  'common.loading': 'Loading…',
  'common.startOver': 'Start over',
  'common.notFound': "We couldn't determine this from the notice.",
  'common.step': 'Step',
  'common.of': 'of',
  'common.optional': 'Optional',
  'common.copied': 'Copied to clipboard.',
  'common.copy': 'Copy text',
  'common.download': 'Download a copy',
  'common.language': 'Language',
  'common.confidence': 'Confidence',
  'common.viewNotice': 'View the original notice text',
  'common.hideNotice': 'Hide the original notice text',

  'error.title': 'Something needs your attention',
  'error.generic': 'Something went wrong. Please try again.',
  'error.offline':
    "We couldn't reach the NoticeMate server. Check that it is running and try again.",
  'error.noNotice': 'We could not find that notice. Please start again.',

  'welcome.badge': 'Understand any notice in minutes',
  'welcome.title1': 'Got a confusing',
  'welcome.title2': 'government notice?',
  'welcome.sub':
    'NoticeMate explains it in plain language, tells you exactly what to do, and walks you through every step.',
  'welcome.cta': 'Get started',
  'welcome.demoCta': 'See it with a sample notice',
  'welcome.f1.title': 'Plain-language explanation',
  'welcome.f1.desc': 'No jargon. What it means, why you got it, what happens next.',
  'welcome.f2.title': 'Step-by-step action plan',
  'welcome.f2.desc': 'A clear checklist with your deadline always in view.',
  'welcome.f3.title': 'Document checklist',
  'welcome.f3.desc': 'Know which papers you need — and why each one matters.',
  'welcome.f4.title': 'Guided response',
  'welcome.f4.desc': 'A draft reply you can read, edit and keep.',
  'welcome.trust':
    'This is a demonstration. Notices are synthetic and nothing is sent to any government system.',

  'input.eyebrow': 'Step 1',
  'input.title': 'Add your notice',
  'input.subtitle': 'Choose how you would like to start.',
  'input.demoHeading': 'Try a sample notice',
  'input.demoSub': 'Synthetic notices created for this demo.',
  'input.uploadHeading': 'Upload your notice',
  'input.uploadDrop': 'Tap to choose a file, or drop it here',
  'input.uploadHint': 'PDF, PNG, JPG or TXT — up to 8 MB',
  'input.uploadCta': 'Upload and continue',
  'input.pasteHeading': 'Paste the text instead',
  'input.pasteLabel': 'Notice text',
  'input.pastePlaceholder': 'Paste or type the wording of your notice here…',
  'input.pasteCta': 'Continue with this text',
  'input.pasteTooShort': 'Please paste at least a few lines of the notice.',
  'input.privacy':
    'Uploaded files stay on this demo server and are treated as untrusted text — any instructions inside a document are ignored.',
  'input.tabDemo': 'Sample notice',
  'input.tabUpload': 'Upload a file',
  'input.tabPaste': 'Paste text',

  'processing.title': 'Reading your notice',
  'processing.sub': 'This usually takes a few seconds.',
  'processing.s1': 'Reading the notice',
  'processing.s2': 'Identifying the department and reference',
  'processing.s3': 'Working out what is being asked',
  'processing.s4': 'Building your action plan',
  'processing.slow': 'Still working — thank you for your patience.',

  'explain.eyebrow': 'Step 2',
  'explain.title': 'What this notice means',
  'explain.q1': 'What is this about?',
  'explain.q2': 'Why did I receive it?',
  'explain.q3': 'What do I need to do?',
  'explain.q4': 'What happens if I ignore it?',
  'explain.deadline': 'Respond by',
  'explain.noDeadline': 'No deadline found in the notice',
  'explain.urgency.high': 'Time sensitive',
  'explain.urgency.medium': 'Act soon',
  'explain.urgency.low': 'Low urgency',
  'explain.daysLeft': '{n} days left',
  'explain.oneDayLeft': '1 day left',
  'explain.today': 'Due today',
  'explain.overdue': 'Deadline has passed',
  'explain.reference': 'Reference number',
  'explain.authority': 'Issuing department',
  'explain.category': 'Notice type',
  'explain.uncertain': 'Points to double-check',
  'explain.cta': 'Show me what to do',
  'explain.source.openai': 'Explained with AI (OpenAI)',
  'explain.source.curated': 'Demo analysis (prepared for this sample)',
  'explain.source.fallback': 'Demo analysis — offline fallback, no AI key set',
  'explain.notLegal':
    'NoticeMate is not a lawyer and this is not legal advice. Always check the original notice.',
  'explain.translatedNote':
    'Explanation shown in your chosen language. The original notice wording is unchanged.',
  'explain.notTranslated':
    'A translation of this explanation is not available, so it is shown in English.',

  'plan.eyebrow': 'Step 3',
  'plan.title': 'Your action plan',
  'plan.subtitle': 'Work through these in order. Your progress is saved.',
  'plan.progress': 'steps done',
  'plan.markDone': 'Mark done',
  'plan.markUndone': 'Not done yet',
  'plan.cta': 'Go to documents',
  'plan.state.not_started': 'To do',
  'plan.state.in_progress': 'In progress',
  'plan.state.completed': 'Done',
  'plan.state.needs_attention': 'Needs attention',

  'docs.eyebrow': 'Step 4',
  'docs.title': 'Documents you need',
  'docs.subtitle': 'Add what you have. You can continue without uploading.',
  'docs.required': 'Required',
  'docs.helpful': 'Helpful',
  'docs.status.needed': 'Not added',
  'docs.status.uploaded': 'Added',
  'docs.status.unavailable': "Don't have it",
  'docs.upload': 'Add file',
  'docs.markUnavailable': "I don't have this",
  'docs.markNeeded': 'Reset',
  'docs.checkTitle': 'What we checked',
  'docs.cta': 'Prepare my response',
  'docs.emptyTitle': 'No documents requested',
  'docs.emptyBody':
    'This notice does not appear to ask for supporting documents. You can go straight to your response.',
  'docs.noteVerify':
    'These are basic checks only — NoticeMate cannot verify a document with any government department.',

  'response.eyebrow': 'Step 5',
  'response.title': 'Your draft response',
  'response.subtitle':
    'Read it carefully and edit anything that is not accurate for you.',
  'response.generate': 'Generate a draft',
  'response.regenerate': 'Generate again',
  'response.label': 'Draft response',
  'response.extraLabel': 'Anything to add? (optional)',
  'response.extraPlaceholder':
    'For example: I have already updated my bank details…',
  'response.cta': 'Review and continue',
  'response.saved': 'Draft saved.',
  'response.source.openai': 'Drafted with AI (OpenAI)',
  'response.source.fallback': 'Demo draft — offline fallback, no AI key set',
  'response.source.user': 'Edited by you',
  'response.checkWarning':
    'Check every name, number and date before you use this anywhere.',

  'review.eyebrow': 'Step 6',
  'review.title': 'Review before submitting',
  'review.subtitle': 'This is a simulated submission — nothing leaves this demo.',
  'review.notice': 'Notice',
  'review.deadline': 'Deadline',
  'review.documents': 'Documents',
  'review.response': 'Your response',
  'review.confirmLabel':
    'I understand this is a demonstration and no notice will be sent to any government department.',
  'review.cta': 'Submit (simulated)',
  'review.needConfirm': 'Please tick the confirmation box to continue.',
  'review.edit': 'Edit response',
  'review.docsCount': '{done} of {total} added',

  'confirm.title': 'Submission recorded',
  'confirm.sub': 'Your simulated submission has been saved in this demo.',
  'confirm.reference': 'Demo reference',
  'confirm.status': 'Status',
  'confirm.whatNext': 'What happens next',
  'confirm.simulated':
    'SIMULATED SUBMISSION — this reference exists only inside NoticeMate. No government department has received anything.',
  'confirm.cta': 'Track this notice',
  'confirm.newNotice': 'Start another notice',

  'status.eyebrow': 'Tracker',
  'status.title': 'Where things stand',
  'status.subtitle': 'A timeline of everything you have done in this demo.',
  'status.legendDone': 'Completed in this demo',
  'status.legendPending': 'Not done yet',
  'status.legendGov': 'Would need a real government integration',
  'status.history': 'Activity log',
  'status.cta': 'Start another notice',
  'status.refresh': 'Refresh',
  'status.govNote':
    'A real deployment would confirm receipt through an official channel. This prototype cannot, and does not, contact any department.',

  'resume.title': 'Continue where you left off?',
  'resume.body': 'You have a notice in progress in this browser.',
  'resume.cta': 'Continue',
  'resume.discard': 'Start fresh',
};

const hi = {
  'demo.banner': 'डेमो प्रोटोटाइप — यह कोई सरकारी सेवा नहीं है',
  'footer.disclaimer':
    'NoticeMate एक हैकाथॉन प्रोटोटाइप है और कोई सरकारी सेवा नहीं है। यहाँ दिखाए गए सभी नोटिस और जानकारी काल्पनिक हैं।',
  'footer.privacy':
    'आपकी जानकारी इसी डेमो में रहती है। कोई भी डेटा किसी सरकारी सिस्टम को नहीं भेजा जाता।',

  'common.back': 'पीछे',
  'common.continue': 'आगे बढ़ें',
  'common.next': 'अगला',
  'common.cancel': 'रद्द करें',
  'common.retry': 'फिर कोशिश करें',
  'common.loading': 'लोड हो रहा है…',
  'common.startOver': 'नए सिरे से शुरू करें',
  'common.notFound': 'यह जानकारी हमें नोटिस में नहीं मिली।',
  'common.step': 'चरण',
  'common.of': 'में से',
  'common.optional': 'वैकल्पिक',
  'common.copied': 'कॉपी हो गया।',
  'common.copy': 'टेक्स्ट कॉपी करें',
  'common.download': 'एक प्रति डाउनलोड करें',
  'common.language': 'भाषा',
  'common.confidence': 'विश्वास स्तर',
  'common.viewNotice': 'मूल नोटिस का टेक्स्ट देखें',
  'common.hideNotice': 'मूल नोटिस का टेक्स्ट छिपाएँ',

  'error.title': 'कुछ ध्यान देने की ज़रूरत है',
  'error.generic': 'कुछ गड़बड़ हो गई। कृपया फिर कोशिश करें।',
  'error.offline':
    'हम NoticeMate सर्वर तक नहीं पहुँच सके। जाँचें कि वह चल रहा है और फिर कोशिश करें।',
  'error.noNotice': 'वह नोटिस नहीं मिला। कृपया दोबारा शुरू करें।',

  'welcome.badge': 'कुछ ही मिनटों में नोटिस समझें',
  'welcome.title1': 'कोई उलझन भरा',
  'welcome.title2': 'सरकारी नोटिस मिला है?',
  'welcome.sub':
    'NoticeMate उसे आसान भाषा में समझाता है, बताता है कि आपको क्या करना है, और हर कदम पर साथ चलता है।',
  'welcome.cta': 'शुरू करें',
  'welcome.demoCta': 'नमूना नोटिस के साथ देखें',
  'welcome.f1.title': 'आसान भाषा में समझ',
  'welcome.f1.desc': 'कोई कठिन शब्द नहीं। इसका मतलब, कारण और आगे क्या होगा।',
  'welcome.f2.title': 'कदम-दर-कदम योजना',
  'welcome.f2.desc': 'स्पष्ट सूची, और आपकी अंतिम तारीख हमेशा सामने।',
  'welcome.f3.title': 'दस्तावेज़ों की सूची',
  'welcome.f3.desc': 'कौन-कौन से कागज़ चाहिए — और हर एक क्यों ज़रूरी है।',
  'welcome.f4.title': 'तैयार जवाब',
  'welcome.f4.desc': 'एक मसौदा जिसे आप पढ़ सकते, बदल सकते और रख सकते हैं।',
  'welcome.trust':
    'यह एक प्रदर्शन है। नोटिस काल्पनिक हैं और कुछ भी किसी सरकारी सिस्टम को नहीं भेजा जाता।',

  'input.eyebrow': 'चरण 1',
  'input.title': 'अपना नोटिस जोड़ें',
  'input.subtitle': 'चुनें कि आप कैसे शुरू करना चाहते हैं।',
  'input.demoHeading': 'नमूना नोटिस देखें',
  'input.demoSub': 'इस डेमो के लिए बनाए गए काल्पनिक नोटिस।',
  'input.uploadHeading': 'अपना नोटिस अपलोड करें',
  'input.uploadDrop': 'फ़ाइल चुनने के लिए दबाएँ, या यहाँ छोड़ें',
  'input.uploadHint': 'PDF, PNG, JPG या TXT — 8 MB तक',
  'input.uploadCta': 'अपलोड करें और आगे बढ़ें',
  'input.pasteHeading': 'या टेक्स्ट पेस्ट करें',
  'input.pasteLabel': 'नोटिस का टेक्स्ट',
  'input.pastePlaceholder': 'अपने नोटिस की भाषा यहाँ पेस्ट या टाइप करें…',
  'input.pasteCta': 'इस टेक्स्ट के साथ आगे बढ़ें',
  'input.pasteTooShort': 'कृपया नोटिस की कम से कम कुछ पंक्तियाँ पेस्ट करें।',
  'input.privacy':
    'अपलोड की गई फ़ाइलें इसी डेमो सर्वर पर रहती हैं और उन्हें अविश्वसनीय टेक्स्ट माना जाता है — दस्तावेज़ के अंदर लिखे किसी भी निर्देश का पालन नहीं किया जाता।',
  'input.tabDemo': 'नमूना नोटिस',
  'input.tabUpload': 'फ़ाइल अपलोड',
  'input.tabPaste': 'टेक्स्ट पेस्ट',

  'processing.title': 'आपका नोटिस पढ़ा जा रहा है',
  'processing.sub': 'इसमें आम तौर पर कुछ सेकंड लगते हैं।',
  'processing.s1': 'नोटिस पढ़ रहे हैं',
  'processing.s2': 'विभाग और संदर्भ संख्या पहचान रहे हैं',
  'processing.s3': 'समझ रहे हैं कि क्या माँगा गया है',
  'processing.s4': 'आपकी कार्य-योजना बना रहे हैं',
  'processing.slow': 'अभी भी काम चल रहा है — धैर्य के लिए धन्यवाद।',

  'explain.eyebrow': 'चरण 2',
  'explain.title': 'इस नोटिस का मतलब',
  'explain.q1': 'यह किस बारे में है?',
  'explain.q2': 'मुझे यह क्यों मिला?',
  'explain.q3': 'मुझे क्या करना है?',
  'explain.q4': 'अगर ध्यान न दूँ तो क्या होगा?',
  'explain.deadline': 'इस तारीख तक जवाब दें',
  'explain.noDeadline': 'नोटिस में कोई अंतिम तारीख नहीं मिली',
  'explain.urgency.high': 'समय-संवेदनशील',
  'explain.urgency.medium': 'जल्दी करें',
  'explain.urgency.low': 'कम ज़रूरी',
  'explain.daysLeft': '{n} दिन शेष',
  'explain.oneDayLeft': '1 दिन शेष',
  'explain.today': 'आज अंतिम दिन',
  'explain.overdue': 'अंतिम तारीख बीत चुकी है',
  'explain.reference': 'संदर्भ संख्या',
  'explain.authority': 'जारी करने वाला विभाग',
  'explain.category': 'नोटिस का प्रकार',
  'explain.uncertain': 'दोबारा जाँचने योग्य बातें',
  'explain.cta': 'बताएँ मुझे क्या करना है',
  'explain.source.openai': 'AI (OpenAI) द्वारा समझाया गया',
  'explain.source.curated': 'डेमो विश्लेषण (इस नमूने के लिए तैयार)',
  'explain.source.fallback': 'डेमो विश्लेषण — ऑफ़लाइन विकल्प, कोई AI कुंजी नहीं',
  'explain.notLegal':
    'NoticeMate वकील नहीं है और यह कानूनी सलाह नहीं है। मूल नोटिस ज़रूर जाँचें।',
  'explain.translatedNote':
    'व्याख्या आपकी चुनी भाषा में दिखाई गई है। मूल नोटिस की भाषा अपरिवर्तित है।',
  'explain.notTranslated':
    'इस व्याख्या का अनुवाद उपलब्ध नहीं है, इसलिए यह अंग्रेज़ी में दिखाई गई है।',

  'plan.eyebrow': 'चरण 3',
  'plan.title': 'आपकी कार्य-योजना',
  'plan.subtitle': 'इन्हें क्रम से पूरा करें। आपकी प्रगति सुरक्षित रहती है।',
  'plan.progress': 'चरण पूरे',
  'plan.markDone': 'पूरा हुआ',
  'plan.markUndone': 'अभी पूरा नहीं',
  'plan.cta': 'दस्तावेज़ों पर जाएँ',
  'plan.state.not_started': 'करना है',
  'plan.state.in_progress': 'चल रहा है',
  'plan.state.completed': 'पूरा',
  'plan.state.needs_attention': 'ध्यान चाहिए',

  'docs.eyebrow': 'चरण 4',
  'docs.title': 'ज़रूरी दस्तावेज़',
  'docs.subtitle': 'जो आपके पास है वह जोड़ें। बिना अपलोड भी आगे बढ़ सकते हैं।',
  'docs.required': 'अनिवार्य',
  'docs.helpful': 'सहायक',
  'docs.status.needed': 'नहीं जोड़ा',
  'docs.status.uploaded': 'जोड़ा गया',
  'docs.status.unavailable': 'मेरे पास नहीं है',
  'docs.upload': 'फ़ाइल जोड़ें',
  'docs.markUnavailable': 'यह मेरे पास नहीं है',
  'docs.markNeeded': 'रीसेट',
  'docs.checkTitle': 'हमने क्या जाँचा',
  'docs.cta': 'मेरा जवाब तैयार करें',
  'docs.emptyTitle': 'कोई दस्तावेज़ नहीं माँगा गया',
  'docs.emptyBody':
    'इस नोटिस में कोई सहायक दस्तावेज़ नहीं माँगा गया लगता है। आप सीधे जवाब पर जा सकते हैं।',
  'docs.noteVerify':
    'ये केवल बुनियादी जाँच हैं — NoticeMate किसी सरकारी विभाग से दस्तावेज़ की पुष्टि नहीं कर सकता।',

  'response.eyebrow': 'चरण 5',
  'response.title': 'आपका मसौदा जवाब',
  'response.subtitle': 'ध्यान से पढ़ें और जो सही न हो उसे बदल दें।',
  'response.generate': 'मसौदा बनाएँ',
  'response.regenerate': 'दोबारा बनाएँ',
  'response.label': 'मसौदा जवाब',
  'response.extraLabel': 'कुछ जोड़ना है? (वैकल्पिक)',
  'response.extraPlaceholder':
    'उदाहरण: मैंने अपने बैंक विवरण पहले ही अपडेट कर दिए हैं…',
  'response.cta': 'समीक्षा करें और आगे बढ़ें',
  'response.saved': 'मसौदा सुरक्षित हो गया।',
  'response.source.openai': 'AI (OpenAI) द्वारा तैयार',
  'response.source.fallback': 'डेमो मसौदा — ऑफ़लाइन विकल्प, कोई AI कुंजी नहीं',
  'response.source.user': 'आपके द्वारा संपादित',
  'response.checkWarning':
    'कहीं भी उपयोग करने से पहले हर नाम, संख्या और तारीख जाँच लें।',

  'review.eyebrow': 'चरण 6',
  'review.title': 'भेजने से पहले समीक्षा',
  'review.subtitle': 'यह एक नकली सबमिशन है — कुछ भी इस डेमो से बाहर नहीं जाता।',
  'review.notice': 'नोटिस',
  'review.deadline': 'अंतिम तारीख',
  'review.documents': 'दस्तावेज़',
  'review.response': 'आपका जवाब',
  'review.confirmLabel':
    'मैं समझता/समझती हूँ कि यह एक प्रदर्शन है और कोई नोटिस किसी सरकारी विभाग को नहीं भेजा जाएगा।',
  'review.cta': 'सबमिट करें (नकली)',
  'review.needConfirm': 'आगे बढ़ने के लिए कृपया पुष्टि बॉक्स पर टिक करें।',
  'review.edit': 'जवाब संपादित करें',
  'review.docsCount': '{total} में से {done} जोड़े गए',

  'confirm.title': 'सबमिशन दर्ज हुआ',
  'confirm.sub': 'आपका नकली सबमिशन इस डेमो में सुरक्षित कर लिया गया है।',
  'confirm.reference': 'डेमो संदर्भ',
  'confirm.status': 'स्थिति',
  'confirm.whatNext': 'आगे क्या होगा',
  'confirm.simulated':
    'नकली सबमिशन — यह संदर्भ संख्या केवल NoticeMate के अंदर है। किसी सरकारी विभाग को कुछ नहीं मिला है।',
  'confirm.cta': 'इस नोटिस को ट्रैक करें',
  'confirm.newNotice': 'दूसरा नोटिस शुरू करें',

  'status.eyebrow': 'ट्रैकर',
  'status.title': 'अब तक की स्थिति',
  'status.subtitle': 'इस डेमो में आपने जो किया उसका पूरा क्रम।',
  'status.legendDone': 'इस डेमो में पूरा हुआ',
  'status.legendPending': 'अभी बाकी',
  'status.legendGov': 'असली सरकारी एकीकरण की ज़रूरत होगी',
  'status.history': 'गतिविधि लॉग',
  'status.cta': 'दूसरा नोटिस शुरू करें',
  'status.refresh': 'ताज़ा करें',
  'status.govNote':
    'असली तैनाती में रसीद की पुष्टि किसी आधिकारिक माध्यम से होती। यह प्रोटोटाइप किसी विभाग से संपर्क नहीं करता।',

  'resume.title': 'जहाँ छोड़ा था वहीं से जारी रखें?',
  'resume.body': 'इस ब्राउज़र में आपका एक नोटिस अधूरा है।',
  'resume.cta': 'जारी रखें',
  'resume.discard': 'नए सिरे से',
};

const te = {
  'demo.banner': 'డెమో నమూనా — ఇది అధికారిక ప్రభుత్వ సేవ కాదు',
  'footer.disclaimer':
    'NoticeMate ఒక హ్యాకథాన్ నమూనా, అధికారిక ప్రభుత్వ సేవ కాదు. ఇందులో చూపిన నోటీసులు, వివరాలు అన్నీ కల్పితమే.',
  'footer.privacy':
    'మీ సమాచారం ఈ డెమోలోనే ఉంటుంది. ఏ ప్రభుత్వ వ్యవస్థకూ డేటా పంపబడదు.',

  'common.back': 'వెనుకకు',
  'common.continue': 'కొనసాగించండి',
  'common.next': 'తదుపరి',
  'common.cancel': 'రద్దు చేయండి',
  'common.retry': 'మళ్ళీ ప్రయత్నించండి',
  'common.loading': 'లోడ్ అవుతోంది…',
  'common.startOver': 'మొదటి నుంచి ప్రారంభించండి',
  'common.notFound': 'ఈ వివరం నోటీసులో మాకు కనిపించలేదు.',
  'common.step': 'దశ',
  'common.of': 'లో',
  'common.optional': 'ఐచ్ఛికం',
  'common.copied': 'కాపీ చేయబడింది.',
  'common.copy': 'టెక్స్ట్ కాపీ చేయండి',
  'common.download': 'ఒక కాపీ డౌన్‌లోడ్ చేయండి',
  'common.language': 'భాష',
  'common.confidence': 'నమ్మకం స్థాయి',
  'common.viewNotice': 'అసలు నోటీసు టెక్స్ట్ చూడండి',
  'common.hideNotice': 'అసలు నోటీసు టెక్స్ట్ దాచండి',

  'error.title': 'కొంత శ్రద్ధ అవసరం',
  'error.generic': 'ఏదో పొరపాటు జరిగింది. మళ్ళీ ప్రయత్నించండి.',
  'error.offline':
    'NoticeMate సర్వర్‌ను చేరుకోలేకపోయాము. అది నడుస్తోందో లేదో చూసి మళ్ళీ ప్రయత్నించండి.',
  'error.noNotice': 'ఆ నోటీసు కనిపించలేదు. దయచేసి మళ్ళీ ప్రారంభించండి.',

  'welcome.badge': 'కొన్ని నిమిషాల్లో నోటీసును అర్థం చేసుకోండి',
  'welcome.title1': 'అర్థంకాని',
  'welcome.title2': 'ప్రభుత్వ నోటీసు వచ్చిందా?',
  'welcome.sub':
    'NoticeMate దానిని సులభమైన భాషలో వివరిస్తుంది, మీరు ఏం చేయాలో చెబుతుంది, ప్రతి దశలో తోడుగా ఉంటుంది.',
  'welcome.cta': 'ప్రారంభించండి',
  'welcome.demoCta': 'నమూనా నోటీసుతో చూడండి',
  'welcome.f1.title': 'సులభ భాషలో వివరణ',
  'welcome.f1.desc': 'కఠిన పదాలు లేవు. అర్థం, కారణం, తర్వాత ఏమవుతుంది.',
  'welcome.f2.title': 'దశల వారీ ప్రణాళిక',
  'welcome.f2.desc': 'స్పష్టమైన జాబితా, గడువు ఎప్పుడూ కళ్ల ముందు.',
  'welcome.f3.title': 'పత్రాల జాబితా',
  'welcome.f3.desc': 'ఏ కాగితాలు కావాలి — ఒక్కొక్కటి ఎందుకు కావాలి.',
  'welcome.f4.title': 'సిద్ధమైన సమాధానం',
  'welcome.f4.desc': 'చదవగల, మార్చగల, భద్రపరచగల ముసాయిదా.',
  'welcome.trust':
    'ఇది ఒక ప్రదర్శన. నోటీసులు కల్పితమే, ఏదీ ప్రభుత్వ వ్యవస్థకు పంపబడదు.',

  'input.eyebrow': 'దశ 1',
  'input.title': 'మీ నోటీసును జోడించండి',
  'input.subtitle': 'ఎలా ప్రారంభించాలో ఎంచుకోండి.',
  'input.demoHeading': 'నమూనా నోటీసు చూడండి',
  'input.demoSub': 'ఈ డెమో కోసం తయారు చేసిన కల్పిత నోటీసులు.',
  'input.uploadHeading': 'మీ నోటీసును అప్‌లోడ్ చేయండి',
  'input.uploadDrop': 'ఫైల్ ఎంచుకోవడానికి నొక్కండి, లేదా ఇక్కడ వదలండి',
  'input.uploadHint': 'PDF, PNG, JPG లేదా TXT — 8 MB వరకు',
  'input.uploadCta': 'అప్‌లోడ్ చేసి కొనసాగించండి',
  'input.pasteHeading': 'లేదా టెక్స్ట్ పేస్ట్ చేయండి',
  'input.pasteLabel': 'నోటీసు టెక్స్ట్',
  'input.pastePlaceholder': 'మీ నోటీసులోని మాటలను ఇక్కడ పేస్ట్ లేదా టైప్ చేయండి…',
  'input.pasteCta': 'ఈ టెక్స్ట్‌తో కొనసాగించండి',
  'input.pasteTooShort': 'దయచేసి నోటీసులోని కనీసం కొన్ని పంక్తులు పేస్ట్ చేయండి.',
  'input.privacy':
    'అప్‌లోడ్ చేసిన ఫైళ్లు ఈ డెమో సర్వర్‌లోనే ఉంటాయి, వాటిని నమ్మదగని టెక్స్ట్‌గా పరిగణిస్తాము — పత్రంలోని ఏ ఆదేశాన్నీ పాటించము.',
  'input.tabDemo': 'నమూనా నోటీసు',
  'input.tabUpload': 'ఫైల్ అప్‌లోడ్',
  'input.tabPaste': 'టెక్స్ట్ పేస్ట్',

  'processing.title': 'మీ నోటీసును చదువుతున్నాము',
  'processing.sub': 'సాధారణంగా కొన్ని సెకన్లు పడుతుంది.',
  'processing.s1': 'నోటీసును చదువుతున్నాము',
  'processing.s2': 'శాఖను, సూచన సంఖ్యను గుర్తిస్తున్నాము',
  'processing.s3': 'ఏమి అడిగారో అర్థం చేసుకుంటున్నాము',
  'processing.s4': 'మీ కార్యాచరణ ప్రణాళిక తయారు చేస్తున్నాము',
  'processing.slow': 'ఇంకా పని జరుగుతోంది — ఓపికకు ధన్యవాదాలు.',

  'explain.eyebrow': 'దశ 2',
  'explain.title': 'ఈ నోటీసు అర్థం',
  'explain.q1': 'ఇది ఏ విషయం గురించి?',
  'explain.q2': 'ఇది నాకు ఎందుకు వచ్చింది?',
  'explain.q3': 'నేను ఏమి చేయాలి?',
  'explain.q4': 'పట్టించుకోకపోతే ఏమవుతుంది?',
  'explain.deadline': 'ఈ తేదీలోపు స్పందించండి',
  'explain.noDeadline': 'నోటీసులో గడువు తేదీ కనిపించలేదు',
  'explain.urgency.high': 'సమయ ప్రాధాన్యం',
  'explain.urgency.medium': 'త్వరగా చేయండి',
  'explain.urgency.low': 'తక్కువ అత్యవసరం',
  'explain.daysLeft': '{n} రోజులు మిగిలాయి',
  'explain.oneDayLeft': '1 రోజు మిగిలింది',
  'explain.today': 'ఈ రోజే గడువు',
  'explain.overdue': 'గడువు ముగిసింది',
  'explain.reference': 'సూచన సంఖ్య',
  'explain.authority': 'జారీ చేసిన శాఖ',
  'explain.category': 'నోటీసు రకం',
  'explain.uncertain': 'మళ్ళీ సరిచూసుకోవాల్సిన అంశాలు',
  'explain.cta': 'నేను ఏమి చేయాలో చూపించండి',
  'explain.source.openai': 'AI (OpenAI) ద్వారా వివరించబడింది',
  'explain.source.curated': 'డెమో విశ్లేషణ (ఈ నమూనా కోసం సిద్ధం చేసినది)',
  'explain.source.fallback': 'డెమో విశ్లేషణ — ఆఫ్‌లైన్ ప్రత్యామ్నాయం, AI కీ లేదు',
  'explain.notLegal':
    'NoticeMate న్యాయవాది కాదు, ఇది చట్టపరమైన సలహా కాదు. అసలు నోటీసును తప్పక చూడండి.',
  'explain.translatedNote':
    'వివరణ మీరు ఎంచుకున్న భాషలో చూపబడింది. అసలు నోటీసు పదాలు మారలేదు.',
  'explain.notTranslated':
    'ఈ వివరణ అనువాదం అందుబాటులో లేదు, కాబట్టి ఇంగ్లీషులో చూపబడింది.',

  'plan.eyebrow': 'దశ 3',
  'plan.title': 'మీ కార్యాచరణ ప్రణాళిక',
  'plan.subtitle': 'వరుసగా పూర్తి చేయండి. మీ ప్రగతి భద్రంగా ఉంటుంది.',
  'plan.progress': 'దశలు పూర్తి',
  'plan.markDone': 'పూర్తయింది',
  'plan.markUndone': 'ఇంకా పూర్తి కాలేదు',
  'plan.cta': 'పత్రాలకు వెళ్ళండి',
  'plan.state.not_started': 'చేయాలి',
  'plan.state.in_progress': 'జరుగుతోంది',
  'plan.state.completed': 'పూర్తి',
  'plan.state.needs_attention': 'శ్రద్ధ అవసరం',

  'docs.eyebrow': 'దశ 4',
  'docs.title': 'మీకు కావాల్సిన పత్రాలు',
  'docs.subtitle': 'మీ దగ్గర ఉన్నవి జోడించండి. అప్‌లోడ్ లేకుండానూ కొనసాగవచ్చు.',
  'docs.required': 'తప్పనిసరి',
  'docs.helpful': 'ఉపయోగకరం',
  'docs.status.needed': 'జోడించలేదు',
  'docs.status.uploaded': 'జోడించబడింది',
  'docs.status.unavailable': 'నా దగ్గర లేదు',
  'docs.upload': 'ఫైల్ జోడించండి',
  'docs.markUnavailable': 'ఇది నా దగ్గర లేదు',
  'docs.markNeeded': 'రీసెట్',
  'docs.checkTitle': 'మేము ఏమి పరిశీలించాము',
  'docs.cta': 'నా సమాధానం సిద్ధం చేయండి',
  'docs.emptyTitle': 'ఏ పత్రమూ అడగలేదు',
  'docs.emptyBody':
    'ఈ నోటీసు అదనపు పత్రాలు అడగడం లేదు. నేరుగా సమాధానానికి వెళ్ళవచ్చు.',
  'docs.noteVerify':
    'ఇవి ప్రాథమిక పరిశీలనలు మాత్రమే — NoticeMate ఏ ప్రభుత్వ శాఖతోనూ పత్రాన్ని ధృవీకరించలేదు.',

  'response.eyebrow': 'దశ 5',
  'response.title': 'మీ ముసాయిదా సమాధానం',
  'response.subtitle': 'జాగ్రత్తగా చదివి, సరికాని దాన్ని మార్చండి.',
  'response.generate': 'ముసాయిదా తయారు చేయండి',
  'response.regenerate': 'మళ్ళీ తయారు చేయండి',
  'response.label': 'ముసాయిదా సమాధానం',
  'response.extraLabel': 'ఏదైనా జోడించాలా? (ఐచ్ఛికం)',
  'response.extraPlaceholder':
    'ఉదాహరణ: నేను ఇప్పటికే నా బ్యాంకు వివరాలు నవీకరించాను…',
  'response.cta': 'సమీక్షించి కొనసాగించండి',
  'response.saved': 'ముసాయిదా భద్రపరచబడింది.',
  'response.source.openai': 'AI (OpenAI) ద్వారా తయారైంది',
  'response.source.fallback': 'డెమో ముసాయిదా — ఆఫ్‌లైన్ ప్రత్యామ్నాయం, AI కీ లేదు',
  'response.source.user': 'మీరు సవరించారు',
  'response.checkWarning':
    'ఎక్కడైనా ఉపయోగించే ముందు ప్రతి పేరు, సంఖ్య, తేదీ సరిచూసుకోండి.',

  'review.eyebrow': 'దశ 6',
  'review.title': 'సమర్పించే ముందు సమీక్ష',
  'review.subtitle': 'ఇది అనుకరణ సమర్పణ — ఏదీ ఈ డెమో బయటకు వెళ్ళదు.',
  'review.notice': 'నోటీసు',
  'review.deadline': 'గడువు',
  'review.documents': 'పత్రాలు',
  'review.response': 'మీ సమాధానం',
  'review.confirmLabel':
    'ఇది ఒక ప్రదర్శన అని, ఏ ప్రభుత్వ శాఖకూ నోటీసు పంపబడదని నేను అర్థం చేసుకున్నాను.',
  'review.cta': 'సమర్పించండి (అనుకరణ)',
  'review.needConfirm': 'కొనసాగడానికి దయచేసి నిర్ధారణ పెట్టెను గుర్తించండి.',
  'review.edit': 'సమాధానం సవరించండి',
  'review.docsCount': '{total}లో {done} జోడించబడ్డాయి',

  'confirm.title': 'సమర్పణ నమోదైంది',
  'confirm.sub': 'మీ అనుకరణ సమర్పణ ఈ డెమోలో భద్రపరచబడింది.',
  'confirm.reference': 'డెమో సూచన',
  'confirm.status': 'స్థితి',
  'confirm.whatNext': 'తర్వాత ఏమి జరుగుతుంది',
  'confirm.simulated':
    'అనుకరణ సమర్పణ — ఈ సూచన సంఖ్య NoticeMate లోపలే ఉంది. ఏ ప్రభుత్వ శాఖకూ ఏదీ చేరలేదు.',
  'confirm.cta': 'ఈ నోటీసును ట్రాక్ చేయండి',
  'confirm.newNotice': 'మరో నోటీసు ప్రారంభించండి',

  'status.eyebrow': 'ట్రాకర్',
  'status.title': 'ఇప్పటి వరకు స్థితి',
  'status.subtitle': 'ఈ డెమోలో మీరు చేసిన అన్నిటి కాలక్రమం.',
  'status.legendDone': 'ఈ డెమోలో పూర్తయింది',
  'status.legendPending': 'ఇంకా పూర్తి కాలేదు',
  'status.legendGov': 'నిజమైన ప్రభుత్వ అనుసంధానం కావాలి',
  'status.history': 'కార్యకలాప నమోదు',
  'status.cta': 'మరో నోటీసు ప్రారంభించండి',
  'status.refresh': 'రిఫ్రెష్',
  'status.govNote':
    'నిజమైన అమలులో రసీదు అధికారిక మార్గం ద్వారా ధృవీకరించబడుతుంది. ఈ నమూనా ఏ శాఖనూ సంప్రదించదు.',

  'resume.title': 'ఆపిన చోటి నుంచి కొనసాగించాలా?',
  'resume.body': 'ఈ బ్రౌజర్‌లో మీ ఒక నోటీసు మధ్యలో ఉంది.',
  'resume.cta': 'కొనసాగించండి',
  'resume.discard': 'కొత్తగా ప్రారంభించండి',
};

const DICTS = { en, hi, te };

let current = 'en';

export function setLanguage(code) {
  current = DICTS[code] ? code : 'en';
  document.documentElement.lang = current;
  return current;
}

export function getLanguage() {
  return current;
}

/** Translate a key, falling back to English and then the key itself. */
export function t(key, vars) {
  let out = DICTS[current]?.[key] ?? en[key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      out = out.replaceAll(`{${k}}`, String(v));
    }
  }
  return out;
}

/** Apply translations to any static element carrying data-i18n. */
export function applyStaticTranslations(root = document) {
  root.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  root.querySelectorAll('[data-i18n-aria]').forEach((el) => {
    el.setAttribute('aria-label', t(el.dataset.i18nAria));
  });
}
