"""
Enhanced GPT-2 Chat AI Response Generator with Trained Model Support
Generates intelligent responses for chat conversations using base or trained GPT-2 model
"""
import sys
import os
import json
import argparse
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from data.chat_database_manager import ChatDatabase

class EnhancedChatGPT2Generator:
    def __init__(self, model_name="gpt2", use_trained_model=False):
        # Database setup
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, "data", "chat_data.db")
        self.db = ChatDatabase(db_path)
        
        # Model setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.trained_model_path = os.path.join(project_root, "ai", "trained_models", "final_chat_model", "trained_chat_model_1.0")
        
        # Load appropriate model
        if use_trained_model and os.path.exists(self.trained_model_path):
            print(f"🤖 Loading trained chat model: trained_chat_model_1.0")
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.trained_model_path)
            self.model = GPT2LMHeadModel.from_pretrained(self.trained_model_path)
            self.model_type = "trained"
        else:
            print(f"🤖 Loading base GPT-2 model: {model_name}")
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model_type = "base"
        
        self.model.to(self.device)
        self.model.eval()
        print(f"✅ Model loaded successfully on {self.device}")
    
    def get_conversation_context(self, session_id, max_messages=10):
        """Get recent conversation context"""
        try:
            if session_id == "latest":
                latest_session = self.db.get_latest_session()
                if latest_session:
                    session_id = latest_session['session_id']
                    print(f"Found latest session: {session_id}")
                else:
                    print("No latest session found")
                    return ""
            
            messages = self.db.get_recent_messages(session_id, limit=max_messages)
            context_parts = []
            for msg in messages:
                sender = "User" if msg['sender_type'] == 'user' else "Contact"
                context_parts.append(f"{sender}: {msg['text']}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error getting context: {e}")
            return ""
    
    def generate_trained_response(self, context, max_length=100):
        """Generate response using trained model format"""
        if self.model_type != "trained":
            return None
            
        try:
            # Format for trained model
            prompt = "<|startoftext|>\n"
            for line in context.split('\n')[-3:]:
                if line.strip():
                    prompt += f"<|client|> {line.strip()}\n"
            prompt += "<|freelancer|>"
            
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            freelancer_start = response.find("<|freelancer|>") + len("<|freelancer|>")
            response = response[freelancer_start:].strip()
            
            # Clean up
            if "<|endoftext|>" in response:
                response = response.split("<|endoftext|>")[0]
            if "<|client|>" in response:
                response = response.split("<|client|>")[0]
                
            return response.strip() if len(response.strip()) > 10 else None
            
        except Exception as e:
            print(f"Error generating trained response: {e}")
            return None
    
    def generate_base_response(self, context, response_type, max_length=100, temperature=0.7):
        """Generate response using base model"""
        try:
            if response_type == "professional":
                prompt = f"Professional Business Conversation:\n{context}\n\nProfessional Response:"
            elif response_type == "friendly":
                prompt = f"Friendly Conversation:\n{context}\n\nFriendly Response:"
            else:
                prompt = f"Conversation:\n{context}\n\nResponse:"
            
            inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2,
                    top_p=0.9
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response[len(prompt):].strip()
            
            # Clean up
            sentences = response.split('.')
            if len(sentences) > 1 and len(sentences[0]) > 10:
                response = sentences[0] + '.'
            
            if not response.endswith(('.', '!', '?')):
                words = response.split()
                if len(words) > 3:
                    response = ' '.join(words[:-1]) + '.'
            
            if response:
                response = response[0].upper() + response[1:]
            
            if len(response) > 200:
                response = response[:197] + "..."
            
            return response
            
        except Exception as e:
            print(f"Error generating base response: {e}")
            return ""
    
    def generate_response(self, session_id, custom_prompt=None, response_type="professional"):
        """Generate AI response suggestions"""
        try:
            context = custom_prompt or self.get_conversation_context(session_id)
            
            if not context:
                return self.generate_generic_response(response_type)
            
            responses = []
            
            # Try trained model first
            if self.model_type == "trained":
                trained_response = self.generate_trained_response(context)
                if trained_response:
                    responses.append(trained_response)
                
                # Generate additional base-style responses
                for i in range(2):
                    base_response = self.generate_base_response(context, response_type, temperature=0.7 + i*0.1)
                    if base_response and base_response not in responses:
                        responses.append(base_response)
            else:
                # Generate multiple base responses
                for i in range(3):
                    response = self.generate_base_response(context, response_type, temperature=0.7 + i*0.1)
                    if response and response not in responses:
                        responses.append(response)
            
            # Calculate confidence
            confidence = self.calculate_confidence(responses)
            
            # Save suggestions
            suggestion_data = {
                'session_id': session_id,
                'suggestion_type': response_type + ("-trained" if self.model_type == "trained" else "-base"),
                'context': context,
                'responses': responses,
                'model_used': self.model_type,
                'confidence': confidence,
                'created_at': datetime.now().isoformat()
            }
            
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(suggestion_data, f, indent=2)
            
            return {
                'success': True,
                'session_id': session_id,
                'response_type': response_type,
                'responses': responses,
                'confidence': confidence,
                'context_length': len(context.split()),
                'model_used': self.model_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    def calculate_confidence(self, responses):
        """Calculate confidence score"""
        if not responses:
            return 0.0
        
        total_score = 0
        for response in responses:
            score = 0.5
            if 10 <= len(response) <= 150:
                score += 0.2
            if response.endswith(('.', '!', '?')):
                score += 0.2
            word_count = len(response.split())
            if 5 <= word_count <= 30:
                score += 0.1
            total_score += min(score, 1.0)
        
        return round(total_score / len(responses), 2)
    
    def generate_generic_response(self, response_type):
        """Generate generic responses when no context available"""
        generic_responses = {
            "professional": [
                "Thank you for your message. I'll review this and get back to you shortly.",
                "I appreciate you reaching out. Let me look into this matter.",
                "Thank you for the information. I'll process this and respond accordingly."
            ],
            "friendly": [
                "Thanks for your message! I'll get back to you soon.",
                "Great to hear from you! Let me check on this for you.",
                "Thanks for reaching out! I'll take a look at this."
            ],
            "technical": [
                "I'll need to analyze this further. Will provide technical details shortly.",
                "Let me review the technical specifications and respond with details.",
                "I'll examine this technically and provide a comprehensive response."
            ]
        }
        
        responses = generic_responses.get(response_type, generic_responses["professional"])
        
        suggestion_data = {
            'session_id': 'generic',
            'suggestion_type': response_type,
            'context': 'No conversation context available',
            'responses': responses,
            'model_used': 'generic',
            'confidence': 0.8,
            'created_at': datetime.now().isoformat()
        }
        
        temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(suggestion_data, f, indent=2)
        
        return {
            'success': True,
            'responses': responses,
            'confidence': 0.8,
            'type': 'generic',
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Enhanced GPT-2 Chat Response Generator')
    parser.add_argument('--session-id', required=True, help='Chat session ID')
    parser.add_argument('--type', default='professional', choices=['professional', 'friendly', 'technical'], help='Response type')
    parser.add_argument('--prompt', help='Custom prompt instead of conversation context')
    parser.add_argument('--model', default='gpt2', help='GPT-2 model variant')
    parser.add_argument('--use-trained', action='store_true', help='Use trained model if available')
    
    args = parser.parse_args()
    
    try:
        generator = EnhancedChatGPT2Generator(
            model_name=args.model, 
            use_trained_model=args.use_trained
        )
        
        result = generator.generate_response(
            session_id=args.session_id,
            custom_prompt=args.prompt,
            response_type=args.type
        )
        
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