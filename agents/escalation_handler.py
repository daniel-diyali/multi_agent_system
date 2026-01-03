from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class EscalationHandler:
    def __init__(self):
        try:
            self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.2)
            self.api_available = True
        except Exception:
            self.model = None
            self.api_available = False
            
        self.prompt = ChatPromptTemplate.from_template("""
You are an escalation handler for customer service. Your role is to:
1. Acknowledge the customer's concern
2. Explain why their issue requires human assistance
3. Provide clear next steps for escalation
4. Set appropriate expectations for response time

Customer Context:
- Account ID: {account_id}
- Issue Complexity: {complexity_reason}

Customer Query: {query}

Provide a professional, empathetic response that explains the escalation process.
Include estimated response times and what information the human agent will have access to.

Response:""")
    
    def handle_query(self, query: str, customer_context: dict) -> str:
        # Use fallback if API is not available
        if not self.api_available:
            complexity_reason = self._determine_complexity(query)
            return self._fallback_response(query, customer_context, complexity_reason)
            
        # Determine complexity reason
        complexity_reason = self._determine_complexity(query)
        account_id = customer_context.get("account_id", "Unknown")
        
        try:
            response = self.model.invoke(
                self.prompt.format_messages(
                    query=query,
                    account_id=account_id,
                    complexity_reason=complexity_reason
                )
            )
            return response.content
        except Exception:
            # Fallback response when API is unavailable
            return self._fallback_response(query, customer_context, complexity_reason)
    
    def _fallback_response(self, query: str, customer_context: dict, complexity_reason: str) -> str:
        """Provide fallback response when OpenAI API is unavailable"""
        account_id = customer_context.get("account_id", "your account")
        
        return f"""I understand your concern regarding {account_id}. {complexity_reason}, so I'm connecting you with a human specialist who can provide personalized assistance.

What happens next:
• A specialist will contact you within 24 hours
• They'll have access to your full account history
• You'll receive a reference number for this request

Is there anything else I can help clarify while we arrange this connection?"""
    
    def _determine_complexity(self, query: str) -> str:
        """Determine why this query needs human escalation"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["cancel", "disconnect", "terminate"]):
            return "Account cancellation requires human verification"
        elif any(word in query_lower for word in ["complaint", "dissatisfied", "angry"]):
            return "Customer complaint requires personalized attention"
        elif any(word in query_lower for word in ["legal", "lawsuit", "attorney"]):
            return "Legal matter requires specialized handling"
        elif any(word in query_lower for word in ["supervisor", "manager", "human"]):
            return "Customer explicitly requested human agent"
        else:
            return "Complex issue requiring human expertise"