from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from agents.intent_classifier import IntentClassifier
from agents.billing_specialist import BillingSpecialist
from agents.account_specialist import AccountSpecialist
from agents.escalation_handler import EscalationHandler

class AgentState(TypedDict):
    messages: list
    current_intent: str
    confidence: float
    customer_context: dict
    response: str
    requires_escalation: bool

class OrchestratorAgent:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.billing_agent = BillingSpecialist()
        self.account_agent = AccountSpecialist()
        self.escalation_agent = EscalationHandler()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("billing_specialist", self._billing_specialist)
        workflow.add_node("account_specialist", self._account_specialist)
        workflow.add_node("escalation_handler", self._escalation_handler)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_to_specialist,
            {
                "billing": "billing_specialist",
                "account": "account_specialist", 
                "escalation": "escalation_handler"
            }
        )
        
        # All specialists end the workflow
        workflow.add_edge("billing_specialist", END)
        workflow.add_edge("account_specialist", END)
        workflow.add_edge("escalation_handler", END)
        
        return workflow.compile()
    
    def _classify_intent(self, state: AgentState) -> AgentState:
        query = state["messages"][-1]["content"]
        result = self.intent_classifier.classify(query)
        
        state["current_intent"] = result["intent"]
        state["confidence"] = result["confidence"]
        return state
    
    def _route_to_specialist(self, state: AgentState) -> Literal["billing", "account", "escalation"]:
        intent = state["current_intent"]
        confidence = state["confidence"]
        
        # Low confidence -> escalate
        if confidence < 0.7:
            return "escalation"
        
        # Route based on intent
        if intent in ["billing_inquiry", "payment_issue"]:
            return "billing"
        elif intent in ["account_management", "password_reset"]:
            return "account"
        else:
            return "escalation"
    
    def _billing_specialist(self, state: AgentState) -> AgentState:
        query = state["messages"][-1]["content"]
        response = self.billing_agent.handle_query(query, state["customer_context"])
        state["response"] = response
        return state
    
    def _account_specialist(self, state: AgentState) -> AgentState:
        query = state["messages"][-1]["content"]
        response = self.account_agent.handle_query(query, state["customer_context"])
        state["response"] = response
        return state
    
    def _escalation_handler(self, state: AgentState) -> AgentState:
        query = state["messages"][-1]["content"]
        response = self.escalation_agent.handle_query(query, state["customer_context"])
        state["response"] = response
        state["requires_escalation"] = True
        return state
    
    def process_query(self, query: str, customer_context: dict = None) -> dict:
        initial_state = {
            "messages": [{"role": "user", "content": query}],
            "current_intent": "",
            "confidence": 0.0,
            "customer_context": customer_context or {},
            "response": "",
            "requires_escalation": False
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "response": result["response"],
            "intent": result["current_intent"],
            "confidence": result["confidence"],
            "requires_escalation": result["requires_escalation"]
        }