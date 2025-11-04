# 🤖 Upwork AI Automation System

**Kompletan automatizovan sistem za Upwork sa AI-powered chat responses, cover letter generisanjem i job scraping-om**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)
![n8n](https://img.shields.io/badge/n8n-workflow-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 📋 Sadržaj

- [Šta sistem radi](#-šta-sistem-radi)
- [Instalacija](#-instalacija)
- [3 Glavna n8n Workflow-a](#-3-glavna-n8n-workflow-a)
- [Chat AI Assistant](#-chat-ai-assistant)
- [Cover Letter Generator](#-cover-letter-generator)
- [Job Scraper](#-job-scraper)
- [ML Phase Detection](#-ml-phase-detection)
- [Response Generation Modes](#-response-generation-modes)
- [Konfiguracija](#%EF%B8%8F-konfiguracija)
- [Troubleshooting](#-troubleshooting)
- [Struktura Projekta](#-struktura-projekta)

---

## 🎯 Šta sistem radi

Sistem automatizuje **sve aspekte Upwork freelancing-a**:

### 🤖 **1. Chat AI Assistant**
- **Real-time chat monitoring** sa ML-powered phase detection
- **8 faza konverzacije** (Initial Response → Contract & Start)
- **BERT ML model** za detekciju faza (100% accuracy, 92.6% za knowledge check)
- **4 response generation modes**:
  - **Template Mode**: 3 brze opcije (~0.1s)
  - **Hybrid Mode**: AI-enhanced personalizacija (1 opcija, ~2s)
  - **Pure AI Mode**: Fully AI-generated (1 opcija, ~3s)  
  - **Summary Mode**: Template + AI context summary (1 opcija, ~2s)
- **Interactive dashboard** sa click-to-copy response opcijama

### 📝 **2. Cover Letter Generator**
- **Automatsko generisanje** svakih 5 minuta
- **AI-powered personalizacija** za svaki job
- **Custom GPT-2 model training** na vašim podacima
- **Database integration** - sve cover letter čuva u SQLite

### 🔍 **3. Job Scraper**
- **Automatski scraping** svakih 2 sata
- **Chrome debug mode** bypass za Cloudflare zaštitu
- **Database storage** sa full-text pretrakom
- **HTML parsing** i ekstrakcija job details

---

## 🚀 Instalacija

### **1. Clone Repository**
```powershell
git clone https://github.com/NewworldProg/WorkFlow.git
cd WorkFlow
```

### **2. Instalacija Dependencies**

#### **Python Setup**
```powershell
# Kreiraj virtual environment
python -m venv venv

# Aktiviraj venv
.\venv\Scripts\Activate.ps1

# Instalraj Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### **Node.js Setup**
```powershell
# Instalraj root dependencies
npm install

# Instalraj JS scraper dependencies
cd js_scrapers
npm install
cd ..
```

#### **Chat AI Setup** (Automatski)
```powershell
# Kompletna automatska instalacija chat AI sistema
powershell -ExecutionPolicy Bypass -File install_chat_ai_requirements.ps1
```

### **3. n8n Setup**
1. Instaliraj n8n globalno: `npm install -g n8n`
2. Importuj workflow fajlove u n8n
3. Ažuriraj file paths u workflow nodovima
4. Aktiviraj workflow-e

### **4. Chrome Debug Setup**
Sistem koristi **2 odvojena Chrome profila**:

#### **Za Job Scraping (Port 9222)**
```powershell
chrome.exe --remote-debugging-port=9222 --user-data-dir="E:\Repoi\UpworkNotif\chrome_profile"
```

#### **Za Chat Monitoring (Port 9223)**
```powershell
chrome.exe --remote-debugging-port=9223 --user-data-dir="E:\Repoi\UpworkNotif\chrome_profile_chat"
```

**Napomena**: Oba profila moraju biti ulogovana u Upwork pre automatizacije.

---

## 🔄 3 Glavna n8n Workflow-a

Sistem ima **3 nezavisna workflow-a** koja orchestriraju sve funkcionalnosti:

---

### **1️⃣ Chat AI Assistant Workflow**
**Fajl:** `n8n_chat_ai_workflow.json`  
**Trigger:** Manual  
**Funkcija:** Real-time chat monitoring sa ML-powered AI responses

#### **Workflow Steps:**
```
Start Chat Session
  ↓
Check Chrome Chat Status (Port 9223)
  ↓
IF Chrome Ready?
  ├─ YES → Wait for Chat Navigation (45s)
  └─ NO  → Start Chrome Chat → Wait 6s → Check Again
  ↓
Run Chat Scraper (js_scrapers/browser_connect_chat.js)
  ↓
Parse Chat Messages (scripts/chat_parser.py)
  ↓
Smart Chat Response - ML Phase Detection
  ├─ Detect Phase (ai/hybrid_phase_detector.py)
  ├─ Template Mode (3 options)
  ├─ Hybrid Mode (1 option)
  ├─ Pure AI Mode (1 option)
  └─ Summary Mode (1 option)
  ↓
Generate & Open Dashboard (scripts/chat_dashboard_generator.py)
```

#### **PowerShell Scripts Used:**
- `run_check_chrome_chat.ps1` - Check Chrome status (port 9223)
- `run_start_chrome_chat_simple.ps1` - Start Chrome chat profile
- `run_chat_scraper.ps1` - Scrape chat messages
- `run_chat_parser.ps1` - Parse HTML to database
- `run_smart_chat_response.ps1 -Mode all` - Generate AI responses (all 4 modes)
- `run_generate_and_open_chat_dashboard.ps1` - Create interactive dashboard

#### **Python Scripts Called:**
- `js_scrapers/browser_connect_chat.js` - Puppeteer chat scraper
- `scripts/chat_parser.py` - HTML parsing to SQLite
- `data/chat_database_manager.py` - Database operations
- `ai/smart_chat_response.py` - Main AI response generator
- `ai/hybrid_phase_detector.py` - ML + keyword phase detector
- `ai/phase_detector.py` - BERT model inference
- `ai/chat_gpt2_generator.py` - GPT-2 response generation
- `scripts/chat_dashboard_generator.py` - Dashboard HTML generator

#### **Database:**
- **Location:** `data/chat_data.db`
- **Tables:** `chat_sessions`, `chat_messages`

#### **Models:**
- **Phase Classifier:** `ai/trained_models/phase_classifier_v1/` (BERT-base-uncased)
- **Response Generator:** GPT-2 base model

---

### **2️⃣ Cover Letter Generator Workflow**
**Fajl:** `n8n_ai_cover_letter_workflow.json`  
**Trigger:** Schedule (Every 5 minutes)  
**Funkcija:** Automatic cover letter generation for new jobs

#### **Workflow Steps:**
```
Every 5 Minutes Trigger
  ↓
Get Latest Job Without Cover Letter (data/database_manager.py)
  ↓
Smart AI Cover Letter (ai/cover_letter_generator.py)
  ↓
Import to DB (data/database_manager.py)
  ↓
Refresh Dashboard (generate_dashboard_enhanced.py)
```

#### **PowerShell Scripts Used:**
- `run_get_latest_job_without_cover_letter.ps1` - Get job from DB
- `run_smart_cover_letter.ps1` - Generate AI cover letter
- `run_import_jobs_to_db.ps1` - Save cover letter to DB
- `run_generate_and_open_dashboard.ps1` - Refresh job dashboard

#### **Python Scripts Called:**
- `data/database_manager.py` - Job database operations
- `ai/cover_letter_generator.py` - AI cover letter generator
- `smart_cover_letter_generator.py` - Wrapper script
- `generate_dashboard_enhanced.py` - Job dashboard generator

#### **Database:**
- **Location:** `upwork_data.db` ili `upwork_jobs.db`
- **Tables:** `jobs`, `cover_letters`

#### **Models:**
- **GPT-2 Fine-tuned:** `trained_models/advanced_cover_letter_model/final/`

---

### **3️⃣ Job Scraper Workflow**
**Fajl:** `n8n_workflow_conditional.json`  
**Trigger:** Schedule (Every 2 hours)  
**Funkcija:** Automatic Upwork job scraping and parsing

#### **Workflow Steps:**
```
Every 2 Hours Trigger
  ↓
Check Chrome Status (Port 9222)
  ↓
IF Chrome Ready?
  ├─ YES → Wait for Human Navigation (20s)
  └─ NO  → Start Chrome → Wait 6s → Check Again
  ↓
Run JS Scraper (js_scrapers/browser_connect_puppeteer.js)
  ↓
Save HTML to Database (data/database_manager.py)
  ↓
Parse HTML (upwork_data_parser.py)
  ↓
Import to DB (data/database_manager.py)
  ↓
Generate & Open Dashboard (generate_dashboard_enhanced.py)
```

#### **PowerShell Scripts Used:**
- `run_check_chrome_n8n.ps1` - Check Chrome status (port 9222)
- `run_start_chrome_simple.ps1` - Start Chrome job profile
- `run_js_scraper.ps1` - Run JavaScript scraper
- `run_save_html_to_db.ps1` - Save HTML to database
- `run_parse_html_only.ps1` - Parse HTML to job data
- `run_import_jobs_to_db.ps1` - Import jobs to database
- `run_generate_and_open_dashboard.ps1` - Generate job dashboard

#### **JavaScript Scripts:**
- `js_scrapers/browser_connect_puppeteer.js` - Puppeteer job scraper

#### **Python Scripts Called:**
- `data/database_manager.py` - Database operations
- `upwork_data_parser.py` - HTML parsing to job data
- `generate_dashboard_enhanced.py` - Job dashboard generator

#### **Database:**
- **Location:** `upwork_data.db`
- **Tables:** `jobs`, `html_snapshots`

---

## 🤖 Chat AI Assistant

### **🧠 ML Phase Detection**

Sistem koristi **BERT-base-uncased** model treniran na 53 Upwork konverzacija za detekciju **8 faza pregovora**:

#### **8 Conversation Phases:**

| Phase ID | Phase Name | Keywords | Next Phase |
|----------|-----------|----------|------------|
| `initial_response` | Initial Response | apply, application, interested, position, job | Ask Job Details |
| `ask_job_details` | Ask Job Details | project, task, what, need, require, about | Language Confirmation |
| `language_confirmation` | Language Confirmation | language, english, dutch, spanish, french | Rate Discussion |
| `rate_negotiation` | Rate Discussion | rate, price, per word, budget, cost, charge | Deadline & Samples |
| `deadline_samples` | Deadline & Samples | deadline, when, sample, example, brief, due | Structure Clarification |
| `structure_clarification` | Structure & Requirements | structure, format, seo, keywords, h1, h2, faq | Contract Acceptance |
| `contract_acceptance` | Contract & Start | contract, agreement, accept, start, begin, deal | None (Work Begins) |
| `knowledge_check` | Knowledge Check | test, quiz, prove, show, demonstrate, example | *HUMAN REVIEW REQUIRED* |

#### **Knowledge Check Phase**
- **Purpose:** Detektuje kada klijent testira znanje freelancer-a
- **Detection Confidence:** 92.6%
- **Flag:** `requires_human: true` - NE generiše automatske odgovore
- **Action:** Dashboard prikazuje upozorenje da treba lični odgovor

#### **Model Details:**
- **Architecture:** BERT-base-uncased (110M parameters)
- **Training Data:** 53 labeled Upwork conversations (`ai/phase_training_data.json`)
- **Training:** 20 epochs, 85/15 train/test split
- **Accuracy:** 100% on training set
- **Production Confidence:** 75-93% for most phases
- **Location:** `ai/trained_models/phase_classifier_v1/`

#### **Fallback System:**
```python
# Hybrid Detection: ML + Keywords
try:
    phase = ml_model.predict(conversation_text)
    confidence = phase.confidence_score
except:
    phase = keyword_detector.detect(conversation_text)
    confidence = keyword_match_score
```

---

### **🎨 Response Generation Modes**

Sistem podržava **4 načina generisanja odgovora** koje možete koristiti zasebno ili zajedno:

#### **Mode Comparison:**

| Mode | Speed | Quality | Use Case | Options | Command |
|------|-------|---------|----------|---------|---------|
| **Template** | ⚡ ~0.1s | 📝 Pre-written | Fast, consistent responses | 3 | `-Mode template` |
| **Hybrid** | 🔄 ~2s | 🤖 AI-enhanced | AI personalization on templates | 1 | `-Mode hybrid` |
| **Pure AI** | 🤖 ~3s | 💭 Fully generated | Creative, unique responses | 1 | `-Mode pure` |
| **Summary** | 📊 ~2s | 📋 Context-aware | Template + conversation summary | 1 | `-Mode summary` |
| **All Modes** | 🔥 ~7s | 🎯 Complete | All 4 modes together | 6 total | `-Mode all` |

#### **1. Template Mode** (Default)
```powershell
.\run_smart_chat_response.ps1 -Mode template
```
- **Speed:** ~0.1 sekunde
- **Output:** 3 pre-written opcije za trenutnu fazu
- **Prednosti:** Brz, pouzdan, profesionalan ton
- **Primer Output:**
```json
{
  "template_options": [
    "Sounds good! What's the deadline for this batch?",
    "Great, we're aligned on the rate. When do you need this delivered?",
    "Perfect! Could you provide: 1) Deadline, and 2) A sample article?"
  ]
}
```

#### **2. Hybrid Mode** (AI + Template)
```powershell
.\run_smart_chat_response.ps1 -Mode hybrid
```
- **Speed:** ~2 sekunde
- **Output:** 1 AI-personalized verzija template-a
- **Prednosti:** Balansiran pristup - template struktura + AI kreativnost
- **Primer Output:**
```json
{
  "hybrid_option": "Thank you for your interest in this topic. What's the deadline for this batch?"
}
```

#### **3. Pure AI Mode** (100% AI)
```powershell
.\run_smart_chat_response.ps1 -Mode pure
```
- **Speed:** ~3 sekunde
- **Output:** 1 potpuno AI-generated odgovor
- **Prednosti:** Kreativni, unique responses
- **Primer Output:**
```json
{
  "pure_ai_option": "I understand your requirements. Could we discuss the timeline in more detail?"
}
```

#### **4. Summary Mode** (Template + Context)
```powershell
.\run_smart_chat_response.ps1 -Mode summary
```
- **Speed:** ~2 sekunde
- **Output:** 1 template + AI-generated summary poslednje 10 poruka
- **Prednosti:** Template + kontekstno razumevanje konverzacije
- **Primer Output:**
```json
{
  "summary_option": "Sounds good! I hope to have more information about the project by the end of the month."
}
```

#### **5. All Modes** (Recommended)
```powershell
.\run_smart_chat_response.ps1 -Mode all
```
- **Speed:** ~7-8 sekundi
- **Output:** SVE 4 mode-a zajedno (3+1+1+1 = 6 opcija)
- **Prednosti:** Kompletna fleksibilnost - biraš najbolju opciju
- **n8n Workflow:** Default mode u `n8n_chat_ai_workflow.json`

---

### **📊 Dashboard Display**

Dashboard prikazuje:

```
┌─────────────────────────────────────────────────────┐
│ 🎯 Current Phase: Rate Discussion                 │
│ 🔬 Confidence: 78.3% (ML Model)                    │
│ ➡️  Next Phase: Deadline & Samples                 │
├─────────────────────────────────────────────────────┤
│ 📝 Template Options (3):                           │
│   [Copy] "Sounds good! What's the deadline?"      │
│   [Copy] "Great! When do you need this?"          │
│   [Copy] "Perfect! Deadline and sample needed?"   │
├─────────────────────────────────────────────────────┤
│ 🤖 Hybrid AI (1):                                  │
│   [Copy] "Thank you! What's the deadline?"        │
├─────────────────────────────────────────────────────┤
│ 💭 Pure AI (1):                                    │
│   [Copy] "Could we discuss the timeline?"         │
├─────────────────────────────────────────────────────┤
│ 📋 Summary AI (1):                                 │
│   [Copy] "Sounds good! I hope to clarify..."      │
├─────────────────────────────────────────────────────┤
│ ❓ Follow-up Questions:                            │
│   • What's the deadline for this batch?           │
│   • Can you share a sample article?               │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Cover Letter Generator

### **Setup**

#### **1. OpenAI Setup (Optional)**
```powershell
# Set API key environment variable
$env:OPENAI_API_KEY = "your-api-key-here"
```

#### **2. Custom GPT-2 Training**
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Train custom model na vašim podacima
python ai/training/examples/train_advanced.py

# Model se čuva u:
# trained_models/advanced_cover_letter_model/final/
```

#### **Training Details:**
- **Dataset:** `ai/training_data.json` (vaši uspešni cover letter-i)
- **Model:** GPT-2 medium (355M parameters)
- **Training:** 5 epochs, optimizovano za CPU
- **Result:** Personalizovani cover letter-i sa vašim stilom

### **Usage**

#### **Automatic (n8n)**
- **Frequency:** Svakih 5 minuta
- **Trigger:** `n8n_ai_cover_letter_workflow.json`
- **Action:** Generiše cover letter za najnoviji job bez cover letter-a

#### **Manual**
```powershell
# Generate single cover letter
.\run_smart_cover_letter.ps1

# Import to database
.\run_import_jobs_to_db.ps1

# Refresh dashboard
.\run_generate_and_open_dashboard.ps1
```

#### **Programmatic**
```python
from ai.cover_letter_generator import CoverLetterGenerator
from data.database_manager import UpworkDatabase

# Initialize
generator = CoverLetterGenerator(preferred_provider='openai')
db = UpworkDatabase()

# Generate
job_data = db.get_latest_job_without_cover_letter()
cover_letter = generator.generate_cover_letter(job_data)

# Save
db.add_cover_letter(
    job_id=job_data['id'],
    ai_provider='openai',
    cover_letter_text=cover_letter
)
```

---

## 🔍 Job Scraper

### **Chrome Debug Mode Bypass**

Glavni izazov sa Upwork scraping-om je **Cloudflare zaštita**. Naš sistem koristi **Chrome debug mode**:

#### **Zašto funkcioniše:**
1. **Chrome ostaje otvoren** u debug modu (port 9222)
2. **Ti se logujueš ručno** i rešavaš Cloudflare challenge
3. **Puppeteer se conectuje** na postojeću sesiju
4. **Cloudflare ne detektuje** jer nije novi browser instance

#### **Setup:**
```powershell
# 1. Start Chrome u debug modu
chrome.exe --remote-debugging-port=9222 --user-data-dir="E:\Repoi\UpworkNotif\chrome_profile"

# 2. Uloguj se u Upwork
# 3. Navigiraj na job search page
# 4. Aktiviraj n8n workflow ili pokreni ručno:
.\run_js_scraper.ps1
```

### **Workflow Automation**

#### **n8n Schedule:**
- **Frequency:** Svakih 2 sata
- **Workflow:** `n8n_workflow_conditional.json`
- **Steps:**
  1. Check Chrome status (port 9222)
  2. IF not ready → Start Chrome → Wait 6s
  3. Wait for human navigation (20s)
  4. Run JS scraper
  5. Save HTML to database
  6. Parse HTML
  7. Import jobs to database
  8. Generate dashboard

#### **Database:**
```sql
-- Jobs table
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    budget TEXT,
    skills TEXT,
    posted_date TEXT,
    url TEXT UNIQUE,
    has_cover_letter INTEGER DEFAULT 0
);

-- HTML Snapshots
CREATE TABLE html_snapshots (
    id INTEGER PRIMARY KEY,
    snapshot_date TEXT,
    html_content TEXT,
    job_count INTEGER
);
```

---

## ⚙️ Konfiguracija

### **File Paths**

Svi PowerShell i n8n workflow-i koriste **apsolutne putanje**. Promeni ih u sledećim fajlovima:

#### **n8n Workflows:**
- `n8n_chat_ai_workflow.json` (10 nodes)
- `n8n_ai_cover_letter_workflow.json` (5 nodes)
- `n8n_workflow_conditional.json` (11 nodes)

#### **Path Format:**
```json
"command": "powershell -ExecutionPolicy Bypass -File \"E:\\Repoi\\UpworkNotif\\run_script.ps1\""
```

**Promeni:** `E:\\Repoi\\UpworkNotif\\` → **tvoja putanja**

### **Chrome Ports**

Sistem koristi **2 odvojena Chrome profila**:

| Profile | Port | Purpose | Location |
|---------|------|---------|----------|
| Job Scraping | 9222 | Scraping job listings | `chrome_profile/` |
| Chat Monitoring | 9223 | Monitoring chat conversations | `chrome_profile_chat/` |

**Proveri dostupnost porta:**
```powershell
# Test job scraping port
Invoke-WebRequest -Uri "http://localhost:9222/json/version"

# Test chat monitoring port
Invoke-WebRequest -Uri "http://localhost:9223/json/version"
```

### **Database Locations**

| Database | Location | Purpose |
|----------|----------|---------|
| Chat Data | `data/chat_data.db` | Chat sessions and messages |
| Job Data | `upwork_data.db` | Scraped jobs and HTML |
| Jobs Database | `upwork_jobs.db` | Alternative jobs storage |

### **Model Locations**

| Model | Location | Purpose |
|-------|----------|---------|
| Phase Classifier | `ai/trained_models/phase_classifier_v1/` | BERT conversation phase detection |
| Cover Letter GPT-2 | `trained_models/advanced_cover_letter_model/final/` | Fine-tuned GPT-2 for cover letters |

---

## 🛠️ Troubleshooting

### **Chrome Connection Issues**

#### **Problem:** "Could not connect to Chrome"
```powershell
# Check if Chrome is running with debug port
Invoke-WebRequest -Uri "http://localhost:9222/json/version"

# If error, restart Chrome:
taskkill /F /IM chrome.exe
chrome.exe --remote-debugging-port=9222 --user-data-dir="E:\Repoi\UpworkNotif\chrome_profile"
```

#### **Problem:** "Port already in use"
```powershell
# Find process using port 9222
netstat -ano | findstr :9222

# Kill process (replace PID)
taskkill /F /PID <PID>
```

### **Database Issues**

#### **Problem:** "No jobs found in database"
```powershell
# Check database exists
Test-Path "E:\Repoi\UpworkNotif\upwork_data.db"

# Run scraper manually
.\run_js_scraper.ps1
.\run_save_html_to_db.ps1
.\run_parse_html_only.ps1
.\run_import_jobs_to_db.ps1
```

#### **Problem:** "Wrong database location" (Chat AI)
```python
# Check which database is being used
python -c "from data.chat_database_manager import ChatDatabase; db = ChatDatabase(); print(db.db_path)"

# Should print: data/chat_data.db
```

### **ML Model Issues**

#### **Problem:** "Model not found"
```powershell
# Check model exists
Test-Path "E:\Repoi\UpworkNotif\ai\trained_models\phase_classifier_v1"

# Retrain model if missing
.\venv\Scripts\Activate.ps1
python ai/train_phase_classifier.py
```

#### **Problem:** "Low phase detection confidence"
```python
# Model falls back to keyword detection
# To improve, add more training data to:
# ai/phase_training_data.json

# Then retrain:
python ai/train_phase_classifier.py
```

### **n8n Workflow Issues**

#### **Problem:** "Workflow connection failed"
```powershell
# Validate workflow structure
python validate_workflow.py n8n_chat_ai_workflow.json

# Check for node name mismatches
```

#### **Problem:** "Command execution timeout"
```json
// Increase timeout in n8n node settings:
"timeout": 300000  // 5 minutes
```

### **GPT-2 Response Issues**

#### **Problem:** "All AI modes return same response"
```python
# Check GPT-2 is being called correctly:
# ai/smart_chat_response.py line ~180

# Should be:
result = gpt2.generate_response(
    session_id=session_id,
    custom_prompt=prompt,
    response_type='professional'
)
response_text = result['responses'][0]

# NOT:
# result = gpt2.generate_response(prompt, max_length=150)
```

#### **Problem:** "Repetitive GPT-2 output (ok ok ok...)"
```python
# Use template mode instead:
.\run_smart_chat_response.ps1 -Mode template

# Or retrain GPT-2 with better data
```

### **Cloudflare Issues**

#### **Problem:** "Cloudflare still blocking scraper"
```powershell
# Solution:
# 1. Keep Chrome open manually
# 2. Solve Cloudflare challenge in browser
# 3. THEN run scraper
# 4. Scraper connects to existing session

# Check Chrome is ready:
.\run_check_chrome_n8n.ps1
# Output should be: {"chrome_ready": true}
```

---

## 📁 Struktura Projekta

```
UpworkNotif/
├── 📁 ai/                                    # AI Components
│   ├── __init__.py
│   ├── chat_gpt2_generator.py                # GPT-2 response generator
│   ├── cover_letter_generator.py             # Cover letter AI
│   ├── phase_detector.py                     # BERT phase classifier
│   ├── hybrid_phase_detector.py              # ML + keyword fallback
│   ├── smart_chat_response.py                # Main response generator (4 modes)
│   ├── train_phase_classifier.py             # BERT training script
│   ├── phase_training_data.json              # 53 labeled conversations
│   └── 📁 trained_models/
│       └── 📁 phase_classifier_v1/           # BERT model (110M params)
│
├── 📁 data/                                  # Database Components
│   ├── chat_database_manager.py              # Chat DB operations
│   ├── database_manager.py                   # Job DB operations
│   └── chat_data.db                          # SQLite chat database
│
├── 📁 js_scrapers/                           # JavaScript Scrapers
│   ├── browser_connect_puppeteer.js          # Job scraper (port 9222)
│   ├── browser_connect_chat.js               # Chat scraper (port 9223)
│   └── package.json
│
├── 📁 scripts/                               # Python Scripts
│   ├── chat_parser.py                        # Chat HTML parser
│   ├── chat_dashboard_generator.py           # Chat dashboard HTML
│   └── upwork_data_parser.py                 # Job HTML parser
│
├── 📁 trained_models/                        # ML Models
│   └── 📁 advanced_cover_letter_model/
│       └── 📁 final/                         # Fine-tuned GPT-2
│
├── 📁 chrome_profile/                        # Chrome Debug Profile (port 9222)
├── 📁 chrome_profile_chat/                   # Chrome Chat Profile (port 9223)
│
├── 📄 n8n_chat_ai_workflow.json              # Chat AI Workflow (10 nodes)
├── 📄 n8n_ai_cover_letter_workflow.json      # Cover Letter Workflow (5 nodes)
├── 📄 n8n_workflow_conditional.json          # Job Scraper Workflow (11 nodes)
│
├── 📄 upwork_data.db                         # Jobs database
├── 📄 chat_dashboard.html                    # Generated chat dashboard
├── 📄 dashboard.html                         # Generated job dashboard
│
├── 🔧 run_check_chrome_chat.ps1              # Check chat Chrome status
├── 🔧 run_check_chrome_n8n.ps1               # Check job Chrome status
├── 🔧 run_start_chrome_chat_simple.ps1       # Start chat Chrome
├── 🔧 run_start_chrome_simple.ps1            # Start job Chrome
├── 🔧 run_chat_scraper.ps1                   # Run chat scraper
├── 🔧 run_chat_parser.ps1                    # Parse chat HTML
├── 🔧 run_smart_chat_response.ps1            # Generate AI responses
├── 🔧 run_generate_and_open_chat_dashboard.ps1  # Chat dashboard
├── 🔧 run_js_scraper.ps1                     # Run job scraper
├── 🔧 run_save_html_to_db.ps1                # Save HTML to DB
├── 🔧 run_parse_html_only.ps1                # Parse job HTML
├── 🔧 run_import_jobs_to_db.ps1              # Import jobs to DB
├── 🔧 run_generate_and_open_dashboard.ps1    # Job dashboard
├── 🔧 run_get_latest_job_without_cover_letter.ps1  # Get job for cover letter
├── 🔧 run_smart_cover_letter.ps1             # Generate cover letter
├── 🔧 run_train_phase_classifier.ps1         # Train BERT model
│
├── 📄 package.json                           # Node.js dependencies
├── 📄 requirements.txt                       # Python dependencies
├── 📄 install_chat_ai_requirements.ps1       # Auto-installer
├── 📄 validate_workflow.py                   # n8n workflow validator
│
└── 📄 README.md                              # This file
```

### **Fajlovi po Kategorijama**

#### **🔄 n8n Workflows (3)**
- `n8n_chat_ai_workflow.json` - Chat AI automation
- `n8n_ai_cover_letter_workflow.json` - Cover letter automation
- `n8n_workflow_conditional.json` - Job scraping automation

#### **🤖 AI Scripts (7)**
- `ai/smart_chat_response.py` - Main response generator
- `ai/hybrid_phase_detector.py` - ML + keyword detector
- `ai/phase_detector.py` - BERT classifier
- `ai/chat_gpt2_generator.py` - GPT-2 generator
- `ai/cover_letter_generator.py` - Cover letter AI
- `ai/train_phase_classifier.py` - Model training
- `ai/phase_training_data.json` - Training dataset

#### **📊 Database Scripts (2)**
- `data/chat_database_manager.py` - Chat operations
- `data/database_manager.py` - Job operations

#### **🕷️ Scraper Scripts (2)**
- `js_scrapers/browser_connect_chat.js` - Chat scraper
- `js_scrapers/browser_connect_puppeteer.js` - Job scraper

#### **📝 Parser Scripts (3)**
- `scripts/chat_parser.py` - Chat HTML parser
- `scripts/chat_dashboard_generator.py` - Chat dashboard
- `upwork_data_parser.py` - Job HTML parser

#### **🔧 PowerShell Wrappers (15)**
- Chat workflow: 6 scripts
- Cover letter workflow: 3 scripts
- Job workflow: 6 scripts

#### **🗄️ Databases (3)**
- `data/chat_data.db` - Chat data
- `upwork_data.db` - Job data
- `upwork_jobs.db` - Alternative job storage

#### **🧠 ML Models (2)**
- `ai/trained_models/phase_classifier_v1/` - BERT (110M params)
- `trained_models/advanced_cover_letter_model/final/` - GPT-2 (355M params)

---

## 📊 Performance

### **Chat AI Assistant**
- **Phase Detection:** ~0.5s (BERT inference)
- **Template Mode:** ~0.1s (instant templates)
- **Hybrid Mode:** ~2s (template + GPT-2)
- **Pure AI Mode:** ~3s (full GPT-2 generation)
- **Summary Mode:** ~2s (template + summary)
- **All Modes:** ~7-8s (sequential execution)
- **Total Workflow:** ~10-15s (scrape → parse → detect → respond)

### **Cover Letter Generator**
- **Single Job:** ~3-5s (GPT-2 generation)
- **Batch Processing:** ~30s for 10 jobs
- **n8n Frequency:** Every 5 minutes

### **Job Scraper**
- **Single Page:** ~5-10s (Puppeteer scraping)
- **HTML Parsing:** ~2-3s (BeautifulSoup)
- **Database Import:** ~1s (SQLite)
- **n8n Frequency:** Every 2 hours

### **Storage**
- **Chat Database:** ~5MB (100 sessions)
- **Job Database:** ~50MB (1000 jobs with HTML)
- **ML Models:** ~450MB (BERT + GPT-2)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Update documentation if needed
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

---

## ⚖️ Legal Disclaimer

**IMPORTANT: Read before using this software**

### � Development Context
This project was developed as **contracted work** for a specific client under a work-for-hire agreement. The code is published for **portfolio and educational purposes only**.

### 🚫 Terms of Use
By accessing or using this code, you agree to the following terms:

1. **No Liability**: The developer(s) of this software are **NOT responsible** for:
   - How this software is used by third parties
   - Any violations of terms of service of third-party platforms (including but not limited to Upwork)
   - Data loss, account suspension, legal issues, or any damages arising from use
   - Compliance with applicable laws and regulations in your jurisdiction

2. **Use at Your Own Risk**: This software is provided "AS IS" without warranty of any kind. Users assume **full responsibility** for:
   - Compliance with Upwork Terms of Service
   - Compliance with automation/scraping policies of any platforms used
   - Any consequences resulting from use of this software
   - Proper configuration and security of their systems

3. **No Endorsement**: This project does **NOT** constitute:
   - Encouragement to violate any terms of service
   - Legal advice or compliance guidance
   - A recommendation to use automation on any platform

4. **Educational Purpose**: This code is shared for:
   - Portfolio demonstration of technical skills
   - Educational reference for ML/automation techniques
   - Code review and learning purposes

### ⚠️ Platform Terms Compliance
**WARNING**: Automated interaction with websites may violate their Terms of Service. Before using this software:
- Review Upwork's Terms of Service and API usage policies
- Ensure compliance with all applicable platform policies
- Consider using official APIs instead of web scraping where available
- Obtain proper authorization before automating any platform interactions

### 🔒 Data Privacy & Security
Users are responsible for:
- Securing their own credentials and authentication tokens
- Proper handling of any personal or sensitive data
- Compliance with GDPR, CCPA, and other privacy regulations
- Not committing sensitive data (cookies, tokens, profiles) to version control

### 📞 Contact
For questions about this disclaimer or the project's development context, contact the repository owner through GitHub Issues.

---

## �📄 License

MIT License - see LICENSE file for details.

**Note**: The MIT License applies to the code itself. It does NOT grant permission to violate any third-party terms of service or applicable laws.

---

## 🆘 Support

- **GitHub Issues:** [Report a bug](../../issues)
- **Documentation:** This README

**Note**: Support is provided on a best-effort basis for portfolio/educational purposes only.

---

## 🎯 Quick Start Summary

```powershell
# 1. Clone & Install
git clone https://github.com/NewworldProg/WorkFlow.git
cd WorkFlow
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
powershell -ExecutionPolicy Bypass -File install_chat_ai_requirements.ps1

# 2. Setup Chrome
chrome.exe --remote-debugging-port=9222 --user-data-dir="chrome_profile"
chrome.exe --remote-debugging-port=9223 --user-data-dir="chrome_profile_chat"

# 3. Import n8n Workflows
# - n8n_chat_ai_workflow.json
# - n8n_ai_cover_letter_workflow.json  
# - n8n_workflow_conditional.json

# 4. Update File Paths u svim workflow nodovima

# 5. Aktiviraj n8n workflows

# 6. Test
.\run_check_chrome_chat.ps1
.\run_check_chrome_n8n.ps1
```

---

**⚡ Built with n8n, BERT, GPT-2, Puppeteer, and Python**  
**🚀 Automated Upwork workflow for maximum productivity**

---

**Author:** AI Automation System  
**Version:** 3.0  
**Last Updated:** 2025-11-03  
**Repository:** https://github.com/NewworldProg/WorkFlow
