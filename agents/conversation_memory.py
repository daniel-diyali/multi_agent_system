from typing import List, Dict
from datetime import datetime, timedelta

class ConversationMemory:
    def __init__(self, max_turns: int = 10, ttl_minutes: int = 30):
        self.conversations = {}
        self.max_turns = max_turns
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                "messages": [],
                "last_updated": datetime.now(),
                "context": {}
            }
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        
        self.conversations[user_id]["messages"].append(message)
        self.conversations[user_id]["last_updated"] = datetime.now()
        
        # Keep only recent messages
        if len(self.conversations[user_id]["messages"]) > self.max_turns:
            self.conversations[user_id]["messages"] = self.conversations[user_id]["messages"][-self.max_turns:]
    
    def get_conversation(self, user_id: str) -> List[Dict]:
        """Get conversation history for user"""
        if user_id not in self.conversations:
            return []
        
        # Check if conversation expired
        if datetime.now() - self.conversations[user_id]["last_updated"] > self.ttl:
            del self.conversations[user_id]
            return []
        
        return self.conversations[user_id]["messages"]
    
    def get_context_summary(self, user_id: str) -> str:
        """Generate context summary for current conversation"""
        messages = self.get_conversation(user_id)
        if not messages:
            return ""
        
        # Extract key context from recent messages
        context_parts = []
        for msg in messages[-3:]:  # Last 3 messages
            if msg["role"] == "user":
                context_parts.append(f"Customer asked: {msg['content']}")
            elif "intent" in msg.get("metadata", {}):
                intent = msg["metadata"]["intent"]
                context_parts.append(f"Classified as: {intent}")
        
        return " | ".join(context_parts)