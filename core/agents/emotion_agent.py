"""
Emotion Agent - Determines creature's emotional response

Adapted from the emotion logic in WiddlePupper's AIAgentSystem.swift
"""

from typing import Dict, Any
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from .ai_client import AIClient


class EmotionAgent:
    """
    Determines the creature's emotional reaction to user input and context
    
    This agent analyzes perception data and determines:
    - Primary emotional response
    - Secondary emotions
    - Whether the creature is willing to translate 
    - Emotional impact on stats
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    async def process(
        self, 
        perception_data: Dict[str, Any], 
        creature_state: CreatureState, 
        template: CreatureTemplate
    ) -> Dict[str, Any]:
        """
        Process perception data and determine emotional response
        """
        
        system_prompt = self._build_system_prompt(creature_state, template)
        
        # Create user message from perception data
        user_message = self._format_perception_data(perception_data)
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8
            )
            
            return self._parse_emotion_response(response)
            
        except Exception as e:
            # Fallback response
            return {
                "primary_emotion": "neutral",
                "secondary_emotions": [],
                "can_translate": False,
                "impact_score": 0.0,
                "state_changes": {},
                "error": str(e)
            }
    
    def _build_system_prompt(self, creature_state: CreatureState, template: CreatureTemplate) -> str:
        """Build the system prompt for emotion analysis"""
        
        stats_summary = []
        for stat_name, value in creature_state.stats.items():
            stats_summary.append(f"- {stat_name.title()}: {value}/100")
        
        system_prompt = f"""You are the Emotion Agent for a {creature_state.species}.

Creature Profile:
- Species: {creature_state.species}
- Template: {template.name}
- Personality traits: {', '.join(creature_state.personality_traits)}
- Current mood: {creature_state.mood}

Current State:
{chr(10).join(stats_summary)}

{template.emotion_prompt_additions}

Based on the perception analysis and creature traits, determine:
1. Your emotional reaction (consider physical state - low energy = tired, low stats = distressed)
2. Whether you're willing to let humans understand you (translation availability)
3. How this interaction affects your emotional state

Physical state constraints:
- Low stats should influence emotional capacity
- Energy levels affect willingness to interact
- Consider species-specific emotional patterns

Response format:
EMOTION: (primary emotion - happy|sad|excited|tired|hungry|angry|neutral|curious|playful)
SECONDARY_EMOTIONS: (other feelings, comma-separated)
TRANSLATE: (yes|no - based on mood and stats)
IMPACT_SCORE: (emotional impact from -1.0 to 1.0)
STATE_CHANGES: (any suggested stat modifications, e.g., happiness +5)"""

        return system_prompt
    
    def _format_perception_data(self, perception_data: Dict[str, Any]) -> str:
        """Format perception data for the emotion agent"""
        
        return f"""Perception Analysis:
User Tone: {perception_data.get('user_tone', 'unknown')}
User Intent: {perception_data.get('user_intent', 'unknown')}
Intent Details: {perception_data.get('intent_details', '')}
Relevance to Needs: {perception_data.get('relevance_to_needs', '')}
Creature Reaction: {perception_data.get('creature_reaction', 'neutral')}
Attention Focus: {perception_data.get('attention_focus', '')}
Expected Response: {perception_data.get('likely_response_type', 'neutral')}"""
    
    def _parse_emotion_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured emotion data"""
        
        emotion_data = {
            "primary_emotion": "neutral",
            "secondary_emotions": [],
            "can_translate": False,
            "impact_score": 0.0,
            "state_changes": {}
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key == "EMOTION":
                    emotion_data["primary_emotion"] = value.lower()
                elif key == "SECONDARY_EMOTIONS":
                    if value:
                        emotion_data["secondary_emotions"] = [e.strip().lower() for e in value.split(',')]
                elif key == "TRANSLATE":
                    emotion_data["can_translate"] = value.lower() in ['yes', 'true', '1']
                elif key == "IMPACT_SCORE":
                    try:
                        emotion_data["impact_score"] = float(value)
                    except ValueError:
                        emotion_data["impact_score"] = 0.0
                elif key == "STATE_CHANGES":
                    # Parse stat changes like "happiness +5, energy -2"
                    if value and value != "none":
                        changes = {}
                        for change in value.split(','):
                            change = change.strip()
                            if '+' in change or '-' in change:
                                parts = change.replace('+', ' +').replace('-', ' -').split()
                                if len(parts) >= 2:
                                    stat_name = parts[0].lower()
                                    try:
                                        stat_value = float(parts[1])
                                        changes[stat_name] = stat_value
                                    except ValueError:
                                        continue
                        emotion_data["state_changes"] = changes
        
        return emotion_data