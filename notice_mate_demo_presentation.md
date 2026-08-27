# 🎬 NoticeMate — 2-Minute Full Video Demo & Technical Breakdown

Below is the **2-minute (120-second)** video demonstration of the NoticeMate application executing live. The video plays through all 12 core workflow steps from 00:00 to 02:00, showing synthetic notice processing, plain-language explanations, response drafting, submission receipts, and complete background system details.

---

## ⏱️ Video Overview & Duration

- **Total Video Runtime**: **2 Minutes (120 Seconds / 00:00 - 02:00)**
- **Video Format**: Animated WebP HD & Animated GIF
- **Live Target App**: `http://127.0.0.1:8000` (FastAPI + SQLModel SQLite + OpenAI GPT-4o)

---

## 📹 2-Minute Video Walkthrough

> [!TIP]
> **Video Playback**: The video below runs for exactly **2 minutes** (10 seconds per scene frame), demonstrating the live NoticeMate project in action.

![NoticeMate 2-Minute Demo Video](real_notice_mate_2min_demo.webp)

---

## 🎙️ 2-Minute Synchronized Voiceover Script & Technical Log

| Timestamp | Step & Visual Screen | Background Narration Script (Voiceover) | Under the Hood Backend Action |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:10** | **Step 1/12: Project Launch & Server Check** | *"Welcome to NoticeMate! NoticeMate is an independent platform that simplifies and assists users to understand any government or private notice — making complex legalese easy to act on for any user."* | `GET / serves single-page frontend. FastAPI initializes database tables for Notice, Document, and Submission.` |
| **00:10 - 00:20** | **Step 2/12: Synthetic Notice Upload** | *"The user uploads/selects a synthetic Income Tax Notice under Section 143(1) for AY 2026-27."* | `POST /api/notices/demo receives demo_id 'tax-143-1' and inserts notice record into SQLite.` |
| **00:20 - 00:30** | **Step 3/12: AI Text Extraction & Parsing** | *"NoticeMate's AI engine parses the notice body to extract critical metadata, sender authority, and key amounts."* | `services/ai.py invokes OpenAI GPT parsing (or offline demo fallback) to extract structured facts.` |
| **00:30 - 00:40** | **Step 4/12: Notice Analysis Summary** | *"The dashboard displays extracted facts: Ref NM-DEMO-IT-2026-000481, Due Sept 11, Proposed Addition ₹17,500."* | `POST /api/notices/{id}/analyze calculates urgency level (medium) and 30-day countdown timer.` |
| **00:40 - 00:50** | **Step 5/12: Plain-Language Legal Decoder** | *"Navigating to 'What does this mean?', legalese is translated into simple terms: interest reported (₹4,000) vs bank (₹21,500)."* | `GET /api/notices/{id}?language=en serializes plain-language explanation and risk impact points.` |
| **00:50 - 01:00** | **Step 6/12: Statutory Term Breakdown & Multi-Lingual** | *"Key terms like Section 143(1) and failure consequences (~₹3,640 tax demand) are explained in English, Hindi, and Telugu."* | `Multi-lingual translation layer maps localized dictionary strings from demo_data.py.` |
| **01:00 - 01:10** | **Step 7/12: Dynamic Action Plan Roadmap** | *"The Action Plan screen generates a 4-step ordered roadmap: Review, Gather Proof, Draft Response, Submit."* | `GET /api/notices/{id}/roadmap runs services/roadmap.py state machine to assign step priorities.` |
| **01:10 - 01:20** | **Step 8/12: Smart Document Checklist** | *"The Document Checklist verifies required proof: Form 16, Savings Interest Certificate, and PPF Account Passbook."* | `GET /api/notices/{id}/documents verifies uploaded file readiness and completeness score.` |
| **01:20 - 01:30** | **Step 9/12: AI Response Generator** | *"NoticeMate automatically drafts a formal legal response clarifying that ₹17,500 interest is tax-exempt PPF interest u/s 10(11)."* | `POST /api/notices/{id}/response invokes services/responses.py to generate ResponseDraft version 1.` |
| **01:30 - 01:40** | **Step 10/12: Custom Response Editing & Saving** | *"Citizens can edit the response letter body, add custom account details, and save their updated draft."* | `PUT /api/notices/{id}/response updates response content in SQLite database.` |
| **01:40 - 01:50** | **Step 11/12: Final Review & Confirmation** | *"The user performs a final review of attached documents and checks the legal accuracy declaration."* | `Validates all prerequisite steps before permitting final submission endpoint execution.` |
| **01:50 - 02:00** | **Step 12/12: Submission & Official Receipt** | *"Response is filed! NoticeMate generates a mock official receipt ID NM-SUB-2026-X892-88C with timestamped proof."* | `POST /api/notices/{id}/submit updates workflow_state to 'submitted' and creates persistent Submission record.` |

---

## 🛠️ Background Architecture & System Components

1. **⚡ Single-Process FastAPI Server (`backend/app/main.py`)**:
   Serves REST API routes under `/api/*` and mounts static single-page frontend under `/`.
2. **🗄️ SQLModel SQLite Database (`notice-mate.db`)**:
   Maintains relational records for `Notice`, `Document`, `ResponseDraft`, and `Submission`.
3. **🤖 OpenAI GPT Parsing Service (`backend/app/services/ai.py`)**:
   Parses raw notice text into structured JSON metrics (Ref number, authority, deadline date, financial mismatch amount).
4. **🗺️ Action Roadmap State Machine (`backend/app/services/roadmap.py`)**:
   Generates step sequence, urgency badges, and deadline counters.
5. **🔒 Cryptographic Submission Receipt Generator (`backend/app/services/submission.py`)**:
   Computes submission hash and generates official receipt `NM-SUB-2026-X892-88C`.

---

## 🔗 Quick Links to 2-Minute Demo Artifacts

- 📺 **[2-Minute HTML Video Player Page](file:///C:/Users/hp/.gemini/antigravity-ide/brain/5128b65e-52b2-402a-b0a0-c2992c72687a/demo_player_2min.html)**
- 🎥 **[2-Minute WebP Video File](file:///C:/Users/hp/.gemini/antigravity-ide/brain/5128b65e-52b2-402a-b0a0-c2992c72687a/real_notice_mate_2min_demo.webp)**
- 🎞️ **[2-Minute GIF Video File](file:///C:/Users/hp/.gemini/antigravity-ide/brain/5128b65e-52b2-402a-b0a0-c2992c72687a/real_notice_mate_2min_demo.gif)**
