"""
Personality Evolution System for CreatureMind

Implements dynamic personality changes based on interactions, emotional experiences,
and environmental influences over time. Personalities can gradually shift based on
the creature's experiences, creating more realistic character development.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import json


class EvolutionTrigger(str, Enum):
    """Types of events that can trigger personality evolution"""
    POSITIVE_INTERACTION = "positive_interaction"
    NEGATIVE_INTERACTION = "negative_interaction"
    REPEATED_BEHAVIOR = "repeated_behavior"
    EMOTIONAL_PEAK = "emotional_peak"
    LEARNING_EXPERIENCE = "learning_experience"
    SOCIAL_BONDING = "social_bonding"
    STRESS_EVENT = "stress_event"
    ACHIEVEMENT = "achievement"
    FAILURE = "failure"
    TIME_PASSAGE = "time_passage"


class PersonalityShift(BaseModel):
    """Represents a gradual shift in personality traits"""
    trait_name: str
    shift_direction: float  # -1.0 to 1.0 (negative = decrease, positive = increase)
    shift_magnitude: float  # 0.0 to 1.0 (how much the trait can change)
    trigger: EvolutionTrigger
    timestamp: datetime = Field(default_factory=datetime.now)
    influence_decay_hours: float = 168.0  # How long this influence lasts (default 1 week)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if this shift influence has expired"""
        expiry_time = self.timestamp + timedelta(hours=self.influence_decay_hours)
        return datetime.now() > expiry_time

    def get_current_influence(self) -> float:
        """Get the current influence strength (decays over time)"""
        if self.is_expired:
            return 0.0
        
        hours_passed = (datetime.now() - self.timestamp).total_seconds() / 3600
        decay_factor = 1.0 - (hours_passed / self.influence_decay_hours)
        return self.shift_magnitude * decay_factor


class EmotionalState(BaseModel):
    """Current emotional state affecting personality"""
    primary_emotion: str
    intensity: float  # 0.0 to 1.0
    valence: float  # -1.0 to 1.0 (negative to positive)
    duration_hours: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)


class PersonalityEvolutionEngine:
    """
    Manages personality evolution based on experiences and interactions
    """
    
    def __init__(self):
        # Evolution sensitivity settings
        self.base_evolution_rate = 0.001  # How quickly traits can change
        self.max_trait_change_per_event = 0.02  # Maximum change from single event
        self.emotional_influence_multiplier = 2.0  # How much emotions amplify changes
        self.relationship_influence_multiplier = 1.5  # How much relationships affect evolution
        
        # Trait interaction matrices (how traits influence each other)
        self.trait_correlations = self._build_trait_correlation_matrix()
        
        # Experience-based evolution rules
        self.evolution_rules = self._build_evolution_rules()

    def evolve_personality(self, 
                          current_trait_vector: np.ndarray,
                          recent_shifts: List[PersonalityShift],
                          emotional_state: Optional[EmotionalState] = None,
                          interaction_context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply personality evolution based on recent experiences
        
        Args:
            current_trait_vector: Current 50-dimensional personality vector
            recent_shifts: List of recent personality shifts to apply
            emotional_state: Current emotional state
            interaction_context: Context about recent interactions
            
        Returns:
            Updated personality vector
        """
        evolved_vector = current_trait_vector.copy()
        
        # Apply active personality shifts
        for shift in recent_shifts:
            if not shift.is_expired:
                influence = shift.get_current_influence()
                trait_index = self._get_trait_index(shift.trait_name)
                
                if trait_index is not None:
                    # Apply direct trait change
                    change = shift.shift_direction * influence * self.base_evolution_rate
                    
                    # Amplify change based on emotional state
                    if emotional_state:
                        emotion_multiplier = self._get_emotional_multiplier(shift.trigger, emotional_state)
                        change *= emotion_multiplier
                    
                    # Apply the change
                    evolved_vector[trait_index] += change
                    
                    # Apply correlated trait changes
                    self._apply_trait_correlations(evolved_vector, trait_index, change * 0.3)
        
        # Apply gradual emotional state influences
        if emotional_state:
            evolved_vector = self._apply_emotional_influence(evolved_vector, emotional_state)
        
        # Apply relationship-based influences
        if interaction_context:
            evolved_vector = self._apply_relationship_influence(evolved_vector, interaction_context)
        
        # Ensure traits stay within bounds [0, 1]
        evolved_vector = np.clip(evolved_vector, 0.0, 1.0)
        
        return evolved_vector

    def create_personality_shift(self,
                                trigger: EvolutionTrigger,
                                interaction_data: Dict[str, Any],
                                emotional_impact: float = 0.0,
                                context: Optional[Dict[str, Any]] = None) -> List[PersonalityShift]:
        """
        Create personality shifts based on an interaction or event
        
        Args:
            trigger: Type of event triggering the shift
            interaction_data: Data about the interaction/event
            emotional_impact: Emotional impact score (-1.0 to 1.0)
            context: Additional context about the situation
            
        Returns:
            List of personality shifts to apply
        """
        shifts = []
        
        # Get evolution rules for this trigger
        rules = self.evolution_rules.get(trigger, [])
        
        for rule in rules:
            # Check if rule conditions are met
            if self._evaluate_rule_conditions(rule, interaction_data, emotional_impact, context):
                
                # Calculate shift magnitude based on impact and rule strength
                magnitude = abs(emotional_impact) * rule.get('base_magnitude', 0.01)
                magnitude = min(magnitude, self.max_trait_change_per_event)
                
                # Determine shift direction
                direction = 1.0 if emotional_impact > 0 else -1.0
                if rule.get('invert_direction', False):
                    direction *= -1.0
                
                # Create the shift
                shift = PersonalityShift(
                    trait_name=rule['trait'],
                    shift_direction=direction,
                    shift_magnitude=magnitude,
                    trigger=trigger,
                    influence_decay_hours=rule.get('decay_hours', 168.0),
                    metadata={
                        'interaction_data': interaction_data,
                        'emotional_impact': emotional_impact,
                        'context': context or {}
                    }
                )
                
                shifts.append(shift)
        
        return shifts

    def analyze_personality_development(self,
                                      initial_vector: np.ndarray,
                                      current_vector: np.ndarray,
                                      shift_history: List[PersonalityShift]) -> Dict[str, Any]:
        """
        Analyze how personality has developed over time
        
        Returns detailed analysis of personality changes
        """
        from ..models.personality_system import TRAIT_INDEX_TO_NAME
        
        # Calculate overall change
        total_change = np.linalg.norm(current_vector - initial_vector)
        
        # Find traits with significant changes
        trait_changes = []
        for i, (initial, current) in enumerate(zip(initial_vector, current_vector)):
            change = current - initial
            if abs(change) > 0.05:  # Threshold for significant change
                trait_changes.append({
                    'trait': TRAIT_INDEX_TO_NAME.get(i, f'trait_{i}'),
                    'initial_value': float(initial),
                    'current_value': float(current),
                    'change': float(change),
                    'change_percentage': float(change / max(initial, 0.01) * 100)
                })
        
        # Analyze shift patterns
        trigger_counts = {}
        for shift in shift_history:
            trigger_counts[shift.trigger.value] = trigger_counts.get(shift.trigger.value, 0) + 1
        
        # Calculate development trends
        most_influenced_traits = sorted(trait_changes, key=lambda x: abs(x['change']), reverse=True)[:5]
        most_common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_personality_change': float(total_change),
            'significant_trait_changes': len(trait_changes),
            'most_influenced_traits': most_influenced_traits,
            'most_common_evolution_triggers': most_common_triggers,
            'development_summary': self._generate_development_summary(trait_changes, trigger_counts),
            'personality_stability': self._calculate_stability_score(shift_history),
            'evolution_trajectory': self._analyze_evolution_trajectory(shift_history)
        }

    def _build_trait_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build matrix of how traits influence each other"""
        # Simplified correlation matrix - in practice this would be based on psychological research
        return {
            'extraversion': {'sociability': 0.7, 'confidence': 0.5, 'enthusiasm': 0.6},
            'conscientiousness': {'focus': 0.6, 'self_control': 0.7, 'perseverance': 0.8},
            'openness': {'creativity': 0.8, 'curiosity': 0.9, 'innovativeness': 0.7},
            'agreeableness': {'empathy': 0.8, 'altruism': 0.7, 'collaboration': 0.6},
            'neuroticism': {'emotional_stability': -0.9, 'resilience': -0.6, 'confidence': -0.4},
            'empathy': {'emotional_expressiveness': 0.6, 'nurturing': 0.7},
            'confidence': {'assertiveness': 0.7, 'decisiveness': 0.5},
            'creativity': {'innovativeness': 0.8, 'open_mindedness': 0.6}
        }

    def _build_evolution_rules(self) -> Dict[EvolutionTrigger, List[Dict[str, Any]]]:
        """Build rules for how different events affect personality traits"""
        return {
            EvolutionTrigger.POSITIVE_INTERACTION: [
                {'trait': 'extraversion', 'base_magnitude': 0.008, 'conditions': ['social_interaction']},
                {'trait': 'agreeableness', 'base_magnitude': 0.006, 'conditions': ['positive_feedback']},
                {'trait': 'confidence', 'base_magnitude': 0.005, 'conditions': ['successful_interaction']},
                {'trait': 'sociability', 'base_magnitude': 0.010, 'conditions': ['social_interaction']},
                {'trait': 'trust', 'base_magnitude': 0.004, 'conditions': ['trust_building']}
            ],
            
            EvolutionTrigger.NEGATIVE_INTERACTION: [
                {'trait': 'caution', 'base_magnitude': 0.008, 'conditions': ['threatening_situation']},
                {'trait': 'trust', 'base_magnitude': 0.006, 'invert_direction': True, 'conditions': ['betrayal_or_harm']},
                {'trait': 'neuroticism', 'base_magnitude': 0.005, 'conditions': ['stress_response']},
                {'trait': 'independence', 'base_magnitude': 0.007, 'conditions': ['rejection_or_isolation']},
                {'trait': 'emotional_stability', 'base_magnitude': 0.004, 'invert_direction': True, 'conditions': ['emotional_distress']}
            ],
            
            EvolutionTrigger.LEARNING_EXPERIENCE: [
                {'trait': 'curiosity', 'base_magnitude': 0.010, 'conditions': ['new_knowledge_gained']},
                {'trait': 'openness', 'base_magnitude': 0.008, 'conditions': ['novel_experience']},
                {'trait': 'intelligence', 'base_magnitude': 0.003, 'conditions': ['problem_solved']},
                {'trait': 'confidence', 'base_magnitude': 0.005, 'conditions': ['skill_mastery']},
                {'trait': 'perseverance', 'base_magnitude': 0.006, 'conditions': ['overcame_difficulty']}
            ],
            
            EvolutionTrigger.SOCIAL_BONDING: [
                {'trait': 'empathy', 'base_magnitude': 0.012, 'conditions': ['emotional_connection']},
                {'trait': 'agreeableness', 'base_magnitude': 0.008, 'conditions': ['cooperative_activity']},
                {'trait': 'loyalty', 'base_magnitude': 0.010, 'conditions': ['trust_developed']},
                {'trait': 'emotional_expressiveness', 'base_magnitude': 0.007, 'conditions': ['emotional_sharing']},
                {'trait': 'altruism', 'base_magnitude': 0.006, 'conditions': ['mutual_support']}
            ],
            
            EvolutionTrigger.ACHIEVEMENT: [
                {'trait': 'confidence', 'base_magnitude': 0.015, 'conditions': ['goal_accomplished']},
                {'trait': 'ambition', 'base_magnitude': 0.008, 'conditions': ['success_experienced']},
                {'trait': 'self_efficacy', 'base_magnitude': 0.012, 'conditions': ['capability_demonstrated']},
                {'trait': 'optimism', 'base_magnitude': 0.006, 'conditions': ['positive_outcome']},
                {'trait': 'perseverance', 'base_magnitude': 0.005, 'conditions': ['effort_rewarded']}
            ],
            
            EvolutionTrigger.FAILURE: [
                {'trait': 'resilience', 'base_magnitude': 0.008, 'conditions': ['recovered_from_setback']},
                {'trait': 'humility', 'base_magnitude': 0.006, 'conditions': ['recognized_limitations']},
                {'trait': 'caution', 'base_magnitude': 0.007, 'conditions': ['learned_from_mistake']},
                {'trait': 'neuroticism', 'base_magnitude': 0.004, 'conditions': ['emotional_impact']},
                {'trait': 'confidence', 'base_magnitude': 0.003, 'invert_direction': True, 'conditions': ['confidence_shaken']}
            ],
            
            EvolutionTrigger.STRESS_EVENT: [
                {'trait': 'neuroticism', 'base_magnitude': 0.010, 'conditions': ['high_stress']},
                {'trait': 'emotional_stability', 'base_magnitude': 0.008, 'invert_direction': True, 'conditions': ['emotional_overwhelm']},
                {'trait': 'resilience', 'base_magnitude': 0.006, 'conditions': ['coping_attempt']},
                {'trait': 'independence', 'base_magnitude': 0.005, 'conditions': ['self_reliance_needed']},
                {'trait': 'caution', 'base_magnitude': 0.007, 'conditions': ['threat_awareness']}
            ],
            
            EvolutionTrigger.TIME_PASSAGE: [
                {'trait': 'wisdom', 'base_magnitude': 0.001, 'conditions': ['experience_accumulation'], 'decay_hours': 720.0},
                {'trait': 'emotional_stability', 'base_magnitude': 0.002, 'conditions': ['maturation'], 'decay_hours': 720.0},
                {'trait': 'patience', 'base_magnitude': 0.001, 'conditions': ['age_related_growth'], 'decay_hours': 720.0}
            ]
        }

    def _get_trait_index(self, trait_name: str) -> Optional[int]:
        """Get the index of a trait in the personality vector"""
        from ..models.personality_system import TRAIT_NAME_TO_INDEX
        return TRAIT_NAME_TO_INDEX.get(trait_name)

    def _get_emotional_multiplier(self, trigger: EvolutionTrigger, emotional_state: EmotionalState) -> float:
        """Calculate how much emotional state amplifies personality changes"""
        base_multiplier = 1.0 + (emotional_state.intensity * self.emotional_influence_multiplier - 1.0)
        
        # Certain triggers are more influenced by emotions
        high_emotion_triggers = [
            EvolutionTrigger.EMOTIONAL_PEAK,
            EvolutionTrigger.STRESS_EVENT,
            EvolutionTrigger.SOCIAL_BONDING,
            EvolutionTrigger.ACHIEVEMENT,
            EvolutionTrigger.FAILURE
        ]
        
        if trigger in high_emotion_triggers:
            base_multiplier *= 1.5
        
        return base_multiplier

    def _apply_trait_correlations(self, trait_vector: np.ndarray, changed_trait_index: int, change_amount: float):
        """Apply correlated changes to related traits"""
        from ..models.personality_system import TRAIT_INDEX_TO_NAME, TRAIT_NAME_TO_INDEX
        
        trait_name = TRAIT_INDEX_TO_NAME.get(changed_trait_index)
        if not trait_name or trait_name not in self.trait_correlations:
            return
        
        correlations = self.trait_correlations[trait_name]
        for related_trait, correlation in correlations.items():
            related_index = TRAIT_NAME_TO_INDEX.get(related_trait)
            if related_index is not None:
                correlated_change = change_amount * correlation
                trait_vector[related_index] += correlated_change

    def _apply_emotional_influence(self, trait_vector: np.ndarray, emotional_state: EmotionalState) -> np.ndarray:
        """Apply gradual influence of sustained emotional states"""
        # This would apply small, temporary changes based on current emotional state
        # For example, sustained happiness might slightly increase extraversion
        influence_map = {
            'happy': {'extraversion': 0.001, 'optimism': 0.001, 'sociability': 0.0008},
            'sad': {'neuroticism': 0.0008, 'emotional_stability': -0.0006},
            'angry': {'assertiveness': 0.001, 'neuroticism': 0.0008, 'agreeableness': -0.0006},
            'excited': {'enthusiasm': 0.001, 'energy': 0.0008, 'extraversion': 0.0006},
            'calm': {'emotional_stability': 0.0008, 'patience': 0.0006, 'neuroticism': -0.0004},
            'anxious': {'neuroticism': 0.001, 'caution': 0.0008, 'confidence': -0.0006}
        }
        
        influences = influence_map.get(emotional_state.primary_emotion, {})
        
        for trait_name, influence in influences.items():
            trait_index = self._get_trait_index(trait_name)
            if trait_index is not None:
                # Scale influence by intensity and duration
                scaled_influence = influence * emotional_state.intensity * min(emotional_state.duration_hours / 24.0, 1.0)
                trait_vector[trait_index] += scaled_influence
        
        return trait_vector

    def _apply_relationship_influence(self, trait_vector: np.ndarray, interaction_context: Dict[str, Any]) -> np.ndarray:
        """Apply influences based on relationship quality and interactions"""
        relationship_quality = interaction_context.get('relationship_quality', 0.5)
        interaction_frequency = interaction_context.get('interaction_frequency', 0.5)
        
        # Strong positive relationships gradually increase prosocial traits
        if relationship_quality > 0.7:
            prosocial_influence = 0.0005 * interaction_frequency
            prosocial_traits = ['agreeableness', 'empathy', 'trust', 'sociability', 'collaboration']
            
            for trait_name in prosocial_traits:
                trait_index = self._get_trait_index(trait_name)
                if trait_index is not None:
                    trait_vector[trait_index] += prosocial_influence
        
        # Poor relationships might increase caution and independence
        elif relationship_quality < 0.3:
            defensive_influence = 0.0003 * interaction_frequency
            defensive_traits = ['caution', 'independence', 'neuroticism']
            
            for trait_name in defensive_traits:
                trait_index = self._get_trait_index(trait_name)
                if trait_index is not None:
                    trait_vector[trait_index] += defensive_influence
        
        return trait_vector

    def _evaluate_rule_conditions(self, rule: Dict[str, Any], interaction_data: Dict[str, Any], 
                                 emotional_impact: float, context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate if conditions for applying an evolution rule are met"""
        conditions = rule.get('conditions', [])
        
        # Simple condition evaluation - in practice this would be more sophisticated
        for condition in conditions:
            if condition in ['social_interaction', 'positive_feedback', 'successful_interaction']:
                if emotional_impact <= 0:
                    return False
            elif condition in ['threatening_situation', 'stress_response', 'emotional_distress']:
                if emotional_impact >= 0:
                    return False
            elif condition in ['new_knowledge_gained', 'novel_experience', 'problem_solved']:
                if not interaction_data.get('learning_occurred', False):
                    return False
        
        return True

    def _generate_development_summary(self, trait_changes: List[Dict], trigger_counts: Dict[str, int]) -> str:
        """Generate a human-readable summary of personality development"""
        if not trait_changes:
            return "Personality has remained stable with minimal changes."
        
        increased_traits = [t['trait'] for t in trait_changes if t['change'] > 0]
        decreased_traits = [t['trait'] for t in trait_changes if t['change'] < 0]
        
        summary_parts = []
        
        if increased_traits:
            summary_parts.append(f"Developed stronger {', '.join(increased_traits[:3])}")
        
        if decreased_traits:
            summary_parts.append(f"Became less {', '.join(decreased_traits[:3])}")
        
        top_trigger = max(trigger_counts.items(), key=lambda x: x[1])[0] if trigger_counts else "unknown"
        summary_parts.append(f"Most influenced by {top_trigger.replace('_', ' ')}")
        
        return ". ".join(summary_parts) + "."

    def _calculate_stability_score(self, shift_history: List[PersonalityShift]) -> float:
        """Calculate how stable the personality has been (0.0 = very unstable, 1.0 = very stable)"""
        if not shift_history:
            return 1.0
        
        recent_shifts = [s for s in shift_history if not s.is_expired]
        total_influence = sum(s.get_current_influence() for s in recent_shifts)
        
        # Normalize to 0-1 scale (lower influence = higher stability)
        stability = max(0.0, 1.0 - min(total_influence / 10.0, 1.0))
        return stability

    def _analyze_evolution_trajectory(self, shift_history: List[PersonalityShift]) -> Dict[str, Any]:
        """Analyze the trajectory of personality evolution over time"""
        if len(shift_history) < 2:
            return {'trajectory': 'insufficient_data', 'trend': 'stable'}
        
        # Group shifts by time periods
        recent_shifts = [s for s in shift_history if (datetime.now() - s.timestamp).days <= 7]
        older_shifts = [s for s in shift_history if (datetime.now() - s.timestamp).days > 7]
        
        recent_magnitude = sum(s.shift_magnitude for s in recent_shifts) / max(len(recent_shifts), 1)
        older_magnitude = sum(s.shift_magnitude for s in older_shifts) / max(len(older_shifts), 1)
        
        if recent_magnitude > older_magnitude * 1.2:
            trend = 'accelerating_change'
        elif recent_magnitude < older_magnitude * 0.8:
            trend = 'stabilizing'
        else:
            trend = 'steady_evolution'
        
        return {
            'trajectory': trend,
            'recent_change_rate': recent_magnitude,
            'historical_change_rate': older_magnitude,
            'evolution_consistency': self._calculate_evolution_consistency(shift_history)
        }

    def _calculate_evolution_consistency(self, shift_history: List[PersonalityShift]) -> float:
        """Calculate how consistent the evolution pattern has been"""
        if len(shift_history) < 3:
            return 1.0
        
        # Calculate variance in shift magnitudes and directions
        magnitudes = [s.shift_magnitude for s in shift_history]
        magnitude_variance = np.var(magnitudes)
        
        # Lower variance = higher consistency
        consistency = max(0.0, 1.0 - magnitude_variance * 10.0)
        return min(consistency, 1.0)