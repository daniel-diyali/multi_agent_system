from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from rag.retriever import KnowledgeBaseRetriever

class AccountSpecialist:
    def __init__(self):
        try:
            self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
            self.api_available = True
        except Exception:
            self.model = None
            self.api_available = False
            
        self.retriever = KnowledgeBaseRetriever("data/sample_data/account")
        self.prompt = ChatPromptTemplate.from_template("""
You are an account management specialist for a telecommunications company.
You help customers with account changes, password resets, plan upgrades, and account information.

Customer Context:
- Account ID: {account_id}
- Account Status: {account_status}
- Plan Type: {plan_type}
- Account Since: {account_since}

Relevant Knowledge Base Information:
{context}

Customer Query: {query}

Provide step-by-step instructions when possible. For security-sensitive operations 
like password resets, explain the verification process required.

Response:""")
    
    def handle_query(self, query: str, customer_context: dict) -> str:
        # Use fallback if API is not available
        if not self.api_available:
            return self._fallback_response(query, customer_context)
            
        # Try to retrieve relevant account information
        try:
            context_docs = self.retriever.retrieve(query, k=3)
            context = "\n".join([doc.page_content for doc in context_docs])
        except Exception:
            context = "No additional context available."
        
        # Format customer context
        account_id = customer_context.get("account_id", "Unknown")
        account_status = customer_context.get("account_status", "Active")
        plan_type = customer_context.get("plan_type", "Individual")
        account_since = customer_context.get("account_since", "2023")
        
        try:
            response = self.model.invoke(
                self.prompt.format_messages(
                    query=query,
                    context=context,
                    account_id=account_id,
                    account_status=account_status,
                    plan_type=plan_type,
                    account_since=account_since
                )
            )
            return response.content
        except Exception:
            # Fallback response when API is unavailable
            return self._fallback_response(query, customer_context)
    
    def _fallback_response(self, query: str, customer_context: dict) -> str:
        """Provide fallback response when OpenAI API is unavailable"""
        account_id = customer_context.get("account_id", "your account")
        query_lower = query.lower().strip()
        
        # Handle greetings
        if query_lower in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']:
            return f"Hello! Welcome to customer service. I'm here to help you with {account_id}. How can I assist you today? I can help with billing questions, account changes, password resets, and more."
        
        # Handle general info requests
        elif "plan" in query_lower or "service" in query_lower:
            return f"I'm here to help with your account {account_id}. We offer various plans and services. Would you like information about upgrading your plan, checking your current services, or something else?"
        
        else:
            return f"I'm your account specialist and I'm here to help with {account_id}. Could you please specify what account-related assistance you need?"