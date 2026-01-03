import asyncio
import json
import websockets
from typing import Dict, Callable
from agents.orchestrator import OrchestratorAgent

class VoiceAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.orchestrator = OrchestratorAgent()
        self.websocket = None
        self.session_config = {
            "modalities": ["text", "audio"],
            "instructions": "You are a helpful customer service agent. Respond naturally and conversationally.",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "turn_detection": {"type": "server_vad"}
        }
    
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        self.websocket = await websockets.connect(uri, extra_headers=headers)
        
        # Send session configuration
        await self.websocket.send(json.dumps({
            "type": "session.update",
            "session": self.session_config
        }))
    
    async def handle_voice_conversation(self, user_id: str, audio_callback: Callable = None):
        """Handle real-time voice conversation"""
        if not self.websocket:
            await self.connect()
        
        try:
            async for message in self.websocket:
                event = json.loads(message)
                await self._handle_event(event, user_id, audio_callback)
        except websockets.exceptions.ConnectionClosed:
            print("Voice connection closed")
    
    async def _handle_event(self, event: Dict, user_id: str, audio_callback: Callable):
        """Handle different types of events from Realtime API"""
        event_type = event.get("type")
        
        if event_type == "conversation.item.input_audio_transcription.completed":
            # User speech transcribed
            transcript = event["transcript"]
            print(f"User said: {transcript}")
            
            # Process through our multi-agent system
            result = self.orchestrator.process_query(transcript, user_id=user_id)
            
            # Send response back to voice API
            await self._send_text_response(result["response"])
            
        elif event_type == "response.audio.delta":
            # Streaming audio response
            if audio_callback:
                audio_data = event["delta"]
                await audio_callback(audio_data)
                
        elif event_type == "response.done":
            print("Response completed")
    
    async def _send_text_response(self, text: str):
        """Send text response to be converted to speech"""
        await self.websocket.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": text}]
            }
        }))
        
        # Trigger response generation
        await self.websocket.send(json.dumps({
            "type": "response.create"
        }))
    
    async def send_audio_input(self, audio_data: bytes):
        """Send audio input to the API"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": audio_data.hex()
            }))
    
    async def disconnect(self):
        """Close the voice connection"""
        if self.websocket:
            await self.websocket.close()

# Example usage for testing
async def demo_voice_agent():
    """Demo function showing voice agent usage"""
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found")
        return
    
    voice_agent = VoiceAgent(api_key)
    
    async def audio_callback(audio_data):
        print(f"Received audio chunk: {len(audio_data)} bytes")
    
    try:
        await voice_agent.handle_voice_conversation("demo_user", audio_callback)
    except KeyboardInterrupt:
        await voice_agent.disconnect()
        print("Voice demo ended")

if __name__ == "__main__":
    asyncio.run(demo_voice_agent())