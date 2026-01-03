from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json

class IntentClassifier:
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)
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
            
        except (json.JSONDecodeError, Exception) as e:
            # Fallback for parsing errors
            return {
                "intent": "escalation",
                "confidence": 0.3
            }