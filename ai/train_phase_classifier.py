"""
Phase Classification Model Training
Trains a model to detect conversation phases with labels
"""
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import os
from datetime import datetime

# Set UTF-8 encoding
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Phase labels
PHASE_LABELS = [
    'initial_response',
    'ask_details', 
    'knowledge_check',
    'language_confirm',
    'rate_negotiation',
    'deadline_samples',
    'structure_clarification',
    'contract_acceptance'
]

PHASE_TO_ID = {phase: idx for idx, phase in enumerate(PHASE_LABELS)}
ID_TO_PHASE = {idx: phase for phase, idx in PHASE_TO_ID.items()}


class PhaseDataset(Dataset):
    """Dataset for conversation phase classification"""
    
    def __init__(self, contexts, phases, tokenizer, max_length=256):
        self.contexts = contexts
        self.phases = phases
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.contexts)
    
    def __getitem__(self, idx):
        context = str(self.contexts[idx])
        phase = self.phases[idx]
        
        encoding = self.tokenizer.encode_plus(
            context,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(PHASE_TO_ID[phase], dtype=torch.long)
        }


class PhaseClassifier(nn.Module):
    """BERT-based phase classifier"""
    
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


def load_training_data(file_path):
    """Load phase training data from JSON"""
    print(f"[INFO] Loading training data from {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    contexts = [item['context'] for item in data]
    phases = [item['phase'] for item in data]
    
    print(f"[OK] Loaded {len(contexts)} training examples")
    print(f"[INFO] Phase distribution:")
    for phase in PHASE_LABELS:
        count = phases.count(phase)
        print(f"  - {phase}: {count} examples")
    
    return contexts, phases


def train_model(model, train_loader, val_loader, epochs=10, learning_rate=2e-5, device='cpu'):
    """Train the phase classification model"""
    print(f"\n[INFO] Training model for {epochs} epochs...")
    print(f"[INFO] Device: {device}")
    
    model = model.to(device)
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for batch in train_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                
                outputs = model(input_ids, attention_mask)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        
        print(f"Epoch {epoch+1}/{epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            print(f"  [BEST] New best validation accuracy: {val_acc:.2f}%")
    
    return model


def evaluate_model(model, test_loader, device='cpu'):
    """Evaluate model and show classification report"""
    print("\n[INFO] Evaluating model...")
    
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, attention_mask)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Convert to phase names
    pred_phases = [ID_TO_PHASE[p] for p in all_preds]
    true_phases = [ID_TO_PHASE[l] for l in all_labels]
    
    print("\n=== Classification Report ===")
    print(classification_report(true_phases, pred_phases, target_names=PHASE_LABELS, zero_division=0))
    
    print("\n=== Confusion Matrix ===")
    cm = confusion_matrix(true_phases, pred_phases, labels=PHASE_LABELS)
    print("Labels:", PHASE_LABELS)
    print(cm)
    
    accuracy = 100 * sum([1 for p, t in zip(all_preds, all_labels) if p == t]) / len(all_labels)
    print(f"\n[RESULT] Overall Accuracy: {accuracy:.2f}%")
    
    return accuracy


def save_model(model, tokenizer, save_dir, metadata=None):
    """Save trained model and tokenizer"""
    print(f"\n[INFO] Saving model to {save_dir}...")
    
    os.makedirs(save_dir, exist_ok=True)
    
    # Save model
    torch.save(model.state_dict(), os.path.join(save_dir, 'phase_classifier.pth'))
    
    # Save tokenizer
    tokenizer.save_pretrained(save_dir)
    
    # Save metadata
    if metadata is None:
        metadata = {}
    
    metadata.update({
        'phase_labels': PHASE_LABELS,
        'phase_to_id': PHASE_TO_ID,
        'id_to_phase': ID_TO_PHASE,
        'model_type': 'bert-base-uncased',
        'n_classes': len(PHASE_LABELS),
        'trained_at': datetime.now().isoformat()
    })
    
    with open(os.path.join(save_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Model saved successfully!")


def main():
    """Main training function"""
    print("=" * 60)
    print("PHASE CLASSIFICATION MODEL TRAINING")
    print("=" * 60)
    
    # Configuration
    DATA_FILE = os.path.join(os.path.dirname(__file__), 'phase_training_data.json')
    SAVE_DIR = os.path.join(os.path.dirname(__file__), 'trained_models', 'phase_classifier_v1')
    BATCH_SIZE = 4
    EPOCHS = 20
    LEARNING_RATE = 2e-5
    TEST_SIZE = 0.15  # Smaller test set for small dataset
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[INFO] Using device: {device}")
    
    # Load data
    contexts, phases = load_training_data(DATA_FILE)
    
    # Split data
    train_contexts, test_contexts, train_phases, test_phases = train_test_split(
        contexts, phases, test_size=TEST_SIZE, random_state=42, stratify=phases
    )
    
    print(f"\n[INFO] Data split:")
    print(f"  Train: {len(train_contexts)} examples")
    print(f"  Test: {len(test_contexts)} examples")
    
    # Initialize tokenizer
    print(f"\n[INFO] Loading BERT tokenizer...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    # Create datasets
    train_dataset = PhaseDataset(train_contexts, train_phases, tokenizer)
    test_dataset = PhaseDataset(test_contexts, test_phases, tokenizer)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # Initialize model
    print(f"\n[INFO] Initializing model...")
    model = PhaseClassifier(n_classes=len(PHASE_LABELS))
    
    # Train model
    model = train_model(
        model, train_loader, test_loader,
        epochs=EPOCHS, learning_rate=LEARNING_RATE, device=device
    )
    
    # Evaluate model
    accuracy = evaluate_model(model, test_loader, device=device)
    
    # Save model
    metadata = {
        'training_samples': len(train_contexts),
        'test_samples': len(test_contexts),
        'accuracy': accuracy,
        'epochs': EPOCHS,
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE
    }
    save_model(model, tokenizer, SAVE_DIR, metadata)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model saved to: {SAVE_DIR}")
    print(f"Final accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    main()
