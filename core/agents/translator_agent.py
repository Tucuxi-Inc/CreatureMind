"""
Translator Agent - Creates final creature language and human translation

Adapted from the translator logic in WiddlePupper's AIAgentSystem.swift
"""

import logging
from typing import Dict, Any
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate
from .ai_client import AIClient

logger = logging.getLogger(__name__)


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
        
        logger.info(f"🔄 TranslatorAgent translating for {creature_state.species}")
        
        system_prompt = self._build_system_prompt(creature_state, template)
        
        # Format decision data for translation
        user_message = self._format_decision_data(decision_data, base_creature_language, creature_state)
        
        try:
            response = await self.ai_client.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.6
            )
            
            logger.info(f"🔄 Creature language generated for {creature_state.species}")
            
            # Get creature stats for translation logic
            happiness = creature_state.stats.get("happiness", 50)
            energy = creature_state.stats.get("energy", 50)
            
            # Determine if translation should be provided based on stats
            can_translate = True
            if happiness < 20 and energy < 20:
                can_translate = False
            elif happiness < 10 or energy < 5:
                can_translate = False
            
            result = self._parse_translation_response(response, decision_data, can_translate)
            
            # Use creature's own translation logic (which is more user-friendly)
            from ..models.creature import Creature
            # We can't directly access the creature here, so we'll create a temporary one
            # In a real implementation, we'd pass the creature or its can_translate status
            
            # For now, use the improved logic directly
            happiness = creature_state.stats.get("happiness", 50)
            energy = creature_state.stats.get("energy", 50)
            
            can_translate = True
            translation_hint = None
            
            # Apply the same improved logic as in creature.can_translate()
            if happiness < 20 and energy < 20:
                can_translate = False
                translation_hint = f"Your {creature_state.species} seems very distressed (happiness: {happiness:.0f}, energy: {energy:.0f}). Try feeding, petting, or playing to help them feel better!"
            elif happiness < 10:
                can_translate = False
                translation_hint = f"Your {creature_state.species} is very upset (happiness: {happiness:.0f}). They need comfort - try petting, feeding, or giving them space to recover."
            elif energy < 5:
                can_translate = False
                translation_hint = f"Your {creature_state.species} is exhausted (energy: {energy:.0f}). They need rest or food to regain energy before they can communicate clearly."
            
            result["can_translate"] = can_translate
            if translation_hint:
                result["translation_hint"] = translation_hint
            
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

Your role is to translate the creature's human language thoughts into authentic creature language.

Current state: {creature_state.mood}
Energy level: {creature_state.stats.get('energy', 50)}/100

Available creature sounds by emotion:
{sounds_summary}

Your task is to translate the human message into creature language:
1. ONLY use expressions appropriate for {creature_state.species}:
   - Physical actions in asterisks that this species can actually do
   - Species-appropriate sounds in asterisks that this species would make
   - Descriptive behaviors authentic to this species

2. SPECIES-SPECIFIC GUIDELINES:
   {self._get_species_guidelines(creature_state.species)}

3. NEVER use:
   - Human words or phrases (except in HUMAN_TRANSLATION)
   - Emojis or punctuation outside asterisks
   - Actions this species cannot physically perform
   - Sounds this species cannot make

4. Match energy level and physical state:
   - Low energy: tired actions, quiet sounds
   - High energy: active behaviors, louder expressions
   - Consider current stats and mood

5. Template authenticity:
   - Follow behavioral patterns from the creature template
   - Use only sounds defined in the template
   - Maintain authentic creature perspective

Response format:
CREATURE_LANGUAGE: [convert the action and vocalization into authentic species-specific language]
DEBUG: [brief notes about creature language choices]

Example for dragon:
Input: Action: "raises head majestically", Vocalization: "low, rumbling growl"
Output:
CREATURE_LANGUAGE: *lifts massive scaled head with ancient dignity* *deep rumble reverberates from chest, echoing like distant thunder*
DEBUG: Dragon displays regal bearing through head position, rumble indicates curiosity"""

        return system_prompt
    
    def _get_species_guidelines(self, species: str) -> str:
        """Get species-specific behavioral guidelines"""
        guidelines = {
            "human": """
   - Use human actions: *nods*, *shrugs*, *gestures*, *leans forward*, *smiles*, *laughs*
   - Use human sounds: *speaks softly*, *chuckles*, *sighs*, *hums*, *whispers*
   - NEVER use animal behaviors: NO tail wagging, purring, barking, ear twitching, etc.
   - Focus on facial expressions, body language, and speech patterns""",
            
            "dog": """
   - Use dog actions: *tail wagging*, *head tilt*, *panting*, *play bow*, *sniffing*
   - Use dog sounds: *woof*, *bark*, *whine*, *growl*, *yip*, *howl*
   - Focus on canine body language and vocalizations""",
            
            "cat": """
   - Use cat actions: *tail flick*, *slow blink*, *head bump*, *kneading*, *stretch*
   - Use cat sounds: *meow*, *purr*, *chirp*, *hiss*, *trill*, *mrow*
   - Focus on feline grace and independence""",
            
            "dragon": """
   - Use dragon actions: *wing flutter*, *smoke puff*, *tail sweep*, *scale shimmer*
   - Use dragon sounds: *rumble*, *roar*, *snort*, *growl*, *whistle*
   - Focus on majestic, powerful movements""",
            
            "fairy": """
   - Use fairy actions: *flutter*, *glow*, *sparkle*, *dance*, *twirl*, *hover*
   - Use fairy sounds: *chime*, *bell*, *whisper*, *giggle*, *sing*, *hum*
   - Focus on magical, delicate movements""",
            
            "elf": """
   - Use elf actions: *graceful movement*, *keen observation*, *light step*, *elegant gesture*
   - Use elf sounds: *whispers*, *soft chant*, *melodic hum*, *gentle voice*
   - Focus on grace and perceptiveness""",
            
            "dwarf": """
   - Use dwarf actions: *sturdy stance*, *strong grip*, *determined nod*, *confident posture*
   - Use dwarf sounds: *gruff voice*, *hearty laugh*, *grumble*, *robust tone*
   - Focus on strength and determination""",
            
            "gnome": """
   - Use gnome actions: *fidgets with tools*, *adjusts spectacles*, *examines closely*, *inventive gesture*
   - Use gnome sounds: *curious mutter*, *excited chatter*, *thoughtful hmm*, *clever giggle*
   - Focus on curiosity and tinkering""",
            
            "sprite": """
   - Use sprite actions: *quick dart*, *shimmering movement*, *tiny gesture*, *delicate flutter*
   - Use sprite sounds: *tiny voice*, *silvery laugh*, *whispered secret*, *musical chime*
   - Focus on quickness and mischief"""
        }
        
        return guidelines.get(species, f"Use behaviors appropriate for {species}")
    
    def _format_decision_data(
        self, 
        decision_data: Dict[str, Any], 
        base_creature_language: str,
        creature_state: CreatureState
    ) -> str:
        """Format decision data for the translator"""
        
        action = decision_data.get('action', 'stands quietly')
        vocalization = decision_data.get('vocalization', 'quiet sound')
        energy_level = decision_data.get('energy_level', 'medium')
        
        return f"""Convert these creature behaviors into authentic {creature_state.species} language:

Action to convert: "{action}"
Vocalization to convert: "{vocalization}"
Energy level: {energy_level}

Current creature state:
- Mood: {creature_state.mood}
- Species: {creature_state.species}

Convert these into species-appropriate actions and sounds that authentically represent a {creature_state.species}'s behavior."""
    
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
    
    def _parse_translation_response(self, response: str, decision_data: Dict[str, Any], can_translate: bool) -> Dict[str, Any]:
        """Parse the AI response into structured translation data"""
        
        # Debug: log the raw response
        logger.info(f"🔍 TRANSLATOR Raw AI response: '{response}'")
        logger.info(f"🔍 TRANSLATOR Response length: {len(response)} chars")
        
        translation_data = {
            "creature_language": "*quiet sound*",
            "human_translation": decision_data.get('human_response') if can_translate else None,
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
                elif key == "DEBUG":
                    translation_data["debug_info"] = value
        
        return translation_data