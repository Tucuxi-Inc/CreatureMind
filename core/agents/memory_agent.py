"""
Memory Agent - Provides relevant past context

Adapted from the memory logic in WiddlePupper's AIAgentSystem.swift
"""

from typing import Dict, Any, Optional, List
from ..models.creature import CreatureState
from .ai_client import AIClient


class MemoryAgent:
    """
    Analyzes creature's memories to provide relevant context for responses
    
    This agent reviews past interactions and provides:
    - Relevant memories from recent interactions
    - Behavioral patterns observed
    - Relationship status with the user
    - Context that might influence the current response
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    async def analyze(
        self, 
        current_input: str,
        perception_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        creature_state: CreatureState,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze memories and provide relevant context
        """
        
        system_prompt = self._build_system_prompt(creature_state)
        
        # Create user message with current context
        user_message = self._format_context_data(
            current_input, perception_data, emotion_data, creature_state
        )
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                chat_history=chat_history,
                temperature=0.6
            )
            
            return self._parse_memory_response(response)
            
        except Exception as e:
            # Fallback response
            return {
                "relevant_memories": "No specific memories recalled",
                "patterns": "No clear patterns identified",
                "relationship": "neutral",
                "context_impact": "minimal",
                "error": str(e)
            }
    
    def _build_system_prompt(self, creature_state: CreatureState) -> str:
        """Build the system prompt for memory analysis"""
        
        # Format recent memories
        memory_summary = "No recent memories available"
        if creature_state.recent_memories:
            memories = []
            for memory in creature_state.recent_memories[:10]:  # Last 10 memories
                hours_ago = memory.hours_since_creation
                memories.append(f"- {memory.description} ({hours_ago:.1f}h ago, impact: {memory.emotional_impact})")
            memory_summary = "\n".join(memories)
        
        system_prompt = f"""You are the Memory Agent for a {creature_state.species}.

Recent memories (up to 10 most recent):
{memory_summary}

Your task is to analyze these memories AND the recent conversation history to provide relevant insights.

Consider:
1. What past interactions are most relevant to the current situation
2. What behavioral patterns have emerged in recent interactions
3. How the relationship with the user has developed over time
4. How past experiences might influence the current emotional state
5. What topics or themes have been discussed recently
6. Whether the user has asked about things mentioned before
7. How the creature's personality has been expressed in past conversations

IMPORTANT: Use both the stored memories AND the chat history to understand the full context 
of the ongoing relationship. Look for:
- Recurring themes in conversations
- Topics the user returns to
- How the creature has responded to similar situations before
- Progress in the relationship (building trust, familiarity, etc.)
- Unresolved conversations or promised activities

Response format:
RELEVANT_MEMORIES: (key past interactions that relate to current situation)
PATTERNS: (behavioral patterns and conversation themes observed over time)
RELATIONSHIP: (current state of bond with user - new|developing|strong|strained|etc)
CONTEXT_IMPACT: (how memories and conversation history affect interpretation of current interaction)"""

        return system_prompt
    
    def _format_context_data(
        self, 
        current_input: str,
        perception_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        creature_state: CreatureState
    ) -> str:
        """Format the current context for memory analysis"""
        
        return f"""Current Interaction Context:
User Input: {current_input}

Perception Analysis:
- User Tone: {perception_data.get('user_tone', 'unknown')}
- User Intent: {perception_data.get('user_intent', 'unknown')}
- Creature's Initial Reaction: {perception_data.get('creature_reaction', 'neutral')}

Emotional Response:
- Primary Emotion: {emotion_data.get('primary_emotion', 'neutral')}
- Can Translate: {emotion_data.get('can_translate', False)}
- Emotional Impact: {emotion_data.get('impact_score', 0.0)}

Current Creature State:
- Mood: {creature_state.mood}
- Hours since last interaction: {creature_state.last_interaction_hours:.1f}
- Personality traits: {', '.join(creature_state.personality_traits)}"""
    
    def _parse_memory_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured memory data"""
        
        memory_data = {
            "relevant_memories": "",
            "patterns": "",
            "relationship": "neutral",
            "context_impact": ""
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper().replace('_', '_')
                value = value.strip()
                
                if key == "RELEVANT_MEMORIES":
                    memory_data["relevant_memories"] = value
                elif key == "PATTERNS":
                    memory_data["patterns"] = value
                elif key == "RELATIONSHIP":
                    memory_data["relationship"] = value.lower()
                elif key == "CONTEXT_IMPACT":
                    memory_data["context_impact"] = value
        
        return memory_data