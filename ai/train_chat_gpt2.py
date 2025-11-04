"""
GPT-2 Chat Model Training Script
Trains GPT-2 model on Upwork chat conversation data
"""
import os
import json
import torch
import numpy as np
from datetime import datetime
from transformers import (
    GPT2LMHeadModel, 
    GPT2Tokenizer, 
    TextDataset, 
    DataCollatorForLanguageModeling,
    Trainer, 
    TrainingArguments
)
from torch.utils.data import Dataset
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatTrainingDataset(Dataset):
    """Custom dataset for chat conversation training"""
    
    def __init__(self, tokenizer, file_path, block_size=512):
        self.tokenizer = tokenizer
        self.block_size = block_size
        
        # Load and preprocess chat data
        self.examples = self.load_and_process_chat_data(file_path)
        
    def load_and_process_chat_data(self, file_path):
        """Load chat data and convert to training format"""
        
        print(f"📚 Loading chat data from: {file_path}")
        
        # Read the training data
        with open(file_path, 'r', encoding='utf-8') as f:
            chat_text = f.read()
        
        print(f"📄 Loaded {len(chat_text)} characters of chat data")
        
        # Parse chat conversations
        conversations = self.parse_chat_conversations(chat_text)
        print(f"💬 Parsed {len(conversations)} conversation segments")
        
        # Convert to training examples
        examples = []
        for i, conv in enumerate(conversations):
            # Create prompt-response pairs
            training_text = self.format_conversation_for_training(conv)
            
            if len(training_text) > 50:  # Only use substantial conversations
                print(f"📝 Training example {i+1}:\n{training_text[:200]}...\n")
                
                # Tokenize
                tokenized = self.tokenizer(
                    training_text,
                    truncation=True,
                    max_length=self.block_size,
                    return_tensors="pt"
                )
                
                examples.append(tokenized['input_ids'].squeeze())
            
        print(f"✅ Created {len(examples)} training examples")
        return examples
    
    def parse_chat_conversations(self, chat_text):
        """Parse chat text into structured conversations"""
        
        conversations = []
        lines = chat_text.split('\n')
        current_conversation = []
        current_speaker = None
        current_message = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect speaker changes
            if 'Noel Angeles' in line:
                # Save previous message
                if current_speaker and current_message.strip():
                    current_conversation.append({
                        'speaker': current_speaker,
                        'message': current_message.strip()
                    })
                    current_message = ""
                
                current_speaker = 'freelancer'
                
            elif 'YM' in line or 'Yuliia M' in line:
                # Save previous message
                if current_speaker and current_message.strip():
                    current_conversation.append({
                        'speaker': current_speaker,
                        'message': current_message.strip()
                    })
                    current_message = ""
                
                current_speaker = 'client'
                
            # Skip system messages and timestamps
            elif any(skip_word in line for skip_word in [
                'View details', 'View contract', 'View offer', 'Est. Budget',
                'AM', 'PM', '2025', '.xlsx', '.docx', 'sent an offer',
                'accepted an offer', 'removed this message'
            ]):
                continue
            else:
                # Add to current message
                if line and current_speaker:
                    if current_message:
                        current_message += " " + line
                    else:
                        current_message = line
        
        # Save last message
        if current_speaker and current_message.strip():
            current_conversation.append({
                'speaker': current_speaker,
                'message': current_message.strip()
            })
        
        # Split conversation into segments for better training
        if current_conversation:
            # Create segments of 3-5 exchanges
            segments = []
            for i in range(0, len(current_conversation), 3):
                segment = current_conversation[i:i+5]
                if len(segment) >= 2:  # At least 2 messages (question-answer)
                    segments.append(segment)
            
            conversations.extend(segments)
            
        return conversations
    
    def format_conversation_for_training(self, conversation):
        """Format conversation for GPT-2 training"""
        
        formatted_text = "<|startoftext|>"
        
        for turn in conversation:
            speaker = turn['speaker']
            message = turn['message']
            
            # Clean up message
            message = message.replace('\n', ' ').strip()
            
            if speaker == 'client':
                formatted_text += f"\n<|client|> {message}"
            else:
                formatted_text += f"\n<|freelancer|> {message}"
        
        formatted_text += "\n<|endoftext|>"
        
        return formatted_text
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return self.examples[idx]

class ChatGPT2Trainer:
    """GPT-2 model trainer for chat conversations"""
    
    def __init__(self, model_name="gpt2", output_dir="ai/trained_models"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "advanced_chat_model"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "final_chat_model"), exist_ok=True)
        
        print(f"🔧 Using device: {self.device}")
        
    def load_model_and_tokenizer(self):
        """Load GPT-2 model and tokenizer"""
        
        print(f"🤖 Loading model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        
        # Add special tokens for chat
        special_tokens = {
            "additional_special_tokens": [
                "<|client|>", 
                "<|freelancer|>", 
                "<|startoftext|>", 
                "<|endoftext|>"
            ]
        }
        
        num_added = self.tokenizer.add_special_tokens(special_tokens)
        print(f"➕ Added {num_added} special tokens")
        
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.to(self.device)
        
        print(f"📊 Model loaded. Vocab size: {len(self.tokenizer)}")
        
    def train_model(self, training_data_path, epochs=5, batch_size=1, learning_rate=3e-5):
        """Train the GPT-2 model on chat data"""
        
        print("🚀 Starting model training...")
        print(f"📋 Training parameters: epochs={epochs}, batch_size={batch_size}, lr={learning_rate}")
        
        # Load model and tokenizer
        self.load_model_and_tokenizer()
        
        # Create dataset
        dataset = ChatTrainingDataset(
            tokenizer=self.tokenizer,
            file_path=training_data_path,
            block_size=512
        )
        
        if len(dataset) == 0:
            raise ValueError("❌ No training examples found!")
        
        print(f"📊 Training on {len(dataset)} examples")
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=os.path.join(self.output_dir, "advanced_chat_model"),
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            save_steps=50,
            save_total_limit=2,
            prediction_loss_only=True,
            learning_rate=learning_rate,
            warmup_steps=20,
            logging_dir=os.path.join(self.output_dir, "logs"),
            logging_steps=5,
            remove_unused_columns=False,
            dataloader_drop_last=False
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset,
        )
        
        # Train the model
        print(f"🔥 Training for {epochs} epochs on {len(dataset)} examples...")
        trainer.train()
        
        # Save the trained model
        final_model_path = os.path.join(self.output_dir, "final_chat_model", "trained_chat_model_1.0")
        os.makedirs(final_model_path, exist_ok=True)
        
        trainer.save_model(final_model_path)
        self.tokenizer.save_pretrained(final_model_path)
        
        print(f"✅ Model training completed!")
        print(f"💾 Advanced model saved to: {os.path.join(self.output_dir, 'advanced_chat_model')}")
        print(f"🎯 Final model saved to: {final_model_path}")
        
        # Save training metadata
        self.save_training_metadata(final_model_path, training_data_path, epochs, batch_size, learning_rate, len(dataset))
        
        return final_model_path
    
    def save_training_metadata(self, model_path, training_data_path, epochs, batch_size, learning_rate, num_examples):
        """Save training metadata"""
        
        metadata = {
            "model_name": "trained_chat_model_1.0",
            "base_model": self.model_name,
            "training_data": training_data_path,
            "training_params": {
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "num_examples": num_examples
            },
            "trained_on": datetime.now().isoformat(),
            "device": str(self.device),
            "vocab_size": len(self.tokenizer),
            "conversation_data": "Upwork freelancer-client chat about iGaming writing project",
            "special_tokens": ["<|client|>", "<|freelancer|>", "<|startoftext|>", "<|endoftext|>"]
        }
        
        metadata_path = os.path.join(model_path, "training_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Training metadata saved to: {metadata_path}")

def analyze_training_data():
    """Analyze training data before training"""
    
    training_data_path = "ai/training_data.txt"
    
    if not os.path.exists(training_data_path):
        print(f"❌ Training data not found at: {training_data_path}")
        return False
    
    print("🔍 Analyzing training data...")
    
    with open(training_data_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"📄 Training data length: {len(content)} characters")
    print(f"📝 First 500 characters:\n{content[:500]}")
    
    # Count conversation participants
    noel_count = content.count("Noel Angeles")
    yuliia_count = content.count("Yuliia M") + content.count("YM")
    
    print(f"\n💬 Conversation analysis:")
    print(f"   👨‍💻 Noel Angeles messages: {noel_count}")
    print(f"   👩‍💼 Yuliia M messages: {yuliia_count}")
    print(f"   💫 Total conversation turns: {noel_count + yuliia_count}")
    
    return True

def main():
    """Main training function"""
    
    try:
        # Analyze data first
        if not analyze_training_data():
            return False
        
        # Set training data path
        training_data_path = "ai/training_data.txt"
        
        print(f"\n🎯 Starting GPT-2 training on Upwork chat data")
        
        # Initialize trainer
        trainer = ChatGPT2Trainer(model_name="gpt2")
        
        # Train model with optimized parameters for small dataset
        model_path = trainer.train_model(
            training_data_path=training_data_path,
            epochs=8,  # More epochs for better learning
            batch_size=1,  # Small batch size for limited data
            learning_rate=2e-5  # Lower learning rate for stable training
        )
        
        print(f"\n🎉 Training completed successfully!")
        print(f"🎯 Trained model available at: {model_path}")
        print(f"🚀 Ready to use trained model in chat generator!")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 Training successful!' if success else '❌ Training failed!'}")