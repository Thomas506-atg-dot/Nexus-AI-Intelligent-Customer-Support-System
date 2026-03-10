"""
Simple JSON-based storage (no SQLAlchemy needed)
"""

import json
import os
from datetime import datetime
import pandas as pd

DATA_FILE = 'conversations.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'conversations': [], 'tickets': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def save_conversation(customer_id, message, response, sentiment, severity, intent, escalated=False, ticket_id=None):
    data = load_data()
    data['conversations'].append({
        'id': len(data['conversations']) + 1,
        'customer_id': customer_id,
        'message': message,
        'response': response,
        'sentiment': sentiment,
        'severity': severity,
        'intent': intent,
        'escalated': escalated,
        'ticket_id': ticket_id,
        'timestamp': datetime.now().isoformat()
    })
    save_data(data)

def create_ticket(customer_id, issue_type, priority):
    data = load_data()
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    data['tickets'].append({
        'ticket_id': ticket_id,
        'customer_id': customer_id,
        'issue_type': issue_type,
        'priority': priority,
        'status': 'OPEN',
        'created_at': datetime.now().isoformat()
    })
    save_data(data)
    return ticket_id

def get_all_conversations():
    data = load_data()
    return pd.DataFrame(data['conversations'])

def get_escalated_conversations():
    data = load_data()
    escalated = [c for c in data['conversations'] if c['escalated']]
    return pd.DataFrame(escalated)

def get_analytics():
    data = load_data()
    convs = data['conversations']
    
    if not convs:
        return {
            'total_chats': 0,
            'escalated': 0,
            'escalation_rate': 0,
            'avg_severity': 0,
            'sentiment_distribution': {}
        }
    
    total = len(convs)
    escalated = sum(1 for c in convs if c['escalated'])
    avg_severity = sum(c['severity'] for c in convs) / total
    
    # Sentiment distribution
    sentiments = {}
    for c in convs:
        s = c['sentiment']
        sentiments[s] = sentiments.get(s, 0) + 1
    
    return {
        'total_chats': total,
        'escalated': escalated,
        'escalation_rate': (escalated/total*100),
        'avg_severity': round(avg_severity, 2),
        'sentiment_distribution': sentiments
    }

def init_sample_orders():
    pass  # No orders in simple version

def get_order_status(order_id, customer_id):
    return None  # No orders in simple version