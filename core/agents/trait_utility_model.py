"""
Trait-Based Utility Model for Decision Making

Implements the utility computation system from "Trait-driven Decision Model for LLM-Wrapped Agent Conversations"
Maps 50-dimensional personality traits to action preferences.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import os


class ActionStyle(BaseModel):
    """Definition of an action style for creatures"""
    name: str
    description: str
    behavior_tags: List[str]
    energy_requirement: str  # "low", "medium", "high"
    social_preference: str   # "solitary", "neutral", "social"


class ContextVector:
    """
    Encodes the current situational context into a numerical vector
    for utility computation
    """
    
    # Context dimensions (25 total as per the document)
    CONTEXT_DIMENSIONS = {
        # Emotional context (0-4)
        "emotional_intensity": 0,
        "emotional_valence": 1,      # positive/negative
        "emotional_stability": 2,
        "user_mood": 3,
        "creature_mood": 4,
        
        # Social context (5-9)
        "user_intent_social": 5,     # greeting, bonding, etc.
        "user_intent_care": 6,       # feeding, grooming, etc.
        "user_intent_play": 7,       # games, activities, etc.
        "user_intent_command": 8,    # training, instructions, etc.
        "relationship_quality": 9,
        
        # Physical context (10-14)
        "energy_level": 10,
        "physical_needs": 11,        # hunger, thirst, etc.
        "comfort_level": 12,
        "safety_level": 13,
        "environment_familiarity": 14,
        
        # Cognitive context (15-19)
        "complexity_level": 15,      # how complex the situation is
        "novelty_level": 16,         # how new/unfamiliar
        "problem_solving_needed": 17,
        "learning_opportunity": 18,
        "creative_potential": 19,
        
        # Temporal context (20-24)
        "time_pressure": 20,
        "routine_vs_special": 21,
        "recent_activity_level": 22,
        "fatigue_level": 23,
        "anticipation_level": 24
    }
    
    @classmethod
    def from_agent_data(
        cls,
        perception_data: Dict[str, Any],
        emotion_data: Dict[str, Any], 
        memory_data: Dict[str, Any],
        creature_state: Any
    ) -> np.ndarray:
        """Convert agent data into a context vector"""
        context = np.zeros(25)
        
        # Emotional context
        emotion_map = {"happy": 0.8, "excited": 0.9, "sad": 0.2, "angry": 0.7, "calm": 0.3, "neutral": 0.5}
        primary_emotion = emotion_data.get('primary_emotion', 'neutral')
        context[cls.CONTEXT_DIMENSIONS["emotional_intensity"]] = emotion_map.get(primary_emotion, 0.5)
        context[cls.CONTEXT_DIMENSIONS["emotional_valence"]] = 0.8 if primary_emotion in ["happy", "excited", "calm"] else 0.3
        
        # Social context
        intent_map = {
            "greet": 0.8, "bonding": 0.9, "play": 0.9, "feed": 0.7, 
            "command": 0.4, "training": 0.5, "comfort": 0.8
        }
        user_intent = perception_data.get('user_intent', 'unknown')
        if user_intent in intent_map:
            context[cls.CONTEXT_DIMENSIONS["user_intent_social"]] = intent_map[user_intent] if user_intent in ["greet", "bonding"] else 0.3
            context[cls.CONTEXT_DIMENSIONS["user_intent_care"]] = intent_map[user_intent] if user_intent in ["feed", "comfort"] else 0.3
            context[cls.CONTEXT_DIMENSIONS["user_intent_play"]] = intent_map[user_intent] if user_intent == "play" else 0.3
            context[cls.CONTEXT_DIMENSIONS["user_intent_command"]] = intent_map[user_intent] if user_intent in ["command", "training"] else 0.3
        
        # Relationship quality
        relationship_map = {"strong": 0.9, "developing": 0.6, "new": 0.3, "strained": 0.1}
        relationship = memory_data.get('relationship', 'neutral')
        context[cls.CONTEXT_DIMENSIONS["relationship_quality"]] = relationship_map.get(relationship, 0.5)
        
        # Physical context
        if hasattr(creature_state, 'stats'):
            context[cls.CONTEXT_DIMENSIONS["energy_level"]] = creature_state.stats.get("energy", 50) / 100
            context[cls.CONTEXT_DIMENSIONS["physical_needs"]] = 1.0 - (creature_state.stats.get("hunger", 50) / 100)
            context[cls.CONTEXT_DIMENSIONS["comfort_level"]] = creature_state.stats.get("happiness", 50) / 100
        
        # Cognitive context
        complexity_map = {"simple": 0.2, "moderate": 0.5, "complex": 0.8}
        complexity = perception_data.get('complexity', 'moderate')
        context[cls.CONTEXT_DIMENSIONS["complexity_level"]] = complexity_map.get(complexity, 0.5)
        
        # Normalize the vector
        norm = np.linalg.norm(context)
        if norm > 0:
            context = context / norm
            
        return context


class TraitUtilityModel:
    """
    Computes utility scores for different action styles based on 
    creature personality traits and current context
    """
    
    # Action styles relevant to creatures
    ACTION_STYLES = {
        "playful": ActionStyle(
            name="playful",
            description="Energetic, fun-loving, and spontaneous behavior",
            behavior_tags=["bouncy", "enthusiastic", "spontaneous"],
            energy_requirement="high",
            social_preference="social"
        ),
        "cautious": ActionStyle(
            name="cautious", 
            description="Careful, observant, and measured responses",
            behavior_tags=["careful", "observant", "deliberate"],
            energy_requirement="low",
            social_preference="neutral"
        ),
        "assertive": ActionStyle(
            name="assertive",
            description="Confident, direct, and decisive behavior", 
            behavior_tags=["confident", "direct", "bold"],
            energy_requirement="medium",
            social_preference="neutral"
        ),
        "nurturing": ActionStyle(
            name="nurturing",
            description="Caring, gentle, and protective responses",
            behavior_tags=["gentle", "caring", "protective"],
            energy_requirement="low",
            social_preference="social"
        ),
        "curious": ActionStyle(
            name="curious",
            description="Inquisitive, exploratory, and investigative",
            behavior_tags=["investigating", "exploring", "questioning"],
            energy_requirement="medium", 
            social_preference="neutral"
        ),
        "defensive": ActionStyle(
            name="defensive",
            description="Protective, wary, and self-preserving",
            behavior_tags=["wary", "protective", "alert"],
            energy_requirement="medium",
            social_preference="solitary"
        ),
        "social": ActionStyle(
            name="social",
            description="Friendly, engaging, and connection-seeking",
            behavior_tags=["friendly", "engaging", "sociable"],
            energy_requirement="medium",
            social_preference="social"
        ),
        "independent": ActionStyle(
            name="independent", 
            description="Self-reliant, autonomous, and self-directed",
            behavior_tags=["autonomous", "self-directed", "aloof"],
            energy_requirement="low",
            social_preference="solitary"
        ),
        "analytical": ActionStyle(
            name="analytical",
            description="Thoughtful, systematic, and problem-solving",
            behavior_tags=["thoughtful", "systematic", "logical"],
            energy_requirement="medium",
            social_preference="neutral"
        ),
        "emotional": ActionStyle(
            name="emotional",
            description="Expressive, empathetic, and feeling-focused",
            behavior_tags=["expressive", "empathetic", "sensitive"],
            energy_requirement="low",
            social_preference="social"
        )
    }
    
    def __init__(self, trait_dim: int = 50, context_dim: int = 25):
        self.trait_dim = trait_dim
        self.context_dim = context_dim
        self.actions = list(self.ACTION_STYLES.keys())
        
        # Initialize weight matrices and biases
        # In a production system, these would be learned from data
        self.W = self._initialize_weight_matrices()
        self.b = {action: 0.0 for action in self.actions}
        
        # Temperature for action selection
        self.temperature = 0.3
    
    def _initialize_weight_matrices(self) -> Dict[str, np.ndarray]:
        """Initialize weight matrices with reasonable defaults based on trait-action relationships"""
        W = {}
        
        for action in self.actions:
            # Create a 50x25 weight matrix for each action
            # Initialize with small random values
            W[action] = np.random.randn(self.trait_dim, self.context_dim) * 0.1
            
            # Set some intuitive weights based on trait-action relationships
            # This is a simplified version - in practice you'd learn these weights
            self._set_intuitive_weights(W[action], action)
        
        return W
    
    def _set_intuitive_weights(self, weight_matrix: np.ndarray, action: str) -> None:
        """Set some intuitive weights for trait-action relationships"""
        # This is a simplified mapping - in practice you'd learn these from data
        
        trait_action_mappings = {
            "playful": {
                "extraversion": [0, 1, 2, 6, 7],  # contexts where extraversion helps playfulness
                "openness": [16, 18, 19],         # novelty and creativity contexts
                "curiosity": [15, 16, 17, 18]     # cognitive contexts
            },
            "cautious": {
                "neuroticism": [10, 11, 13],      # physical safety contexts
                "conscientiousness": [15, 20],    # complexity and time pressure
            },
            "nurturing": {
                "agreeableness": [5, 6, 9],       # social care contexts
                "empathy": [0, 1, 3, 4]           # emotional contexts
            }
            # Add more mappings as needed
        }
        
        if action in trait_action_mappings:
            for trait_name, context_indices in trait_action_mappings[action].items():
                # This is simplified - you'd want proper trait name to index mapping
                trait_idx = hash(trait_name) % self.trait_dim  # Placeholder
                for context_idx in context_indices:
                    if context_idx < self.context_dim:
                        weight_matrix[trait_idx, context_idx] += 0.3
    
    def compute_utilities(self, trait_vector: np.ndarray, context_vector: np.ndarray) -> Dict[str, float]:
        """Compute utility scores for each action style"""
        utilities = {}
        
        for action in self.actions:
            # U(a|P,x) = P^T * W_a * x + b_a
            utility = float(trait_vector.T @ self.W[action] @ context_vector + self.b[action])
            utilities[action] = utility
        
        return utilities
    
    def select_action_style(self, utilities: Dict[str, float], temperature: Optional[float] = None) -> str:
        """Select action style using softmax with temperature"""
        if temperature is None:
            temperature = self.temperature
        
        # Convert utilities to probabilities using softmax
        values = np.array(list(utilities.values()))
        
        # Handle edge case where all utilities are the same
        if np.all(values == values[0]):
            return np.random.choice(list(utilities.keys()))
        
        # Apply temperature scaling
        scaled_values = values / temperature
        
        # Softmax
        exp_values = np.exp(scaled_values - np.max(scaled_values))  # Subtract max for numerical stability
        probabilities = exp_values / np.sum(exp_values)
        
        # Sample from the distribution
        action = np.random.choice(list(utilities.keys()), p=probabilities)
        return action
    
    def get_action_guidance(self, action_style: str) -> Dict[str, Any]:
        """Get behavioral guidance for an action style"""
        if action_style not in self.ACTION_STYLES:
            return {
                "description": "Act naturally according to your species",
                "behavior_tags": ["natural"],
                "energy_level": "medium"
            }
        
        style = self.ACTION_STYLES[action_style]
        return {
            "description": style.description,
            "behavior_tags": style.behavior_tags,
            "energy_level": style.energy_requirement,
            "social_preference": style.social_preference
        }
    
    def save_weights(self, filepath: str) -> None:
        """Save the learned weight matrices"""
        data = {
            "W": {action: matrix.tolist() for action, matrix in self.W.items()},
            "b": self.b,
            "temperature": self.temperature
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load_weights(self, filepath: str) -> None:
        """Load weight matrices from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.W = {action: np.array(matrix) for action, matrix in data["W"].items()}
            self.b = data["b"]
            self.temperature = data.get("temperature", 0.3)