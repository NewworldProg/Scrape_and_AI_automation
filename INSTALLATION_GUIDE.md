# 📦 Installation Guide - Upwork AI Automation System

## ✅ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 5 GB free | 10 GB free |
| **Python** | 3.8+ | 3.10+ |
| **Node.js** | 16+ | 18+ |
| **GPU** | Not required | CUDA GPU (for faster training) |

---

## 🚀 Installation Steps

### **1. Clone Repository**

```powershell
# Clone to any directory you want
git clone https://github.com/NewworldProg/WorkFlow.git
cd WorkFlow
```

**⚠️ Important:** You can install this in **ANY directory** - all scripts use `$PSScriptRoot` for portability!

---

### **2. Install Python Dependencies**

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install all required packages
pip install -r requirements.txt

# Or use the automated installer
powershell -ExecutionPolicy Bypass -File install_chat_ai_requirements.ps1
```

**Installed packages include:**
- `torch` (PyTorch for ML)
- `transformers` (BERT + GPT-2)
- `scikit-learn` (ML utilities)
- `selenium` / `beautifulsoup4` (Web scraping)
- `openai` (Optional: OpenAI API integration)

**Total size:** ~2-3 GB (including PyTorch)

---

### **3. Install Node.js Dependencies**

```powershell
# Install Puppeteer and other Node packages
npm install
```

**Total size:** ~250 MB (including Chromium binary)

---

### **4. Setup Chrome for Automation**

The system uses **2 separate Chrome instances**:

#### **Instance 1: Job Scraping (Port 9222)**
```powershell
.\run_start_chrome_simple.ps1
```
- Opens Chrome on port `9222`
- Creates `chrome_profile/` folder automatically
- Used by: `n8n_workflow_conditional.json`

#### **Instance 2: Chat Monitoring (Port 9223)**
```powershell
.\run_start_chrome_chat_simple.ps1
```
- Opens Chrome on port `9223`
- Creates `chrome_profile_chat/` folder automatically
- Used by: `n8n_chat_ai_workflow.json`

**⚠️ Chrome Path Detection:**
Scripts automatically detect Chrome in these locations:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
- `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`

If your Chrome is in a different location, edit the script manually.

---

### **5. Setup n8n Workflows**

#### **Install n8n (if not already installed):**
```powershell
npm install -g n8n
```

#### **Start n8n:**
```powershell
n8n start
```
Access at: `http://localhost:5678`

#### **Import Workflows:**

1. Open n8n web interface
2. Go to **Workflows** → **Import from File**
3. Import these 3 workflows:
   - `n8n_chat_ai_workflow.json` (Chat AI Assistant)
   - `n8n_ai_cover_letter_workflow.json` (Cover Letter Generator)
   - `n8n_workflow_conditional.json` (Job Scraper)

#### **⚠️ Important: Update File Paths in n8n**

After importing, update **ALL Execute Command nodes** with your actual paths:

**Find & Replace in each workflow:**
- Old: `E:\Repoi\UpworkNotif\`
- New: `YOUR_ACTUAL_PATH\` (e.g., `C:\Users\YourName\WorkFlow\`)

**Example nodes to update:**
- "Execute: Start Chrome" → Update path to `run_start_chrome_simple.ps1`
- "Execute: Scrape Chat" → Update path to `run_chat_scraper.ps1`
- "Execute: AI Response" → Update path to `run_smart_chat_response.ps1`

**Tip:** Use n8n's **Search & Replace** feature:
1. Open workflow
2. Click workflow settings (3 dots)
3. Search for `E:\Repoi\UpworkNotif`
4. Replace with your actual path

---

### **6. Train ML Models (Optional)**

The system uses **pre-trained models** from Hugging Face, but you can train custom models:

#### **Train Phase Classifier (BERT):**
```powershell
.\run_train_phase_classifier.ps1
```
- Trains on `ai/phase_training_data.json`
- Saves to `ai/trained_models/phase_classifier_v1/`
- Training time: ~5-10 minutes (CPU), ~2 minutes (GPU)

#### **Train Chat GPT-2 (Optional):**
```powershell
python ai/train_chat_gpt2.py --data ai/training_data.txt --epochs 3
```
- Fine-tunes GPT-2 on your conversation data
- Training time: ~30-60 minutes (CPU), ~10 minutes (GPU)

---

### **7. Configuration Files**

#### **Update Database Paths (if needed):**

All scripts use **relative paths** by default:
```python
# In Python scripts
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chat_data.db')
```

#### **Environment Variables (Optional):**

Create `.env` file for API keys:
```
OPENAI_API_KEY=your_openai_key_here
MONGODB_URI=your_mongodb_uri_here
```

---

## 🧪 Testing Installation

### **Test Chrome Automation:**
```powershell
.\run_check_chrome_chat.ps1
.\run_check_chrome_n8n.ps1
```
Should output: `Chrome is running on port XXXX`

### **Test AI System:**
```powershell
# Test phase detection
python ai/test_trained_model.py

# Test chat response generation
.\run_smart_chat_response.ps1
```

### **Test n8n Workflows:**
1. Activate each workflow in n8n
2. Trigger manually (click "Execute Workflow")
3. Check execution logs for errors

---

## 📂 Project Structure After Installation

```
WorkFlow/
├── venv/                    # Python virtual environment (~1.2 GB)
├── node_modules/            # Node.js packages (~250 MB)
├── chrome_profile/          # Chrome data (auto-created)
├── chrome_profile_chat/     # Chrome chat data (auto-created)
├── data/                    # Databases (auto-created)
│   ├── chat_data.db
│   ├── upwork_data.db
│   └── upwork_jobs.db
├── ai/
│   └── trained_models/      # ML models
│       └── phase_classifier_v1/  # BERT model (~440 MB)
├── run_*.ps1                # All scripts (portable!)
└── README.md
```

**Total installed size:** ~3-4 GB (without training checkpoints)

---

## 🔧 Troubleshooting

### **Issue: "Chrome not found"**
**Solution:** Install Chrome or update script with your Chrome path:
```powershell
# Edit run_start_chrome_simple.ps1
$chrome = "C:\Your\Custom\Path\chrome.exe"
```

### **Issue: "pip install fails"**
**Solution:** Install Visual C++ Build Tools:
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++"

### **Issue: "n8n workflow fails"**
**Solution:** Update all file paths in workflow nodes to match your installation directory.

### **Issue: "Module not found" in Python**
**Solution:** Activate virtual environment first:
```powershell
.\venv\Scripts\Activate.ps1
```

### **Issue: "Port already in use"**
**Solution:** Kill existing Chrome process:
```powershell
Get-Process chrome | Stop-Process -Force
```

---

## 🎯 Quick Start Summary

```powershell
# 1. Clone & Navigate
git clone https://github.com/NewworldProg/WorkFlow.git
cd WorkFlow

# 2. Install Dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install

# 3. Start Chrome Instances
.\run_start_chrome_simple.ps1      # Port 9222 (job scraping)
.\run_start_chrome_chat_simple.ps1 # Port 9223 (chat)

# 4. Setup n8n
npm install -g n8n
n8n start
# Import workflows and update paths

# 5. Test
.\run_check_chrome_chat.ps1
.\run_smart_chat_response.ps1
```

---

## 📞 Support

- **GitHub Issues:** [Report problems](../../issues)
- **Documentation:** [README.md](README.md)
- **Legal:** [See Legal Disclaimer in README](README.md#-legal-disclaimer)

---

## ✅ Installation Complete!

Once everything is set up, you can:
- ✅ Run automated job scraping
- ✅ Generate AI-powered chat responses
- ✅ Create personalized cover letters
- ✅ Monitor conversations with ML phase detection

**🚀 All scripts work from ANY directory - fully portable!**

---

**Version:** 3.0  
**Last Updated:** 2025-11-05  
**Tested On:** Windows 10/11, Python 3.8-3.11, Node.js 16-18
