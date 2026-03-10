from database import create_ticket

class EscalationManager:
    def __init__(self):
        self.escalation_queue = []
    
    def escalate(self, customer_id, message, analysis):
        ticket_id = create_ticket(
            customer_id=customer_id,
            issue_type=analysis['intent'],
            priority=analysis['severity']
        )
        
        escalation_data = {
            'ticket_id': ticket_id,
            'customer_id': customer_id,
            'message': message,
            'severity': analysis['severity'],
            'sentiment': analysis['label']
        }
        self.escalation_queue.append(escalation_data)
        
        alert_msg = self._generate_alert(escalation_data)
        return ticket_id, alert_msg
    
    def _generate_alert(self, data):
        severity = data['severity']
        
        if severity >= 9:
            return f"""🚨 URGENT ESCALATION 🚨

Ticket #{data['ticket_id']} created.

A senior agent will contact you within 15 minutes."""
        
        elif severity >= 7:
            return f"""⚠️ Priority Support

Ticket #{data['ticket_id']} created.

A human agent will assist you within 1 hour."""
        
        else:
            return f"""Ticket #{data['ticket_id']} created.

Our team will review and respond shortly."""
    
    def get_queue(self):
        return self.escalation_queue

escalation_manager = EscalationManager()