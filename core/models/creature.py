"""
Creature Model - Generalized from WiddlePupper's Dog.swift

Represents any type of creature/character with configurable stats, personality, and behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum


class StatConfig(BaseModel):
    """Configuration for a creature stat"""
    min_value: float = 0
    max_value: float = 100
    decay_rate: float = 0.1  # Points per hour of inactivity
    default_start: float = 75


class CreatureStats(BaseModel):
    """Dynamic stats system - can be configured per creature type"""
    values: Dict[str, float] = Field(default_factory=dict)
    configs: Dict[str, StatConfig] = Field(default_factory=dict)
    
    def get_stat(self, stat_name: str) -> float:
        """Get a stat value, ensuring it's within bounds"""
        if stat_name not in self.values:
            return self.configs.get(stat_name, StatConfig()).default_start
        
        config = self.configs.get(stat_name, StatConfig())
        return max(config.min_value, min(config.max_value, self.values[stat_name]))
    
    def set_stat(self, stat_name: str, value: float) -> None:
        """Set a stat value, ensuring it's within bounds"""
        config = self.configs.get(stat_name, StatConfig())
        self.values[stat_name] = max(config.min_value, min(config.max_value, value))
    
    def modify_stat(self, stat_name: str, delta: float) -> None:
        """Modify a stat by a delta amount"""
        current = self.get_stat(stat_name)
        self.set_stat(stat_name, current + delta)


class Memory(BaseModel):
    """Creature memory - adapted from WiddlePupper's Memory.swift"""
    id: UUID = Field(default_factory=uuid4)
    type: str  # "chat", "feeding", "activity", etc.
    description: str
    emotional_impact: float = 0.0  # -1.0 to 1.0
    timestamp: datetime = Field(default_factory=datetime.now)
    expiration_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        if self.expiration_date is None:
            return False
        return datetime.now() > self.expiration_date
    
    @property
    def hours_since_creation(self) -> float:
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() / 3600


class CreaturePersonality(BaseModel):
    """Personality configuration for a creature"""
    traits: List[str] = Field(default_factory=list)
    custom_description: str = ""
    base_temperament: str = "neutral"  # "calm", "energetic", "aggressive", etc.
    
    # Enhanced personality system
    enhanced_personality: Optional[Any] = None


class Creature(BaseModel):
    """
    Generalized creature model based on WiddlePupper's Dog class
    
    Can represent any type of creature - dogs, cats, dragons, fairies, etc.
    Stats, personality, and behavior are all configurable via creature templates.
    """
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    species: str  # "dog", "cat", "dragon", "fairy", etc.
    template_id: str  # References creature template for behavior/language
    
    # Personality and traits
    personality: CreaturePersonality = Field(default_factory=CreaturePersonality)
    nicknames: List[str] = Field(default_factory=list)
    
    # Dynamic stats system
    stats: CreatureStats = Field(default_factory=CreatureStats)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    last_interaction_time: datetime = Field(default_factory=datetime.now)
    last_stats_update: datetime = Field(default_factory=datetime.now)
    
    # Memory system
    memories: List[Memory] = Field(default_factory=list)
    
    # Learning/progression system (generalized from training)
    learned_abilities: List[str] = Field(default_factory=list)
    ability_progress: Dict[str, float] = Field(default_factory=dict)
    
    def update_interaction_time(self) -> None:
        """Update the last interaction timestamp"""
        self.last_interaction_time = datetime.now()
    
    def add_memory(self, memory_type: str, description: str, 
                   emotional_impact: float = 0.0, metadata: Dict[str, Any] = None) -> Memory:
        """Add a new memory"""
        memory = Memory(
            type=memory_type,
            description=description,
            emotional_impact=emotional_impact,
            metadata=metadata or {}
        )
        self.memories.append(memory)
        return memory
    
    def get_recent_memories(self, hours: float = 24, memory_type: str = None) -> List[Memory]:
        """Get memories from the last N hours, optionally filtered by type"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.memories if m.timestamp > cutoff and not m.is_expired]
        
        if memory_type:
            recent = [m for m in recent if m.type == memory_type]
        
        return sorted(recent, key=lambda m: m.timestamp, reverse=True)
    
    def update_stats_for_inactivity(self) -> None:
        """Apply stat decay based on time since last interaction"""
        now = datetime.now()
        hours_inactive = (now - self.last_interaction_time).total_seconds() / 3600
        
        # Apply decay to all configured stats
        for stat_name, config in self.stats.configs.items():
            if config.decay_rate > 0:
                decay_amount = config.decay_rate * hours_inactive
                current = self.stats.get_stat(stat_name)
                self.stats.set_stat(stat_name, current - decay_amount)
        
        self.last_stats_update = now
    
    def can_translate(self) -> bool:
        """
        Determine if this creature is in a state to allow human language translation
        Based on creature template rules and current stats
        """
        # More user-friendly translation rules
        # Creatures should generally be willing to communicate unless they're really upset
        
        happiness = self.stats.get_stat("happiness")
        energy = self.stats.get_stat("energy")
        
        # Very restrictive conditions - only refuse translation if creature is in bad shape
        # This creates a better user experience where creatures are generally communicative
        
        # Won't translate if BOTH happiness AND energy are very low (indicating serious distress)
        if happiness < 20 and energy < 20:
            return False
            
        # Won't translate if happiness is extremely low (creature is very upset/depressed)
        if happiness < 10:
            return False
            
        # Won't translate if energy is extremely low (creature is exhausted/unconscious)
        if energy < 5:
            return False
            
        # In all other cases, creature will try to communicate
        # This includes when stats are moderate (30-50) - creature might be tired or a bit unhappy
        # but still willing to communicate their needs
        return True
    
    def get_mood_description(self) -> str:
        """Get a text description of the creature's current mood based on stats"""
        # This could be made more sophisticated with creature-specific logic
        happiness = self.stats.get_stat("happiness")
        energy = self.stats.get_stat("energy")
        
        if happiness >= 80 and energy >= 70:
            return "joyful"
        elif happiness >= 60 and energy >= 50:
            return "content"
        elif happiness < 30:
            return "unhappy"
        elif energy < 30:
            return "tired"
        else:
            return "neutral"


class CreatureState(BaseModel):
    """Snapshot of a creature's current state for agent processing"""
    creature_id: UUID
    stats: Dict[str, float]
    mood: str
    last_interaction_hours: float
    recent_memories: List[Memory]
    personality_traits: List[str]
    species: str
    template_id: str
    
    @classmethod
    def from_creature(cls, creature: Creature) -> "CreatureState":
        """Create a state snapshot from a creature"""
        now = datetime.now()
        hours_since_interaction = (now - creature.last_interaction_time).total_seconds() / 3600
        
        return cls(
            creature_id=creature.id,
            stats={name: creature.stats.get_stat(name) for name in creature.stats.configs.keys()},
            mood=creature.get_mood_description(),
            last_interaction_hours=hours_since_interaction,
            recent_memories=creature.get_recent_memories(hours=12),
            personality_traits=creature.personality.traits,
            species=creature.species,
            template_id=creature.template_id
        )