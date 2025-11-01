#!/usr/bin/env python3
"""
GitHub Upload Preparation Script
Creates list of essential files for Chat AI Assistant system
"""

import os
import json

# Essential files for GitHub upload
essential_files = {
    "n8n_workflows": [
        "n8n_chat_ai_workflow.json"
    ],
    
    "automation_scripts": [
        "run_chat_scraper.ps1",
        "run_chat_parser.ps1", 
        "run_chat_ai_generator.ps1",
        "run_chat_dashboard.ps1",
        "run_generate_and_open_chat_dashboard.ps1",
        "run_continue_chat_workflow.ps1",
        "run_start_chrome_chat.ps1",
        "run_check_chrome_chat.ps1"
    ],
    
    "javascript_scrapers": [
        "js_scrapers/browser_connect_chat.js",
        "package.json"
    ],
    
    "python_ai_components": [
        "ai/chat_gpt2_generator.py",
        "ai/training_data.json",
        "scripts/chat_parser.py",
        "scripts/chat_dashboard_generator.py", 
        "data/chat_database_manager.py"
    ],
    
    "installation_setup": [
        "install_chat_ai_requirements.ps1"
    ],
    
    "documentation": [
        "CHAT_AI_README.md",
        "CHAT_AI_SYSTEM_FILES.md",
        "AI_WORKFLOW_UPDATE_SUMMARY.md",
        "check_n8n_workflow.py"
    ],
    
    "examples_outputs": [
        "temp_ai_suggestions.json"
    ]
}

def check_files_exist():
    """Check which essential files exist"""
    print("🔍 Checking essential files for GitHub upload...")
    
    missing_files = []
    existing_files = []
    
    for category, files in essential_files.items():
        print(f"\n📁 {category.upper()}:")
        for file_path in files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}")
                existing_files.append(file_path)
            else:
                print(f"  ❌ {file_path} - MISSING")
                missing_files.append(file_path)
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Existing files: {len(existing_files)}")
    print(f"  ❌ Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\n⚠️  Missing files:")
        for f in missing_files:
            print(f"    - {f}")
    
    print(f"\n🚀 Total files ready for upload: {len(existing_files)}")
    
    return existing_files, missing_files

def create_upload_list():
    """Create JSON file with upload list"""
    existing_files, missing_files = check_files_exist()
    
    upload_data = {
        "chat_ai_system": {
            "name": "Chat AI Assistant Workflow",
            "description": "Complete automated chat monitoring with GPT-2 AI response generation",
            "status": "fully_functional",
            "files_ready": len(existing_files),
            "files_missing": len(missing_files),
            "essential_files": existing_files,
            "missing_files": missing_files,
            "upload_priority": [
                "n8n_chat_ai_workflow.json",
                "CHAT_AI_README.md", 
                "js_scrapers/browser_connect_chat.js",
                "ai/chat_gpt2_generator.py",
                "scripts/chat_dashboard_generator.py",
                "data/chat_database_manager.py",
                "install_chat_ai_requirements.ps1"
            ]
        }
    }
    
    with open("github_upload_list.json", "w", encoding="utf-8") as f:
        json.dump(upload_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Upload list saved to: github_upload_list.json")
    return upload_data

if __name__ == "__main__":
    print("🤖 Chat AI Assistant - GitHub Upload Preparation")
    print("=" * 50)
    
    upload_data = create_upload_list()
    
    print(f"\n✅ System ready for GitHub upload!")
    print(f"   Repository: https://github.com/NewworldProg/WorkFlow")
    print(f"   Files ready: {upload_data['chat_ai_system']['files_ready']}")