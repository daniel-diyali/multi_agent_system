from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.orchestrator import OrchestratorAgent
from evaluation.metrics import EvaluationMetrics
import uvicorn

app = FastAPI(
    title="Multi-Agent Customer Service API",
    description="T-Mobile-style intent-driven AI customer service system",
    version="1.0.0"
)

# Initialize agents
orchestrator = OrchestratorAgent()
evaluator = EvaluationMetrics()

class CustomerQuery(BaseModel):
    user_id: str
    message: str
    conversation_history: List[Dict] = []
    customer_context: Optional[Dict] = None

class AgentResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    requires_escalation: bool
    agent_used: str

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(query: CustomerQuery):
    """Main chat endpoint that routes queries through the orchestrator"""
    try:
        # Process query through orchestrator
        result = orchestrator.process_query(
            query.message, 
            query.customer_context or {}
        )
        
        # Determine which agent was used based on intent
        agent_mapping = {
            "billing_inquiry": "billing_specialist",
            "account_management": "account_specialist", 
            "escalation": "escalation_handler",
            "complaint": "escalation_handler",
            "general_info": "account_specialist",
            "technical_support": "escalation_handler"
        }
        
        agent_used = agent_mapping.get(result["intent"], "escalation_handler")
        
        return AgentResponse(
            response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
            requires_escalation=result["requires_escalation"],
            agent_used=agent_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/evaluate")
async def evaluate_system():
    """Run evaluation metrics on the system"""
    try:
        results = evaluator.run_full_evaluation()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running evaluation: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Multi-agent system is running"}

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Multi-Agent Customer Service System",
        "description": "Intent-driven AI system inspired by T-Mobile's IntentCX",
        "endpoints": {
            "chat": "/chat - Main customer service endpoint",
            "evaluate": "/evaluate - Run system evaluation",
            "health": "/health - Health check",
            "docs": "/docs - API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)