"""
Perception Agent - Analyzes user input and current context

Adapted from the perception logic in WiddlePupper's AIAgentSystem.swift
"""

from typing import Dict, Any, Optional
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from .ai_client import AIClient


class PerceptionAgent:
    """
    Analyzes user input from both text and current context
    
    This agent determines:
    - Emotional tone of the user message
    - User's likely intention
    - How the input relates to creature's current needs
    - Contextual factors that might influence the response
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    async def analyze(
        self, 
        user_input: str, 
        creature_state: CreatureState, 
        template: CreatureTemplate,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user input and return perception data
        
        Adapted from WiddlePupper's perception agent prompt logic.
        """
        
        # Build the system prompt for perception analysis
        system_prompt = self._build_system_prompt(creature_state, template)
        
        # Add any additional context
        context_info = ""
        if context:
            context_info = f"\nAdditional context: {context}"
        
        user_message = f"{user_input}{context_info}"
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7
            )
            
            return self._parse_perception_response(response)
            
        except Exception as e:
            # Fallback response if AI call fails
            return {
                "user_tone": "unknown",
                "user_intent": "unknown", 
                "intent_details": "",
                "relevance_to_needs": "unknown",
                "creature_reaction": "neutral",
                "attention_focus": "user_presence",
                "likely_response_type": "cautious",
                "error": str(e)
            }
    
    def _build_system_prompt(self, creature_state: CreatureState, template: CreatureTemplate) -> str:
        """Build the system prompt for perception analysis"""
        
        # Get creature's current stats summary
        stats_summary = []
        for stat_name, value in creature_state.stats.items():
            stats_summary.append(f"- {stat_name.title()}: {value}/100")
        
        # Get recent memories summary
        memory_summary = "No recent memories"
        if creature_state.recent_memories:
            recent = creature_state.recent_memories[:3]
            memory_summary = "; ".join([m.description for m in recent])
        
        system_prompt = f"""You are a Perception Agent analyzing user input for a {creature_state.species}.

Creature Profile:
- Species: {creature_state.species}
- Template: {template.name}
- Personality traits: {', '.join(creature_state.personality_traits)}
- Current mood: {creature_state.mood}

Current State:
{chr(10).join(stats_summary)}

Recent memories: {memory_summary}
Last interaction: {creature_state.last_interaction_hours:.1f} hours ago

{template.perception_prompt_additions}

Important analysis guidelines:
1. Analyze the emotional tone of the message (friendly, commanding, playful, worried, etc.)
2. Determine the user's likely intention (greet, request_activity, express_concern, command, etc.)
3. Evaluate how this relates to the creature's current physical/emotional needs
4. Consider how this creature type's traits affect perception
5. Consider the context of recent interactions

Response format:
USER_TONE: (emotional tone of user message)
USER_INTENT: (what the user appears to want)
INTENT_DETAILS: (specific details about the intent, if any)
RELEVANCE_TO_NEEDS: (how this relates to current needs/state)
CREATURE_REACTION: (how this creature type would initially react)
ATTENTION_FOCUS: (what aspect the creature finds most interesting/concerning)
LIKELY_RESPONSE_TYPE: (excited|cautious|confused|eager|tired|hungry|playful|defensive)"""

        return system_prompt
    
    def _parse_perception_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        
        perception_data = {
            "user_tone": "neutral",
            "user_intent": "unknown",
            "intent_details": "",
            "relevance_to_needs": "",
            "creature_reaction": "neutral", 
            "attention_focus": "",
            "likely_response_type": "neutral"
        }
        
        # Parse the response line by line
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace('_', '_')
                value = value.strip()
                
                if key == "user_tone":
                    perception_data["user_tone"] = value
                elif key == "user_intent":
                    perception_data["user_intent"] = value
                elif key == "intent_details":
                    perception_data["intent_details"] = value
                elif key == "relevance_to_needs":
                    perception_data["relevance_to_needs"] = value
                elif key == "creature_reaction":
                    perception_data["creature_reaction"] = value
                elif key == "attention_focus":
                    perception_data["attention_focus"] = value
                elif key == "likely_response_type":
                    perception_data["likely_response_type"] = value
        
        return perception_data