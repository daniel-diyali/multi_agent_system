from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from rag.retriever import KnowledgeBaseRetriever

class BillingSpecialist:
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
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
        # Retrieve relevant billing information
        context_docs = self.retriever.retrieve(query, k=3)
        context = "\n".join([doc.page_content for doc in context_docs])
        
        # Format customer context
        account_id = customer_context.get("account_id", "Unknown")
        current_plan = customer_context.get("current_plan", "Standard Plan")
        last_bill = customer_context.get("last_bill", "$0.00")
        
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