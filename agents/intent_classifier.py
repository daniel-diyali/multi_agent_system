from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os

class IntentClassifier:
    def __init__(self):
        try:
            self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)
            self.api_available = True
        except Exception:
            self.model = None
            self.api_available = False
            
        self.prompt = ChatPromptTemplate.from_template("""
You are an expert intent classifier for customer service queries.

Classify this customer query into ONE of these intents:
- billing_inquiry: Questions about bills, charges, pricing, payments
- account_management: Password reset, plan changes, upgrades, account info
- technical_support: Network issues, 5G coverage, speed problems, device issues
- complaint: Complaints about service, billing disputes, dissatisfaction
- general_info: Information about plans, features, coverage areas
- escalation: Explicit request for human agent or supervisor

Customer Query: {query}

Respond with valid JSON only:
{{"intent": "intent_name", "confidence": 0.95}}

Confidence should be 0.0-1.0 based on how certain you are.
""")
    
    def classify(self, query: str) -> dict:
        # Use fallback if API is not available
        if not self.api_available:
            return self._fallback_classify(query)
            
        try:
            response = self.model.invoke(
                self.prompt.format_messages(query=query)
            )
            
            # Parse JSON response
            result = json.loads(response.content)
            
            # Validate confidence is between 0 and 1
            confidence = max(0.0, min(1.0, result.get("confidence", 0.5)))
            
            return {
                "intent": result.get("intent", "general_info"),
                "confidence": confidence
            }
            
        except Exception as e:
            # Fallback with rule-based classification when API fails
            return self._fallback_classify(query)
    
    def _fallback_classify(self, query: str) -> dict:
        """Rule-based fallback when OpenAI API is unavailable"""
        query_lower = query.lower().strip()
        
        # Greeting keywords - handle simple greetings
        if query_lower in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']:
            return {"intent": "general_info", "confidence": 0.9}
        
        # Billing keywords
        elif any(word in query_lower for word in ['bill', 'charge', 'payment', 'cost', 'fee', 'invoice']):
            return {"intent": "billing_inquiry", "confidence": 0.8}
        
        # Account keywords
        elif any(word in query_lower for word in ['password', 'account', 'login', 'upgrade', 'plan', 'change']):
            return {"intent": "account_management", "confidence": 0.8}
        
        # Technical keywords
        elif any(word in query_lower for word in ['network', 'signal', 'speed', 'connection', 'outage', 'technical']):
            return {"intent": "technical_support", "confidence": 0.8}
        
        # Complaint keywords
        elif any(word in query_lower for word in ['complaint', 'angry', 'frustrated', 'terrible', 'awful']):
            return {"intent": "complaint", "confidence": 0.8}
        
        # Escalation keywords
        elif any(word in query_lower for word in ['manager', 'supervisor', 'human', 'agent', 'cancel']):
            return {"intent": "escalation", "confidence": 0.9}
        
        # Default to general info with lower confidence
        else:
            return {"intent": "general_info", "confidence": 0.6}