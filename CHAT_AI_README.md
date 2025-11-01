# 🤖 Chat AI Assistant Workflow

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)
![n8n](https://img.shields.io/badge/n8n-workflow-orange.svg)

**Automated Chat AI Assistant with GPT-2 Response Generation**

A complete workflow system that monitors chat conversations, generates intelligent AI responses using GPT-2, and provides an interactive dashboard for real-time assistance.

## 🎯 **What It Does**

- **🔍 Monitors Chat Conversations** - Automatically scrapes chat messages from various platforms (Upwork, LinkedIn, etc.)
- **🧠 AI Response Generation** - Uses local GPT-2 model to generate contextual response suggestions
- **📊 Interactive Dashboard** - Real-time dashboard with AI suggestions and workflow controls
- **⚡ n8n Automation** - Complete workflow automation with 10 connected nodes
- **🔄 Continuous Monitoring** - Automatic refresh and workflow continuation

## 🚀 **Quick Start**

### **1. Installation**
```powershell
# Clone the repository
git clone https://github.com/NewworldProg/WorkFlow.git
cd WorkFlow

# Run automated installation
powershell -ExecutionPolicy Bypass -File install_chat_ai_requirements.ps1
```

### **2. Setup n8n Workflow**
1. Import `n8n_chat_ai_workflow.json` into your n8n instance
2. Update file paths in workflow nodes to match your system
3. Activate the workflow

### **3. Start Monitoring**
1. Run the workflow in n8n (manual trigger)
2. Navigate to your chat page when prompted
3. View AI suggestions in the auto-opened dashboard

## 📋 **System Requirements**

- **Python 3.8+** with virtual environment
- **Node.js 16+** with npm
- **Chrome Browser** (for automation)
- **n8n** (workflow automation)
- **Windows PowerShell** (for automation scripts)

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflow │───▶│  Chrome + Chat  │───▶│ JavaScript      │
│   (10 nodes)   │    │   Page Open     │    │ Scraper         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Interactive     │◄───│   SQLite        │◄───│  Message        │
│ Dashboard       │    │   Database      │    │  Parser         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ▲                                               │
        │               ┌─────────────────┐            │
        └───────────────│  GPT-2 AI       │◄───────────┘
                        │  Generator      │
                        └─────────────────┘
```

## 🛠️ **Core Components**

### **🕷️ Chat Scraper**
- JavaScript/Puppeteer-based scraping
- Multi-platform support (Upwork, LinkedIn, generic)
- Chrome remote debugging integration

### **🧠 AI Engine**
- Local GPT-2 model (no API keys required)
- Context-aware response generation
- Multiple response types (professional, friendly, technical)

### **📊 Dashboard**
- Real-time chat monitoring
- AI response suggestions
- Copy-to-clipboard functionality
- Workflow continuation controls

### **⚙️ Database**
- SQLite for chat sessions and messages
- Temporary file system for AI suggestions
- Session management and history

## 📁 **Key Files**

- `n8n_chat_ai_workflow.json` - Complete n8n workflow
- `js_scrapers/browser_connect_chat.js` - Main chat scraper
- `ai/chat_gpt2_generator.py` - GPT-2 AI response generator
- `scripts/chat_dashboard_generator.py` - Interactive dashboard
- `data/chat_database_manager.py` - Database management

## 🎮 **Usage**

### **Basic Workflow**
1. **Start**: Trigger n8n workflow manually
2. **Navigate**: Go to your chat page when prompted (45s window)
3. **Monitor**: System automatically scrapes messages
4. **Generate**: AI creates response suggestions
5. **Use**: Copy suggested responses from dashboard
6. **Continue**: Click "Continue Workflow" for ongoing monitoring

### **Manual Commands**
```powershell
# Run individual components
.\run_chat_scraper.ps1          # Scrape current chat
.\run_chat_parser.ps1           # Parse latest HTML
.\run_chat_ai_generator.ps1     # Generate AI responses
.\run_chat_dashboard.ps1        # Open dashboard
```

## 🔧 **Configuration**

### **Chrome Setup**
- Chat monitoring: Port 9223
- Separate from job scraping (port 9222)
- Debug mode enabled

### **AI Model**
- Default: GPT-2 base model
- Configurable response types
- Context window: 10 recent messages

## 📈 **Performance**

- **Response Time**: ~2-3 seconds for AI generation
- **Accuracy**: Context-aware responses based on conversation flow
- **Scalability**: Handles multiple chat sessions
- **Storage**: SQLite database with session management

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the complete workflow
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

For issues and questions:
- Check the troubleshooting section in documentation
- Review log files in the data directory
- Ensure all dependencies are installed correctly

---

**⚡ Built with n8n, GPT-2, and JavaScript automation**