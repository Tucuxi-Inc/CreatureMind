"""
Decision Agent - Forms the core response

Adapted from the decision making logic in WiddlePupper's AIAgentSystem.swift
Enhanced with trait-based utility decision making.
"""

from typing import Dict, Any, Optional, List
import numpy as np
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from ..models.personality_system import PersonalityMode, EnhancedPersonality
from .ai_client import AIClient
from .production_trait_utility_model import ProductionTraitUtilityModel, ContextVector


class DecisionAgent:
    """
    Forms the core response based on all previous agent inputs
    
    This agent synthesizes information from perception, emotion, and memory
    agents to create the creature's fundamental response, including:
    - Physical actions and behaviors
    - Vocalizations and sounds
    - Underlying intentions and motivations
    
    Enhanced with trait-based utility decision making for more sophisticated
    personality-driven behavior selection.
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.utility_model = ProductionTraitUtilityModel()
        self.trait_influence_strength = 0.7  # How much personality affects decisions vs context
    
    async def decide(
        self, 
        perception_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        memory_data: Dict[str, Any],
        creature_state: CreatureState,
        template: CreatureTemplate,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Make the core decision about how the creature should respond
        
        Enhanced with trait-based utility computation for personality-driven behavior selection.
        """
        
        # Get personality information
        enhanced_personality = self._get_enhanced_personality(creature_state)
        
        # If using complex personality mode, compute trait-driven action style
        action_style = None
        utilities = None
        
        if enhanced_personality and enhanced_personality.mode == PersonalityMode.COMPLEX:
            # Build context vector from agent inputs
            context_vector = ContextVector.from_agent_data(
                perception_data, emotion_data, memory_data, creature_state
            )
            
            # Get trait vector
            trait_vector = enhanced_personality.get_trait_vector()
            
            # Compute utilities for different action styles
            utilities = self.utility_model.compute_utilities(trait_vector, context_vector)
            
            # Select action style based on personality
            action_style = self.utility_model.select_action_style(utilities)
        
        # Build system prompt (enhanced with trait information)
        system_prompt = self._build_enhanced_system_prompt(
            creature_state, template, enhanced_personality, action_style, utilities
        )
        
        # Combine all agent inputs
        user_message = self._format_agent_inputs(
            perception_data, emotion_data, memory_data, creature_state
        )
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                chat_history=chat_history,
                temperature=0.7
            )
            
            decision_result = self._parse_decision_response(response)
            
            # Add trait-based debug information
            if action_style and utilities:
                decision_result["debug_info"] = {
                    "selected_action_style": action_style,
                    "action_utilities": utilities,
                    "personality_mode": enhanced_personality.mode.value if enhanced_personality else "simple"
                }
            
            return decision_result
            
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

Based on all agent inputs and the recent conversation history, form a response that:
1. Reflects the determined emotional state
2. Considers personality and species traits
3. Incorporates relevant memories and conversation context
4. References or builds upon recent topics/interactions when appropriate
5. Maintains authentic creature behavior
6. Shows awareness of ongoing relationship development
7. MOST IMPORTANTLY: Matches current physical state

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
    
    def _get_enhanced_personality(self, creature_state: CreatureState) -> Optional[EnhancedPersonality]:
        """Extract enhanced personality from creature state"""
        # Get the creature from global creatures dict
        # In a production system, this would be handled differently
        from api.server import creatures
        
        creature = creatures.get(str(creature_state.creature_id))
        if creature and creature.personality.enhanced_personality:
            return creature.personality.enhanced_personality
        
        return None
    
    def _build_enhanced_system_prompt(
        self, 
        creature_state: CreatureState, 
        template: CreatureTemplate,
        enhanced_personality: Optional[EnhancedPersonality],
        action_style: Optional[str],
        utilities: Optional[Dict[str, float]]
    ) -> str:
        """Build enhanced system prompt with trait-based guidance"""
        
        if enhanced_personality and enhanced_personality.mode == PersonalityMode.COMPLEX and action_style:
            return self._build_trait_aware_prompt(
                creature_state, template, enhanced_personality, action_style, utilities
            )
        else:
            return self._build_system_prompt(creature_state, template)
    
    def _build_trait_aware_prompt(
        self,
        creature_state: CreatureState,
        template: CreatureTemplate, 
        enhanced_personality: EnhancedPersonality,
        action_style: str,
        utilities: Dict[str, float]
    ) -> str:
        """Build prompt that incorporates trait-driven action style"""
        
        # Get top 5 traits for this creature
        trait_vector = enhanced_personality.get_trait_vector()
        dominant_traits = enhanced_personality.get_dominant_traits(5)
        top_traits = [f"{trait} ({score:.2f})" for trait, score in dominant_traits]
        
        # Get action style guidance
        action_guidance = self.utility_model.get_action_guidance(action_style)
        
        # Get current stats
        stats_summary = []
        for stat_name, value in creature_state.stats.items():
            stats_summary.append(f"- {stat_name.title()}: {value}/100")
        
        system_prompt = f"""You are the Decision Making Agent for a {creature_state.species}.

ENHANCED TRAIT-DRIVEN PERSONALITY:
- Personality Mode: Complex (50-dimensional trait system)
- Dominant traits: {', '.join(top_traits)}
- Selected action style: {action_style}
- Style confidence: {utilities[action_style]:.2f}

BEHAVIORAL GUIDANCE ({action_style.upper()}):
{action_guidance['description']}
- Behavior tags: {', '.join(action_guidance['behavior_tags'])}
- Energy requirement: {action_guidance['energy_level']}
- Social preference: {action_guidance['social_preference']}

Creature Profile:
- Species: {creature_state.species}
- Template: {template.name}
- Current mood: {creature_state.mood}

Current State:
{chr(10).join(stats_summary)}

Species-Specific Behaviors:
{chr(10).join([f"- {behavior}" for behavior in template.language.behavioral_patterns])}

{template.decision_prompt_additions}

CRITICAL: Your response MUST align with the {action_style} action style. This means:
{self._get_style_specific_guidance(action_style)}

Based on all agent inputs and the conversation history, form a response that:
1. Reflects the determined emotional state
2. STRONGLY emphasizes the selected action style ({action_style})
3. Incorporates dominant personality traits: {', '.join([trait for trait, _ in dominant_traits[:3]])}
4. Considers relevant memories and conversation context
5. References or builds upon recent topics/interactions when appropriate
6. Shows awareness of relationship development through conversation history
7. Maintains authentic creature behavior
8. Matches current physical state and energy level

Physical state constraints:
- Low energy: avoid energetic actions, use tired behaviors
- Low stats: show signs of need/distress
- High stats: more willing to engage and be active
- Consider species-specific energy patterns

Response format:
ACTION: (physical response - must strongly reflect {action_style} style and energy state)
VOCALIZATION: (species-appropriate sounds - match {action_style} style and energy level)
INTENTION: (what the creature wants to convey - influenced by {action_style} approach)
ENERGY_LEVEL: (low|medium|high - for response intensity)"""

        return system_prompt
    
    def _get_style_specific_guidance(self, action_style: str) -> str:
        """Provide specific guidance for each action style"""
        style_guides = {
            "playful": "Be energetic, fun-loving, and spontaneous. Use bouncy movements and happy sounds. Initiate games and activities.",
            "cautious": "Be careful, observant, and measured. Move slowly and assess before acting. Show wariness of new situations.", 
            "assertive": "Be confident, direct, and decisive. Stand tall and communicate clearly. Take charge of the situation.",
            "nurturing": "Be caring, gentle, and protective. Use soft sounds and comforting gestures. Focus on the wellbeing of others.",
            "curious": "Be inquisitive and investigative. Explore new things with interest. Ask questions through behavior.",
            "defensive": "Be protective and alert. Watch for threats. Position yourself defensively while staying ready to react.",
            "social": "Be friendly and engaging. Seek connection and interaction. Use welcoming body language and sounds.",
            "independent": "Be self-reliant and autonomous. Make your own decisions. Maintain personal space and dignity.",
            "analytical": "Be thoughtful and systematic. Consider all angles before responding. Show careful problem-solving behavior.",
            "emotional": "Be expressive and empathetic. Show your feelings clearly. Respond to the emotional needs of others."
        }
        return style_guides.get(action_style, "Act naturally according to your species and current state.")