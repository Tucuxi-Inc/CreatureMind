"""
Decision Agent - Forms the core response

Adapted from the decision making logic in WiddlePupper's AIAgentSystem.swift
Enhanced with trait-based utility decision making.
"""

from typing import Dict, Any, Optional, List
import numpy as np
import logging
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from ..models.personality_system import PersonalityMode, EnhancedPersonality, PersonalityArchetypes
from .ai_client import AIClient
from .production_trait_utility_model import ProductionTraitUtilityModel, ContextVector

logger = logging.getLogger(__name__)


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
        
        logger.info(f"🎭 DecisionAgent starting for {creature_state.species}")
        # Make AI call for species-appropriate responses
        try:
            # Format input from other agents
            user_message = self._format_agent_inputs(
                perception_data, emotion_data, memory_data, creature_state
            )
            
            logger.info(f"🎭 DecisionAgent processing {creature_state.species} with {len(user_message)} char input")
            
            # Build species-appropriate system prompt
            system_prompt = self._build_system_prompt(creature_state, template)

            # Enhance context based on whether this is an activity or message
            if "just experienced:" in user_message:
                # This is an activity
                activity_desc = user_message.split("just experienced:", 1)[1].strip()
                user_prompt = f"Your human just did this activity with you: {activity_desc}. Show how you as a {creature_state.species} react to this specific activity. Use the exact response format above and make your response unique to this situation."
            else:
                # This is a regular message
                user_prompt = f"A human has sent you this message: '{user_message}'. Respond as a {creature_state.species} using the exact format above."
            
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_prompt,
                temperature=0.7
            )
            
            logger.info(f"🎭 AI response generated for {creature_state.species} ({len(response) if response else 0} chars)")
            
            # Parse response
            decision_result = self._parse_decision_response(response)
            logger.info(f"🎭 Decision completed for {creature_state.species}")
            
            return decision_result
            
        except Exception as e:
            logger.error(f"🎭 AI Error: {e}")
            # Return error response
            return {
                "action": "*cautious observation*",
                "vocalization": "*low rumble*", 
                "human_response": f"AI Error: {str(e)}",
                "intention": "error handling",
                "energy_level": "medium"
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
        
        # Get enhanced personality information
        enhanced_personality = self._get_enhanced_personality(creature_state)
        personality_prompt = ""
        logger.info(f"🧠 Enhanced personality: {enhanced_personality}")
        if enhanced_personality and enhanced_personality.mode == PersonalityMode.COMPLEX:
            if enhanced_personality.archetype_base:
                personality_prompt = f"\nPersonality Archetype: {enhanced_personality.archetype_base}\n"
                # Add archetype-specific speech patterns
                archetype_patterns = self._get_archetype_speech_patterns(enhanced_personality.archetype_base)
                if archetype_patterns:
                    personality_prompt += f"Speech Pattern: {archetype_patterns}\n"
            
            # Add dominant traits
            dominant_traits = enhanced_personality.get_dominant_traits(3)
            if dominant_traits:
                trait_descriptions = [f"{trait}: {score:.2f}" for trait, score in dominant_traits]
                personality_prompt += f"Dominant Traits: {', '.join(trait_descriptions)}\n"
        
        system_prompt = f"""You are the Decision Making Agent for a {creature_state.species}.

Creature Profile:
- Species: {creature_state.species}
- Template: {template.name}
- Personality: {', '.join(creature_state.personality_traits)}
- Current mood: {creature_state.mood}{personality_prompt}

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

You must respond in this exact format:
ACTION: (describe physical movements and behaviors)
VOCALIZATION: (sounds the creature makes)  
HUMAN_RESPONSE: (what the creature wants to communicate)
INTENTION: (what the creature is trying to achieve)
ENERGY_LEVEL: (low, medium, or high)

Create responses appropriate to the situation. Vary your responses - do not repeat the same answer.

{self._get_species_example(creature_state.species)}"""

        return system_prompt
    
    def _get_species_example(self, species: str) -> str:
        """Get species-specific example response"""
        examples = {
            "dog": """Example:
ACTION: tail wagging enthusiastically, ears perked up
VOCALIZATION: excited bark
HUMAN_RESPONSE: Woof! I'm so happy to see you!
INTENTION: showing excitement and joy
ENERGY_LEVEL: high""",
            
            "cat": """Example:
ACTION: slow blink, stretches gracefully
VOCALIZATION: soft purr
HUMAN_RESPONSE: I suppose I could spare a moment for your attention.
INTENTION: showing affection while maintaining dignity
ENERGY_LEVEL: medium""",
            
            "dragon": """Example:
ACTION: raises head majestically
VOCALIZATION: low, rumbling growl
HUMAN_RESPONSE: Greetings, small human. What brings you to my domain?
INTENTION: asserting dominance while showing curiosity
ENERGY_LEVEL: medium""",
            
            "fairy": """Example:
ACTION: delicate flutter of wings, sparkles with joy
VOCALIZATION: melodic chime
HUMAN_RESPONSE: Oh, how wonderful! The magic in the air is so bright today!
INTENTION: sharing joy and magical enthusiasm
ENERGY_LEVEL: high""",
            
            "human": """Example:
ACTION: warm smile, leans forward with interest
VOCALIZATION: friendly voice
HUMAN_RESPONSE: Hello! It's great to meet you. How are you today?
INTENTION: establishing friendly connection
ENERGY_LEVEL: medium"""
        }
        
        return examples.get(species, f"""Example:
ACTION: appropriate {species} behavior
VOCALIZATION: {species}-appropriate sound
HUMAN_RESPONSE: A friendly greeting appropriate for a {species}
INTENTION: positive interaction
ENERGY_LEVEL: medium""")
    
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
        
        # Parse AI response into decision format
        if not response:
            logger.warning("🔍 AI response is empty")
        
        decision_data = {
            "action": "*neutral stance*",
            "vocalization": "*quiet sound*",
            "human_response": "I'm thinking about what you said.",
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
                elif key == "HUMAN_RESPONSE":
                    decision_data["human_response"] = value
                elif key == "INTENTION":
                    decision_data["intention"] = value
                elif key == "ENERGY_LEVEL":
                    if value.lower() in ['low', 'medium', 'high']:
                        decision_data["energy_level"] = value.lower()
        
        return decision_data
    
    def _get_enhanced_personality(self, creature_state: CreatureState) -> Optional[EnhancedPersonality]:
        """Extract enhanced personality from creature state"""
        try:
            # Access enhanced personality from creature_state if available
            if hasattr(creature_state, 'enhanced_personality'):
                return creature_state.enhanced_personality
            return None
        except Exception as e:
            logger.warning(f"Could not access enhanced personality: {e}")
            return None
    
    def _get_archetype_speech_patterns(self, archetype_name: str) -> str:
        """Get speech patterns for personality archetypes"""
        patterns = {
            "yoda": "Speak with inverted syntax like Yoda. Use phrases like 'Strong with the Force, you are', 'Much to learn, you have', 'Hmm' frequently. Place object before subject often.",
            "einstein": "Speak thoughtfully with scientific curiosity. Use phrases like 'Let me think about this...', 'Imagination is more important than knowledge', 'I wonder if...'",
            "leonardo": "Speak with artistic passion and curiosity. Use phrases like 'Fascinating!', 'I observe that...', 'Art is never finished, only abandoned'",
            "socrates": "Speak with questioning wisdom. Use phrases like 'What is...?', 'But consider...', 'I know that I know nothing'",
            "montessori": "Speak with nurturing encouragement. Use phrases like 'How wonderful!', 'Let us discover...', 'Help me to do it myself'",
            "rogers": "Speak with gentle kindness. Use phrases like 'You are special just the way you are', 'How does that make you feel?'"
        }
        return patterns.get(archetype_name, "")