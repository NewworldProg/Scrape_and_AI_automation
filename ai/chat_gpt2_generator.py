"""
GPT-2 Chat AI Response Generator
Generates intelligent responses for chat conversations
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

# import necessary libraries
import torch # torch for model handling
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config # transformers for GPT-2 model
from data.chat_database_manager import ChatDatabase # chat database manager

class ChatGPT2Generator:
    # initialize GPT-2 model and tokenizer
    #1. gets project root directory and saves path to variable
    #2. insisde path initialize database manager with correct path
    #3. device for model handling cuda or cpu
    #4. try to load model
    #5. try to load tokenizer
    #6. if fails log error and raise
    def __init__(self, model_name="gpt2", use_trained_model=False):
        # Use correct database path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Initialize database manager
        db_path = os.path.join(project_root, "data", "chat_data.db")
        # Create database if it doesn't exist
        self.db = ChatDatabase(db_path)
        
        # Check for trained model
        self.trained_model_path = os.path.join(project_root, "ai", "trained_models", "final_chat_model", "trained_chat_model_1.0")
        self.use_trained = use_trained_model and os.path.exists(self.trained_model_path)
        
        # Initialize device for model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Load model
        self.load_model(model_name)
    def load_model(self, model_name):
        """Load GPT-2 model and tokenizer"""
        try:
            if self.use_trained:
                print(f"Loading trained chat model: {self.trained_model_path}")
                self.tokenizer = GPT2Tokenizer.from_pretrained(self.trained_model_path)
                self.model = GPT2LMHeadModel.from_pretrained(self.trained_model_path)
                print("Trained chat model loaded successfully")
            else:
                print(f"Loading base GPT-2 model: {model_name}")
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
                self.model = GPT2LMHeadModel.from_pretrained(model_name)
                
                # Add pad token if it doesn't exist
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                print("Base GPT-2 model loaded successfully")
            
            # Move model to device
            self.model.to(self.device)
            # Set model to evaluation mode
            self.model.eval()
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise
    
    def generate_trained_response(self, context, max_length=100):
        """Generate response using trained chat model"""
        if not self.use_trained:
            return None
            
        try:
            # Format context for trained model  
            prompt = "<|startoftext|>\n"
            
            # Add recent context as client messages
            for line in context.split('\n')[-3:]:  # Last 3 lines
                if line.strip():
                    prompt += f"<|client|> {line.strip()}\n"
            
            prompt += "<|freelancer|>"
            
            # Tokenize
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.encode("<|endoftext|>")[0]
                )
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the freelancer response
            freelancer_start = full_response.find("<|freelancer|>") + len("<|freelancer|>")
            response = full_response[freelancer_start:].strip()
            
            # Clean up response
            if "<|endoftext|>" in response:
                response = response.split("<|endoftext|>")[0]
            if "<|client|>" in response:
                response = response.split("<|client|>")[0]
                
            # Further cleanup
            response = response.strip()
            if len(response) > 200:
                response = response[:197] + "..."
                
            return response if len(response) > 10 else None
            
        except Exception as e:
            print(f"Error generating trained response: {str(e)}")
            return None
    #1. check inside db for latest session if "latest" is provided
    #2. retrieve recent messages and context for the session
    def get_conversation_context(self, session_id, max_messages=10):
        """Get recent conversation context"""
        try:
            # Handle "latest" session ID
            if session_id == "latest":
                print("Looking for latest session...")
                # inside db look for latest session and extract session id
                latest_session = self.db.get_latest_session()
                if latest_session:
                    session_id = latest_session['session_id']
                    print(f"Found latest session: {session_id}")
                else:
                    print("No latest session found")
                    return ""
            
            print(f"Getting messages for session: {session_id}")
            messages = self.db.get_recent_messages(session_id, limit=max_messages)
            print(f"Found {len(messages)} messages")
            # Build context string from sender and message text
            context_parts = []
            for msg in messages:
                sender = "User" if msg['sender_type'] == 'user' else "Contact"
                context_parts.append(f"{sender}: {msg['text']}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"[ERROR] Error getting context: {e}")
            return ""
    # Generate AI response
    #1.  get context from conversation or use custom prompt
    #2. if no context generate generic response
    #3. create prompt based on response type
    #4. generate multiple response options by calling generate single response function multiple times
    #5. create suggestion data and save to temp file
    #6. return structured response data
    def generate_response(self, session_id, custom_prompt=None, response_type="professional"):
        """Generate AI response suggestions"""
        try:
            # inside variable put output from conversation context function
            context = custom_prompt or self.get_conversation_context(session_id)

            # if there is no context generate generic response
            if not context:
                return self.generate_generic_response(response_type)
            
            # Try trained model first if available
            if self.use_trained:
                trained_response = self.generate_trained_response(context)
                if trained_response:
                    responses = [trained_response]
                    
                    # Generate additional responses with base model
                    base_responses = self.generate_base_responses(context, response_type, count=2)
                    responses.extend(base_responses)
                    
                    # Create AI suggestions
                    suggestion_data = {
                        'session_id': session_id,
                        'suggestion_type': f"{response_type}-trained",
                        'context': context,
                        'responses': responses,
                        'model_used': 'trained_chat_model_1.0',
                        'confidence': self.calculate_confidence(responses),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Save as temporary file for dashboard
                    temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(suggestion_data, f, indent=2)
                    
                    return {
                        'success': True,
                        'session_id': session_id,
                        'response_type': f"{response_type}-trained",
                        'responses': responses,
                        'confidence': suggestion_data['confidence'],
                        'context_length': len(context.split()),
                        'timestamp': datetime.now().isoformat(),
                        'model_used': 'trained_chat_model_1.0'
                    }
            
            # Fallback to base model responses
            return self.generate_base_model_response(session_id, context, response_type)
            
        except Exception as e:
            print(f"[ERROR] Generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    def generate_base_responses(self, context, response_type, count=3):
        """Generate responses using base model"""
        try:
            # Create prompt based on response type
            if response_type == "professional":
                prompt = f"""Professional Business Conversation:
{context}

Professional Response:"""
            elif response_type == "friendly":
                prompt = f"""Friendly Conversation:
{context}

Friendly Response:"""
            elif response_type == "technical":
                prompt = f"""Technical Discussion:
{context}

Technical Response:"""
            else:
                prompt = f"""Conversation:
{context}

Response:"""
            
            # Generate multiple response options
            responses = []
            for i in range(count):
                response = self.generate_single_response(prompt, temperature=0.7 + i*0.1)
                if response and response not in responses:
                    responses.append(response)
            
            return responses
            
        except Exception as e:
            print(f"[ERROR] Base response generation error: {e}")
            return []
    
    def generate_base_model_response(self, session_id, context, response_type):
        """Generate response using base model only"""
        try:
            # Generate responses using base model
            responses = self.generate_base_responses(context, response_type, count=3)
            
            # Create AI suggestions (temporary, not saved to database)
            suggestion_data = {
                'session_id': session_id,
                'suggestion_type': response_type,
                'context': context,
                'responses': responses,
                'model_used': 'gpt2',
                'confidence': self.calculate_confidence(responses),
                'created_at': datetime.now().isoformat()
            }
            
            # Save as temporary file for dashboard (don't save to database)
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(suggestion_data, f, indent=2)
            
            return {
                'success': True,
                'session_id': session_id,
                'response_type': response_type,
                'responses': responses,
                'confidence': suggestion_data['confidence'],
                'context_length': len(context.split()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    # Generate a single response
    #1. tokenize input prompt and move to device
    #2. generate response with model and generate parameters
    # 3. decode response
    #4. extract new part of response
    #5. clean up response in clean_response function
    #6. return cleaned response
    def generate_single_response(self, prompt, max_length=100, temperature=0.7):
        """Generate a single response"""
        try:
            # Tokenize input prompt, decide on return tensors and move to device
            inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate response
            # use no_grad for inference
            # inside variable put model generate with generate and inputs and parameters
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
            
            # Decode response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new part (response)
            response = generated_text[len(prompt):].strip()
            
            # Clean up response in clean_response function
            response = self.clean_response(response)
            # return cleaned response
            return response
            # catch exceptions and log error
        except Exception as e:
            print(f"[ERROR] Single generation error: {e}")
            return ""
    # try to clean the response 
    #1. check if response is empty and return empty string if it is
    #2. loop through sentences in response and by splitting by period
    #3. keep sentence if longer than 10 characters
    #4. loop through words in response and add period if last word is not proper punctuation
    #5. capitalize first letter of response
    #6. if response is longer than 200 characters truncate and add ellipsis
    def clean_response(self, response):
        """Clean and format the generated response"""
        if not response:
            return ""
        
        # Remove common artifacts
        response = response.strip()
        
        # Stop at first sentence if multiple sentences
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[0]) > 10:
            response = sentences[0] + '.'
        
        # Remove incomplete sentences
        if not response.endswith(('.', '!', '?')):
            words = response.split()
            if len(words) > 3:
                response = ' '.join(words[:-1]) + '.'
        
        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:]
        
        # Limit length
        if len(response) > 200:
            response = response[:197] + "..."
        
        return response
    # Calculate confidence score for responses
    #1. make metric for evaluating confidence
    #2. loop through responses
    #. set base score for each response
    #3. if length is between 10 and 150 characters reward with 0.2 points
    #4. if response ends with proper punctuation reward with 0.2 points
    #5. if word count is between 5 and 30 words reward with 0.1 points
    #6. return average confidence score rounded to two decimal places
    def calculate_confidence(self, responses):
        """Calculate confidence score for responses"""
        if not responses:
            return 0.0
        
        # Simple confidence based on response quality
        total_score = 0
        for response in responses:
            score = 0.5  # Base score
            
            # Length factor
            if 10 <= len(response) <= 150:
                score += 0.2
            
            # Completeness factor
            if response.endswith(('.', '!', '?')):
                score += 0.2
            
            # Word count factor
            word_count = len(response.split())
            if 5 <= word_count <= 30:
                score += 0.1
            
            total_score += min(score, 1.0)
        
        return round(total_score / len(responses), 2)
    # fall back to generic responses
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
        
        # Create suggestion data for temp file
        suggestion_data = {
            'session_id': 'generic',
            'suggestion_type': response_type,
            'context': 'No conversation context available',
            'responses': responses,
            'model_used': 'gpt2-generic',
            'confidence': 0.8,
            'created_at': datetime.now().isoformat()
        }
        
        # Save as temporary file for dashboard
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
    # Generate follow-up questions
    #1. get conversation by id from database and extract context
    #2. if no context return error
    #3. setup prompt for follow-up questions with context
    #4. call generate_single_response function and give it prompt and parameters
    #5. parse response into lines and extract questions
    #6. return structured response data with questions
    def generate_follow_up_questions(self, session_id):
        # get conversation by id from database
        try:
            context = self.get_conversation_context(session_id, max_messages=5)
            
            if not context:
                return {
                    'success': False,
                    'error': 'No context available'
                }
            # setup prompt for follow-up questions
            prompt = f"""Based on this conversation, generate helpful follow-up questions:

{context}

Relevant follow-up questions:
1."""
            # call generate_single_response function and give it prompt and parameters
            response = self.generate_single_response(prompt, max_length=150, temperature=0.8)

            # variable to hold parsed questions
            questions = []
            # split response into lines and parse each line
            if response:
                lines = response.split('\n')
                # loop through lines and extract questions
                for line in lines:
                    # strip line from whitespace
                    line = line.strip()
                    # check if line is a question
                    if line and (line.startswith(('1.', '2.', '3.', '-')) or '?' in line):
                        # strip line from question number or bullet point
                        question = line.lstrip('123456789.- ')
                        # if question has more than 10 characters and contains a question mark
                        if len(question) > 10 and '?' in question:
                            # add question to questions list
                            questions.append(question)
            
            return {
                'success': True,
                'session_id': session_id,
                'questions': questions[:3],  # Limit to 3 questions
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_simple_response(self, session_id="latest", response_type="professional"):
        """Generate simple response suggestion without context"""
        try:
            # Get conversation context
            context = self.get_conversation_context(session_id)
            
            if context and self.use_trained:
                # Use trained model for simple response
                response = self.generate_trained_response(context, max_length=100)
                
                if response:
                    # Clean response - remove context, keep only suggestion
                    clean_response = self.clean_response_for_output(response)
                    return {
                        "suggestion": clean_response,
                        "confidence": 0.85,
                        "type": response_type + "-trained"
                    }
            
            # Fallback to simple generic response
            return self.generate_simple_generic_response(response_type)
            
        except Exception as e:
            print(f"[ERROR] Simple generation error: {e}")
            return {"suggestion": "Thank you for your message.", "confidence": 0.5}

    def clean_response_for_output(self, response):
        """Clean response to keep only the suggestion part"""
        if not response:
            return "Thank you for your message."
        
        # Remove conversation markers
        response = response.replace("<|client|>", "").replace("<|freelancer|>", "")
        response = response.replace("<|startoftext|>", "").replace("<|endoftext|>", "")
        
        # Take only first sentence or meaningful part
        sentences = response.split('.')
        if sentences and len(sentences[0].strip()) > 10:
            clean = sentences[0].strip()
            return clean + "."
        
        # Fallback - clean up and truncate
        clean = response.strip()
        if len(clean) > 100:
            clean = clean[:97] + "..."
        
        return clean if len(clean) > 10 else "Thank you for your message."

    def generate_simple_generic_response(self, response_type):
        """Generate simple generic responses"""
        import random
        
        simple_responses = {
            "professional": [
                "Thank you for your message. I'll review this and respond shortly.",
                "I appreciate you reaching out. Let me look into this matter.",
                "Thank you for the information. I'll process this accordingly."
            ],
            "friendly": [
                "Thanks for your message! I'll get back to you soon.",
                "Great to hear from you! Let me check on this for you.",
                "Thanks for reaching out! I'll take a look at this."
            ],
            "technical": [
                "I'll analyze this and provide technical details shortly.",
                "Let me review the technical specifications and respond.",
                "I'll examine this technically and provide comprehensive details."
            ]
        }
        
        responses = simple_responses.get(response_type, simple_responses["professional"])
        
        return {
            "suggestion": random.choice(responses),
            "confidence": 0.7,
            "type": response_type
        }

def main():
    """Main AI generation function"""
    parser = argparse.ArgumentParser(description='GPT-2 Chat Response Generator')
    parser.add_argument('--session-id', required=True, help='Chat session ID')
    parser.add_argument('--type', default='professional', choices=['professional', 'friendly', 'technical'], help='Response type')
    parser.add_argument('--prompt', help='Custom prompt instead of conversation context')
    parser.add_argument('--questions', action='store_true', help='Generate follow-up questions')
    parser.add_argument('--model', default='gpt2', help='GPT-2 model variant')
    parser.add_argument('--use-trained', action='store_true', help='Use trained model if available')
    
    args = parser.parse_args()
    
    try:
        generator = ChatGPT2Generator(model_name=args.model, use_trained_model=args.use_trained)
        
        if args.questions:
            result = generator.generate_follow_up_questions(args.session_id)
        else:
            result = generator.generate_response(
                session_id=args.session_id,
                custom_prompt=args.prompt,
                response_type=args.type
            )
        
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)