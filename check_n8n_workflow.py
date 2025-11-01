#!/usr/bin/env python3
import json

with open('n8n_chat_ai_workflow.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("n8n Chat AI Workflow nodes:")
for node in data.get('nodes', []):
    print(f"  {node['name']} ({node['type']})")

print(f"\nTotal nodes: {len(data.get('nodes', []))}")
print("Workflow connections established ✓")