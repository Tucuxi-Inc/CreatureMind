"""
Creature Template System

Defines the configuration templates that determine how different creature types behave,
what stats they have, what sounds they make, etc.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LanguageConfig(BaseModel):
    """Configuration for creature language/sounds"""
    # Sound mappings for different emotional states/actions
    sounds: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Cultural variations (e.g., different bark sounds in different languages)
    cultural_sounds: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    
    # Conditions that must be met for human translation to be available
    translation_conditions: Dict[str, str] = Field(default_factory=dict)
    
    # Behavioral patterns specific to this creature type
    behavioral_patterns: List[str] = Field(default_factory=list)


class ActivityConfig(BaseModel):
    """Configuration for activities this creature type can perform"""
    name: str
    stat_effects: Dict[str, float] = Field(default_factory=dict)
    energy_cost: float = 0
    description: str = ""
    required_stats: Dict[str, float] = Field(default_factory=dict)


class CreatureTemplate(BaseModel):
    """
    Template that defines a creature type's characteristics and behavior
    
    This is the configuration that makes a "dog" different from a "dragon"
    """
    
    # Basic identification
    id: str  # e.g., "loyal_dog", "ancient_dragon", "playful_cat"
    name: str  # Human-readable name
    species: str  # Base species category
    category: str = "mammal"  # "mammal", "reptile", "mythical", etc.
    
    # Description and traits
    description: str = ""
    default_personality_traits: List[str] = Field(default_factory=list)
    temperament_options: List[str] = Field(default_factory=list)
    
    # Stats configuration
    stat_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Language and behavior
    language: LanguageConfig = Field(default_factory=LanguageConfig)
    
    # Available activities
    activities: List[ActivityConfig] = Field(default_factory=list)
    
    # Learning/progression system
    learnable_abilities: List[str] = Field(default_factory=list)
    ability_difficulty: Dict[str, int] = Field(default_factory=dict)  # 1-5 scale
    
    # AI prompt customization
    perception_prompt_additions: str = ""
    emotion_prompt_additions: str = ""
    decision_prompt_additions: str = ""
    
    def get_default_stats(self) -> Dict[str, float]:
        """Get the default starting stats for this creature type"""
        defaults = {}
        for stat_name, config in self.stat_configs.items():
            defaults[stat_name] = config.get("default_start", 75)
        return defaults
    
    def get_sound_for_emotion(self, emotion: str, energy_level: float = 50) -> str:
        """Get an appropriate sound for the given emotion and energy level"""
        if emotion not in self.language.sounds:
            emotion = "neutral"
        
        sounds = self.language.sounds.get(emotion, ["*quiet sound*"])
        
        # Simple energy-based selection (could be more sophisticated)
        if energy_level < 30:
            # Use first sound (typically quieter/more tired)
            return sounds[0] if sounds else "*tired sound*"
        elif energy_level > 70:
            # Use last sound (typically more energetic)
            return sounds[-1] if sounds else "*energetic sound*"
        else:
            # Use middle sound or random
            import random
            return random.choice(sounds) if sounds else "*neutral sound*"
    
    def can_learn_ability(self, ability: str) -> bool:
        """Check if this creature type can learn the given ability"""
        return ability in self.learnable_abilities
    
    def get_ability_difficulty(self, ability: str) -> int:
        """Get the learning difficulty for an ability (1-5, 0 = can't learn)"""
        if not self.can_learn_ability(ability):
            return 0
        return self.ability_difficulty.get(ability, 3)  # Default medium difficulty


# Predefined base templates that can be extended
BASE_TEMPLATES = {
    "mammal": CreatureTemplate(
        id="base_mammal",
        name="Base Mammal",
        species="mammal",
        stat_configs={
            "happiness": {"min_value": 0, "max_value": 100, "decay_rate": 0.1, "default_start": 75},
            "energy": {"min_value": 0, "max_value": 100, "decay_rate": 0.2, "default_start": 80},
            "hunger": {"min_value": 0, "max_value": 100, "decay_rate": 0.3, "default_start": 40}
        },
        language=LanguageConfig(
            sounds={
                "happy": ["*content sound*"],
                "sad": ["*whimper*"],
                "excited": ["*energetic sound*"],
                "tired": ["*yawn*"],
                "neutral": ["*quiet sound*"]
            },
            translation_conditions={
                "happiness": "> 40",
                "energy": "> 30"
            }
        )
    ),
    
    "reptile": CreatureTemplate(
        id="base_reptile", 
        name="Base Reptile",
        species="reptile",
        stat_configs={
            "happiness": {"min_value": 0, "max_value": 100, "decay_rate": 0.05, "default_start": 60},
            "energy": {"min_value": 0, "max_value": 100, "decay_rate": 0.1, "default_start": 70},
            "temperature": {"min_value": 0, "max_value": 100, "decay_rate": 0.15, "default_start": 75}
        },
        language=LanguageConfig(
            sounds={
                "happy": ["*content hiss*"],
                "angry": ["*warning hiss*", "*aggressive rattle*"],
                "cold": ["*sluggish movement*"],
                "warm": ["*basking stretch*"]
            },
            translation_conditions={
                "happiness": "> 30",
                "temperature": "> 50"
            }
        )
    ),
    
    "mythical": CreatureTemplate(
        id="base_mythical",
        name="Base Mythical Creature", 
        species="mythical",
        stat_configs={
            "happiness": {"min_value": 0, "max_value": 100, "decay_rate": 0.08, "default_start": 70},
            "energy": {"min_value": 0, "max_value": 100, "decay_rate": 0.12, "default_start": 85},
            "magical_power": {"min_value": 0, "max_value": 100, "decay_rate": 0.05, "default_start": 90}
        },
        language=LanguageConfig(
            sounds={
                "mystical": ["*ethereal shimmer*", "*magical resonance*"],
                "powerful": ["*ancient rumble*", "*otherworldly presence*"],
                "weakened": ["*fading glow*", "*tired magic*"]
            },
            translation_conditions={
                "magical_power": "> 40"
            }
        )
    )
}