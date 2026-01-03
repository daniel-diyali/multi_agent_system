from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from rag.retriever import KnowledgeBaseRetriever

class BillingSpecialist:
    def __init__(self):
        try:
            self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
            self.api_available = True
        except Exception:
            self.model = None
            self.api_available = False
            
        self.retriever = KnowledgeBaseRetriever("data/sample_data/billing")
        self.prompt = ChatPromptTemplate.from_template("""
You are a billing specialist for a telecommunications company. 
You help customers with billing questions, payment issues, and account charges.

Customer Context:
- Account ID: {account_id}
- Current Plan: {current_plan}
- Last Bill Amount: {last_bill}

Relevant Knowledge Base Information:
{context}

Customer Query: {query}

Provide a helpful, accurate response. If you cannot resolve the issue completely, 
suggest next steps or escalation to billing department.

Response:""")
    
    def handle_query(self, query: str, customer_context: dict) -> str:
        # Use fallback if API is not available
        if not self.api_available:
            return self._fallback_response(query, customer_context)
            
        # Try to retrieve relevant billing information
        try:
            context_docs = self.retriever.retrieve(query, k=3)
            context = "\n".join([doc.page_content for doc in context_docs])
        except Exception:
            context = "No additional context available."
        
        # Format customer context
        account_id = customer_context.get("account_id", "Unknown")
        current_plan = customer_context.get("current_plan", "Standard Plan")
        last_bill = customer_context.get("last_bill", "$0.00")
        
        try:
            response = self.model.invoke(
                self.prompt.format_messages(
                    query=query,
                    context=context,
                    account_id=account_id,
                    current_plan=current_plan,
                    last_bill=last_bill
                )
            )
            return response.content
        except Exception:
            # Fallback response when API is unavailable
            return self._fallback_response(query, customer_context)
    
    def _fallback_response(self, query: str, customer_context: dict) -> str:
        """Provide fallback response when OpenAI API is unavailable"""
        account_id = customer_context.get("account_id", "your account")
        
        if "bill" in query.lower() or "charge" in query.lower():
            return f"I understand you have a billing question regarding {account_id}. Let me help you with that. For detailed billing information, I can connect you with our billing department or you can check your account online."
        elif "payment" in query.lower():
            return f"For payment assistance on {account_id}, I can help you set up automatic payments or provide payment options. Would you like me to guide you through the payment process?"
        else:
            return f"I'm here to help with your billing inquiry for {account_id}. Could you please provide more specific details about what you'd like assistance with?"