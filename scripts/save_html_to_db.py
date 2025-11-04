"""
Script to save latest raw HTML file to database
Called from n8n workflow after JS scraper
"""
import sys
import os
import json
from datetime import datetime

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.database_manager import UpworkDatabase

def save_latest_html_to_db():
    """Find latest HTML file and save to database"""
    try:
        # Initialize database
        db = UpworkDatabase()
        
        # Look for latest HTML file in data_raw
        data_raw_dir = os.path.join("data", "data_raw")
        
        if not os.path.exists(data_raw_dir):
            print(f"❌ Directory {data_raw_dir} does not exist")
            return {"success": False, "error": "data_raw directory not found"}
        
        # Find latest HTML file
        html_files = [f for f in os.listdir(data_raw_dir) if f.endswith('.html')]
        
        if not html_files:
            print("❌ No HTML files found in data_raw")
            return {"success": False, "error": "No HTML files found"}
        
        # Get the latest file by modification time
        latest_file = None
        latest_time = 0
        
        for filename in html_files:
            filepath = os.path.join(data_raw_dir, filename)
            mtime = os.path.getmtime(filepath)
            if mtime > latest_time:
                latest_time = mtime
                latest_file = filename
        
        if not latest_file:
            print("❌ Could not determine latest file")
            return {"success": False, "error": "Could not find latest file"}
        
        # Read the HTML content
        latest_filepath = os.path.join(data_raw_dir, latest_file)
        
        with open(latest_filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Estimate content quality
        content_length = len(html_content)
        has_job_content = 'job-tile' in html_content or 'job' in html_content.lower()
        
        # Save to database
        scrape_id = db.add_scraped_data(
            scrape_type="browser",
            source_url="https://www.upwork.com/search/jobs/",
            raw_content=html_content,
            file_path=latest_filepath,
            notes=f"Browser scrape from {latest_file} - {content_length} chars"
        )
        
        print(f"✅ HTML saved to database with scrape_id: {scrape_id}")
        print(f"📁 File: {latest_file}")
        print(f"📊 Content length: {content_length:,} characters")
        print(f"🔍 Contains job content: {has_job_content}")
        
        result = {
            "success": True,
            "scrape_id": scrape_id,
            "filename": latest_file,
            "content_length": content_length,
            "has_job_content": has_job_content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Return JSON for n8n
        print(json.dumps(result))
        return result
        
    except Exception as e:
        error_msg = f"Error saving HTML to database: {str(e)}"
        print(f"❌ {error_msg}")
        result = {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result))
        return result

if __name__ == "__main__":
    save_latest_html_to_db()