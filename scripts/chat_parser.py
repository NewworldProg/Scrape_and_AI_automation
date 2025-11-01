#!/usr/bin/env python3
"""
Chat Parser for n8n Workflow
Parses chat messages from HTML files saved by chat scraper
"""

import os
import sys
import json
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from data.chat_database_manager import ChatDatabase

class ChatParser:
    def __init__(self, db_path="data/chat_data.db"):
        # path to chat database
        self.db_path = os.path.join(project_root, db_path)
        # initialize database manager
        self.db = ChatDatabase(self.db_path)
    #================== functions for extracting messages for different platforms ===================
    # function for Upwork HTML 
    def parse_upwork_messages(self, soup):
        # find messages by using multiple selectors
        messages = []
        
        # Multiple selectors for Upwork messages
        selectors = [
            '[data-test*="message"]',
            '.message-item',
            '.conversation-message',
            '[class*="message"]',
            '.message-container'
        ]
        # look in each selector
        # if selector finds elements extract content
        # save elements inside message_data
        # append message_data to messages list
        # return messages list
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} messages with selector: {selector}")
                
                for element in elements:
                    message_data = self._extract_message_data(element, 'upwork')
                    if message_data:
                        messages.append(message_data)
                break
        
        return messages
    
    def parse_linkedin_messages(self, soup):
        """Parse LinkedIn chat messages"""
        messages = []
        
        selectors = [
            '.msg-s-message-list-item',
            '.message-item',
            '[data-test*="message"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    message_data = self._extract_message_data(element, 'linkedin')
                    if message_data:
                        messages.append(message_data)
                break
                
        return messages
    
    def parse_discord_messages(self, soup):
        """Parse Discord chat messages"""
        messages = []
        
        selectors = [
            '[data-list-item-id*="chat-messages"]',
            '.message-content',
            '[class*="message"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    message_data = self._extract_message_data(element, 'discord')
                    if message_data:
                        messages.append(message_data)
                break
                
        return messages
    
    def _extract_message_data(self, element, platform):
        """Extract message data from HTML element"""
        try:
            # Get text content
            text = element.get_text(strip=True)
            if not text or len(text) < 2:
                return None
            
            # Try to extract timestamp
            timestamp = self._extract_timestamp(element)
            
            # Try to extract sender
            sender = self._extract_sender(element, platform)
            
            # Try to determine message type
            message_type = self._determine_message_type(element, text)
            
            return {
                'text': text,
                'sender': sender,
                'timestamp': timestamp,
                'sender_type': message_type,  # Map to correct database column
                'platform': platform,
                'html_snippet': str(element)[:500],  # First 500 chars for debugging
                'message_id': f"{platform}_{hash(text)}_{timestamp}",  # Generate message_id
                'order': 0  # Will be set properly in save function
            }
            
        except Exception as e:
            print(f"Error extracting message data: {e}")
            return None
    # ================== functions to extract messages end ================

    # ================== functions to extract metadata from messages ===================
    # loop through common patterns to find timestamp
    # 1. find time elements
    # 2. in element look for datetime or data-time attributes
    # 3. return current time if none found
    def _extract_timestamp(self, element):
        """Try to extract timestamp from message element"""
        # Look for time elements
        time_element = element.find(['time', '[datetime]', '[data-time]'])
        if time_element:
            datetime_attr = time_element.get('datetime') or time_element.get('data-time')
            if datetime_attr:
                return datetime_attr
        
        # where is the text
        # Look for timestamp patterns in text
        text = element.get_text()
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(AM|PM)',
            r'\d{1,2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        
        return datetime.now().isoformat()
    
    # Try to extract sender/author from message element
    # 1. look for common CSS selectors
    # 2. return "unknown" if none found
    def _extract_sender(self, element, platform):
        """Try to extract sender/author from message element"""
        sender_selectors = [
            '[data-test*="author"]',
            '[data-test*="sender"]',
            '.message-author',
            '.sender-name',
            '.username',
            '[class*="author"]',
            '[class*="sender"]'
        ]
        
        for selector in sender_selectors:
            sender_element = element.select_one(selector)
            if sender_element:
                sender = sender_element.get_text(strip=True)
                if sender:
                    return sender
        
        return "unknown"
    # determine if message is incoming or outgoing
    # 1. look for common CSS selectors
    # 2. return "unknown" if none found
    def _determine_message_type(self, element, text):
        """Determine if message is incoming or outgoing"""
        # Look for CSS classes that indicate message direction
        classes = ' '.join(element.get('class', []))
        
        if any(word in classes.lower() for word in ['sent', 'outgoing', 'own', 'me']):
            return 'outgoing'
        elif any(word in classes.lower() for word in ['received', 'incoming', 'other', 'them']):
            return 'incoming'
        
        return 'unknown'
    # ================== functions to extract metadata end ===================

    # ================== functions to parse HTML files ===================
    # function to parse chat messages from HTML file
    def parse_html_file(self, html_file_path):
        # path to HTML file
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")
        
        print(f"Parsing HTML file: {html_file_path}")
        # open and read HTML content from file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # inside variable library for parsing and content of the file and where to save
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Detect platform from filename or URL in HTML
        platform = self._detect_platform_from_html(soup, html_file_path)
        print(f"Detected platform: {platform}")
        
        # Parse messages based on platform
        messages = []
        if platform == 'upwork':
            messages = self.parse_upwork_messages(soup)
        elif platform == 'linkedin':
            messages = self.parse_linkedin_messages(soup)
        elif platform == 'discord':
            messages = self.parse_discord_messages(soup)
        else:
            # Generic parsing
            messages = self.parse_generic_messages(soup)
        
        print(f"Parsed {len(messages)} messages")
        return messages, platform
    
    def parse_generic_messages(self, soup):
        """Generic message parsing for unknown platforms"""
        messages = []
        
        # Try common message selectors
        selectors = [
            '[data-test*="message"]',
            '.message',
            '.chat-message',
            '[class*="message"]',
            'p', 'div[class*="text"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 0:
                print(f"Using generic selector: {selector} ({len(elements)} elements)")
                for element in elements:
                    message_data = self._extract_message_data(element, 'generic')
                    if message_data and len(message_data['text']) > 10:  # Filter out very short texts
                        messages.append(message_data)
                
                if messages:  # If we found messages, stop trying other selectors
                    break
        
        return messages
    
    def _detect_platform_from_html(self, soup, file_path):
        """Detect platform from HTML content or filename"""
        html_text = soup.get_text().lower()
        file_name = os.path.basename(file_path).lower()
        
        if 'upwork' in html_text or 'upwork' in file_name:
            return 'upwork'
        elif 'linkedin' in html_text or 'linkedin' in file_name:
            return 'linkedin'
        elif 'discord' in html_text or 'discord' in file_name:
            return 'discord'
        elif 'teams' in html_text or 'teams' in file_name:
            return 'teams'
        elif 'slack' in html_text or 'slack' in file_name:
            return 'slack'
        
        return 'unknown'
    
    def save_to_database(self, messages, platform, session_id=None):
        """Save parsed messages to database"""
        if not session_id:
            session_id = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save chat session - match database schema exactly
        session_data = {
            'session_id': session_id,
            'platform': platform,  # This maps to chat_platform in database
            'title': f"{platform.title()} Chat Session",
            'participant': 'Unknown',
            'url': '',
            'started_at': datetime.now(),
            'total_messages': len(messages)
        }
        
        try:
            print(f"Attempting to save session with data: {session_data}")
            result = self.db.save_chat_session(session_data)
            print(f"Session saved successfully: {result}")
        except Exception as e:
            print(f"Error saving session: {e}")
            import traceback
            traceback.print_exc()
        
        # Save messages
        for i, message in enumerate(messages):
            message['session_id'] = session_id
            message['order'] = i + 1  # Set message order
        
        try:
            self.db.save_chat_messages(session_id, messages)
            print(f"Messages saved: {len(messages)}")
        except Exception as e:
            print(f"Error saving messages: {e}")
        
        print(f"Saved {len(messages)} messages to database with session_id: {session_id}")
        return session_id
    
    def process_latest_html(self):
        """Process the most recent HTML file in data directory"""
        data_dir = os.path.join(project_root, 'data')
        html_files = [f for f in os.listdir(data_dir) if f.startswith('chat_raw_') and f.endswith('.html')]
        
        if not html_files:
            print("No chat HTML files found")
            return None
        
        # Get most recent file
        latest_file = max(html_files, key=lambda f: os.path.getctime(os.path.join(data_dir, f)))
        html_path = os.path.join(data_dir, latest_file)
        
        print(f"Processing latest HTML file: {latest_file}")
        
        # Parse messages
        messages, platform = self.parse_html_file(html_path)
        
        if messages:
            # Save to database
            session_id = self.save_to_database(messages, platform)
            
            # Create result
            result = {
                'success': True,
                'html_file': latest_file,
                'platform': platform,
                'messages_count': len(messages),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'messages': messages[:5]  # Include first 5 messages in result
            }
        else:
            result = {
                'success': False,
                'error': 'No messages found',
                'html_file': latest_file,
                'platform': platform,
                'timestamp': datetime.now().isoformat()
            }
        
        print(json.dumps(result, indent=2))
        return result

def main():
    parser = argparse.ArgumentParser(description='Parse chat messages from HTML')
    parser.add_argument('--html-file', help='Specific HTML file to parse')
    parser.add_argument('--latest', action='store_true', help='Process latest HTML file')
    
    args = parser.parse_args()
    
    chat_parser = ChatParser()
    
    try:
        if args.html_file:
            messages, platform = chat_parser.parse_html_file(args.html_file)
            session_id = chat_parser.save_to_database(messages, platform)
            print(f"Processed {len(messages)} messages from {args.html_file}")
        else:
            # Process latest by default
            result = chat_parser.process_latest_html()
            
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()