"""
Lightweight Phase Detector - Uses both keyword matching and ML model (when available)
Falls back to keyword-based detection if ML model not trained yet
"""
import os
import json

class HybridPhaseDetector:
    """Detects conversation phase using keywords + optional ML model"""
    
    def __init__(self):
        self.model_dir = os.path.join(os.path.dirname(__file__), 'trained_models', 'phase_classifier_v1')
        self.use_ml_model = False
        self.ml_detector = None
        
        # Try to load ML model if available
        if os.path.exists(os.path.join(self.model_dir, 'metadata.json')):
            try:
                import sys
                sys.path.append(os.path.dirname(__file__))
                from phase_detector import PhaseDetector
                self.ml_detector = PhaseDetector(self.model_dir)
                self.use_ml_model = True
                print(f"[OK] Using ML phase detector (accuracy: {self.ml_detector.metadata.get('accuracy', 0):.2f}%)")
            except Exception as e:
                print(f"[WARN] ML model exists but couldn't load: {e}")
                print(f"[INFO] Falling back to keyword-based detection")
        else:
            print(f"[INFO] ML model not found. Using keyword-based detection.")
            print(f"[TIP] Train ML model with: python ai/train_phase_classifier.py")
        
        # Keyword patterns for fallback
        self.keyword_patterns = {
            'initial_response': {
                'keywords': ['apply', 'application', 'interested', 'position', 'job', 'available', 'experience', 'hello', 'are you available', 'saw your'],
                'weight': 1.0
            },
            'ask_details': {
                'keywords': ['project', 'task', 'what', 'need', 'require', 'about', 'tell me', 'types of', 'materials', 'deliverables', 'scope'],
                'weight': 1.0
            },
            'knowledge_check': {
                'keywords': ['test', 'question', 'know', 'familiar', 'experience with', 'can you explain', 'how would you', 'what do you think', 'technical', 'specific', 'your opinion', 'sample', 'write a'],
                'weight': 1.2  # Higher weight - important to catch!
            },
            'language_confirm': {
                'keywords': ['language', 'english', 'dutch', 'spanish', 'french', 'german', 'which language', 'bilingual'],
                'weight': 1.0
            },
            'rate_negotiation': {
                'keywords': ['rate', 'price', 'per word', 'budget', 'cost', 'charge', 'pay', 'how much', 'offer'],
                'weight': 1.0
            },
            'deadline_samples': {
                'keywords': ['deadline', 'when', 'sample', 'example', 'brief', 'due', 'delivery', 'monday', 'today', 'friday', 'week'],
                'weight': 1.0
            },
            'structure_clarification': {
                'keywords': ['structure', 'format', 'seo', 'keywords', 'h1', 'h2', 'faq', 'links', 'tone', 'voice', 'yoast', 'meta'],
                'weight': 1.0
            },
            'contract_acceptance': {
                'keywords': ['contract', 'agreement', 'accept', 'start', 'begin', 'okay', 'deal', 'offer', 'milestone'],
                'weight': 1.0
            }
        }
    
    def detect_phase_keywords(self, context):
        """Fallback keyword-based phase detection"""
        if not context:
            return {
                'phase': 'initial_response',
                'confidence': 0.5,
                'method': 'default'
            }
        
        ctx_lower = context.lower()
        phase_scores = {}
        
        # Score each phase
        for phase_id, pattern in self.keyword_patterns.items():
            score = 0
            keywords = pattern['keywords']
            weight = pattern['weight']
            
            for keyword in keywords:
                if keyword in ctx_lower:
                    score += 1
            
            # Normalize and apply weight
            if keywords:
                phase_scores[phase_id] = (score / len(keywords)) * weight
        
        # Find best match
        if phase_scores:
            best_phase = max(phase_scores, key=phase_scores.get)
            confidence = phase_scores[best_phase]
            
            # If confidence too low, default to initial
            if confidence < 0.15:
                best_phase = 'initial_response'
                confidence = 0.5
        else:
            best_phase = 'initial_response'
            confidence = 0.5
        
        return {
            'phase': best_phase,
            'confidence': round(confidence, 4),
            'method': 'keyword_matching'
        }
    
    def detect_phase(self, context):
        """Detect phase using ML model if available, otherwise keywords"""
        # Try ML model first
        if self.use_ml_model and self.ml_detector:
            try:
                result = self.ml_detector.predict(context)
                result['method'] = 'ml_model'
                return result
            except Exception as e:
                print(f"[WARN] ML detection failed: {e}. Using keywords.")
        
        # Fallback to keywords
        return self.detect_phase_keywords(context)
    
    def get_phase_info(self, phase_id):
        """Get detailed information about a phase"""
        phase_details = {
            'initial_response': {
                'name': 'Initial Response (After Cover Letter)',
                'next_phase': 'ask_details',
                'requires_human': False,
                'description': 'First response from employer after cover letter'
            },
            'ask_details': {
                'name': 'Ask Job Details',
                'next_phase': 'knowledge_check',
                'requires_human': False,
                'description': 'Asking about project details, scope, requirements'
            },
            'knowledge_check': {
                'name': 'Knowledge Check (Testing Expertise)',
                'next_phase': 'language_confirm',
                'requires_human': True,
                'description': '⚠️ Employer testing knowledge - DEFER TO HUMAN if unsure'
            },
            'language_confirm': {
                'name': 'Language Confirmation',
                'next_phase': 'rate_negotiation',
                'requires_human': False,
                'description': 'Confirming which language(s) needed'
            },
            'rate_negotiation': {
                'name': 'Rate Discussion',
                'next_phase': 'deadline_samples',
                'requires_human': False,
                'description': 'Discussing rates and pricing'
            },
            'deadline_samples': {
                'name': 'Deadline & Samples',
                'next_phase': 'structure_clarification',
                'requires_human': False,
                'description': 'Confirming deadline and requesting samples/briefs'
            },
            'structure_clarification': {
                'name': 'Structure & Requirements',
                'next_phase': 'contract_acceptance',
                'requires_human': False,
                'description': 'Clarifying content structure and SEO requirements'
            },
            'contract_acceptance': {
                'name': 'Contract & Start',
                'next_phase': None,
                'requires_human': False,
                'description': 'Accepting contract and starting work'
            }
        }
        
        return phase_details.get(phase_id, phase_details['initial_response'])


def test_hybrid_detector():
    """Test the hybrid detector"""
    print("=" * 60)
    print("TESTING HYBRID PHASE DETECTOR")
    print("=" * 60)
    
    detector = HybridPhaseDetector()
    
    test_cases = [
        "Hello! I saw your application. Are you available?",
        "We need content about casino games. Can you handle technical topics?",
        "Can you explain what RTP means in slot machines?",
        "Which language do you prefer - English or Dutch?",
        "Our budget is $0.06 per word. Does that work?",
        "We need the first batch by Monday. Can you deliver?",
        "Each article needs H1, H2s, and FAQ section with SEO.",
        "I'm sending the contract now. Please accept to start.",
        "Can you write a sample paragraph about responsible gambling?"
    ]
    
    print(f"\n[INFO] Detection method: {detector.use_ml_model and 'ML Model' or 'Keyword Matching'}\n")
    
    for i, context in enumerate(test_cases, 1):
        result = detector.detect_phase(context)
        phase_info = detector.get_phase_info(result['phase'])
        
        print(f"{i}. Context: \"{context[:60]}...\"" if len(context) > 60 else f"{i}. Context: \"{context}\"")
        print(f"   → Phase: {phase_info['name']}")
        print(f"   → Confidence: {result['confidence']:.2%}")
        print(f"   → Method: {result['method']}")
        if phase_info['requires_human']:
            print(f"   ⚠️  HUMAN REVIEW REQUIRED")
        print()


if __name__ == "__main__":
    test_hybrid_detector()
