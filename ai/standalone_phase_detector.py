"""
Standalone Phase Detector - Updates database with detected phases
Separates phase detection from response generation for efficiency
"""
import sys
import os
import json
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.chat_database_manager import ChatDatabase
from ai.phase_detector import PhaseDetector

class StandalonePhaseDetector:
    """Phase detector that only detects phases and updates database"""
    # init model
    def __init__(self):
        # var to hold root dir
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # var to hold db path
        db_path = os.path.join(project_root, "data", "chat_data.db")
        # initialize database
        self.db = ChatDatabase(db_path)
        # var to hold model dir
        model_dir = os.path.join(project_root, "ai", "trained_models", "phase_classifier_v1")
        
        print("\n" + "="*60)
        print("STANDALONE PHASE DETECTOR")
        print("="*60)
        # error if model not found
        if not os.path.exists(model_dir):
            print(f"❌ ERROR: BERT model not found at {model_dir}")
            print(f"   Run: python ai/train_phase_classifier.py")
            print("="*60 + "\n")
            raise FileNotFoundError("BERT model not trained")
        
        try:
            # call PhaseDetector class
            self.phase_detector = PhaseDetector(model_dir)
            print("✅ BERT PHASE DETECTOR LOADED")
            # print model metadata
            print(f"   Accuracy: {self.phase_detector.metadata.get('accuracy')}%")
            print("="*60 + "\n")
            # except on error
        except Exception as e:
            print(f"❌ ERROR loading BERT model: {e}")
            print("="*60 + "\n")
            raise
    # function to call detection and update db
    def detect_and_update_phase(self, session_id='latest'):
        """Detect phase and update database (main function)"""
        
        print(f"[PHASE DETECT] Starting detection for session: {session_id}")
        
        # get latest session if 'latest' specified
        if session_id == 'latest':
            latest = self.db.get_latest_session()
            if latest:
                session_id = latest['session_id']
                print(f"[SESSION] Using latest session: {session_id}")
            else:
                return {'success': False, 'error': 'No active sessions found'}
        # error if no session id
        if not session_id:
            return {'success': False, 'error': 'No session ID provided'}
        
        # Get conversation context limit to last 10 messages
        messages = self.db.get_recent_messages(session_id, limit=10)
        # error if no messages
        if not messages:
            return {'success': False, 'error': f'No messages found for session {session_id}'}
        
        # Build context string for PhaseDetector tokenization
        context = "\n".join([f"{m['sender_type']}: {m['text']}" for m in messages])
        context_preview = context[:100] + "..." if len(context) > 100 else context
        
        print(f"[CONTEXT] {len(messages)} messages, {len(context)} chars")
        print(f"[PREVIEW] {context_preview}")
        
        # Detect phase using BERT model from the given context
        print("[BERT] Analyzing conversation phase...")
        phase_result = self.phase_detector.predict(context)
        
        phase = phase_result['phase']
        confidence = phase_result['confidence']
        
        print(f"[RESULT] Phase: {phase}")
        print(f"[RESULT] Confidence: {confidence:.1%}")
        
        # Update session with detected phase
        success = self.db.update_session_phase(session_id, phase, confidence)
        
        if success:
            print(f"[SUCCESS] Database updated with phase: {phase}")
            
            return {
                'success': True,
                'session_id': session_id,
                'phase': phase,
                'confidence': confidence,
                'context_length': len(context),
                'messages_count': len(messages),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'Failed to update database with detected phase'
            }

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Standalone Phase Detector')
    parser.add_argument('--session', default='latest', 
                       help='Session ID to analyze (default: latest)')
    parser.add_argument('--output', default='json',
                       help='Output format: json or simple (default: json)')
    
    args = parser.parse_args()
    
    try:
        detector = StandalonePhaseDetector()
        result = detector.detect_and_update_phase(args.session)
        
        if args.output == 'json':
            print("\n" + "="*60)
            print("PHASE DETECTION RESULT")
            print("="*60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if result['success']:
                print(f"\n✅ Phase: {result['phase']} ({result['confidence']:.1%})")
            else:
                print(f"\n❌ Error: {result['error']}")
                
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        if args.output == 'json':
            print(json.dumps(error_result, indent=2))
        else:
            print(f"\n❌ Error: {e}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()