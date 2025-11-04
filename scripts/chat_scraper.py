"""
Chat Scraper for Chat AI Assistant
Connects to Chrome and scrapes chat data
"""
import sys
import os
import argparse
import json
import hashlib
import time
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from data.chat_database_manager import ChatDatabase

class ChatScraper:
    def __init__(self, debug_port=9223):
        self.debug_port = debug_port
        self.db = ChatDatabase()
        self.driver = None
        
    def connect_to_browser(self):
        """Connect to existing Chrome browser"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"✅ Connected to Chrome on port {self.debug_port}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Chrome: {e}")
            return False
    
    def detect_platform(self, url):
        """Detect chat platform from URL"""
        url_lower = url.lower()
        
        if 'upwork.com' in url_lower:
            return 'upwork'
        elif 'freelancer.com' in url_lower:
            return 'freelancer'
        elif 'fiverr.com' in url_lower:
            return 'fiverr'
        elif 'discord.com' in url_lower:
            return 'discord'
        elif 'slack.com' in url_lower:
            return 'slack'
        elif 'teams.microsoft.com' in url_lower:
            return 'teams'
        elif 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'telegram' in url_lower:
            return 'telegram'
        else:
            return 'unknown'
    
    def scrape_chat_data(self):
        """Main chat scraping function"""
        try:
            current_url = self.driver.current_url
            platform = self.detect_platform(current_url)
            
            print(f"Current URL: {current_url}")
            print(f"Detected platform: {platform}")
            
            # Get page HTML
            html_content = self.driver.page_source
            
            # Generate session ID from URL
            session_id = hashlib.md5(current_url.encode()).hexdigest()[:12]
            
            # Save raw HTML
            raw_id = self.db.save_raw_chat_html(session_id, html_content, current_url)
            print(f"Raw HTML saved with ID: {raw_id}")
            
            # Parse chat based on platform
            chat_data = self.parse_chat_by_platform(platform)
            
            if chat_data:
                # Save session
                session_data = {
                    'session_id': session_id,
                    'platform': platform,
                    'title': chat_data.get('title', 'Unknown Chat'),
                    'participant': chat_data.get('participant', 'Unknown'),
                    'url': current_url,
                    'started_at': datetime.now(),
                    'total_messages': len(chat_data.get('messages', []))
                }
                
                self.db.save_chat_session(session_data)
                print(f"Session saved: {session_id}")
                
                # Save messages
                if chat_data.get('messages'):
                    saved_count = self.db.save_chat_messages(session_id, chat_data['messages'])
                    print(f"Saved {saved_count} new messages")
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'platform': platform,
                    'title': chat_data.get('title'),
                    'participant': chat_data.get('participant'),
                    'messages_count': len(chat_data.get('messages', [])),
                    'messages_saved': saved_count,
                    'raw_id': raw_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to parse chat data',
                    'platform': platform,
                    'raw_id': raw_id
                }
                
        except Exception as e:
            print(f"Scraping error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_chat_by_platform(self, platform):
        """Parse chat based on detected platform"""
        try:
            if platform == 'upwork':
                return self.parse_upwork_chat()
            elif platform == 'discord':
                return self.parse_discord_chat()
            elif platform == 'linkedin':
                return self.parse_linkedin_chat()
            else:
                return self.parse_generic_chat()
                
        except Exception as e:
            print(f"❌ Parse error for {platform}: {e}")
            return None
    
    def parse_upwork_chat(self):
        """Parse Upwork chat specifically"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Get chat title
            try:
                title_selectors = [
                    "[data-test='room-header-title']",
                    ".room-header h1",
                    ".message-thread-header h1",
                    "h1"
                ]
                
                chat_title = "Upwork Chat"
                for selector in title_selectors:
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if title_element.text.strip():
                            chat_title = title_element.text.strip()
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception:
                chat_title = "Upwork Chat"
            
            # Get participant name
            try:
                participant_selectors = [
                    "[data-test='room-header-subtitle']",
                    ".room-header .subtitle",
                    ".participant-name"
                ]
                
                participant = "Unknown"
                for selector in participant_selectors:
                    try:
                        participant_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if participant_element.text.strip():
                            participant = participant_element.text.strip()
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception:
                participant = "Unknown"
            
            # Get messages
            messages = []
            try:
                message_selectors = [
                    "[data-test='message']",
                    ".message",
                    ".chat-message",
                    ".message-item"
                ]
                
                message_elements = []
                for selector in message_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            message_elements = elements
                            break
                    except NoSuchElementException:
                        continue
                
                print(f"🔍 Found {len(message_elements)} message elements")
                
                for i, msg_elem in enumerate(message_elements[-20:]):  # Last 20 messages
                    try:
                        # Get sender
                        sender_selectors = [
                            "[data-test='message-author']",
                            ".message-author",
                            ".sender-name",
                            ".author"
                        ]
                        
                        sender = "Unknown"
                        for selector in sender_selectors:
                            try:
                                sender_elem = msg_elem.find_element(By.CSS_SELECTOR, selector)
                                if sender_elem.text.strip():
                                    sender = sender_elem.text.strip()
                                    break
                            except NoSuchElementException:
                                continue
                        
                        # Get message text
                        text_selectors = [
                            "[data-test='message-text']",
                            ".message-text",
                            ".message-content",
                            ".text-content"
                        ]
                        
                        message_text = ""
                        for selector in text_selectors:
                            try:
                                text_elem = msg_elem.find_element(By.CSS_SELECTOR, selector)
                                if text_elem.text.strip():
                                    message_text = text_elem.text.strip()
                                    break
                            except NoSuchElementException:
                                continue
                        
                        # Fallback: get any text from message element
                        if not message_text:
                            message_text = msg_elem.text.strip()
                        
                        if not message_text:
                            continue
                        
                        # Get timestamp
                        timestamp = datetime.now().isoformat()
                        try:
                            time_selectors = [
                                "[data-test='message-time']",
                                ".message-time",
                                ".timestamp",
                                "time"
                            ]
                            
                            for selector in time_selectors:
                                try:
                                    time_elem = msg_elem.find_element(By.CSS_SELECTOR, selector)
                                    timestamp = time_elem.get_attribute('title') or time_elem.text or timestamp
                                    break
                                except NoSuchElementException:
                                    continue
                        except Exception:
                            pass
                        
                        # Determine sender type
                        sender_type = 'user' if any(word in sender.lower() for word in ['you', 'me', 'myself']) else 'other'
                        
                        messages.append({
                            'message_id': f"{hashlib.md5(f'{sender}_{message_text}_{i}'.encode()).hexdigest()[:12]}",
                            'sender': sender,
                            'sender_type': sender_type,
                            'text': message_text,
                            'timestamp': timestamp,
                            'order': i
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Error parsing message {i}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error finding messages: {e}")
            
            return {
                'title': chat_title,
                'participant': participant,
                'messages': messages,
                'started_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Upwork parse error: {e}")
            return None
    
    def parse_generic_chat(self):
        """Generic chat parser for unknown platforms"""
        try:
            # Get page title
            chat_title = self.driver.title or "Unknown Chat"
            
            # Try to find any text that looks like messages
            messages = []
            
            # Look for common message patterns
            possible_selectors = [
                ".message", ".chat-message", ".msg", "[class*='message']",
                ".conversation .text", ".chat .content", "[role='listitem']",
                "div[class*='text']", "div[class*='content']"
            ]
            
            message_elements = []
            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        message_elements.extend(elements)
                except Exception:
                    continue
            
            # Remove duplicates and filter
            seen_texts = set()
            for i, elem in enumerate(message_elements[-20:]):  # Last 20 elements
                try:
                    text = elem.text.strip()
                    if (len(text) > 5 and len(text) < 1000 and 
                        text not in seen_texts and
                        not any(word in text.lower() for word in ['cookie', 'privacy', 'policy', 'login', 'signup'])):
                        
                        seen_texts.add(text)
                        
                        messages.append({
                            'message_id': f"generic_{hashlib.md5(text.encode()).hexdigest()[:12]}",
                            'sender': 'Unknown',
                            'sender_type': 'other',
                            'text': text,
                            'timestamp': datetime.now().isoformat(),
                            'order': len(messages)
                        })
                        
                        if len(messages) >= 10:  # Limit to 10 messages
                            break
                            
                except Exception:
                    continue
            
            return {
                'title': chat_title,
                'participant': 'Unknown',
                'messages': messages,
                'started_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Generic parse error: {e}")
            return None
    
    def parse_linkedin_chat(self):
        """Parse LinkedIn messages"""
        try:
            chat_title = "LinkedIn Messages"
            participant = "LinkedIn Contact"
            
            # LinkedIn specific selectors
            messages = []
            try:
                msg_selectors = [
                    ".msg-s-message-list-item",
                    ".message-item",
                    "[data-test-id*='message']"
                ]
                
                for selector in msg_selectors:
                    try:
                        message_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if message_elements:
                            break
                    except Exception:
                        continue
                
                for i, msg_elem in enumerate(message_elements[-15:]):
                    try:
                        text = msg_elem.text.strip()
                        if len(text) > 5:
                            messages.append({
                                'message_id': f"linkedin_{i}_{int(time.time())}",
                                'sender': 'Contact',
                                'sender_type': 'other',
                                'text': text,
                                'timestamp': datetime.now().isoformat(),
                                'order': i
                            })
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"❌ LinkedIn messages parse error: {e}")
            
            return {
                'title': chat_title,
                'participant': participant,
                'messages': messages,
                'started_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ LinkedIn parse error: {e}")
            return None
    
    def close(self):
        """Close browser connection"""
        if self.driver:
            print("🔗 Disconnecting from browser (browser stays open)")
            self.driver.quit()

def main():
    """Main chat scraping function"""
    parser = argparse.ArgumentParser(description='Chat Scraper for AI Assistant')
    parser.add_argument('--port', type=int, default=9223, help='Chrome debug port')
    args = parser.parse_args()
    
    try:
        scraper = ChatScraper(debug_port=args.port)
        
        # Connect to existing browser
        if not scraper.connect_to_browser():
            result = {
                'success': False,
                'error': 'Failed to connect to browser',
                'port': args.port
            }
            print(json.dumps(result))
            return False
        
        # Wait a moment for page to stabilize
        time.sleep(2)
        
        # Scrape chat data
        result = scraper.scrape_chat_data()
        
        # Print result for n8n
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result.get('success', False)
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(result))
        return False
        
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)