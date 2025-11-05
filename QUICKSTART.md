# ⚡ Quick Start Guide - 5 Minutes Setup

## 🎯 For First-Time Users (GitHub ZIP Download)

### **Step 1: Download & Extract** (30 seconds)

1. Go to: https://github.com/NewworldProg/WorkFlow
2. Click **Code** → **Download ZIP**
3. Extract to any folder (e.g., `C:\Projects\WorkFlow`)
4. Open **PowerShell** in that folder:
   - Right-click folder → **Open in Terminal**
   - Or: `cd C:\Projects\WorkFlow`

---

### **Step 2: Install Python Dependencies** (5-10 minutes)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install all packages
pip install -r requirements.txt
```

**⏱️ Installation time:** 
- Without GPU: ~5-7 minutes
- With CUDA GPU: ~8-10 minutes (downloads CUDA version)

**💾 Disk space needed:** ~2-3 GB (PyTorch is large)

---

### **Step 3: Install Node.js Dependencies** (2-3 minutes)

```powershell
npm install
```

**⏱️ Installation time:** ~2-3 minutes  
**💾 Disk space:** ~250 MB (includes Chromium for Puppeteer)

---

### **Step 4: Start Chrome Automation** (10 seconds)

```powershell
# Start first Chrome instance (job scraping - port 9222)
.\run_start_chrome_simple.ps1

# Start second Chrome instance (chat monitoring - port 9223)
.\run_start_chrome_chat_simple.ps1
```

**✅ Expected result:**
- Two Chrome windows open
- Console shows: `Chrome started with profile: ...`

---

### **Step 5: Setup n8n Workflows** (5 minutes)

#### **A) Install n8n:**
```powershell
npm install -g n8n
```

#### **B) Start n8n:**
```powershell
n8n start
```
- Opens at: http://localhost:5678
- Create account (first-time only)

#### **C) Import Workflows:**

1. In n8n web interface: **Workflows** → **Import from File**
2. Import these 3 files:
   - `n8n_chat_ai_workflow.json`
   - `n8n_ai_cover_letter_workflow.json`
   - `n8n_workflow_conditional.json`

#### **D) Update Paths in Workflows:**

⚠️ **CRITICAL STEP** - Update file paths in all workflows:

**For EACH imported workflow:**
1. Open workflow
2. Find all **Execute Command** nodes (yellow boxes)
3. Click each node
4. Update the **Command** field:
   - Find: `E:\Repoi\UpworkNotif\`
   - Replace with: `YOUR_ACTUAL_PATH\` (e.g., `C:\Projects\WorkFlow\`)

**Example nodes to update:**
```powershell
# Before:
powershell -File "E:\Repoi\UpworkNotif\run_smart_chat_response.ps1"

# After:
powershell -File "C:\Projects\WorkFlow\run_smart_chat_response.ps1"
```

**🔧 Shortcut - Use Find & Replace:**
1. Click workflow settings (3 dots top-right)
2. Search: `E:\Repoi\UpworkNotif`
3. Replace: `C:\Projects\WorkFlow` (your actual path)
4. Replace All

#### **E) Activate Workflows:**
- Toggle **Active** switch for each workflow

---

### **Step 6: Test Everything** (2 minutes)

#### **Test 1: Chrome is running**
```powershell
.\run_check_chrome_chat.ps1
.\run_check_chrome_n8n.ps1
```
✅ Should output: `Chrome is running on port XXXX`

#### **Test 2: AI system works**
```powershell
.\run_smart_chat_response.ps1
```
✅ Should generate dashboard: `chat_dashboard.html`

#### **Test 3: n8n workflows**
1. Go to n8n: http://localhost:5678
2. Open `Chat AI Workflow`
3. Click **Execute Workflow**
4. Check execution log (should be green ✅)

---

## ✅ Setup Complete!

### **What You Can Do Now:**

1. **Automatic Job Scraping**
   - Workflow: `n8n_workflow_conditional.json`
   - Runs: Every 2 hours
   - Scrapes Upwork jobs → saves to database

2. **AI Chat Responses**
   - Workflow: `n8n_chat_ai_workflow.json`
   - Runs: Every 5 minutes
   - Monitors chat → generates AI responses → shows dashboard

3. **Cover Letter Generation**
   - Workflow: `n8n_ai_cover_letter_workflow.json`
   - Runs: Every 5 minutes
   - Fetches jobs without cover letters → generates AI cover letters

### **View Results:**

```powershell
# Open chat dashboard
.\run_generate_and_open_chat_dashboard.ps1

# Open job dashboard
.\run_generate_and_open_dashboard.ps1
```

---

## 🆘 Common Issues

### **Issue: "pip: command not found"**
**Fix:** Install Python 3.8+ from https://python.org
- ✅ Check "Add Python to PATH" during installation

### **Issue: "npm: command not found"**
**Fix:** Install Node.js 16+ from https://nodejs.org

### **Issue: "Chrome not found"**
**Fix:** Install Google Chrome from https://google.com/chrome

### **Issue: "cannot be loaded because running scripts is disabled"**
**Fix:** Enable PowerShell scripts:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Issue: n8n workflow fails with "path not found"**
**Fix:** You forgot Step 5D - update paths in workflow nodes!

### **Issue: "Module not found" in Python**
**Fix:** Activate virtual environment first:
```powershell
.\venv\Scripts\Activate.ps1
```

---

## 📚 Full Documentation

- **Complete Setup:** [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- **System Architecture:** [README.md](README.md)
- **Legal Information:** [README.md#legal-disclaimer](README.md#-legal-disclaimer)

---

## ⏱️ Total Setup Time

| Step | Time | Difficulty |
|------|------|-----------|
| Download & Extract | 30 sec | ⭐ Easy |
| Python Install | 5-10 min | ⭐⭐ Medium |
| Node.js Install | 2-3 min | ⭐ Easy |
| Chrome Setup | 10 sec | ⭐ Easy |
| n8n Workflows | 5 min | ⭐⭐⭐ Advanced |
| Testing | 2 min | ⭐⭐ Medium |
| **TOTAL** | **~15-20 min** | ⭐⭐ Medium |

**💡 Tip:** The hardest part is updating n8n workflow paths (Step 5D). Take your time!

---

## 🎯 Next Steps

Once setup is complete:
1. ✅ Login to Upwork in both Chrome instances
2. ✅ Let workflows run for 1 hour
3. ✅ Check dashboards for results
4. ✅ Customize AI responses in `ai/phase_training_data.json`
5. ✅ Train custom models with your data

---

**🚀 Ready to automate your Upwork workflow!**

**Version:** 3.0  
**Updated:** 2025-11-05
