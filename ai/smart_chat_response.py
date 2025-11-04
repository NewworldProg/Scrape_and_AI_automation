"""
Smart Chat Response Generator with Phase Detection
Detects conversation phase and provides appropriate templates
Uses ML model when available, falls back to keyword matching
"""
import sys
import os
import json
import argparse
from datetime import datetime
import random

# Set UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.chat_database_manager import ChatDatabase
from ai.hybrid_phase_detector import HybridPhaseDetector

class SmartChatResponse:
    """Smart response generator with conversation phase detection"""
    
    # Response generation modes
    RESPONSE_MODES = {
        'template': {
            'name': 'Template Only (Fast)',
            'description': 'Pre-written professional templates - instant, consistent, reliable',
            'speed': 'Fastest (~0.1s)',
            'quality': 'Consistent',
            'options': 5  # More template options
        },
        'hybrid': {
            'name': 'Hybrid (Template + AI Enhancement)',
            'description': 'Template base with AI personalization from chat context',
            'speed': 'Medium (~2s)',
            'quality': 'Personalized',
            'options': 3
        },
        'pure': {
            'name': 'Pure AI Generation',
            'description': 'Fully AI-generated response based on phase and context',
            'speed': 'Slower (~3s)',
            'quality': 'Unique',
            'options': 3
        },
        'summary': {
            'name': 'Template + AI Summary',
            'description': 'Template response + AI-generated context summary',
            'speed': 'Medium (~2s)',
            'quality': 'Enhanced',
            'options': 3
        }
    }
    
    PHASES = {
        'initial_response': {
            'name': 'Initial Response (After Cover Letter)',
            'keywords': ['apply', 'application', 'interested', 'position', 'job', 'available', 'experience', 'hello', 'are you available'],
            'next_phase': 'ask_details',
            'description': 'First response from employer after cover letter'
        },
        'ask_details': {
            'name': 'Ask Job Details',
            'keywords': ['project', 'task', 'what', 'need', 'require', 'about', 'tell me', 'types of', 'materials'],
            'next_phase': 'knowledge_check',
            'description': 'Asking about project details, scope, requirements'
        },
        'knowledge_check': {
            'name': 'Knowledge Check (Testing Expertise)',
            'keywords': ['test', 'question', 'know', 'familiar', 'experience with', 'can you explain', 'how would you', 'what do you think', 'technical', 'specific'],
            'next_phase': 'language_confirm',
            'description': '⚠️ Employer testing knowledge - DEFER TO HUMAN if unsure',
            'requires_human': True
        },
        'language_confirm': {
            'name': 'Language Confirmation',
            'keywords': ['language', 'english', 'dutch', 'spanish', 'french', 'german', 'which language'],
            'next_phase': 'rate_negotiation',
            'description': 'Confirming which language(s) needed'
        },
        'rate_negotiation': {
            'name': 'Rate Discussion',
            'keywords': ['rate', 'price', 'per word', 'budget', 'cost', 'charge', 'pay', 'how much'],
            'next_phase': 'deadline_samples',
            'description': 'Discussing rates and pricing'
        },
        'deadline_samples': {
            'name': 'Deadline & Samples',
            'keywords': ['deadline', 'when', 'sample', 'example', 'brief', 'due', 'delivery', 'monday', 'today'],
            'next_phase': 'structure_clarification',
            'description': 'Confirming deadline and requesting samples/briefs'
        },
        'structure_clarification': {
            'name': 'Structure & Requirements',
            'keywords': ['structure', 'format', 'seo', 'keywords', 'h1', 'h2', 'faq', 'links', 'tone', 'voice'],
            'next_phase': 'contract_acceptance',
            'description': 'Clarifying content structure and SEO requirements'
        },
        'contract_acceptance': {
            'name': 'Contract & Start',
            'keywords': ['contract', 'agreement', 'accept', 'start', 'begin', 'okay', 'deal', 'offer'],
            'next_phase': None,
            'description': 'Accepting contract and starting work'
        }
    }
    
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, "data", "chat_data.db")
        self.db = ChatDatabase(db_path)
        
        # Initialize hybrid phase detector (ML + keyword fallback)
        self.phase_detector = HybridPhaseDetector()
        print(f"[OK] Smart Chat Response initialized")
        print(f"[INFO] Detection method: {'ML Model' if self.phase_detector.use_ml_model else 'Keyword Matching'}")
    
    def detect_conversation_phase(self, context_text: str):
        """Detect current phase of conversation based on context."""
        # Use hybrid detector (ML or keyword-based)
        result = self.phase_detector.detect_phase(context_text)
        phase_id = result['phase']
        confidence = result['confidence']
        detection_method = result['method']
        
        # Get phase details
        phase_info = self.phase_detector.get_phase_info(phase_id)
        
        return {
            'phase_id': phase_id,
            'phase_name': phase_info['name'],
            'confidence': round(confidence, 2),
            'next_phase': phase_info['next_phase'],
            'next_phase_name': self.phase_detector.get_phase_info(phase_info['next_phase'])['name'] if phase_info['next_phase'] else None,
            'description': phase_info['description'],
            'detection_method': detection_method,
            'requires_human': phase_info.get('requires_human', False)
        }
    
    def get_phase_templates(self, phase_id: str, num_options=3):
        """Get template responses for specific conversation phase."""
        templates = {
            'initial_response': [
                "Thank you for reaching out! I'm very interested in this position. Could you tell me more about the project scope and requirements?",
                "Good day! Yes, I'm available and excited about this opportunity. What are the main deliverables you need?",
                "Hello! I'd love to work on this project. Can you share more details about what you're looking for?",
                "Thanks for contacting me! I'm definitely interested. Can you provide more information about the content type and volume?",
                "Hi! Your project sounds interesting. I'm available to start. What are the specific requirements?"
            ],
            'ask_details': [
                "Thank you for the details. Could you confirm: which language do you need (English/Dutch)? And approximately how many words per week?",
                "Great! To ensure I can deliver exactly what you need, could you clarify the language and expected volume?",
                "Thanks for the info. Which language should the content be in, and what's the typical word count per article?",
                "Perfect! Just to clarify - what language and how many articles would you need per week?",
                "Sounds good! Could you specify the language preference and approximate volume?"
            ],
            'knowledge_check': [
                "⚠️ KNOWLEDGE CHECK DETECTED - This requires human expertise. Please review the question manually.",
                "⚠️ Technical question detected. Recommend human review to provide accurate, specific answer.",
                "⚠️ This appears to be a knowledge test. Human input needed for best response."
            ],
            'language_confirm': [
                "Perfect! For Dutch content, my rate is $0.06-0.07 per word depending on volume and complexity. What's your budget?",
                "Understood - Dutch content. I charge $0.06-0.07 per word. Does this work with your budget?",
                "Got it! My rate for Dutch is $0.06-0.07 per word. Shall we discuss the specific rate based on volume?",
                "Excellent! I specialize in Dutch content. My rate is $0.06-0.07 per word. Does this fit your budget?",
                "Great! For high-quality Dutch content, I work at $0.06-0.07 per word. What's your budget range?"
            ],
            'rate_negotiation': [
                "Sounds good! What's the deadline for this batch? And could you share a sample article so I can match your tone and style?",
                "Great, we're aligned on the rate. When do you need this delivered? Also, do you have example content I can reference?",
                "Perfect! Could you provide: 1) Deadline, and 2) A sample article to ensure I match your quality expectations?",
                "Excellent! Now, when would you need the first delivery? And do you have sample content for style reference?",
                "That works perfectly! What's the timeline, and can you share examples of the content style you want?"
            ],
            'deadline_samples': [
                "Thank you for the sample. I see you need H2/H3 structure with SEO optimization. Do you have specific keyword targets or a detailed brief?",
                "Got the deadline and sample. For structure: should I follow a specific template (intro, H2s, FAQs, conclusion)?",
                "Thanks! Could you clarify the content structure you prefer? (e.g., word count per section, number of H2s, FAQ format)",
                "Perfect! Do you have a content brief or specific structure requirements (headings, word count, SEO elements)?",
                "Great! Should I follow a particular format or structure for the articles?"
            ],
            'structure_clarification': [
                "Perfect! I have all the details. If you can send the contract, I can start right away.",
                "Excellent - I understand the requirements completely. Ready to begin as soon as we formalize the agreement.",
                "All clear! Please send the contract and I'll deliver the first batch by [deadline].",
                "Got it! Everything is clear now. Send the contract and I'll get started immediately.",
                "Perfect! I have all the information I need. Ready to start once we formalize the agreement."
            ],
            'contract_acceptance': [
                "Contract accepted! I'll start working on this immediately and keep you updated.",
                "Thank you! I've accepted the offer. I'll deliver high-quality work by the deadline.",
                "Great! Starting now. You can expect the first deliverable by [deadline].",
                "Accepted! Starting work immediately. I'll keep you posted on progress.",
                "Done! Contract accepted. Working on the first batch now - delivery on schedule."
            ]
        }
        
        all_templates = templates.get(phase_id, templates['initial_response'])
        
        # Return requested number of options
        if num_options >= len(all_templates):
            return all_templates
        
        # Return first num_options templates
        return all_templates[:num_options]
    
    def get_phase_questions(self, phase_id: str):
        """Get relevant follow-up questions for each phase."""
        questions = {
            'initial_response': [
                "What is the main focus of the content? (casino reviews, slots, blog posts)",
                "Which topics should I prioritize?",
                "Are there specific guidelines I should follow?"
            ],
            'ask_details': [
                "Which language do you need: English or Dutch?",
                "How many words per article typically?",
                "What's the expected volume per week?"
            ],
            'knowledge_check': [
                "⚠️ READ THE QUESTION CAREFULLY - This requires YOUR expertise",
                "⚠️ Provide detailed, specific answer based on YOUR experience",
                "⚠️ If unsure, ask for clarification rather than guessing"
            ],
            'language_confirm': [
                "What's your budget per word?",
                "Is there flexibility on rates for larger volumes?",
                "Do you have a preferred payment structure?"
            ],
            'rate_negotiation': [
                "What's the deadline for this batch/article?",
                "Can you share a sample article for tone reference?",
                "Do you have a content brief template?"
            ],
            'deadline_samples': [
                "What structure do you prefer? (H1, H2s, FAQs, links)",
                "Are there specific SEO keywords to target?",
                "Should I include internal/external links?"
            ],
            'structure_clarification': [
                "Should I send a draft for review first?",
                "What's the revision process?",
                "When can we formalize the contract?"
            ],
            'contract_acceptance': [
                "Shall I start with the first batch immediately?",
                "How would you like me to submit completed work?",
                "What's the best way to communicate during the project?"
            ]
        }
        
        return questions.get(phase_id, questions['initial_response'])
    
    def get_conversation_context(self, session_id, max_messages=10):
        """Get recent conversation context"""
        try:
            if session_id == "latest":
                latest_session = self.db.get_latest_session()
                if latest_session:
                    session_id = latest_session['session_id']
                else:
                    return ""
            
            messages = self.db.get_recent_messages(session_id, limit=max_messages)
            context_parts = []
            for msg in messages:
                sender = "User" if msg['sender_type'] == 'user' else "Contact"
                context_parts.append(f"{sender}: {msg['text']}")
            
            return "\n".join(context_parts)
        except Exception as e:
            print(f"[ERROR] Error getting context: {e}")
            return ""
    
    def generate_ai_response(self, phase_id, context, mode='pure', session_id='latest'):
        """
        Generate AI-powered response based on mode
        
        Modes:
        - 'pure': Fully AI-generated from scratch
        - 'hybrid': Template base + AI personalization
        - 'summary': Template + AI context summary
        """
        try:
            # Try to import GPT-2 generator if available
            try:
                from ai.chat_gpt2_generator import ChatGPT2Generator
                gpt2 = ChatGPT2Generator()
                has_gpt2 = True
            except Exception as e:
                has_gpt2 = False
                print(f"[WARN] GPT-2 not available: {e}")
            
            phase_info = self.phase_detector.get_phase_info(phase_id)
            
            if mode == 'pure' and has_gpt2:
                # Pure AI generation - use custom prompt
                prompt = f"Professional Upwork response for {phase_info['name']}.\n\nContext: {context[-300:]}\n\nGenerate a professional, contextual response:"
                result = gpt2.generate_response(
                    session_id=session_id,
                    custom_prompt=prompt,
                    response_type='professional'
                )
                
                # Extract first response from result
                if result.get('success') and result.get('responses'):
                    return result['responses'][0]
                else:
                    print(f"[WARN] Pure AI mode failed, using template")
                    templates = self.get_phase_templates(phase_id, num_options=1)
                    return templates[0]
            
            elif mode == 'hybrid' and has_gpt2:
                # Template + AI enhancement
                templates = self.get_phase_templates(phase_id, num_options=1)
                base_template = templates[0]
                
                # Use GPT-2 to enhance template with context
                prompt = f"Base message: {base_template}\n\nConversation context: {context[-250:]}\n\nEnhance the message to be more contextual and personalized:"
                result = gpt2.generate_response(
                    session_id=session_id,
                    custom_prompt=prompt,
                    response_type='professional'
                )
                
                if result.get('success') and result.get('responses'):
                    return result['responses'][0]
                else:
                    return base_template
            
            elif mode == 'summary' and has_gpt2:
                # Template + AI context summary
                templates = self.get_phase_templates(phase_id, num_options=1)
                base_template = templates[0]
                
                # Generate AI summary of context
                prompt = f"Conversation context: {context[-300:]}\n\nSummarize the key points in one sentence:"
                result = gpt2.generate_response(
                    session_id=session_id,
                    custom_prompt=prompt,
                    response_type='technical'
                )
                
                if result.get('success') and result.get('responses'):
                    summary = result['responses'][0]
                    return f"{base_template}\n\n📝 Context: {summary}"
                else:
                    return base_template
            
            else:
                # Fallback to template (if no GPT-2 or unknown mode)
                templates = self.get_phase_templates(phase_id, num_options=1)
                return templates[0]
        
        except Exception as e:
            print(f"[WARN] AI generation failed: {e}. Using template.")
            import traceback
            traceback.print_exc()
            templates = self.get_phase_templates(phase_id, num_options=1)
            return templates[0]
    
    def generate_all_modes_response(self, session_id='latest'):
        """
        Generate responses from ALL 4 modes sequentially (not parallel).
        Returns combined results for dashboard display.
        Executes one by one to avoid CPU overload.
        """
        try:
            print("[INFO] Generating responses from all 4 modes (sequential)...")
            print("[INFO] This will take ~7-8 seconds total")
            
            # Get conversation context once
            context = self.get_conversation_context(session_id)
            
            # Detect conversation phase once
            phase_detection = self.detect_conversation_phase(context)
            phase_id = phase_detection['phase_id']
            
            print(f"\n[PHASE] Detected: {phase_detection['phase_name']} (confidence: {phase_detection['confidence']:.0%})")
            
            all_modes_results = {}
            
            # 1. TEMPLATE mode (fastest)
            print("\n[1/4] Generating TEMPLATE responses (3 options)...")
            templates = self.get_phase_templates(phase_id, num_options=3)
            all_modes_results['template'] = {
                'mode_name': 'Template Only (Fast)',
                'description': 'Pre-written professional templates',
                'num_options': len(templates),
                'responses': templates,
                'speed': '~0.1s',
                'recommended': templates[0]
            }
            print(f"      ✅ Generated {len(templates)} template options")
            
            # 2. HYBRID mode
            print("\n[2/4] Generating HYBRID response (1 AI-enhanced option)...")
            hybrid_response = self.generate_ai_response(phase_id, context, mode='hybrid', session_id=session_id)
            all_modes_results['hybrid'] = {
                'mode_name': 'Hybrid (Template + AI)',
                'description': 'Template base with AI personalization',
                'num_options': 1,
                'responses': [hybrid_response],
                'speed': '~2s',
                'recommended': hybrid_response
            }
            print(f"      ✅ Generated 1 hybrid option")
            
            # 3. PURE AI mode
            print("\n[3/4] Generating PURE AI response (1 fully generated option)...")
            pure_response = self.generate_ai_response(phase_id, context, mode='pure', session_id=session_id)
            all_modes_results['pure'] = {
                'mode_name': 'Pure AI Generation',
                'description': 'Fully AI-generated from context',
                'num_options': 1,
                'responses': [pure_response],
                'speed': '~3s',
                'recommended': pure_response
            }
            print(f"      ✅ Generated 1 pure AI option")
            
            # 4. SUMMARY mode
            print("\n[4/4] Generating SUMMARY response (1 template + context option)...")
            summary_response = self.generate_ai_response(phase_id, context, mode='summary', session_id=session_id)
            all_modes_results['summary'] = {
                'mode_name': 'Template + AI Summary',
                'description': 'Template with AI context summary',
                'num_options': 1,
                'responses': [summary_response],
                'speed': '~2s',
                'recommended': summary_response
            }
            print(f"      ✅ Generated 1 summary option")
            
            # Get follow-up questions
            phase_questions = self.get_phase_questions(phase_id)
            
            # Check if requires human
            requires_human = phase_detection.get('requires_human', False)
            
            # Build combined result
            result = {
                'success': True,
                'session_id': session_id,
                'generation_mode': 'all_modes',
                'detected_phase': phase_detection,
                'all_modes': all_modes_results,
                'total_options': sum(m['num_options'] for m in all_modes_results.values()),
                'modes_generated': list(all_modes_results.keys()),
                'follow_up_questions': phase_questions,
                'next_steps': f"After this, move to: {phase_detection['next_phase_name']}" if phase_detection['next_phase_name'] else "Contract finalized - ready to start work!",
                'requires_human_review': requires_human,
                'warning': '⚠️ KNOWLEDGE CHECK - Human expertise required!' if requires_human else None,
                'timestamp': datetime.now().isoformat(),
                'model_used': 'smart-phase-detector'
            }
            
            # Save for dashboard
            try:
                temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'session_id': session_id,
                        'suggestion_type': 'all-modes-combined',
                        'phase': phase_detection['phase_name'],
                        'next_phase': phase_detection['next_phase_name'],
                        'all_modes': all_modes_results,
                        'total_options': result['total_options'],
                        'created_at': result['timestamp'],
                        'model_used': 'smart-phase-detector',
                        'confidence': phase_detection['confidence'],
                        'detection_method': phase_detection.get('detection_method', 'unknown')
                    }, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            
            print(f"\n[SUCCESS] Generated {result['total_options']} total options across 4 modes!")
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'session_id': session_id}
        """
        Generate comprehensive smart response with phase detection and templates.
        
        Modes:
        - 'template': Fast, pre-written templates (5 options)
        - 'hybrid': Template base + AI personalization (3 options)
        - 'pure': Fully AI-generated responses (3 options)
        - 'summary': Template + AI context summary (3 options)
        """
        try:
            # Validate mode
            if mode not in self.RESPONSE_MODES:
                print(f"[WARN] Invalid mode '{mode}', using 'template'")
                mode = 'template'
            
            mode_info = self.RESPONSE_MODES[mode]
            print(f"[INFO] Response mode: {mode_info['name']}")
            print(f"[INFO] {mode_info['description']}")
            
            # Get conversation context
            context = self.get_conversation_context(session_id)
            
            # Detect conversation phase
            phase_detection = self.detect_conversation_phase(context)
            phase_id = phase_detection['phase_id']
            
            # Get responses based on mode
            if mode == 'template':
                # Template only - fast, 5 options
                num_options = 5
                templates = self.get_phase_templates(phase_id, num_options=num_options)
                recommended = random.choice(templates)
                all_options = templates
                
            elif mode in ['hybrid', 'pure', 'summary']:
                # AI-enhanced modes - 3 options
                num_options = 3
                all_options = []
                
                # Generate AI responses
                for i in range(num_options):
                    ai_response = self.generate_ai_response(phase_id, context, mode=mode, session_id=session_id)
                    all_options.append(ai_response)
                
                recommended = all_options[0]
            
            else:
                # Fallback
                templates = self.get_phase_templates(phase_id, num_options=3)
                recommended = random.choice(templates)
                all_options = templates
            
            # Get follow-up questions for this phase
            phase_questions = self.get_phase_questions(phase_id)
            
            # Check if this phase requires human intervention
            requires_human = phase_detection.get('requires_human', False)
            
            result = {
                'success': True,
                'session_id': session_id,
                'response_mode': mode,
                'mode_info': mode_info,
                'detected_phase': phase_detection,
                'recommended_response': recommended,
                'all_response_options': all_options,
                'num_options': len(all_options),
                'follow_up_questions': phase_questions,
                'next_steps': f"After this, move to: {phase_detection['next_phase_name']}" if phase_detection['next_phase_name'] else "Contract finalized - ready to start work!",
                'requires_human_review': requires_human,
                'warning': '⚠️ KNOWLEDGE CHECK - Human expertise required!' if requires_human else None,
                'timestamp': datetime.now().isoformat(),
                'model_used': 'smart-phase-detector'
            }
            
            # Save for dashboard
            try:
                temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'session_id': session_id,
                        'suggestion_type': 'smart-phase-response',
                        'response_mode': mode,
                        'mode_description': mode_info['description'],
                        'phase': phase_detection['phase_name'],
                        'next_phase': phase_detection['next_phase_name'],
                        'responses': all_options,
                        'num_options': len(all_options),
                        'recommended': recommended,
                        'created_at': result['timestamp'],
                        'model_used': 'smart-phase-detector',
                        'confidence': phase_detection['confidence'],
                        'detection_method': phase_detection.get('detection_method', 'unknown')
                    }, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'session_id': session_id}

def main():
    """Main smart response function"""
    parser = argparse.ArgumentParser(description='Smart Chat Response Generator')
    parser.add_argument('--session-id', default='latest', help='Chat session ID')
    parser.add_argument('--mode', default='template', 
                       choices=['template', 'hybrid', 'pure', 'summary', 'all'],
                       help='''Response generation mode:
                       template = Fast pre-written templates (5 options)
                       hybrid = Template + AI personalization (3 options)
                       pure = Fully AI-generated (3 options)
                       summary = Template + AI context summary (3 options)
                       all = Generate ALL modes (14 total options, ~7-8s)''')
    
    args = parser.parse_args()
    
    try:
        generator = SmartChatResponse()
        
        # Check if generating all modes
        if args.mode == 'all':
            result = generator.generate_all_modes_response(session_id=args.session_id)
        else:
            result = generator.generate_smart_response(
                session_id=args.session_id,
                mode=args.mode
            )
        
        # Print result for n8n
        print("\n" + "="*60)
        print("FINAL OUTPUT:")
        print("="*60)
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
