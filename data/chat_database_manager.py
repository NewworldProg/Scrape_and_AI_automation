"""
Chat Database Manager for Chat AI Assistant
Manages chat sessions, messages, and AI responses
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ChatDatabase:
    def __init__(self, db_path: str = "chat_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize chat database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                chat_platform TEXT,
                chat_title TEXT,
                participant_name TEXT,
                chat_url TEXT,
                started_at DATETIME,
                last_activity DATETIME,
                total_messages INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                phase TEXT,
                phase_confidence REAL,
                phase_updated_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message_id TEXT UNIQUE,
                sender TEXT,
                sender_type TEXT,
                message_text TEXT,
                timestamp DATETIME,
                message_order INTEGER,
                scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        # Raw chat HTML data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_chat_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                html_content TEXT,
                page_url TEXT,
                scrape_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                content_length INTEGER,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        # GPT-2 AI responses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpt2_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                context_messages TEXT,
                generated_response TEXT,
                response_type TEXT,
                confidence_score REAL,
                model_version TEXT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[OK] Chat database initialized")
    
    def save_raw_chat_html(self, session_id: str, html_content: str, page_url: str) -> int:
        """Save raw chat HTML"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO raw_chat_data (session_id, html_content, page_url, content_length)
            VALUES (?, ?, ?, ?)
        ''', (session_id, html_content, page_url, len(html_content)))
        
        raw_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return raw_id
    
    def save_chat_session(self, session_data: Dict) -> str:
        """Save or update chat session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO chat_sessions 
            (session_id, chat_platform, chat_title, participant_name, chat_url,
             started_at, last_activity, total_messages, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data['session_id'],
            session_data.get('platform', 'unknown'),
            session_data.get('title', 'Unknown Chat'),
            session_data.get('participant', 'Unknown'),
            session_data.get('url', ''),
            session_data.get('started_at', datetime.now()),
            datetime.now(),
            session_data.get('total_messages', 0),
            'active'
        ))
        
        conn.commit()
        conn.close()
        
        return session_data['session_id']
    
    def save_chat_messages(self, session_id: str, messages: List[Dict]) -> int:
        """Save chat messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for msg in messages:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO chat_messages 
                    (session_id, message_id, sender, sender_type, message_text, 
                     timestamp, message_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    msg['message_id'],
                    msg['sender'],
                    msg['sender_type'],
                    msg['text'],
                    msg['timestamp'],
                    msg['order']
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as e:
                print(f"⚠️ Error saving message: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return saved_count
    
    def get_latest_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get latest messages from chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sender, sender_type, message_text, timestamp, message_order
            FROM chat_messages 
            WHERE session_id = ?
            ORDER BY message_order DESC
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row[0],
                'sender_type': row[1],
                'text': row[2],
                'timestamp': row[3],
                'order': row[4]
            })
        
        conn.close()
        return messages
    
    def get_latest_session(self) -> Optional[Dict]:
        """Get most recent active session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, chat_platform, chat_title, participant_name, 
                   last_activity, total_messages, chat_url
            FROM chat_sessions 
            WHERE status = 'active'
            ORDER BY last_activity DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'session_id': row[0],
                'platform': row[1],
                'title': row[2],
                'participant': row[3],
                'last_activity': row[4],
                'total_messages': row[5],
                'url': row[6]
            }
        return None
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_text, sender, timestamp, sender_type
            FROM chat_messages 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'text': row[0],
                'sender': row[1],
                'timestamp': row[2],
                'sender_type': row[3]
            })
        
        return list(reversed(messages))  # Return in chronological order
    
    def save_gpt2_response(self, session_id: str, response_data: Dict) -> int:
        """Save GPT-2 generated response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gpt2_responses 
            (session_id, context_messages, generated_response, response_type,
             confidence_score, model_version)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            json.dumps(response_data.get('context', [])),
            response_data['response'],
            response_data.get('type', 'general'),
            response_data.get('confidence', 0.7),
            response_data.get('model_version', 'gpt2-chat-v1')
        ))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return response_id
    
    def get_dashboard_data(self) -> Dict:
        """Get data for chat dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Active sessions
        cursor.execute('''
            SELECT cs.session_id, cs.chat_platform, cs.chat_title, 
                   cs.participant_name, cs.last_activity, cs.total_messages,
                   COUNT(cm.id) as recent_messages
            FROM chat_sessions cs
            LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
                AND cm.scraped_at > datetime('now', '-1 hour')
            WHERE cs.status = 'active'
            GROUP BY cs.session_id
            ORDER BY cs.last_activity DESC
            LIMIT 5
        ''')
        
        active_sessions = [
            {
                'session_id': row[0],
                'platform': row[1],
                'title': row[2],
                'participant': row[3],
                'last_activity': row[4],
                'total_messages': row[5],
                'recent_messages': row[6]
            }
            for row in cursor.fetchall()
        ]
        
        # Recent GPT-2 responses
        cursor.execute('''
            SELECT session_id, generated_response, response_type, 
                   confidence_score, model_version, generated_at, used
            FROM gpt2_responses
            ORDER BY generated_at DESC
            LIMIT 10
        ''')
        
        recent_responses = [
            {
                'session_id': row[0],
                'response': row[1][:150] + '...' if len(row[1]) > 150 else row[1],
                'type': row[2],
                'confidence': row[3],
                'model_version': row[4],
                'generated_at': row[5],
                'used': row[6]
            }
            for row in cursor.fetchall()
        ]
        
        # Statistics
        cursor.execute('SELECT COUNT(*) FROM chat_sessions WHERE status = "active"')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        total_messages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM gpt2_responses')
        total_ai_responses = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM gpt2_responses WHERE used = 1')
        used_responses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'active_sessions': active_sessions,
            'recent_responses': recent_responses,
            'stats': {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_ai_responses': total_ai_responses,
                'used_responses': used_responses
            }
        }
    
    def update_session_phase(self, session_id: str, phase: str, confidence: float) -> bool:
        """Update session with detected phase"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE chat_sessions 
                SET phase = ?, phase_confidence = ?, phase_updated_at = ?
                WHERE session_id = ?
            ''', (phase, confidence, datetime.now(), session_id))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                print(f"[DB] Updated session {session_id} with phase: {phase} ({confidence:.1%})")
                return True
            else:
                print(f"[DB WARN] Session {session_id} not found for phase update")
                return False
                
        except Exception as e:
            print(f"[DB ERROR] Failed to update phase: {e}")
            return False
    
    def get_session_with_phase(self, session_id: str) -> Optional[Dict]:
        """Get session including detected phase"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, chat_platform, chat_title, participant_name,
                   last_activity, total_messages, phase, phase_confidence, phase_updated_at
            FROM chat_sessions 
            WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'session_id': row[0],
                'platform': row[1],
                'title': row[2],
                'participant': row[3],
                'last_activity': row[4],
                'total_messages': row[5],
                'phase': row[6],
                'phase_confidence': row[7],
                'phase_updated_at': row[8]
            }
        return None

if __name__ == "__main__":
    # Test database creation
    db = ChatDatabase()
    print("[OK] Chat database test completed!")