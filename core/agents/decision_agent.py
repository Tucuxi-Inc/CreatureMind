"""
Decision Agent - Forms the core response

Adapted from the decision making logic in WiddlePupper's AIAgentSystem.swift
"""

from typing import Dict, Any
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from .ai_client import AIClient


class DecisionAgent:
    """
    Forms the core response based on all previous agent inputs
    
    This agent synthesizes information from perception, emotion, and memory
    agents to create the creature's fundamental response, including:
    - Physical actions and behaviors
    - Vocalizations and sounds
    - Underlying intentions and motivations
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    async def decide(
        self, 
        perception_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        memory_data: Dict[str, Any],
        creature_state: CreatureState,
        template: CreatureTemplate
    ) -> Dict[str, Any]:
        """
        Make the core decision about how the creature should respond
        """
        
        system_prompt = self._build_system_prompt(creature_state, template)
        
        # Combine all agent inputs
        user_message = self._format_agent_inputs(
            perception_data, emotion_data, memory_data, creature_state
        )
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7
            )
            
            return self._parse_decision_response(response)
            
        except Exception as e:
            # Fallback response
            return {
                "action": "*quiet observation*",
                "vocalization": "*soft sound*",
                "intention": "cautious acknowledgment",
                "energy_level": "low",
                "error": str(e)
            }
    
    def _build_system_prompt(self, creature_state: CreatureState, template: CreatureTemplate) -> str:
        """Build the system prompt for decision making"""
        
        # Get current stats
        stats_summary = []
        for stat_name, value in creature_state.stats.items():
            stats_summary.append(f"- {stat_name.title()}: {value}/100")
        
        # Get available behaviors from template
        behaviors = template.language.behavioral_patterns
        behavior_summary = "\n".join([f"- {behavior}" for behavior in behaviors])
        
        system_prompt = f"""You are the Decision Making Agent for a {creature_state.species}.

Creature Profile:
- Species: {creature_state.species}
- Template: {template.name}
- Personality: {', '.join(creature_state.personality_traits)}
- Current mood: {creature_state.mood}

Current State:
{chr(10).join(stats_summary)}

Species-Specific Behaviors:
{behavior_summary}

{template.decision_prompt_additions}

Based on all agent inputs, form a response that:
1. Reflects the determined emotional state
2. Considers personality and species traits
3. Incorporates relevant memories and context
4. Maintains authentic creature behavior
5. MOST IMPORTANTLY: Matches current physical state

Physical state constraints:
- Low energy: avoid energetic actions, use tired behaviors
- Low stats: show signs of need/distress
- High stats: more willing to engage and be active
- Consider species-specific energy patterns

Response format:
ACTION: (physical response - must match energy and emotional state)
VOCALIZATION: (species-appropriate sounds - match energy level and emotion)
INTENTION: (what the creature wants to convey to the user)
ENERGY_LEVEL: (low|medium|high - for response intensity)"""

        return system_prompt
    
    def _format_agent_inputs(
        self, 
        perception_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        memory_data: Dict[str, Any],
        creature_state: CreatureState
    ) -> str:
        """Format all agent inputs for decision making"""
        
        return f"""Agent Analysis Summary:

PERCEPTION:
- User tone: {perception_data.get('user_tone', 'unknown')}
- User intent: {perception_data.get('user_intent', 'unknown')}
- Relevance to needs: {perception_data.get('relevance_to_needs', '')}
- Expected response type: {perception_data.get('likely_response_type', 'neutral')}

EMOTION:
- Primary emotion: {emotion_data.get('primary_emotion', 'neutral')}
- Secondary emotions: {', '.join(emotion_data.get('secondary_emotions', []))}
- Can translate: {emotion_data.get('can_translate', False)}
- Emotional impact: {emotion_data.get('impact_score', 0.0)}

MEMORY:
- Relevant memories: {memory_data.get('relevant_memories', 'none')}
- Behavioral patterns: {memory_data.get('patterns', 'none')}
- Relationship status: {memory_data.get('relationship', 'neutral')}
- Context impact: {memory_data.get('context_impact', 'minimal')}

CURRENT STATE:
- Mood: {creature_state.mood}
- Time since last interaction: {creature_state.last_interaction_hours:.1f} hours
- Stats: {creature_state.stats}"""
    
    def _parse_decision_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured decision data"""
        
        decision_data = {
            "action": "*neutral stance*",
            "vocalization": "*quiet sound*",
            "intention": "acknowledgment",
            "energy_level": "medium"
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key == "ACTION":
                    decision_data["action"] = value
                elif key == "VOCALIZATION":
                    decision_data["vocalization"] = value
                elif key == "INTENTION":
                    decision_data["intention"] = value
                elif key == "ENERGY_LEVEL":
                    if value.lower() in ['low', 'medium', 'high']:
                        decision_data["energy_level"] = value.lower()
        
        return decision_data