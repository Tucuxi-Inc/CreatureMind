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
    """Enhanced Mock AI client - provides contextual, species-aware responses without OpenAI API"""
    
    def __init__(self):
        self.call_count = 0
        self.response_history = []  # Track recent responses to avoid repetition
        
        # Species-specific language patterns
        self.species_languages = {
            "dog": {
                "sounds": ["*woof*", "*bark*", "*whine*", "*growl*", "*yip*", "*howl*"],
                "actions": ["*tail wagging*", "*panting*", "*head tilt*", "*play bow*", "*sniffing*", "*ears perked*"]
            },
            "cat": {
                "sounds": ["*meow*", "*purr*", "*chirp*", "*hiss*", "*trill*", "*mrow*"],
                "actions": ["*tail flick*", "*slow blink*", "*head bump*", "*kneading*", "*ear twitch*", "*stretch*"]
            },
            "dragon": {
                "sounds": ["*rumble*", "*roar*", "*snort*", "*growl*", "*chirp*", "*whistle*"],
                "actions": ["*wing flutter*", "*smoke puff*", "*tail sweep*", "*head rise*", "*claw tap*", "*scale shimmer*"]
            },
            "fairy": {
                "sounds": ["*chime*", "*bell*", "*whisper*", "*giggle*", "*sing*", "*hum*"],
                "actions": ["*flutter*", "*glow*", "*sparkle*", "*dance*", "*twirl*", "*hover*"]
            },
            "human": {
                "sounds": ["*speaks softly*", "*chuckles*", "*sighs*", "*hums*", "*whispers*", "*laughs*"],
                "actions": ["*nods*", "*shrugs*", "*gestures*", "*leans forward*", "*tilts head*", "*smiles*"]
            },
            "elf": {
                "sounds": ["*whispers*", "*soft chant*", "*melodic hum*", "*quiet words*", "*musical tone*", "*gentle voice*"],
                "actions": ["*graceful movement*", "*keen observation*", "*light step*", "*alert posture*", "*elegant gesture*", "*perked ears*"]
            },
            "dwarf": {
                "sounds": ["*gruff voice*", "*hearty laugh*", "*grumble*", "*firm words*", "*deep chuckle*", "*robust tone*"],
                "actions": ["*sturdy stance*", "*strong grip*", "*determined nod*", "*steady gaze*", "*crossed arms*", "*confident posture*"]
            },
            "gnome": {
                "sounds": ["*tinkling voice*", "*curious mutter*", "*excited chatter*", "*thoughtful hmm*", "*quick words*", "*clever giggle*"],
                "actions": ["*fidgets with tools*", "*adjusts spectacles*", "*examines closely*", "*nimble fingers*", "*bright expression*", "*inventive gesture*"]
            },
            "sprite": {
                "sounds": ["*tiny voice*", "*silvery laugh*", "*whispered secret*", "*musical chime*", "*delicate sound*", "*ethereal tone*"],
                "actions": ["*quick dart*", "*shimmering movement*", "*tiny gesture*", "*mischievous grin*", "*delicate flutter*", "*playful dance*"]
            }
        }
        
        # Contextual response patterns based on user input
        self.response_patterns = {
            "question": [
                "Hmm, that's an interesting question. Let me think about that.",
                "You're asking something important. I'm not sure I understand completely.",
                "That's a good question. I wish I could explain better.",
                "I hear your question, but I'm not sure how to answer that right now.",
                "You want to know something. I'll try to help you understand."
            ],
            "protect": [
                "Protection is important. I want to keep you safe too.",
                "I may be small, but I care about your safety.",
                "Protecting each other - that's what friends do.",
                "I wish I could shield you from all harm.",
                "Safety and trust go together, don't they?",
                "I'll do my best to watch over you.",
                "Even though I'm just a small creature, I'll try to keep you safe.",
                "Your safety matters to me. We should look out for each other.",
                "I can't fight big dangers, but I'll warn you if I sense trouble.",
                "Together we're stronger. I'll be your guardian companion."
            ],
            "greeting": [
                "Hello! It's good to see you again.",
                "Welcome back! I missed you.",
                "Hey there! How are you feeling today?",
                "Good to see you! What brings you here?",
                "Hi! I'm glad you're here with me."
            ],
            "care": [
                "I appreciate how much you care about me.",
                "Your kindness means a lot to me.",
                "It feels good to be cared for like this.",
                "Thank you for looking after me.",
                "I feel safe when you're caring for me."
            ],
            "negative": [
                "I sense you might be upset about something.",
                "Something seems to be bothering you.",
                "I wish I could help you feel better.",
                "Your feelings matter to me.",
                "Is there anything I can do to help?"
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
        """Enhanced mock responses with species awareness and contextual understanding"""
        
        self.call_count += 1
        
        # Extract species from system prompt
        species = self._extract_species_from_prompt(system_prompt)
        
        # Analyze user input for context
        context_type = self._analyze_user_input(user_message)
        
        # Generate agent-specific responses with species and context awareness
        if "Perception Agent" in system_prompt:
            return self._generate_perception_response(user_message, context_type)
        elif "Emotion Agent" in system_prompt:
            return self._generate_emotion_response(user_message, context_type)
        elif "Memory Agent" in system_prompt:
            return self._generate_memory_response(user_message, context_type, chat_history)
        elif "Decision" in system_prompt:
            return self._generate_decision_response(user_message, context_type, species)
        elif "Translator" in system_prompt:
            return self._generate_translation_response(user_message, context_type, species)
        else:
            return "RESPONSE: *observes quietly*"
    
    def _extract_species_from_prompt(self, prompt: str) -> str:
        """Extract creature species from system prompt"""
        prompt_lower = prompt.lower()
        for species in self.species_languages.keys():
            if species in prompt_lower:
                return species
        return "dog"  # default fallback
    
    def _analyze_user_input(self, message: str) -> str:
        """Analyze user input to determine context type - order matters for priority"""
        message_lower = message.lower()
        
        # Check for specific topics first (higher priority)
        if any(word in message_lower for word in ['protect', 'safe', 'guard', 'defend', 'danger']):
            return "protect"
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good day']):
            return "greeting"
        elif any(word in message_lower for word in ['love', 'care', 'sweet', 'good', 'nice', 'kind']):
            return "care"
        elif any(word in message_lower for word in ['bad', 'sad', 'angry', 'upset', 'hurt', 'no', 'won\'t']):
            return "negative"
        # Questions are checked last since they often contain other keywords
        elif any(word in message_lower for word in ['?', 'why', 'how', 'what', 'when', 'where', 'will you']):
            return "question"
        else:
            return "neutral"
    
    def _generate_perception_response(self, message: str, context_type: str) -> str:
        """Generate perception agent response"""
        tone_map = {
            "question": "curious",
            "protect": "concerned", 
            "greeting": "friendly",
            "care": "warm",
            "negative": "worried",
            "neutral": "calm"
        }
        
        intent_map = {
            "question": "seek information",
            "protect": "discuss safety",
            "greeting": "social connection",
            "care": "express affection",
            "negative": "express concern",
            "neutral": "general interaction"
        }
        
        tone = tone_map.get(context_type, "neutral")
        intent = intent_map.get(context_type, "communicate")
        
        return f"USER_TONE: {tone}\nUSER_INTENT: {intent}\nRELEVANCE_TO_NEEDS: {context_type} interaction"
    
    def _generate_emotion_response(self, message: str, context_type: str) -> str:
        """Generate emotion agent response"""
        emotion_map = {
            "question": ["curious", "thoughtful", "interested"],
            "protect": ["concerned", "caring", "protective"],
            "greeting": ["happy", "excited", "welcoming"],
            "care": ["content", "loved", "warm"],
            "negative": ["sad", "worried", "empathetic"],
            "neutral": ["calm", "neutral", "observant"]
        }
        
        emotions = emotion_map.get(context_type, ["neutral"])
        primary_emotion = emotions[self.call_count % len(emotions)]
        
        return f"EMOTION: {primary_emotion}\nTRANSLATE: yes\nSTATE_CHANGES: happiness +{2 if context_type in ['care', 'greeting'] else 1}"
    
    def _generate_memory_response(self, message: str, context_type: str, chat_history) -> str:
        """Generate memory agent response"""
        memory_patterns = {
            "question": "user asks thoughtful questions",
            "protect": "user cares about safety and protection", 
            "greeting": "user is friendly and social",
            "care": "user shows affection and kindness",
            "negative": "user sometimes expresses concerns",
            "neutral": "user communicates regularly"
        }
        
        pattern = memory_patterns.get(context_type, "user interacts normally")
        memory_count = len(chat_history) if chat_history else 0
        
        return f"RELEVANT_MEMORIES: {memory_count} previous interactions\nPATTERNS: {pattern}\nRELATIONSHIP: developing trust\nCONTEXT_IMPACT: building understanding"
    
    def _generate_decision_response(self, message: str, context_type: str, species: str) -> str:
        """Generate decision agent response with species-specific actions and human response"""
        action_map = {
            "question": "thoughtful pause",
            "protect": "alert stance",
            "greeting": "welcoming approach",
            "care": "gentle nuzzle",
            "negative": "concerned observation",
            "neutral": "attentive listening"
        }
        
        # Get species-specific vocalizations
        species_data = self.species_languages.get(species, self.species_languages["dog"])
        sound = species_data["sounds"][self.call_count % len(species_data["sounds"])]
        
        action = action_map.get(context_type, "neutral stance")
        
        # Get contextual human response 
        responses = self.response_patterns.get(context_type, ["I hear you and I'm thinking about what you said."])
        available_responses = [r for r in responses if r not in self.response_history]
        if not available_responses:
            available_responses = responses
            self.response_history.clear()
        
        human_response = available_responses[self.call_count % len(available_responses)]
        self.response_history.append(human_response)
        
        # Keep history manageable
        if len(self.response_history) > 10:
            self.response_history = self.response_history[-5:]
        
        return f"ACTION: {action}\nVOCALIZATION: {sound}\nHUMAN_RESPONSE: {human_response}\nINTENTION: respond to {context_type}\nENERGY_LEVEL: medium"
    
    def _generate_translation_response(self, message: str, context_type: str, species: str) -> str:
        """Generate translation of human message into creature language"""
        # Extract human response from the message
        human_response = "I hear you."  # Default fallback
        
        # Parse the human response from the input message
        if '"' in message:
            # Extract text between quotes
            start = message.find('"') + 1
            end = message.find('"', start)
            if start > 0 and end > start:
                human_response = message[start:end]
        
        # Get species-specific language elements
        species_data = self.species_languages.get(species, self.species_languages["dog"])
        sound = species_data["sounds"][self.call_count % len(species_data["sounds"])]
        action = species_data["actions"][self.call_count % len(species_data["actions"])]
        
        creature_language = f"{sound} {action}"
        
        return f"CREATURE_LANGUAGE: {creature_language}\nHUMAN_TRANSLATION: {human_response}\nDEBUG: Translated human response into {species} language"


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