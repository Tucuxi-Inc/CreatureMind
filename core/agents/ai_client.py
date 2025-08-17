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
    
    def __init__(self, api_key: str, model: str = "gpt-4-1106-preview"):
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
    """Mock AI client for testing"""
    
    def __init__(self):
        self.responses = {
            "perception": "USER_TONE: friendly\nUSER_INTENT: greet\nRELEVANCE_TO_NEEDS: social interaction",
            "emotion": "EMOTION: happy\nTRANSLATE: yes\nSTATE_CHANGES: happiness +5",
            "memory": "RELEVANT_MEMORIES: recent greeting\nPATTERNS: user is friendly",
            "decision": "ACTION: tail wag\nVOCALIZATION: happy bark\nINTENTION: show friendliness",
            "translation": "BARK: *woof woof* *tail wagging*\nTRANSLATION: Hello there, friend!"
        }
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        chat_history: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Return mock responses for testing"""
        
        # Simple mock logic based on system prompt content
        if "Perception Agent" in system_prompt:
            return self.responses["perception"]
        elif "Emotion Agent" in system_prompt:
            return self.responses["emotion"]
        elif "Memory Agent" in system_prompt:
            return self.responses["memory"]
        elif "Decision" in system_prompt:
            return self.responses["decision"]
        elif "Translator" in system_prompt:
            return self.responses["translation"]
        else:
            return "RESPONSE: *generic creature sound* *neutral behavior*"


def create_ai_client(client_type: str = "openai", **kwargs) -> AIClient:
    """Factory function to create AI clients"""
    
    if client_type == "openai":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        model = kwargs.get("model", "gpt-4-1106-preview")
        return OpenAIClient(api_key=api_key, model=model)
    
    elif client_type == "mock":
        return MockAIClient()
    
    else:
        raise ValueError(f"Unknown client type: {client_type}")