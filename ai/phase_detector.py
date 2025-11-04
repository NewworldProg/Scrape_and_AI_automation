"""
Phase Classifier Inference
Uses trained model to detect conversation phases
"""
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
import json
import os
from datetime import datetime

# Set UTF-8 encoding
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class PhaseClassifier(nn.Module):
    """BERT-based phase classifier (same architecture as training)"""
    
    def __init__(self, n_classes=8, dropout=0.3):
        super(PhaseClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, n_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)


class PhaseDetector:
    """Load and use trained phase classifier"""
    
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load metadata
        metadata_path = os.path.join(model_dir, 'metadata.json')
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        self.phase_labels = self.metadata['phase_labels']
        self.id_to_phase = {int(k): v for k, v in self.metadata['id_to_phase'].items()}
        
        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(model_dir)
        
        # Load model
        self.model = PhaseClassifier(n_classes=len(self.phase_labels))
        model_path = os.path.join(model_dir, 'phase_classifier.pth')
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        print(f"[OK] Phase classifier loaded from {model_dir}")
        print(f"[INFO] Model trained on {self.metadata.get('training_samples', 'unknown')} samples")
        print(f"[INFO] Accuracy: {self.metadata.get('accuracy', 'unknown'):.2f}%")
    
    def predict(self, context, return_probabilities=False):
        """Predict conversation phase from context"""
        # Tokenize
        encoding = self.tokenizer.encode_plus(
            context,
            add_special_tokens=True,
            max_length=256,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_phase = self.id_to_phase[predicted.item()]
        confidence_score = confidence.item()
        
        result = {
            'phase': predicted_phase,
            'confidence': round(confidence_score, 4)
        }
        
        if return_probabilities:
            all_probs = {
                self.phase_labels[i]: round(probabilities[0][i].item(), 4)
                for i in range(len(self.phase_labels))
            }
            result['all_probabilities'] = all_probs
        
        return result
    
    def predict_batch(self, contexts):
        """Predict phases for multiple contexts"""
        results = []
        for context in contexts:
            result = self.predict(context)
            results.append(result)
        return results


def test_detector():
    """Test the phase detector"""
    print("=" * 60)
    print("TESTING PHASE DETECTOR")
    print("=" * 60)
    
    model_dir = os.path.join(os.path.dirname(__file__), 'trained_models', 'phase_classifier_v1')
    
    if not os.path.exists(model_dir):
        print(f"[ERROR] Model not found at {model_dir}")
        print("[INFO] Please train the model first using train_phase_classifier.py")
        return
    
    detector = PhaseDetector(model_dir)
    
    # Test cases
    test_cases = [
        "Hello! I saw your application. Are you available?",
        "We need content about casino games. Can you handle technical topics?",
        "Can you explain what RTP means in slot machines?",
        "Which language do you prefer - English or Dutch?",
        "Our budget is $0.06 per word. Does that work?",
        "We need the first batch by Monday. Can you deliver?",
        "Each article needs H1, H2s, and FAQ section with SEO.",
        "I'm sending the contract now. Please accept to start."
    ]
    
    print("\n[INFO] Testing with sample contexts:\n")
    
    for i, context in enumerate(test_cases, 1):
        result = detector.predict(context, return_probabilities=True)
        print(f"{i}. Context: \"{context}\"")
        print(f"   → Phase: {result['phase']}")
        print(f"   → Confidence: {result['confidence']:.2%}")
        print(f"   → Top 3 probabilities:")
        
        sorted_probs = sorted(result['all_probabilities'].items(), key=lambda x: x[1], reverse=True)[:3]
        for phase, prob in sorted_probs:
            print(f"      - {phase}: {prob:.2%}")
        print()


if __name__ == "__main__":
    test_detector()
