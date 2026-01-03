from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from rag.retriever import KnowledgeBaseRetriever

class AccountSpecialist:
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
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
        # Retrieve relevant account information
        context_docs = self.retriever.retrieve(query, k=3)
        context = "\n".join([doc.page_content for doc in context_docs])
        
        # Format customer context
        account_id = customer_context.get("account_id", "Unknown")
        account_status = customer_context.get("account_status", "Active")
        plan_type = customer_context.get("plan_type", "Individual")
        account_since = customer_context.get("account_since", "2023")
        
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