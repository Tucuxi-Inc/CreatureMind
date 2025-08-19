"""
AI Client - Generalized from WiddlePupper's OpenAIService.swift

Handles communication with AI services (OpenAI, Claude, etc.)
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import openai
from openai import AsyncOpenAI


class AIClient(ABC):
    """Abstract base class for AI service clients"""
    
    @abstractmethod
    async def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        chat_history: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate a response using the AI service"""
        pass


class OpenAIClient(AIClient):
    """
    OpenAI client implementation
    
    Adapted from WiddlePupper's OpenAIService.swift but with async Python patterns.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4.1-nano"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 2.0
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        chat_history: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using OpenAI API
        
        Includes retry logic and error handling similar to WiddlePupper's implementation.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            for message in chat_history[-10:]:  # Limit to last 10 messages
                messages.append(message)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
                
            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise
            
            except openai.APIError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
        
        raise Exception("Max retries exceeded")


class MockAIClient(AIClient):
    """Mock AI client for testing - provides realistic responses without OpenAI API"""
    
    def __init__(self):
        self.call_count = 0
        self.base_responses = {
            "perception": [
                "USER_TONE: friendly\nUSER_INTENT: greet\nRELEVANCE_TO_NEEDS: social interaction",
                "USER_TONE: excited\nUSER_INTENT: play\nRELEVANCE_TO_NEEDS: entertainment",
                "USER_TONE: caring\nUSER_INTENT: care\nRELEVANCE_TO_NEEDS: comfort",
                "USER_TONE: curious\nUSER_INTENT: explore\nRELEVANCE_TO_NEEDS: mental stimulation"
            ],
            "emotion": [
                "EMOTION: happy\nTRANSLATE: yes\nSTATE_CHANGES: happiness +5",
                "EMOTION: excited\nTRANSLATE: yes\nSTATE_CHANGES: happiness +8",
                "EMOTION: content\nTRANSLATE: yes\nSTATE_CHANGES: happiness +3",
                "EMOTION: curious\nTRANSLATE: yes\nSTATE_CHANGES: happiness +2"
            ],
            "memory": [
                "RELEVANT_MEMORIES: recent greeting\nPATTERNS: user is friendly",
                "RELEVANT_MEMORIES: previous play session\nPATTERNS: user likes interactive activities",
                "RELEVANT_MEMORIES: feeding time\nPATTERNS: user takes good care of me",
                "RELEVANT_MEMORIES: quiet time together\nPATTERNS: user provides comfort"
            ],
            "decision": [
                "ACTION: tail wag\nVOCALIZATION: happy bark\nINTENTION: show friendliness",
                "ACTION: playful bounce\nVOCALIZATION: excited yip\nINTENTION: invite play",
                "ACTION: gentle approach\nVOCALIZATION: soft whine\nINTENTION: seek comfort",
                "ACTION: alert posture\nVOCALIZATION: curious whuff\nINTENTION: investigate"
            ],
            "translation": [
                "CREATURE_LANGUAGE: *woof woof* *tail wagging*\nHUMAN_TRANSLATION: Hello there, friend! I'm so happy to see you!\nDEBUG: Enthusiastic greeting",
                "CREATURE_LANGUAGE: *excited yipping* *bouncing*\nHUMAN_TRANSLATION: Want to play? This looks like fun!\nDEBUG: Playful invitation",
                "CREATURE_LANGUAGE: *gentle whuff* *nuzzling motion*\nHUMAN_TRANSLATION: Thank you for taking care of me. I feel safe with you.\nDEBUG: Appreciative response",
                "CREATURE_LANGUAGE: *curious sniff* *head tilt*\nHUMAN_TRANSLATION: What's that? I'm interested in what you're doing!\nDEBUG: Inquisitive behavior",
                "CREATURE_LANGUAGE: *contented sigh* *relaxed posture*\nHUMAN_TRANSLATION: I'm feeling good right now. Life is peaceful.\nDEBUG: Satisfied state"
            ]
        }
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        chat_history: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Return varied mock responses for testing"""
        
        self.call_count += 1
        
        # Select varied responses based on system prompt and call count
        if "Perception Agent" in system_prompt:
            responses = self.base_responses["perception"]
        elif "Emotion Agent" in system_prompt:
            responses = self.base_responses["emotion"]
        elif "Memory Agent" in system_prompt:
            responses = self.base_responses["memory"]
        elif "Decision" in system_prompt:
            responses = self.base_responses["decision"]
        elif "Translator" in system_prompt:
            responses = self.base_responses["translation"]
        else:
            return "RESPONSE: *generic creature sound* *neutral behavior*"
        
        # Cycle through responses to provide variation
        return responses[self.call_count % len(responses)]


def create_ai_client(client_type: str = "openai", **kwargs) -> AIClient:
    """Factory function to create AI clients"""
    
    if client_type == "openai":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        model = kwargs.get("model", "gpt-4.1-nano")
        return OpenAIClient(api_key=api_key, model=model)
    
    elif client_type == "mock":
        return MockAIClient()
    
    else:
        raise ValueError(f"Unknown client type: {client_type}")