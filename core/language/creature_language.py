"""
Creature Language System - Generalized from WiddlePupper's BarkLanguage.swift

Handles species-specific language generation, cultural localization, and
behavioral patterns for different creature types.
"""

from typing import Dict, Any
import random
from ..models.creature import CreatureState
from ..models.creature_template import CreatureTemplate


class CreatureLanguage:
    """
    Generates creature-appropriate language based on emotional state and species type
    
    Adapted from WiddlePupper's BarkLanguage system but generalized for any creature.
    """
    
    def __init__(self, template: CreatureTemplate):
        self.template = template
        self.current_language = "en"  # Default language
    
    def generate_response(
        self, 
        decision_data: Dict[str, Any], 
        emotion_state: str,
        creature_state: CreatureState
    ) -> str:
        """
        Generate base creature language response
        
        This creates a rough translation that will be refined by the translator agent.
        """
        
        # Get energy level from decision data or creature state
        energy_level = decision_data.get("energy_level", "medium")
        energy_value = creature_state.stats.get("energy", 50)
        
        # Map energy level to numeric value if needed
        if energy_level == "low":
            energy_value = min(energy_value, 30)
        elif energy_level == "high":
            energy_value = max(energy_value, 70)
        
        # Get emotion-appropriate sound
        emotion_sound = self._get_emotion_sound(emotion_state, energy_value)
        
        # Get action from decision
        action = decision_data.get("action", "*quiet observation*")
        
        # Get vocalization from decision
        vocalization = decision_data.get("vocalization", "*soft sound*")
        
        # Combine into creature language
        base_response = f"{action} {vocalization} {emotion_sound}"
        
        # Apply state modifiers
        modified_response = self._apply_state_modifiers(base_response, creature_state)
        
        return modified_response.strip()
    
    def _get_emotion_sound(self, emotion: str, energy_level: float) -> str:
        """Get appropriate sound for emotion and energy level"""
        
        if emotion not in self.template.language.sounds:
            emotion = "neutral"
        
        sounds = self.template.language.sounds.get(emotion, ["*quiet sound*"])
        
        # Select sound based on energy level
        if energy_level < 30:
            # Low energy - use first (typically quieter) sound
            return sounds[0] if sounds else "*tired sound*"
        elif energy_level > 70:
            # High energy - use last (typically more energetic) sound
            return sounds[-1] if sounds else "*energetic sound*"
        else:
            # Medium energy - use middle or random sound
            return sounds[len(sounds)//2] if sounds else "*neutral sound*"
    
    def _apply_state_modifiers(self, base_response: str, creature_state: CreatureState) -> str:
        """Apply state-based modifications to the response"""
        
        modified = base_response
        stats = creature_state.stats
        
        # Energy level modifications
        energy = stats.get("energy", 50)
        if energy < 20:
            # Very low energy - replace active actions with tired ones
            modified = self._replace_energetic_actions(modified, "very_tired")
        elif energy < 40:
            # Low energy - replace some actions with tired alternatives
            modified = self._replace_energetic_actions(modified, "tired")
        
        # Happiness modifications
        happiness = stats.get("happiness", 50)
        if happiness < 30:
            # Low happiness - add sad elements
            if "*happy*" in modified.lower():
                modified = modified.replace("*happy*", "*subdued*")
            if not any(sad_word in modified.lower() for sad_word in ["*droop*", "*whimper*", "*sad*"]):
                modified = "*subdued demeanor* " + modified
        
        # Hunger modifications
        hunger = stats.get("hunger", 50)
        if hunger < 30:
            # Very hungry - add hunger indicators
            if not any(hunger_word in modified.lower() for hunger_word in ["*stomach*", "*food*", "*hungry*"]):
                modified = "*stomach rumbles quietly* " + modified
        
        return modified
    
    def _replace_energetic_actions(self, text: str, energy_state: str) -> str:
        """Replace energetic actions with tired alternatives"""
        
        if energy_state == "very_tired":
            replacements = {
                "*jump*": "*slow movement*",
                "*bounce*": "*gentle sway*",
                "*run*": "*slow walk*",
                "*pounce*": "*careful approach*",
                "*leap*": "*small step*",
                "*excited*": "*weary*",
                "*energetic*": "*tired*"
            }
        else:  # tired
            replacements = {
                "*jump*": "*small hop*",
                "*bounce*": "*gentle movement*",
                "*run*": "*trot*",
                "*excited*": "*mildly interested*"
            }
        
        for original, replacement in replacements.items():
            text = text.replace(original, replacement)
        
        return text
    
    def get_busy_response(self) -> str:
        """Get a response when the creature mind is busy processing"""
        busy_sounds = self.template.language.sounds.get("confused", ["*thoughtful pause*"])
        return f"*processing* {random.choice(busy_sounds)}"
    
    def get_error_response(self) -> str:
        """Get a response when an error occurs"""
        confused_sounds = self.template.language.sounds.get("confused", ["*confused sound*"])
        return f"*tilted head* {random.choice(confused_sounds)}"
    
    def localize_for_language(self, text: str, language_code: str = None) -> str:
        """
        Apply cultural localization to creature language
        
        This could be expanded to include cultural variations of creature sounds.
        """
        if language_code is None:
            language_code = self.current_language
        
        # Basic cultural sound mapping
        cultural_sounds = self.template.language.cultural_sounds.get(language_code, {})
        
        localized = text
        for generic_sound, cultural_sound in cultural_sounds.items():
            localized = localized.replace(f"*{generic_sound}*", f"*{cultural_sound}*")
        
        return localized
    
    def set_language(self, language_code: str):
        """Set the current language for localization"""
        self.current_language = language_code