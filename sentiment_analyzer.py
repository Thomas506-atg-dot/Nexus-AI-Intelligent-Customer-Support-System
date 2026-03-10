from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self):
        self.urgent_keywords = ['urgent', 'angry', 'refund', 'cancel', 'terrible', 'worst', 'hate', 'complaint']
        self.intent_patterns = {
            'ORDER': ['order', 'track', 'shipping', 'delivery'],
            'REFUND': ['refund', 'return', 'money back'],
            'COMPLAINT': ['complaint', 'issue', 'problem', 'broken']
        }
    
    def analyze(self, text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            label = 'POSITIVE'
        elif polarity < -0.1:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        text_lower = text.lower()
        severity = int((1 - polarity) * 5) + sum(1 for kw in self.urgent_keywords if kw in text_lower) * 2
        if text.isupper():
            severity += 3
        severity = min(10, max(1, severity))
        
        intent = 'GENERAL'
        for int_name, keywords in self.intent_patterns.items():
            if any(kw in text_lower for kw in keywords):
                intent = int_name
                break
        
        return {'label': label, 'severity': severity, 'intent': intent}
    
    def should_escalate(self, analysis):
        return analysis['severity'] >= 7

analyzer = SentimentAnalyzer()