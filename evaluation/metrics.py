from typing import List, Dict
import json
from agents.intent_classifier import IntentClassifier
from agents.orchestrator import OrchestratorAgent

class EvaluationMetrics:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.orchestrator = OrchestratorAgent()
        self.test_cases = self._load_test_cases()
    
    def evaluate_intent_accuracy(self) -> Dict[str, float]:
        """Evaluate intent classification accuracy on test dataset"""
        correct = 0
        total = len(self.test_cases)
        intent_breakdown = {}
        
        for test_case in self.test_cases:
            query = test_case["query"]
            expected_intent = test_case["expected_intent"]
            
            result = self.intent_classifier.classify(query)
            predicted_intent = result["intent"]
            
            # Track per-intent accuracy
            if expected_intent not in intent_breakdown:
                intent_breakdown[expected_intent] = {"correct": 0, "total": 0}
            
            intent_breakdown[expected_intent]["total"] += 1
            
            if predicted_intent == expected_intent:
                correct += 1
                intent_breakdown[expected_intent]["correct"] += 1
        
        # Calculate per-intent accuracy
        for intent in intent_breakdown:
            breakdown = intent_breakdown[intent]
            breakdown["accuracy"] = breakdown["correct"] / breakdown["total"]
        
        return {
            "overall_accuracy": correct / total,
            "total_cases": total,
            "correct_predictions": correct,
            "per_intent_accuracy": intent_breakdown
        }
    
    def evaluate_confidence_calibration(self) -> Dict[str, float]:
        """Evaluate how well confidence scores correlate with accuracy"""
        high_conf_correct = 0
        high_conf_total = 0
        low_conf_correct = 0
        low_conf_total = 0
        
        for test_case in self.test_cases:
            query = test_case["query"]
            expected_intent = test_case["expected_intent"]
            
            result = self.intent_classifier.classify(query)
            predicted_intent = result["intent"]
            confidence = result["confidence"]
            
            is_correct = predicted_intent == expected_intent
            
            if confidence >= 0.8:  # High confidence
                high_conf_total += 1
                if is_correct:
                    high_conf_correct += 1
            else:  # Low confidence
                low_conf_total += 1
                if is_correct:
                    low_conf_correct += 1
        
        return {
            "high_confidence_accuracy": high_conf_correct / max(high_conf_total, 1),
            "low_confidence_accuracy": low_conf_correct / max(low_conf_total, 1),
            "high_confidence_cases": high_conf_total,
            "low_confidence_cases": low_conf_total
        }
    
    def evaluate_end_to_end_system(self) -> Dict[str, float]:
        """Evaluate the complete orchestrator system"""
        successful_routes = 0
        appropriate_escalations = 0
        total_cases = len(self.test_cases)
        
        for test_case in self.test_cases:
            query = test_case["query"]
            expected_intent = test_case["expected_intent"]
            should_escalate = test_case.get("should_escalate", False)
            
            try:
                result = self.orchestrator.process_query(
                    query, 
                    customer_context={"account_id": "TEST123"}
                )
                
                # Check if routing was appropriate
                if result["intent"] == expected_intent:
                    successful_routes += 1
                
                # Check escalation decisions
                if should_escalate == result["requires_escalation"]:
                    appropriate_escalations += 1
                    
            except Exception as e:
                print(f"Error processing query: {query}, Error: {e}")
        
        return {
            "routing_accuracy": successful_routes / total_cases,
            "escalation_accuracy": appropriate_escalations / total_cases,
            "total_test_cases": total_cases
        }
    
    def _load_test_cases(self) -> List[Dict]:
        """Load test cases from JSON file or return default set"""
        try:
            with open("evaluation/test_cases.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default test cases
            return [
                {
                    "query": "My bill is higher than usual this month",
                    "expected_intent": "billing_inquiry",
                    "should_escalate": False
                },
                {
                    "query": "I forgot my password and can't log in",
                    "expected_intent": "account_management", 
                    "should_escalate": False
                },
                {
                    "query": "I want to cancel my service immediately",
                    "expected_intent": "escalation",
                    "should_escalate": True
                },
                {
                    "query": "What plans do you offer for families?",
                    "expected_intent": "general_info",
                    "should_escalate": False
                },
                {
                    "query": "I'm very unhappy with your service and want to speak to a manager",
                    "expected_intent": "escalation",
                    "should_escalate": True
                }
            ]
    
    def run_full_evaluation(self) -> Dict:
        """Run complete evaluation suite"""
        return {
            "intent_classification": self.evaluate_intent_accuracy(),
            "confidence_calibration": self.evaluate_confidence_calibration(),
            "end_to_end_system": self.evaluate_end_to_end_system()
        }