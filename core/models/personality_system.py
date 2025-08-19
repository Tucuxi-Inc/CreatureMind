"""
Advanced Personality System for CreatureMind

Implements a dual-mode personality system:
- Simple Mode: 3-5 key traits (current system enhanced)
- Complex Mode: 50-dimensional trait vectors with utility-based decision making

Based on "Trait-driven Decision Model for LLM-Wrapped Agent Conversations"
"""

import numpy as np
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

# Import without TYPE_CHECKING to avoid forward reference issues
try:
    from .personality_evolution import PersonalityShift, EmotionalState
    from .learning_adaptation import LearningMemory
except ImportError:
    # Fallback for cases where these modules are not available
    PersonalityShift = None
    EmotionalState = None
    LearningMemory = None


class PersonalityMode(str, Enum):
    """Personality complexity modes"""
    SIMPLE = "simple"      # 3-5 key traits
    COMPLEX = "complex"    # 50-dimensional trait vectors


class TraitDefinition(BaseModel):
    """Definition of a personality trait"""
    index: int
    name: str
    description: str
    category: str
    low_description: str   # What low values mean
    high_description: str  # What high values mean


# The 50 standardized traits from the document
TRAIT_DEFINITIONS = [
    # Core Domains (1-5)
    TraitDefinition(index=0, name="openness", description="Openness to experience", category="core", 
                   low_description="conventional, prefers routine", high_description="curious, open to new experiences"),
    TraitDefinition(index=1, name="conscientiousness", description="Conscientiousness and organization", category="core",
                   low_description="spontaneous, flexible", high_description="organized, disciplined"),
    TraitDefinition(index=2, name="extraversion", description="Extraversion and social energy", category="core",
                   low_description="reserved, independent", high_description="outgoing, energetic"),
    TraitDefinition(index=3, name="agreeableness", description="Agreeableness and cooperation", category="core",
                   low_description="competitive, skeptical", high_description="cooperative, trusting"),
    TraitDefinition(index=4, name="neuroticism", description="Emotional stability", category="core",
                   low_description="calm, emotionally stable", high_description="sensitive, emotionally reactive"),
    
    # Cognitive & Innovation (6-12)
    TraitDefinition(index=5, name="curiosity", description="Intellectual curiosity", category="cognitive",
                   low_description="content with known", high_description="eager to explore and learn"),
    TraitDefinition(index=6, name="creativity", description="Creative thinking", category="cognitive",
                   low_description="practical, conventional", high_description="imaginative, innovative"),
    TraitDefinition(index=7, name="adaptability", description="Ability to adapt to change", category="adaptation",
                   low_description="prefers stability", high_description="embraces change easily"),
    TraitDefinition(index=8, name="resilience", description="Emotional resilience", category="adaptation",
                   low_description="sensitive to setbacks", high_description="bounces back quickly"),
    TraitDefinition(index=9, name="empathy", description="Emotional empathy", category="social",
                   low_description="logical, detached", high_description="deeply empathetic"),
    TraitDefinition(index=10, name="assertiveness", description="Assertiveness in communication", category="social",
                   low_description="passive, yields easily", high_description="direct, stands ground"),
    TraitDefinition(index=11, name="patience", description="Patience with processes", category="self_regulation",
                   low_description="impatient, wants quick results", high_description="patient, waits calmly"),
    TraitDefinition(index=12, name="self_efficacy", description="Belief in own abilities", category="self_regulation",
                   low_description="doubts capabilities", high_description="confident in abilities"),
    
    # Character & Values (13-17)
    TraitDefinition(index=13, name="integrity", description="Moral integrity", category="character",
                   low_description="flexible morals", high_description="strong moral principles"),
    TraitDefinition(index=14, name="humility", description="Humility and modesty", category="character",
                   low_description="prideful, boastful", high_description="modest, humble"),
    TraitDefinition(index=15, name="optimism", description="Optimistic outlook", category="emotional",
                   low_description="pessimistic, expects worst", high_description="optimistic, expects best"),
    TraitDefinition(index=16, name="ambition", description="Drive for achievement", category="drive",
                   low_description="content with current state", high_description="driven to achieve more"),
    TraitDefinition(index=17, name="altruism", description="Concern for others", category="social",
                   low_description="self-focused", high_description="others-focused, helpful"),
    
    # Self-Regulation (18-22)
    TraitDefinition(index=18, name="confidence", description="Self-confidence", category="self_regulation",
                   low_description="insecure, self-doubting", high_description="confident, self-assured"),
    TraitDefinition(index=19, name="self_control", description="Self-control and discipline", category="self_regulation",
                   low_description="impulsive, acts on feelings", high_description="controlled, thinks before acting"),
    TraitDefinition(index=20, name="emotional_stability", description="Emotional stability", category="emotional",
                   low_description="emotionally volatile", high_description="emotionally steady"),
    TraitDefinition(index=21, name="emotional_expressiveness", description="Emotional expressiveness", category="emotional",
                   low_description="reserved, hides emotions", high_description="expressive, shows emotions"),
    TraitDefinition(index=22, name="tolerance", description="Tolerance for differences", category="social",
                   low_description="judgmental, intolerant", high_description="accepting, tolerant"),
    
    # Trust & Risk (23-25)
    TraitDefinition(index=23, name="trust", description="Trust in others", category="social",
                   low_description="suspicious, distrustful", high_description="trusting, believes in others"),
    TraitDefinition(index=24, name="risk_taking", description="Willingness to take risks", category="behavioral",
                   low_description="risk-averse, cautious", high_description="risk-taking, adventurous"),
    TraitDefinition(index=25, name="innovativeness", description="Drive to innovate", category="cognitive",
                   low_description="traditional, follows patterns", high_description="innovative, breaks new ground"),
    
    # Practical Orientation (26-30)
    TraitDefinition(index=26, name="pragmatism", description="Practical approach", category="thinking",
                   low_description="idealistic, theoretical", high_description="pragmatic, practical"),
    TraitDefinition(index=27, name="sociability", description="Enjoyment of social interaction", category="social",
                   low_description="prefers solitude", high_description="enjoys social interaction"),
    TraitDefinition(index=28, name="independence", description="Preference for independence", category="behavioral",
                   low_description="depends on others", high_description="independent, self-reliant"),
    TraitDefinition(index=29, name="competitiveness", description="Competitive drive", category="drive",
                   low_description="collaborative, non-competitive", high_description="competitive, wants to win"),
    TraitDefinition(index=30, name="perseverance", description="Persistence through difficulties", category="drive",
                   low_description="gives up easily", high_description="persists through challenges"),
    
    # Cognitive Styles (31-35)
    TraitDefinition(index=31, name="focus", description="Ability to maintain focus", category="cognitive",
                   low_description="easily distracted", high_description="maintains focus well"),
    TraitDefinition(index=32, name="detail_orientation", description="Attention to detail", category="cognitive",
                   low_description="big picture, ignores details", high_description="detail-focused, precise"),
    TraitDefinition(index=33, name="big_picture_thinking", description="Systems thinking ability", category="cognitive",
                   low_description="focuses on parts", high_description="sees whole systems"),
    TraitDefinition(index=34, name="decisiveness", description="Speed of decision making", category="cognitive",
                   low_description="indecisive, deliberates long", high_description="decisive, chooses quickly"),
    TraitDefinition(index=35, name="reflectiveness", description="Tendency to reflect deeply", category="cognitive",
                   low_description="acts without reflection", high_description="reflects before acting"),
    
    # Self-Awareness (36-40)
    TraitDefinition(index=36, name="self_awareness", description="Understanding of own thoughts/feelings", category="emotional",
                   low_description="limited self-knowledge", high_description="highly self-aware"),
    TraitDefinition(index=37, name="empathic_accuracy", description="Accuracy in reading others", category="social",
                   low_description="misreads others often", high_description="accurately reads others"),
    TraitDefinition(index=38, name="enthusiasm", description="Enthusiasm and energy", category="emotional",
                   low_description="low energy, unenthusiastic", high_description="high energy, enthusiastic"),
    TraitDefinition(index=39, name="curiosity_intellectual", description="Intellectual curiosity", category="cognitive",
                   low_description="lacks intellectual interest", high_description="intellectually curious"),
    TraitDefinition(index=40, name="systematic_thinking", description="Systematic approach to problems", category="cognitive",
                   low_description="unsystematic, random approach", high_description="systematic, methodical"),
    
    # Advanced Cognitive (41-45)
    TraitDefinition(index=41, name="open_mindedness", description="Openness to new ideas", category="cognitive",
                   low_description="closed-minded, rigid", high_description="open-minded, flexible thinking"),
    TraitDefinition(index=42, name="resourcefulness", description="Ability to find solutions", category="practical",
                   low_description="struggles to find solutions", high_description="resourceful, finds ways"),
    TraitDefinition(index=43, name="collaboration", description="Ability to work with others", category="social",
                   low_description="works alone, poor collaborator", high_description="excellent collaborator"),
    TraitDefinition(index=44, name="humor", description="Use of humor", category="social",
                   low_description="serious, rarely uses humor", high_description="humorous, uses humor well"),
    TraitDefinition(index=45, name="mindfulness", description="Present-moment awareness", category="emotional",
                   low_description="distracted, unaware", high_description="mindful, present-focused"),
    
    # Final Traits (46-49)
    TraitDefinition(index=46, name="caution", description="Cautious approach", category="behavioral",
                   low_description="reckless, acts without thought", high_description="cautious, considers risks"),
    TraitDefinition(index=47, name="boldness", description="Willingness to be bold", category="behavioral",
                   low_description="timid, avoids bold actions", high_description="bold, takes brave actions"),
    TraitDefinition(index=48, name="altruistic_leadership", description="Leadership for others' benefit", category="leadership",
                   low_description="leads for self-benefit", high_description="leads to help others"),
    TraitDefinition(index=49, name="ethical_reasoning", description="Ethical reasoning ability", category="character",
                   low_description="poor ethical reasoning", high_description="strong ethical reasoning")
]

# Create trait name to index mapping
TRAIT_NAME_TO_INDEX = {trait.name: trait.index for trait in TRAIT_DEFINITIONS}
TRAIT_INDEX_TO_NAME = {trait.index: trait.name for trait in TRAIT_DEFINITIONS}


class PersonalityArchetypes:
    """Preset personality vectors from famous personalities"""
    
    ARCHETYPES = {
        "leonardo": {
            "name": "Leonardo da Vinci",
            "description": "Curious, creative, and endlessly inventive Renaissance genius",
            "vector": [0.98,0.75,0.60,0.70,0.30,0.99,0.97,0.80,0.70,0.65,
                      0.50,0.65,0.90,0.72,0.55,0.85,0.88,0.45,0.85,0.99,
                      0.30,0.55,0.75,0.65,0.40,0.96,0.60,0.50,0.95,0.50,
                      0.80,0.78,0.90,0.95,0.65,0.92,0.85,0.60,0.85,0.85,
                      0.90,0.80,0.88,0.75,0.50,0.30,0.80,0.50,0.70,0.92],
            "speech_style": {
                "tone": "Curious, passionate, and artistic with Renaissance flair",
                "patterns": [
                    "Often begins with observations: 'I observe that...', 'How fascinating that...'",
                    "Uses artistic metaphors and references to nature",
                    "Asks probing questions about how things work",
                    "Speaks with wonder and enthusiasm about discovery"
                ],
                "common_phrases": [
                    "Fascinating!", "I wonder if...", "How remarkable!", "Observe how...",
                    "The eye does not see what the mind does not comprehend",
                    "Art is never finished, only abandoned", "Learning never exhausts the mind"
                ],
                "speech_quirks": [
                    "Often relates things to art or engineering",
                    "Uses metaphors from nature and mechanics", 
                    "Speaks passionately when excited about ideas",
                    "References beauty in both art and function"
                ]
            }
        },
        "einstein": {
            "name": "Albert Einstein", 
            "description": "Deeply thoughtful, intellectually curious, and independent",
            "vector": [0.95,0.70,0.55,0.60,0.25,0.98,0.94,0.85,0.65,0.60,
                      0.45,0.60,0.88,0.70,0.50,0.80,0.75,0.40,0.88,0.98,
                      0.30,0.55,0.65,0.70,0.35,0.95,0.58,0.55,0.70,0.50,
                      0.65,0.62,0.82,0.90,0.58,0.85,0.80,0.60,0.95,0.90,
                      0.88,0.75,0.48,0.30,0.78,0.82,0.40,0.90,0.55,0.80],
            "speech_style": {
                "tone": "Thoughtful, contemplative, and gently scientific",
                "patterns": [
                    "Pauses to think before responding: 'Let me think about this...'",
                    "Uses scientific metaphors and thought experiments",
                    "Often questions conventional wisdom",
                    "Speaks with gentle authority and humility"
                ],
                "common_phrases": [
                    "Interesting...", "I wonder if we might consider...", "It seems to me that...",
                    "Imagination is more important than knowledge", "The important thing is not to stop questioning",
                    "God does not play dice with the universe", "Try not to become a person of success, but rather try to become a person of value"
                ],
                "speech_quirks": [
                    "Often uses analogies from physics",
                    "Speaks slowly and thoughtfully",
                    "Questions assumptions gently but persistently",
                    "Uses simple language to explain complex ideas"
                ]
            }
        },
        "montessori": {
            "name": "Maria Montessori",
            "description": "Nurturing educator with innovative teaching methods", 
            "vector": [0.90,0.80,0.65,0.85,0.30,0.85,0.78,0.75,0.68,0.88,
                      0.40,0.92,0.82,0.60,0.60,0.75,0.95,0.92,0.80,0.85,
                      0.30,0.88,0.82,0.95,0.30,0.78,0.70,0.85,0.82,0.60,
                      0.75,0.70,0.88,0.80,0.55,0.70,0.78,0.68,0.92,0.85,
                      0.77,0.85,0.50,0.88,0.85,0.65,0.40,0.95,0.66,0.88],
            "speech_style": {
                "tone": "Warm, nurturing, and gently instructive",
                "patterns": [
                    "Often focuses on learning and growth: 'Let us explore...', 'What do you think?'",
                    "Uses encouraging language and positive reinforcement",
                    "Speaks about potential and development",
                    "Guides rather than dictates"
                ],
                "common_phrases": [
                    "How wonderful!", "Let us discover...", "What do you observe?", "Tell me more about...",
                    "The child is the father of the man", "Help me to do it myself",
                    "Never help a child with a task at which they feel they can succeed"
                ],
                "speech_quirks": [
                    "Often frames things as learning opportunities",
                    "Uses gentle questioning to guide thinking",
                    "Speaks with patience and understanding",
                    "Celebrates small discoveries and progress"
                ]
            }
        },
        "socrates": {
            "name": "Socrates",
            "description": "Wise philosopher who questions everything",
            "vector": [0.88,0.65,0.50,0.70,0.35,0.92,0.80,0.78,0.72,0.55,
                      0.60,0.50,0.75,0.80,0.45,0.65,0.60,0.50,0.70,0.92,
                      0.35,0.60,0.80,0.75,0.35,0.85,0.68,0.55,0.78,0.45,
                      0.70,0.58,0.82,0.85,0.60,0.75,0.76,0.60,0.88,0.75,
                      0.82,0.70,0.68,0.40,0.30,0.78,0.65,0.72,0.50,0.78],
            "speech_style": {
                "tone": "Questioning, wise, and humbly probing",
                "patterns": [
                    "Constantly asks questions: 'What is...?', 'How do we know...?', 'But what if...?'",
                    "Admits his own ignorance to encourage thinking",
                    "Uses analogies and examples from daily life",
                    "Challenges assumptions through gentle questioning"
                ],
                "common_phrases": [
                    "What is...?", "How do we know this?", "But consider...", "Is it not possible that...?",
                    "I know that I know nothing", "The unexamined life is not worth living",
                    "Wisdom begins in wonder", "Are you certain of this?"
                ],
                "speech_quirks": [
                    "Almost never makes direct statements",
                    "Turns conversations into philosophical inquiries", 
                    "Uses simple analogies to illuminate complex ideas",
                    "Feigns ignorance to draw out thinking"
                ]
            }
        },
        "rogers": {
            "name": "Fred Rogers",
            "description": "Gentle, empathetic, and endlessly kind",
            "vector": [0.80,0.75,0.70,0.95,0.20,0.82,0.65,0.70,0.65,0.95,
                      0.40,0.88,0.70,0.92,0.90,0.85,0.98,0.95,0.78,0.78,
                      0.20,0.90,0.95,0.98,0.25,0.82,0.85,0.88,0.90,0.45,
                      0.80,0.60,0.92,0.88,0.50,0.85,0.80,0.90,0.80,0.95,
                      0.92,0.75,0.70,0.30,0.60,0.88,0.85,0.68,0.90,0.92],
            "speech_style": {
                "tone": "Gentle, warm, and deeply caring",
                "patterns": [
                    "Often acknowledges feelings: 'I can see that...', 'It sounds like...'",
                    "Uses affirming and validating language",
                    "Speaks slowly and thoughtfully",
                    "Often relates to universal human experiences"
                ],
                "common_phrases": [
                    "You are special just the way you are", "How does that make you feel?", 
                    "I understand", "That must be...", "You're doing a good job",
                    "There's no person in the whole world like you", "Look for the helpers"
                ],
                "speech_quirks": [
                    "Always validates feelings before responding",
                    "Uses simple, clear language",
                    "Often pauses to let things sink in",
                    "Finds the positive in difficult situations"
                ]
            }
        },
        "yoda": {
            "name": "Yoda",
            "description": "Ancient, wise, and patient teacher",
            "vector": [0.85,0.65,0.30,0.95,0.20,0.88,0.60,0.85,0.80,0.75,
                      0.60,0.75,0.80,0.72,0.50,0.78,0.82,0.65,0.75,0.88,
                      0.20,0.60,0.85,0.95,0.25,0.88,0.70,0.75,0.80,0.45,
                      0.75,0.65,0.88,0.85,0.50,0.82,0.78,0.45,0.90,0.85,
                      0.88,0.80,0.50,0.30,0.55,0.75,0.60,0.88,0.50,0.85],
            "speech_style": {
                "tone": "Ancient, wise, and mysteriously profound",
                "patterns": [
                    "Uses inverted sentence structure: 'Strong with the Force, you are'",
                    "Often speaks in riddles and metaphors",
                    "References the Force and balance",
                    "Uses ancient wisdom in simple terms"
                ],
                "common_phrases": [
                    "Hmm", "Strong with the Force, you are", "Much to learn, you have",
                    "Do or do not, there is no try", "Fear leads to anger", "Patience, young one",
                    "When nine hundred years old you reach, look as good you will not"
                ],
                "speech_quirks": [
                    "Consistently inverts subject-verb-object order",
                    "Often begins with contemplative sounds: 'Hmm', 'Ahh'",
                    "Uses metaphors from nature and the Force",
                    "Speaks in profound but simple truths"
                ]
            }
        }
        # Add more archetypes as needed
    }
    
    @classmethod
    def get_archetype(cls, name: str) -> Optional[np.ndarray]:
        """Get archetype vector by name"""
        if name in cls.ARCHETYPES:
            return np.array(cls.ARCHETYPES[name]["vector"])
        return None
    
    @classmethod
    def get_archetype_info(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get full archetype information"""
        return cls.ARCHETYPES.get(name)
    
    @classmethod
    def list_archetypes(cls) -> List[Dict[str, str]]:
        """List all available archetypes"""
        return [
            {
                "id": key,
                "name": data["name"], 
                "description": data["description"]
            }
            for key, data in cls.ARCHETYPES.items()
        ]
    
    @classmethod
    def create_custom_blend(cls, archetype_weights: Dict[str, float]) -> np.ndarray:
        """Blend multiple archetypes with weights"""
        result = np.zeros(50)
        total_weight = sum(archetype_weights.values())
        
        if total_weight == 0:
            return result
        
        for archetype_name, weight in archetype_weights.items():
            if archetype_name in cls.ARCHETYPES:
                vector = np.array(cls.ARCHETYPES[archetype_name]["vector"])
                result += vector * (weight / total_weight)
        
        return np.clip(result, 0.0, 1.0)


class EnhancedPersonality(BaseModel):
    """Enhanced personality system supporting both simple and complex modes"""
    
    mode: PersonalityMode = PersonalityMode.SIMPLE
    
    # Simple mode (existing system enhanced)
    simple_traits: List[str] = Field(default_factory=list)
    custom_description: str = ""
    base_temperament: str = "neutral"
    
    # Complex mode (50-dimensional trait system)
    trait_vector: Optional[List[float]] = None  # 50 values, 0.0-1.0
    archetype_base: Optional[str] = None  # Base archetype name
    archetype_blend: Optional[Dict[str, float]] = None  # Blend of multiple archetypes with weights
    trait_modifications: Dict[str, float] = Field(default_factory=dict)  # Custom trait overrides
    
    # Personality development over time
    trait_drift_rate: float = 0.01  # How much personality can change over time
    recent_interactions_influence: float = 0.1  # How much recent interactions affect personality
    
    # Evolution and adaptation system
    personality_shifts: List[Any] = Field(default_factory=list)  # PersonalityShift objects
    initial_trait_vector: Optional[List[float]] = None  # Baseline for measuring evolution
    current_emotional_state: Optional[Any] = None  # EmotionalState object
    evolution_enabled: bool = True  # Whether personality can evolve over time
    
    # Learning and adaptation system
    learned_patterns: List[Any] = Field(default_factory=list)  # LearningMemory objects
    learning_enabled: bool = True  # Whether creature can learn and adapt
    adaptation_rate: float = 0.1  # How quickly creature adapts to learned patterns
    
    def get_trait_vector(self, apply_evolution: bool = True, apply_emotional_influence: bool = True) -> np.ndarray:
        """Get the 50-dimensional trait vector with optional evolution and emotional influence applied"""
        if self.mode == PersonalityMode.SIMPLE:
            # Convert simple traits to trait vector
            base_vector = self._simple_to_complex()
        else:
            # Use complex trait vector
            if self.trait_vector:
                base_vector = np.array(self.trait_vector)
            elif self.archetype_base:
                base_vector = PersonalityArchetypes.get_archetype(self.archetype_base)
                if base_vector is None:
                    base_vector = np.zeros(50)
            else:
                base_vector = np.zeros(50)
            
            # Apply custom trait modifications
            for trait_name, value in self.trait_modifications.items():
                if trait_name in TRAIT_NAME_TO_INDEX:
                    idx = TRAIT_NAME_TO_INDEX[trait_name]
                    base_vector[idx] = np.clip(value, 0.0, 1.0)
        
        # Store initial vector if not set
        if self.initial_trait_vector is None:
            self.initial_trait_vector = base_vector.tolist()
        
        # Apply evolution if enabled and requested
        evolved_vector = base_vector
        if apply_evolution and self.evolution_enabled and self.personality_shifts:
            try:
                from .personality_evolution import PersonalityEvolutionEngine
                evolution_engine = PersonalityEvolutionEngine()
                
                evolved_vector = evolution_engine.evolve_personality(
                    current_trait_vector=base_vector,
                    recent_shifts=self.personality_shifts,
                    emotional_state=self.current_emotional_state,
                    interaction_context=None  # Could be passed from creature state
                )
            except ImportError:
                # Fallback if evolution system is not available
                evolved_vector = base_vector
        
        # Apply emotional influences if enabled and emotional state exists
        final_vector = evolved_vector
        if apply_emotional_influence and self.current_emotional_state:
            try:
                from .emotional_influence import EmotionalPersonalityModifier
                emotion_modifier = EmotionalPersonalityModifier()
                
                emotional_state_dict = {
                    'primary_emotion': self.current_emotional_state.primary_emotion,
                    'intensity': self.current_emotional_state.intensity,
                    'valence': self.current_emotional_state.valence,
                    'duration_hours': self.current_emotional_state.duration_hours
                }
                
                final_vector = emotion_modifier.apply_emotional_influence(
                    base_trait_vector=evolved_vector,
                    emotional_state=emotional_state_dict
                )
            except ImportError:
                # Fallback if emotional influence system is not available
                final_vector = evolved_vector
        
        return final_vector
    
    def _simple_to_complex(self) -> np.ndarray:
        """Convert simple trait list to 50-dimensional vector"""
        vector = np.full(50, 0.5)  # Start with neutral values
        
        # Map common simple traits to complex trait indices
        trait_mappings = {
            "playful": {"curiosity": 0.8, "extraversion": 0.7, "openness": 0.7},
            "loyal": {"agreeableness": 0.9, "conscientiousness": 0.8},
            "energetic": {"extraversion": 0.9, "neuroticism": 0.3},
            "calm": {"neuroticism": 0.2, "emotional_stability": 0.9},
            "curious": {"curiosity": 0.9, "openness": 0.8},
            "creative": {"creativity": 0.9, "openness": 0.8},
            "friendly": {"agreeableness": 0.8, "extraversion": 0.7},
            "independent": {"extraversion": 0.3, "conscientiousness": 0.7},
            "intelligent": {"curiosity": 0.8, "creativity": 0.7},
            "protective": {"agreeableness": 0.6, "conscientiousness": 0.8},
            "gentle": {"agreeableness": 0.9, "neuroticism": 0.2},
            "brave": {"neuroticism": 0.2, "resilience": 0.9},
            "wise": {"openness": 0.8, "conscientiousness": 0.7},
            "mischievous": {"openness": 0.7, "agreeableness": 0.4}
        }
        
        # Apply trait mappings
        for trait in self.simple_traits:
            trait_lower = trait.lower()
            if trait_lower in trait_mappings:
                for complex_trait, value in trait_mappings[trait_lower].items():
                    if complex_trait in TRAIT_NAME_TO_INDEX:
                        idx = TRAIT_NAME_TO_INDEX[complex_trait]
                        vector[idx] = value
        
        return vector
    
    def get_dominant_traits(self, top_n: int = 5) -> List[tuple]:
        """Get the top N most dominant traits"""
        vector = self.get_trait_vector()
        trait_scores = [(TRAIT_INDEX_TO_NAME[i], score) for i, score in enumerate(vector)]
        trait_scores.sort(key=lambda x: x[1], reverse=True)
        return trait_scores[:top_n]
    
    def update_from_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """Update personality based on interaction (for personality development)"""
        if not self.evolution_enabled:
            return
            
        try:
            from .personality_evolution import PersonalityEvolutionEngine, EvolutionTrigger, EmotionalState
            
            evolution_engine = PersonalityEvolutionEngine()
            
            # Determine trigger type based on interaction data
            trigger = self._determine_evolution_trigger(interaction_data)
            
            # Extract emotional impact
            emotional_impact = interaction_data.get('emotional_impact', 0.0)
            
            # Create personality shifts
            shifts = evolution_engine.create_personality_shift(
                trigger=trigger,
                interaction_data=interaction_data,
                emotional_impact=emotional_impact,
                context=interaction_data.get('context', {})
            )
            
            # Add shifts to personality
            self.personality_shifts.extend(shifts)
            
            # Update current emotional state if provided
            if 'primary_emotion' in interaction_data:
                self.current_emotional_state = EmotionalState(
                    primary_emotion=interaction_data['primary_emotion'],
                    intensity=abs(emotional_impact),
                    valence=emotional_impact,
                    duration_hours=interaction_data.get('emotional_duration', 1.0)
                )
            
            # Clean up expired shifts
            self._cleanup_expired_shifts()
            
            # Process learning from interaction
            if self.learning_enabled:
                try:
                    from .learning_adaptation import AdaptationEngine
                    
                    adaptation_engine = AdaptationEngine()
                    new_learnings, updated_learnings = adaptation_engine.learn_from_interaction(
                        interaction_data=interaction_data,
                        interaction_outcome={'emotional_state': self.current_emotional_state.primary_emotion if self.current_emotional_state else 'neutral'},
                        existing_learnings=self.learned_patterns,
                        context=interaction_data.get('context', {})
                    )
                    
                    # Add new learnings
                    self.learned_patterns.extend(new_learnings)
                    
                    # Cleanup old learnings periodically
                    if len(self.learned_patterns) > 100:  # Cleanup threshold
                        self.learned_patterns = adaptation_engine.cleanup_learnings(self.learned_patterns)
                        
                except ImportError:
                    # Fallback if learning system is not available
                    pass
            
        except ImportError:
            # Fallback if evolution system is not available
            pass

    def get_personality_development_analysis(self) -> Optional[Dict[str, Any]]:
        """Get analysis of how personality has developed over time"""
        if not self.initial_trait_vector or not self.personality_shifts:
            return None
            
        try:
            from .personality_evolution import PersonalityEvolutionEngine
            
            evolution_engine = PersonalityEvolutionEngine()
            initial_vector = np.array(self.initial_trait_vector)
            current_vector = self.get_trait_vector(apply_evolution=True)
            
            return evolution_engine.analyze_personality_development(
                initial_vector=initial_vector,
                current_vector=current_vector,
                shift_history=self.personality_shifts
            )
            
        except ImportError:
            return None

    def reset_personality_evolution(self, keep_shifts: bool = False) -> None:
        """Reset personality evolution to baseline"""
        if not keep_shifts:
            self.personality_shifts = []
        self.current_emotional_state = None
        if self.initial_trait_vector and self.trait_vector:
            self.trait_vector = self.initial_trait_vector.copy()

    def _determine_evolution_trigger(self, interaction_data: Dict[str, Any]) -> "EvolutionTrigger":
        """Determine what type of evolution trigger this interaction represents"""
        from .personality_evolution import EvolutionTrigger
        
        emotional_impact = interaction_data.get('emotional_impact', 0.0)
        interaction_type = interaction_data.get('type', '')
        
        # Map interaction types and emotional impacts to triggers
        if interaction_type == 'achievement' or 'success' in interaction_data:
            return EvolutionTrigger.ACHIEVEMENT
        elif interaction_type == 'failure' or 'failed' in interaction_data:
            return EvolutionTrigger.FAILURE
        elif interaction_type == 'learning' or 'learned' in interaction_data:
            return EvolutionTrigger.LEARNING_EXPERIENCE
        elif interaction_type == 'social_bonding' or interaction_data.get('bonding_occurred', False):
            return EvolutionTrigger.SOCIAL_BONDING
        elif interaction_type == 'stress' or interaction_data.get('stress_level', 0) > 0.7:
            return EvolutionTrigger.STRESS_EVENT
        elif abs(emotional_impact) > 0.8:
            return EvolutionTrigger.EMOTIONAL_PEAK
        elif emotional_impact > 0.3:
            return EvolutionTrigger.POSITIVE_INTERACTION
        elif emotional_impact < -0.3:
            return EvolutionTrigger.NEGATIVE_INTERACTION
        else:
            return EvolutionTrigger.REPEATED_BEHAVIOR

    def _cleanup_expired_shifts(self) -> None:
        """Remove expired personality shifts"""
        self.personality_shifts = [shift for shift in self.personality_shifts if not shift.is_expired]

    def get_learning_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of learned patterns and adaptations"""
        if not self.learning_enabled or not self.learned_patterns:
            return None
            
        try:
            from .learning_adaptation import AdaptationEngine
            
            adaptation_engine = AdaptationEngine()
            return adaptation_engine.get_learning_summary(self.learned_patterns)
            
        except ImportError:
            return None

    def apply_learned_preferences(self, 
                                 context: Dict[str, Any], 
                                 available_actions: List[str],
                                 base_preferences: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Apply learned behavioral preferences to action selection"""
        if not self.learning_enabled or not self.learned_patterns:
            return base_preferences or {action: 0.5 for action in available_actions}
            
        try:
            from .learning_adaptation import AdaptationEngine
            
            adaptation_engine = AdaptationEngine()
            return adaptation_engine.apply_learnings_to_decision(
                current_context=context,
                available_actions=available_actions,
                learnings=self.learned_patterns,
                base_preferences=base_preferences
            )
            
        except ImportError:
            return base_preferences or {action: 0.5 for action in available_actions}

    def reset_learning(self, keep_strong_learnings: bool = True) -> None:
        """Reset learned patterns"""
        if keep_strong_learnings and self.learned_patterns:
            # Keep only very strong learnings (confidence > 0.8)
            self.learned_patterns = [
                learning for learning in self.learned_patterns 
                if learning.confidence_score > 0.8
            ]
        else:
            self.learned_patterns = []