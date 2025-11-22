# 🤖 Scrape and AI Automation System

**Complete automated system for web scraping and AI automation with intelligent chat responses, content generation, and data processing**

## ⚠️ **AI Model Training Notice**

**Starting AI models use base/untrained models with fallback logic:**
- **Phase Detection**: Uses base BERT (lower accuracy)  
- **Chat Responses**: Uses base GPT-2 (less contextual)
- **Cover Letters**: Uses base GPT-2 (generic responses)

**For better performance, train custom models using the training data in:**
- [`ai/phase_detector_trainer/`](ai/phase_detector_trainer/) - BERT phase detection training
- [`ai/chat_bot_trainer/`](ai/chat_bot_trainer/) - GPT-2 chat response training  
- [`ai/cover_letter_trainer/`](ai/cover_letter_trainer/) - GPT-2 cover letter training

📖 **[See AI Training Guide](README-ai-training.md)** for detailed instructions.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)
![n8n](https://img.shields.io/badge/n8n-workflow-orange.svg)
![BERT](https://img.shields.io/badge/ML-BERT-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🚀 Quick Start

- 📖 **[Installation Guide](INSTALLATION_GUIDE.md)** - Complete setup instructions
- 🎯 **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes

---

## 🔄 How It Works

This system uses **n8n workflows** to orchestrate automated web scraping and AI automation tasks:

```
n8n Frontend → PowerShell Scripts → Python/JavaScript Code
```

### 🎯 **4 Independent Workflows**

| Workflow | Description | README |
|----------|-------------|---------|
| **Web Scraper** | Automated web scraping with Chrome debug mode | [📖 README-job-scraper.md](README-job-scraper.md) |
| **AI Content Generator** | AI-powered personalized content generation | [📖 README-cover-letter.md](README-cover-letter.md) |
| **Chat AI Assistant** | Smart chat responses with BERT + GPT-2 | [📖 README-chat-ai.md](README-chat-ai.md) |
| **Database Cleanup** | Automated database maintenance | [📖 README-database-cleanup.md](README-database-cleanup.md) |

### ⚙️ **How Scripts Execute**

1. **n8n Workflow** triggers on schedule or manual activation
2. **PowerShell Script** (`run_scripts/`) executes with parameters
3. **Python/JavaScript Code** (`scripts/`, `ai/`, `js_scrapers/`) performs the actual work
4. **Database Storage** (`data/`) saves results
5. **Dashboard Generation** (`dashboard_generate/`) creates HTML reports

---

## 📁 Project Structure

```
📦 Scrape_and_AI_automation/
├── 🔄 n8n_workflow_conditional.json      # Web scraper workflow
├── 📝 n8n_ai_cover_letter_workflow.json  # AI content generator workflow  
├── 🤖 n8n_chat_ai_workflow.json          # Chat AI assistant workflow
├── 🗂️ n8n_database_cleanup_workflow.json # Database maintenance workflow
├── 🎯 install_n8n.ps1                    # One-click n8n workflow installer
│
├── 📁 run_scripts/                       # PowerShell workflow runners
│   ├── run_js_scraper.ps1               # Execute web scraping
│   ├── run_smart_cover_letter.ps1       # Generate AI content
│   ├── run_chat_scraper.ps1             # Monitor chat conversations
│   ├── run_chat_parser.ps1              # Parse chat HTML to database
│   ├── run_check_chrome_n8n.ps1         # Check scraping Chrome status (port 9222)
│   ├── run_check_chrome_chat.ps1        # Check chat Chrome status (port 9223)
│   ├── run_start_chrome_simple.ps1      # Start scraping Chrome profile
│   ├── run_start_chrome_chat_simple.ps1 # Start chat Chrome profile
│   ├── run_detect_phase_standalone.ps1  # BERT phase detection only
│   ├── run_generate_response.ps1        # Database-driven response generation
│   ├── run_save_html_to_db.ps1          # Save scraped HTML to database
│   ├── run_parse_html_only.ps1          # Parse scraped HTML
│   ├── run_import_jobs_to_db.ps1        # Import data to database
│   ├── run_get_latest_job_without_cover_letter.ps1 # Get items for AI processing
│   ├── run_generate_and_open_dashboard.ps1 # Data dashboard generator
│   └── run_generate_and_open_chat_dashboard.ps1 # Chat dashboard generator
│
├── 📁 scripts/                          # Core inference scripts (use trained models)
│   ├── phase_detector.py               # BERT phase detection (with fallback)
│   ├── smart_chat_response.py          # GPT-2 chat responses (with fallback)
│   ├── standalone_phase_detector.py    # Phase detection testing
│   ├── smart_cover_letter_generator.py # AI content generation (with fallback)
│   ├── data_parser.py                  # Parse scraped HTML data
│   └── chat_parser.py                  # Parse chat conversations
│
├── 📁 ai/                              # AI & Machine Learning
│   ├── 📁 phase_detector_trainer/      # BERT Phase Detection Training
│   │   ├── train_phase_classifier.py   # Training script (87.5% accuracy)
│   │   ├── 📁 training_data/           # 53 labeled conversations
│   │   │   └── phase_training_data.json
│   │   └── 📁 trained_models/          # Output trained BERT models
│   │       └── phase_classifier_v1/    # Production model
│   ├── 📁 chat_bot_trainer/            # GPT-2 Chat Response Training  
│   │   ├── train_chat_gpt2.py          # Training script
│   │   ├── 📁 training_data/           # 11 conversation examples
│   │   │   └── training_data_parsed.json
│   │   └── 📁 trained_models/          # Output trained GPT-2 models
│   │       └── final_chat_model/       # Production chat model
│   └── 📁 cover_letter_trainer/        # GPT-2 Cover Letter Training
│       ├── model_training.py           # Training script
│       ├── 📁 training_data/           # Cover letter templates
│       │   └── training_data.json
│       └── 📁 trained_models/          # Output cover letter models
│           └── custom_cover_letter_model/ # Production model
│
├── 📁 js_scrapers/                     # Browser automation
│   ├── browser_connect_puppeteer.js    # Web scraping (Chrome port 9222)
│   ├── browser_connect_chat.js         # Chat monitoring (Chrome port 9223)
│   └── package.json                    # Node.js dependencies
│
├── 📁 data/                            # Database management
│   ├── database_manager.py             # Main database operations
│   ├── chat_database_manager.py        # Chat database operations
│   ├── chat_data.db                    # SQLite chat database
│   └── upwork_data.db                  # Main data database
│
├── 📁 dashboard_generate/              # HTML dashboard creation
│   ├── generate_dashboard_enhanced.py  # Data dashboard with stats
│   └── chat_dashboard_generator.py     # Chat response dashboard
│
├── 📁 trained_models/                  # Additional ML models
│   └── 📁 advanced_cover_letter_model/ # Fine-tuned GPT-2 for cover letters
│       └── 📁 final/                   # Production model files
│
├── 📁 chrome_profile/                  # Scraping Chrome profile (port 9222)
├── 📁 chrome_profile_chat/             # Chat monitoring Chrome profile (port 9223)
├── 📁 n8n/                            # Generated n8n workflows (created after install_n8n.ps1)
│   ├── n8n_workflow_conditional.json  # Ready-to-import web scraper workflow
│   ├── n8n_ai_cover_letter_workflow.json # Ready-to-import content generator workflow
│   ├── n8n_chat_ai_workflow.json      # Ready-to-import chat AI workflow
│   └── n8n_database_cleanup_workflow.json # Ready-to-import cleanup workflow
├── 📁 backup_n8n_original/             # Auto-generated workflow backups
├── 📁 docs/                           # Additional documentation
├── 📁 cookies/                        # Browser session data
│
├── 📄 README-job-scraper.md           # Web scraper workflow documentation
├── 📄 README-cover-letter.md          # Content generator workflow documentation
├── 📄 README-chat-ai.md               # Chat AI workflow documentation
├── 📄 README-database-cleanup.md      # Database cleanup workflow documentation
├── 📄 README-ai-training.md           # AI training guide
├── 📄 INSTALLATION_GUIDE.md           # Complete installation instructions
├── 📄 QUICKSTART.md                   # Quick setup guide
├── 📄 PATH_INSTALLATION_GUIDE.md      # Path configuration guide
│
├── 📄 requirements.txt                 # Python dependencies
├── 📄 package.json                     # Node.js dependencies
├── 📄 upwork_jobs.db                   # Alternative data database
├── 📄 dashboard.html                   # Generated data dashboard
├── 📄 chat_dashboard.html              # Generated chat dashboard
├── 📄 temp_ai_suggestions.json         # Temporary AI response data
└── 📄 temp_selected_job.json           # Temporary selection data
```

## ⚖️ Legal Disclaimer

**IMPORTANT: Read before using this software**

### 🎯 Development Context
This project was developed as **contracted work** for a specific client under a work-for-hire agreement. The code is published for **portfolio and educational purposes only**.

### 🚫 Terms of Use
By accessing or using this code, you agree to the following terms:

1. **No Liability**: The developer(s) of this software are **NOT responsible** for:
   - How this software is used by third parties
   - Any violations of terms of service of third-party platforms
   - Data loss, account suspension, legal issues, or any damages arising from use
   - Compliance with applicable laws and regulations in your jurisdiction

2. **Use at Your Own Risk**: This software is provided "AS IS" without warranty of any kind. Users assume **full responsibility** for:
   - Compliance with platform Terms of Service
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
- Review platform Terms of Service and API usage policies
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

## 📄 License

MIT License - see LICENSE file for details.

**Note**: The MIT License applies to the code itself. It does NOT grant permission to violate any third-party terms of service or applicable laws.

