import pytest
from agents.intent_classifier import IntentClassifier
from agents.orchestrator import OrchestratorAgent
from agents.conversation_memory import ConversationMemory

class TestIntentClassifier:
    def setup_method(self):
        self.classifier = IntentClassifier()
    
    def test_billing_intent(self):
        result = self.classifier.classify("My bill is too high")
        assert result["intent"] == "billing_inquiry"
        assert result["confidence"] > 0.5
    
    def test_account_intent(self):
        result = self.classifier.classify("I forgot my password")
        assert result["intent"] == "account_management"
        assert result["confidence"] > 0.5
    
    def test_escalation_intent(self):
        result = self.classifier.classify("I want to speak to a manager")
        assert result["intent"] == "escalation"
        assert result["confidence"] > 0.5

class TestConversationMemory:
    def setup_method(self):
        self.memory = ConversationMemory(max_turns=5)
    
    def test_add_message(self):
        self.memory.add_message("user1", "user", "Hello")
        messages = self.memory.get_conversation("user1")
        assert len(messages) == 1
        assert messages[0]["content"] == "Hello"
    
    def test_context_summary(self):
        self.memory.add_message("user1", "user", "My bill is high")
        self.memory.add_message("user1", "assistant", "I can help", {"intent": "billing_inquiry"})
        summary = self.memory.get_context_summary("user1")
        assert "billing_inquiry" in summary
    
    def test_max_turns_limit(self):
        for i in range(10):
            self.memory.add_message("user1", "user", f"Message {i}")
        messages = self.memory.get_conversation("user1")
        assert len(messages) == 5  # max_turns limit

class TestOrchestrator:
    def setup_method(self):
        self.orchestrator = OrchestratorAgent()
    
    def test_billing_routing(self):
        result = self.orchestrator.process_query("Why is my bill $100?", user_id="test1")
        assert result["intent"] == "billing_inquiry"
        assert len(result["response"]) > 0
    
    def test_conversation_memory(self):
        # First query
        self.orchestrator.process_query("My bill is high", user_id="test2")
        # Second query should have context
        result = self.orchestrator.process_query("Why is that?", user_id="test2")
        assert len(result["response"]) > 0