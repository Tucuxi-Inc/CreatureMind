"""
Translator Agent - Creates final creature language and human translation

Adapted from the translator logic in WiddlePupper's AIAgentSystem.swift
"""

from typing import Dict, Any
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from .ai_client import AIClient


class TranslatorAgent:
    """
    Creates the final creature language response and optional human translation
    
    This agent takes the decision data and:
    - Converts it into species-appropriate language (barks, roars, etc.)
    - Applies cultural localization
    - Provides human translation only if creature allows it
    - Ensures authenticity to creature perspective
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    async def translate(
        self, 
        decision_data: Dict[str, Any],
        base_creature_language: str,
        creature_state: CreatureState,
        template: CreatureTemplate
    ) -> Dict[str, Any]:
        """
        Create final creature language and translation
        """
        
        system_prompt = self._build_system_prompt(creature_state, template)
        
        # Format decision data for translation
        user_message = self._format_decision_data(decision_data, base_creature_language, creature_state)
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.6
            )
            
            result = self._parse_translation_response(response)
            
            # Check translation conditions from template
            result["can_translate"] = self._check_translation_conditions(creature_state, template)
            
            return result
            
        except Exception as e:
            # Fallback response
            return {
                "creature_language": base_creature_language or "*quiet sound*",
                "human_translation": None,
                "can_translate": False,
                "error": str(e)
            }
    
    def _build_system_prompt(self, creature_state: CreatureState, template: CreatureTemplate) -> str:
        """Build the system prompt for translation"""
        
        # Get available sounds for this creature type
        available_sounds = []
        for emotion, sounds in template.language.sounds.items():
            available_sounds.extend([f"{emotion}: {', '.join(sounds)}"])
        sounds_summary = "\n".join(available_sounds)
        
        system_prompt = f"""You are the Translator Agent for a {creature_state.species}.

Current state: {creature_state.mood}
Energy level: {creature_state.stats.get('energy', 50)}/100

Available creature sounds by emotion:
{sounds_summary}

Review and refine the creature language to:
1. ONLY use these types of responses:
   - Physical actions in asterisks: *tail wag*, *stretch*, *pounce*
   - Creature sounds in asterisks: sounds appropriate to this species
   - Descriptive behaviors: *lying down*, *alert posture*, *gentle approach*

2. NEVER use:
   - Human words or phrases
   - Emojis or punctuation outside asterisks
   - Generic sounds not appropriate to this species

3. Match energy level and physical state:
   - Low energy: tired actions, quiet sounds
   - High energy: active behaviors, loud vocalizations
   - Consider current stats and mood

4. Species authenticity:
   - Use sounds and behaviors appropriate to {creature_state.species}
   - Follow behavioral patterns from the template
   - Maintain creature perspective throughout

5. Cultural appropriateness:
   - Use sounds that match the creature's "language"
   - Consider regional variations if applicable

Response format:
CREATURE_LANGUAGE: (refined creature language using ONLY actions and sounds)
HUMAN_TRANSLATION: (what the creature is trying to communicate, in simple human language)
DEBUG: (explanation of choices made)"""

        return system_prompt
    
    def _format_decision_data(
        self, 
        decision_data: Dict[str, Any], 
        base_creature_language: str,
        creature_state: CreatureState
    ) -> str:
        """Format decision data for the translator"""
        
        return f"""Decision Analysis:
Action: {decision_data.get('action', 'unknown')}
Vocalization: {decision_data.get('vocalization', 'unknown')}
Intention: {decision_data.get('intention', 'unknown')}
Energy Level: {decision_data.get('energy_level', 'medium')}

Base creature language: {base_creature_language}

Current creature state:
- Mood: {creature_state.mood}
- Energy: {creature_state.stats.get('energy', 50)}/100
- Species: {creature_state.species}

Please refine this into authentic creature language and provide human translation."""
    
    def _check_translation_conditions(self, creature_state: CreatureState, template: CreatureTemplate) -> bool:
        """Check if translation conditions are met based on template rules"""
        
        conditions = template.language.translation_conditions
        
        for stat_condition, requirement in conditions.items():
            stat_value = creature_state.stats.get(stat_condition, 0)
            
            # Parse requirement (e.g., "> 50", ">= 30", "< 20")
            if requirement.startswith(">="):
                threshold = float(requirement[2:].strip())
                if stat_value < threshold:
                    return False
            elif requirement.startswith("<="):
                threshold = float(requirement[2:].strip())
                if stat_value > threshold:
                    return False
            elif requirement.startswith(">"):
                threshold = float(requirement[1:].strip())
                if stat_value <= threshold:
                    return False
            elif requirement.startswith("<"):
                threshold = float(requirement[1:].strip())
                if stat_value >= threshold:
                    return False
            elif requirement.startswith("="):
                threshold = float(requirement[1:].strip())
                if stat_value != threshold:
                    return False
        
        return True
    
    def _parse_translation_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured translation data"""
        
        translation_data = {
            "creature_language": "*quiet sound*",
            "human_translation": None,
            "debug_info": ""
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper().replace('_', '_')
                value = value.strip()
                
                if key == "CREATURE_LANGUAGE":
                    translation_data["creature_language"] = value
                elif key == "HUMAN_TRANSLATION":
                    translation_data["human_translation"] = value
                elif key == "DEBUG":
                    translation_data["debug_info"] = value
        
        return translation_data