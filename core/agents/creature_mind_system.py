"""
Creature Mind System - Generalized from WiddlePupper's AIAgentSystem.swift

Multi-agent AI system that creates believable creature consciousness through
specialized agents working together.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..models.creature import Creature, CreatureState, Memory
from ..models.creature_template import CreatureTemplate
from .ai_client import AIClient
from .perception_agent import PerceptionAgent
from .emotion_agent import EmotionAgent
from .memory_agent import MemoryAgent
from .decision_agent import DecisionAgent
from .translator_agent import TranslatorAgent
from ..language.creature_language import CreatureLanguage


class CreatureMindResponse:
    """Response from the creature mind system"""
    
    def __init__(self):
        self.creature_language: str = ""
        self.human_translation: Optional[str] = None
        self.can_translate: bool = False
        self.emotional_state: str = "neutral"
        self.stats_delta: Dict[str, float] = {}
        self.memory_created: Optional[Memory] = None
        self.debug_info: Dict[str, Any] = {}


class CreatureMindSystem:
    """
    Main orchestrator for the multi-agent creature consciousness system
    
    Adapted from WiddlePupper's AIAgentSystem.swift but generalized for any creature type.
    """
    
    def __init__(self, creature: Creature, template: CreatureTemplate, ai_client: AIClient):
        self.creature = creature
        self.template = template
        self.ai_client = ai_client
        
        # Initialize specialized agents
        self.perception_agent = PerceptionAgent(ai_client)
        self.emotion_agent = EmotionAgent(ai_client)
        self.memory_agent = MemoryAgent(ai_client)
        self.decision_agent = DecisionAgent(ai_client)
        self.translator_agent = TranslatorAgent(ai_client)
        
        # Language system for creature-specific sounds/behaviors
        self.creature_language = CreatureLanguage(template)
        
        # State tracking
        self.is_processing = False
        self.chat_history: List[Dict[str, str]] = []
    
    async def process_message(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> CreatureMindResponse:
        """
        Process user input through the multi-agent system
        
        This is the main entry point that orchestrates all agents to create a response.
        Adapted from AIAgentSystem.swift's processMessage method.
        """
        
        if self.is_processing:
            return self._create_busy_response()
        
        self.is_processing = True
        response = CreatureMindResponse()
        
        try:
            # Update creature's interaction time
            self.creature.update_interaction_time()
            
            # Create current state snapshot
            current_state = CreatureState.from_creature(self.creature)
            
            # Store user message in chat history
            user_message = {"role": "user", "content": user_input}
            self.chat_history.append(user_message)
            
            # 1. Perception Agent - Analyze user input and current context
            perception_result = await self.perception_agent.analyze(
                user_input=user_input,
                creature_state=current_state,
                template=self.template,
                context=context
            )
            response.debug_info["perception"] = perception_result
            
            # 2. Emotion Agent - Determine creature's emotional response
            emotion_result = await self.emotion_agent.process(
                perception_data=perception_result,
                creature_state=current_state,
                template=self.template
            )
            response.emotional_state = emotion_result.get("primary_emotion", "neutral")
            response.debug_info["emotion"] = emotion_result
            
            # 3. Memory Agent - Provide relevant past context
            memory_result = await self.memory_agent.analyze(
                current_input=user_input,
                perception_data=perception_result,
                emotion_data=emotion_result,
                creature_state=current_state
            )
            response.debug_info["memory"] = memory_result
            
            # 4. Decision Agent - Form the core response
            decision_result = await self.decision_agent.decide(
                perception_data=perception_result,
                emotion_data=emotion_result,
                memory_data=memory_result,
                creature_state=current_state,
                template=self.template
            )
            response.debug_info["decision"] = decision_result
            
            # 5. Generate creature language response
            base_creature_language = self.creature_language.generate_response(
                decision_data=decision_result,
                emotion_state=response.emotional_state,
                creature_state=current_state
            )
            
            # 6. Translator Agent - Create final creature language and human translation
            translation_result = await self.translator_agent.translate(
                decision_data=decision_result,
                base_creature_language=base_creature_language,
                creature_state=current_state,
                template=self.template
            )
            
            response.creature_language = translation_result["creature_language"]
            response.can_translate = translation_result["can_translate"]
            if response.can_translate:
                response.human_translation = translation_result["human_translation"]
            
            response.debug_info["translation"] = translation_result
            
            # Create memory of this interaction
            response.memory_created = self.creature.add_memory(
                memory_type="chat",
                description=f"User: {user_input}",
                emotional_impact=emotion_result.get("impact_score", 0.0),
                metadata={
                    "creature_response": response.creature_language,
                    "translation": response.human_translation,
                    "can_translate": response.can_translate,
                    "emotion": response.emotional_state
                }
            )
            
            # Add creature response to chat history
            creature_message = {"role": "assistant", "content": response.creature_language}
            self.chat_history.append(creature_message)
            
            # Apply any stat changes from the interaction
            self._apply_interaction_effects(emotion_result, response)
            
            # Update personality based on interaction (evolution system)
            if hasattr(self.creature.personality, 'enhanced_personality') and self.creature.personality.enhanced_personality:
                interaction_data = {
                    'type': 'message',
                    'emotional_impact': emotion_result.get('impact_score', 0.0),
                    'primary_emotion': response.emotional_state,
                    'context': context or {},
                    'learning_occurred': 'learn' in user_input.lower() or 'teach' in user_input.lower(),
                    'bonding_occurred': response.stats_delta.get('happiness', 0) > 10,
                    'stress_level': max(0, -emotion_result.get('impact_score', 0.0))
                }
                self.creature.personality.enhanced_personality.update_from_interaction(interaction_data)
            
        except Exception as e:
            response = self._create_error_response(str(e))
        finally:
            self.is_processing = False
        
        return response
    
    def _create_busy_response(self) -> CreatureMindResponse:
        """Create a response when the system is already processing"""
        response = CreatureMindResponse()
        response.creature_language = self.creature_language.get_busy_response()
        response.can_translate = False
        return response
    
    def _create_error_response(self, error: str) -> CreatureMindResponse:
        """Create a response when an error occurs"""
        response = CreatureMindResponse()
        response.creature_language = self.creature_language.get_error_response()
        response.can_translate = False
        response.debug_info["error"] = error
        return response
    
    def _apply_interaction_effects(self, emotion_result: Dict[str, Any], response: CreatureMindResponse) -> None:
        """Apply stat changes based on the interaction"""
        # Basic interaction effects - could be made more sophisticated
        
        # Positive interactions generally increase happiness slightly
        emotional_impact = emotion_result.get("impact_score", 0.0)
        if emotional_impact > 0:
            self.creature.stats.modify_stat("happiness", emotional_impact * 2)
            response.stats_delta["happiness"] = emotional_impact * 2
        
        # Any interaction slightly reduces boredom/restlessness
        if "energy" in self.creature.stats.configs:
            self.creature.stats.modify_stat("energy", -1)  # Small energy cost for interaction
            response.stats_delta["energy"] = -1
    
    async def process_activity(self, activity_name: str, parameters: Dict[str, Any] = None) -> CreatureMindResponse:
        """
        Process a specific activity (feeding, playing, etc.)
        
        Similar to WiddlePupper's processActivity method but generalized.
        """
        # Find activity in template
        activity = None
        for template_activity in self.template.activities:
            if template_activity.name == activity_name:
                activity = template_activity
                break
        
        if not activity:
            return self._create_error_response(f"Unknown activity: {activity_name}")
        
        # Check if creature can perform this activity
        current_state = CreatureState.from_creature(self.creature)
        for stat_name, required_value in activity.required_stats.items():
            if current_state.stats.get(stat_name, 0) < required_value:
                return self._create_error_response(f"Cannot perform {activity_name}: insufficient {stat_name}")
        
        # Apply activity effects
        response = CreatureMindResponse()
        activity_stats_delta = {}
        
        for stat_name, effect in activity.stat_effects.items():
            self.creature.stats.modify_stat(stat_name, effect)
            activity_stats_delta[stat_name] = effect
        
        # Energy cost
        if activity.energy_cost > 0:
            self.creature.stats.modify_stat("energy", -activity.energy_cost)
            activity_stats_delta["energy"] = activity_stats_delta.get("energy", 0) - activity.energy_cost
        
        # Generate creature response to the activity
        activity_prompt = f"The creature just experienced: {activity.description}"
        if parameters:
            activity_prompt += f" with parameters: {json.dumps(parameters)}"
        
        # Update personality based on activity (evolution system)
        if hasattr(self.creature.personality, 'enhanced_personality') and self.creature.personality.enhanced_personality:
            # Determine activity impact based on stat changes and activity type
            happiness_change = activity_stats_delta.get('happiness', 0)
            energy_change = activity_stats_delta.get('energy', 0)
            
            # Map activity types to evolution triggers and characteristics
            activity_evolution_map = {
                'feed': {'trigger_type': 'achievement' if happiness_change > 0 else 'failure'},
                'play': {'trigger_type': 'positive_interaction', 'bonding': True},
                'pet': {'trigger_type': 'social_bonding', 'bonding': True},
                'walk': {'trigger_type': 'learning_experience', 'exploration': True},
                'train': {'trigger_type': 'learning_experience', 'skill_building': True},
                'rest': {'trigger_type': 'repeated_behavior', 'self_care': True}
            }
            
            activity_info = activity_evolution_map.get(activity_name, {'trigger_type': 'repeated_behavior'})
            
            interaction_data = {
                'type': activity_info['trigger_type'],
                'emotional_impact': happiness_change / 50.0,  # Normalize to -1.0 to 1.0 range
                'primary_emotion': 'happy' if happiness_change > 0 else ('sad' if happiness_change < 0 else 'neutral'),
                'context': {'activity': activity_name, 'parameters': parameters or {}},
                'learning_occurred': activity_info.get('skill_building', False) or activity_info.get('exploration', False),
                'bonding_occurred': activity_info.get('bonding', False) and happiness_change > 0,
                'stress_level': max(0, -happiness_change / 50.0),
                'success': happiness_change > 0,
                'failed': happiness_change < -10
            }
            self.creature.personality.enhanced_personality.update_from_interaction(interaction_data)
        
        # Get the creature's behavioral response to the activity
        message_response = await self.process_message(activity_prompt, context={"activity": activity_name})
        
        # Preserve the activity stat changes by merging with message response changes
        final_stats_delta = activity_stats_delta.copy()
        for stat_name, message_delta in message_response.stats_delta.items():
            final_stats_delta[stat_name] = final_stats_delta.get(stat_name, 0) + message_delta
        
        # Update the response with preserved activity effects
        message_response.stats_delta = final_stats_delta
        
        return message_response
    
    def get_creature_status(self) -> Dict[str, Any]:
        """Get current creature status for debugging/monitoring"""
        current_state = CreatureState.from_creature(self.creature)
        status = {
            "creature_id": str(self.creature.id),
            "name": self.creature.name,
            "species": self.creature.species,
            "template": self.template.id,
            "stats": current_state.stats,
            "mood": current_state.mood,
            "can_translate": self.creature.can_translate(),
            "last_interaction": self.creature.last_interaction_time.isoformat(),
            "memory_count": len(self.creature.memories),
            "chat_history_length": len(self.chat_history)
        }
        
        # Add personality development information if enhanced personality is available
        if hasattr(self.creature.personality, 'enhanced_personality') and self.creature.personality.enhanced_personality:
            enhanced = self.creature.personality.enhanced_personality
            development_analysis = enhanced.get_personality_development_analysis()
            
            status["personality"] = {
                "mode": enhanced.mode.value,
                "evolution_enabled": enhanced.evolution_enabled,
                "active_shifts": len([s for s in enhanced.personality_shifts if not s.is_expired]),
                "total_shifts": len(enhanced.personality_shifts),
                "current_emotional_state": enhanced.current_emotional_state.primary_emotion if enhanced.current_emotional_state else None,
                "development_analysis": development_analysis
            }
        
        return status