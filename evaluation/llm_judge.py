from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
from typing import Dict, List

class LLMJudge:
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)
        self.evaluation_prompt = ChatPromptTemplate.from_template("""
You are an expert evaluator for customer service AI responses.

Evaluate this customer service interaction on a scale of 1-5 for each criterion:

Customer Query: {query}
AI Response: {response}
Intent Classification: {intent}
Customer Context: {context}

Rate each criterion (1=Poor, 5=Excellent):

1. RELEVANCE: How well does the response address the customer's specific question?
2. ACCURACY: Is the information provided correct and helpful?
3. CLARITY: Is the response clear and easy to understand?
4. EMPATHY: Does the response show appropriate understanding of customer needs?
5. COMPLETENESS: Does the response fully address the query or provide next steps?

Respond with valid JSON only:
{{
  "relevance": 4,
  "accuracy": 5,
  "clarity": 4,
  "empathy": 3,
  "completeness": 4,
  "overall_score": 4.0,
  "reasoning": "Brief explanation of the scores"
}}
""")
    
    def evaluate_response(self, query: str, response: str, intent: str, context: Dict = None) -> Dict:
        """Evaluate a single response using LLM-as-judge"""
        try:
            context_str = json.dumps(context) if context else "No context provided"
            
            result = self.model.invoke(
                self.evaluation_prompt.format_messages(
                    query=query,
                    response=response,
                    intent=intent,
                    context=context_str
                )
            )
            
            evaluation = json.loads(result.content)
            
            # Ensure all scores are valid
            for key in ["relevance", "accuracy", "clarity", "empathy", "completeness"]:
                evaluation[key] = max(1, min(5, evaluation.get(key, 3)))
            
            # Calculate overall score
            scores = [evaluation[key] for key in ["relevance", "accuracy", "clarity", "empathy", "completeness"]]
            evaluation["overall_score"] = sum(scores) / len(scores)
            
            return evaluation
            
        except Exception as e:
            return {
                "relevance": 3,
                "accuracy": 3,
                "clarity": 3,
                "empathy": 3,
                "completeness": 3,
                "overall_score": 3.0,
                "reasoning": f"Evaluation failed: {str(e)}"
            }
    
    def batch_evaluate(self, test_cases: List[Dict]) -> Dict:
        """Evaluate multiple responses and return aggregate metrics"""
        evaluations = []
        
        for case in test_cases:
            evaluation = self.evaluate_response(
                case["query"],
                case["response"],
                case.get("intent", "unknown"),
                case.get("context", {})
            )
            evaluations.append(evaluation)
        
        # Calculate aggregate metrics
        metrics = {}
        criteria = ["relevance", "accuracy", "clarity", "empathy", "completeness", "overall_score"]
        
        for criterion in criteria:
            scores = [eval[criterion] for eval in evaluations]
            metrics[f"avg_{criterion}"] = sum(scores) / len(scores)
            metrics[f"min_{criterion}"] = min(scores)
            metrics[f"max_{criterion}"] = max(scores)
        
        # Quality distribution
        overall_scores = [eval["overall_score"] for eval in evaluations]
        metrics["excellent_responses"] = len([s for s in overall_scores if s >= 4.5]) / len(overall_scores)
        metrics["good_responses"] = len([s for s in overall_scores if 3.5 <= s < 4.5]) / len(overall_scores)
        metrics["poor_responses"] = len([s for s in overall_scores if s < 3.5]) / len(overall_scores)
        
        return {
            "aggregate_metrics": metrics,
            "individual_evaluations": evaluations,
            "total_evaluated": len(evaluations)
        }