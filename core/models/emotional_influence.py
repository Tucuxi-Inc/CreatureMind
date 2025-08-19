"""
Emotional State Influence on Personality Traits

Implements real-time emotional influences on personality traits, allowing creatures
to temporarily exhibit different personality characteristics based on their current
emotional state. This creates more dynamic and realistic personality expression.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum


class EmotionalInfluence(BaseModel):
    """Represents how an emotional state influences personality traits"""
    emotion: str
    trait_influences: Dict[str, float]  # trait_name -> influence_strength (-1.0 to 1.0)
    intensity_multiplier: float = 1.0  # How much emotion intensity affects the influence
    duration_decay: float = 0.9  # How quickly influence fades over time


class EmotionalPersonalityModifier:
    """
    Manages real-time emotional influences on personality traits
    
    This system allows creatures to temporarily exhibit different personality
    characteristics based on their current emotional state, while their core
    personality remains stable.
    """
    
    def __init__(self):
        # Emotional influence mappings based on psychological research
        self.emotional_influences = self._build_emotional_influence_map()
        
        # Settings for emotional influence dynamics
        self.max_influence_strength = 0.3  # Maximum trait modification from emotions
        self.influence_decay_rate = 0.95  # How quickly emotional influences fade
        self.emotion_threshold = 0.1  # Minimum emotion intensity to trigger influence
        
    def apply_emotional_influence(self,
                                 base_trait_vector: np.ndarray,
                                 emotional_state: Dict[str, Any],
                                 previous_influences: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        Apply current emotional state influences to personality traits
        
        Args:
            base_trait_vector: Base 50-dimensional personality vector
            emotional_state: Current emotional state information
            previous_influences: Previously applied influences (for decay)
            
        Returns:
            Modified trait vector with emotional influences applied
        """
        from ..models.personality_system import TRAIT_NAME_TO_INDEX
        
        modified_vector = base_trait_vector.copy()
        
        # Extract emotional state information
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        intensity = emotional_state.get('intensity', 0.0)
        valence = emotional_state.get('valence', 0.0)
        duration_hours = emotional_state.get('duration_hours', 0.0)
        
        # Skip if emotion is too weak to influence personality
        if intensity < self.emotion_threshold:
            return modified_vector
        
        # Get influence mapping for this emotion
        influence_map = self.emotional_influences.get(primary_emotion, {})
        
        # Apply emotional influences
        for trait_name, base_influence in influence_map.items():
            trait_index = TRAIT_NAME_TO_INDEX.get(trait_name)
            if trait_index is not None:
                # Calculate total influence strength
                influence_strength = base_influence * intensity * self.max_influence_strength
                
                # Apply valence modifier (positive emotions enhance positive traits)
                if valence != 0:
                    influence_strength *= (1.0 + valence * 0.5)
                
                # Apply duration modifier (sustained emotions have stronger influence)
                duration_modifier = min(1.0 + (duration_hours / 24.0) * 0.5, 2.0)
                influence_strength *= duration_modifier
                
                # Apply the influence
                modified_vector[trait_index] += influence_strength
        
        # Apply secondary emotional influences (emotional combinations)
        secondary_emotions = emotional_state.get('secondary_emotions', [])
        for emotion in secondary_emotions:
            secondary_influence_map = self.emotional_influences.get(emotion, {})
            for trait_name, base_influence in secondary_influence_map.items():
                trait_index = TRAIT_NAME_TO_INDEX.get(trait_name)
                if trait_index is not None:
                    # Secondary emotions have reduced influence
                    influence_strength = base_influence * intensity * self.max_influence_strength * 0.5
                    modified_vector[trait_index] += influence_strength
        
        # Apply decay to previous influences if provided
        if previous_influences:
            self._apply_influence_decay(modified_vector, previous_influences)
        
        # Ensure traits stay within bounds
        modified_vector = np.clip(modified_vector, 0.0, 1.0)
        
        return modified_vector

    def get_emotional_personality_summary(self,
                                         base_traits: Dict[str, float],
                                         modified_traits: Dict[str, float],
                                         emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of how emotions are affecting personality
        
        Returns analysis of emotional influences on personality expression
        """
        trait_changes = {}
        significant_changes = []
        
        for trait_name in base_traits:
            if trait_name in modified_traits:
                change = modified_traits[trait_name] - base_traits[trait_name]
                if abs(change) > 0.05:  # Threshold for significant change
                    trait_changes[trait_name] = change
                    change_type = "increased" if change > 0 else "decreased"
                    significant_changes.append(f"{trait_name} {change_type} by {abs(change):.2f}")
        
        # Determine overall emotional influence pattern
        influence_pattern = self._analyze_influence_pattern(trait_changes, emotional_state)
        
        return {
            "primary_emotion": emotional_state.get('primary_emotion', 'neutral'),
            "emotion_intensity": emotional_state.get('intensity', 0.0),
            "trait_changes": trait_changes,
            "significant_changes": significant_changes,
            "influence_pattern": influence_pattern,
            "temporary_personality_shift": len(significant_changes) > 0,
            "emotional_dominance": self._calculate_emotional_dominance(trait_changes)
        }

    def predict_emotional_behavior(self,
                                  emotional_state: Dict[str, Any],
                                  base_personality: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict how emotional state will affect behavior patterns
        
        Returns behavioral predictions based on emotional influences
        """
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        intensity = emotional_state.get('intensity', 0.0)
        
        # Behavioral prediction mappings
        behavior_predictions = {
            'happy': {
                'social_tendency': 'increased',
                'risk_taking': 'slightly_increased',
                'cooperation': 'increased',
                'energy_level': 'high',
                'decision_making': 'optimistic_bias'
            },
            'sad': {
                'social_tendency': 'decreased',
                'risk_taking': 'decreased',
                'cooperation': 'neutral_to_decreased',
                'energy_level': 'low',
                'decision_making': 'pessimistic_bias'
            },
            'angry': {
                'social_tendency': 'confrontational',
                'risk_taking': 'increased',
                'cooperation': 'decreased',
                'energy_level': 'high',
                'decision_making': 'aggressive_bias'
            },
            'anxious': {
                'social_tendency': 'avoidant',
                'risk_taking': 'strongly_decreased',
                'cooperation': 'cautious',
                'energy_level': 'medium_to_high',
                'decision_making': 'overly_cautious'
            },
            'excited': {
                'social_tendency': 'very_increased',
                'risk_taking': 'increased',
                'cooperation': 'enthusiastic',
                'energy_level': 'very_high',
                'decision_making': 'impulsive_tendency'
            },
            'calm': {
                'social_tendency': 'balanced',
                'risk_taking': 'measured',
                'cooperation': 'steady',
                'energy_level': 'stable',
                'decision_making': 'rational'
            }
        }
        
        base_prediction = behavior_predictions.get(primary_emotion, behavior_predictions['calm'])
        
        # Modify predictions based on intensity
        intensity_modifier = {
            'low': 0.3,
            'medium': 0.7,
            'high': 1.0,
            'very_high': 1.3
        }
        
        intensity_level = 'low' if intensity < 0.3 else ('medium' if intensity < 0.7 else 'high')
        modifier = intensity_modifier[intensity_level]
        
        # Apply base personality influences
        prediction = base_prediction.copy()
        prediction['intensity_modifier'] = modifier
        prediction['personality_context'] = self._apply_personality_context(base_prediction, base_personality)
        
        return prediction

    def _build_emotional_influence_map(self) -> Dict[str, Dict[str, float]]:
        """Build mapping of emotions to trait influences"""
        return {
            'happy': {
                'extraversion': 0.4,
                'optimism': 0.6,
                'sociability': 0.5,
                'enthusiasm': 0.7,
                'confidence': 0.3,
                'agreeableness': 0.4,
                'emotional_expressiveness': 0.5,
                'neuroticism': -0.3
            },
            'sad': {
                'extraversion': -0.5,
                'optimism': -0.7,
                'sociability': -0.4,
                'enthusiasm': -0.6,
                'confidence': -0.4,
                'neuroticism': 0.4,
                'empathy': 0.3,
                'reflectiveness': 0.4
            },
            'angry': {
                'agreeableness': -0.6,
                'assertiveness': 0.7,
                'neuroticism': 0.5,
                'emotional_expressiveness': 0.6,
                'patience': -0.8,
                'tolerance': -0.5,
                'risk_taking': 0.4,
                'competitiveness': 0.5
            },
            'anxious': {
                'neuroticism': 0.8,
                'caution': 0.7,
                'confidence': -0.5,
                'risk_taking': -0.6,
                'emotional_stability': -0.6,
                'independence': -0.3,
                'trust': -0.4,
                'social_anxiety': 0.6
            },
            'excited': {
                'enthusiasm': 0.8,
                'extraversion': 0.6,
                'energy': 0.7,
                'optimism': 0.5,
                'risk_taking': 0.4,
                'sociability': 0.6,
                'spontaneity': 0.7,
                'patience': -0.4
            },
            'calm': {
                'emotional_stability': 0.6,
                'patience': 0.5,
                'neuroticism': -0.5,
                'reflectiveness': 0.4,
                'focus': 0.3,
                'self_control': 0.4,
                'mindfulness': 0.6
            },
            'fearful': {
                'caution': 0.8,
                'neuroticism': 0.6,
                'risk_taking': -0.7,
                'confidence': -0.5,
                'independence': -0.4,
                'trust': -0.3,
                'boldness': -0.6
            },
            'curious': {
                'curiosity': 0.7,
                'openness': 0.6,
                'innovativeness': 0.5,
                'intellectual_curiosity': 0.8,
                'exploration': 0.6,
                'focus': 0.4
            },
            'content': {
                'emotional_stability': 0.5,
                'optimism': 0.4,
                'patience': 0.4,
                'agreeableness': 0.3,
                'neuroticism': -0.4,
                'satisfaction': 0.6
            },
            'frustrated': {
                'patience': -0.7,
                'neuroticism': 0.5,
                'agreeableness': -0.4,
                'emotional_stability': -0.5,
                'perseverance': -0.3,
                'assertiveness': 0.4
            },
            'lonely': {
                'sociability': -0.5,
                'extraversion': -0.4,
                'neuroticism': 0.4,
                'empathy': 0.3,
                'independence': -0.6,
                'emotional_expressiveness': -0.3
            },
            'proud': {
                'confidence': 0.6,
                'self_efficacy': 0.5,
                'humility': -0.4,
                'assertiveness': 0.4,
                'optimism': 0.4,
                'ambition': 0.3
            }
        }

    def _apply_influence_decay(self, trait_vector: np.ndarray, previous_influences: Dict[str, float]):
        """Apply decay to previous emotional influences"""
        from ..models.personality_system import TRAIT_NAME_TO_INDEX
        
        for trait_name, previous_influence in previous_influences.items():
            trait_index = TRAIT_NAME_TO_INDEX.get(trait_name)
            if trait_index is not None:
                # Apply decay to previous influence
                decayed_influence = previous_influence * self.influence_decay_rate
                trait_vector[trait_index] += decayed_influence

    def _analyze_influence_pattern(self, trait_changes: Dict[str, float], emotional_state: Dict[str, Any]) -> str:
        """Analyze the overall pattern of emotional influence"""
        if not trait_changes:
            return "stable"
        
        increases = sum(1 for change in trait_changes.values() if change > 0)
        decreases = sum(1 for change in trait_changes.values() if change < 0)
        
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        intensity = emotional_state.get('intensity', 0.0)
        
        if intensity > 0.8:
            return f"strong_{primary_emotion}_influence"
        elif increases > decreases * 2:
            return f"enhancing_{primary_emotion}_pattern"
        elif decreases > increases * 2:
            return f"suppressing_{primary_emotion}_pattern"
        else:
            return f"mixed_{primary_emotion}_influence"

    def _calculate_emotional_dominance(self, trait_changes: Dict[str, float]) -> float:
        """Calculate how much emotions are dominating personality expression"""
        if not trait_changes:
            return 0.0
        
        total_change = sum(abs(change) for change in trait_changes.values())
        return min(total_change / len(trait_changes), 1.0)

    def _apply_personality_context(self, base_prediction: Dict[str, str], base_personality: Dict[str, float]) -> Dict[str, Any]:
        """Apply base personality context to behavioral predictions"""
        context = {}
        
        # Check if base personality reinforces or conflicts with emotional tendencies
        if 'extraversion' in base_personality:
            if base_personality['extraversion'] > 0.7:
                context['extraversion_note'] = "naturally_outgoing_personality_amplifies_social_emotions"
            elif base_personality['extraversion'] < 0.3:
                context['extraversion_note'] = "introverted_personality_may_resist_social_emotional_impulses"
        
        if 'neuroticism' in base_personality:
            if base_personality['neuroticism'] > 0.7:
                context['stability_note'] = "naturally_sensitive_personality_amplifies_negative_emotions"
            elif base_personality['neuroticism'] < 0.3:
                context['stability_note'] = "emotionally_stable_personality_dampens_emotional_extremes"
        
        return context