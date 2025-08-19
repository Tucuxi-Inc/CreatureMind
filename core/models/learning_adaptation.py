"""
Learning and Adaptation System for CreatureMind

Implements sophisticated learning mechanisms that allow creatures to adapt their
behavior patterns, preferences, and responses based on repeated interactions and
outcomes. This creates truly dynamic creatures that grow and change over time.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import json


class LearningType(str, Enum):
    """Types of learning that can occur"""
    BEHAVIORAL_PATTERN = "behavioral_pattern"      # Learning preferred behaviors
    USER_PREFERENCE = "user_preference"            # Learning user's likes/dislikes
    INTERACTION_OUTCOME = "interaction_outcome"    # Learning from interaction results
    EMOTIONAL_PATTERN = "emotional_pattern"        # Learning emotional associations
    CONTEXTUAL_RESPONSE = "contextual_response"    # Learning context-appropriate responses
    SKILL_DEVELOPMENT = "skill_development"        # Learning new capabilities
    SOCIAL_DYNAMICS = "social_dynamics"            # Learning relationship patterns


class LearningMemory(BaseModel):
    """Represents a learned pattern or association"""
    learning_type: LearningType
    pattern_id: str                               # Unique identifier for this learning
    description: str                              # Human-readable description
    trigger_conditions: Dict[str, Any]            # Conditions that activate this learning
    learned_response: Dict[str, Any]              # What was learned
    confidence_score: float = 0.5                # How confident we are in this learning (0-1)
    reinforcement_count: int = 1                  # How many times this has been reinforced
    last_reinforced: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    success_rate: float = 0.5                    # Success rate when applying this learning
    context_tags: List[str] = Field(default_factory=list)  # Tags for context matching
    
    def reinforce(self, success: bool = True, strength: float = 1.0):
        """Reinforce this learning with a new outcome"""
        self.reinforcement_count += 1
        self.last_reinforced = datetime.now()
        
        # Update confidence based on success
        if success:
            self.confidence_score = min(1.0, self.confidence_score + 0.1 * strength)
            self.success_rate = (self.success_rate * (self.reinforcement_count - 1) + 1.0) / self.reinforcement_count
        else:
            self.confidence_score = max(0.0, self.confidence_score - 0.05 * strength)
            self.success_rate = (self.success_rate * (self.reinforcement_count - 1) + 0.0) / self.reinforcement_count
    
    @property
    def is_stale(self) -> bool:
        """Check if this learning is becoming stale (not reinforced recently)"""
        days_since_reinforcement = (datetime.now() - self.last_reinforced).days
        return days_since_reinforcement > 30  # Consider stale after 30 days
    
    @property
    def strength(self) -> float:
        """Overall strength of this learning (combines confidence and reinforcement)"""
        base_strength = (self.confidence_score + min(self.reinforcement_count / 10.0, 1.0)) / 2.0
        
        # Reduce strength for stale learnings
        if self.is_stale:
            days_stale = (datetime.now() - self.last_reinforced).days
            decay_factor = max(0.1, 1.0 - (days_stale - 30) / 365.0)  # Decay over a year
            base_strength *= decay_factor
        
        return base_strength


class AdaptationEngine:
    """
    Manages learning and adaptation processes for creatures
    
    This system allows creatures to learn from their experiences and adapt
    their behavior patterns, emotional responses, and decision-making over time.
    """
    
    def __init__(self):
        # Learning configuration
        self.learning_rate = 0.1                    # How quickly new patterns are learned
        self.pattern_threshold = 0.7                # Confidence threshold for applying learnings
        self.max_learnings_per_type = 50           # Maximum learnings to keep per type
        self.adaptation_strength = 0.3              # How much learnings affect behavior
        
        # Learning pattern templates
        self.learning_templates = self._build_learning_templates()

    def learn_from_interaction(self,
                              interaction_data: Dict[str, Any],
                              interaction_outcome: Dict[str, Any],
                              existing_learnings: List[LearningMemory],
                              context: Optional[Dict[str, Any]] = None) -> Tuple[List[LearningMemory], List[LearningMemory]]:
        """
        Learn from an interaction and its outcome
        
        Args:
            interaction_data: Information about the interaction
            interaction_outcome: Results/outcome of the interaction
            existing_learnings: Previously learned patterns
            context: Additional context information
            
        Returns:
            Tuple of (new_learnings, updated_learnings)
        """
        new_learnings = []
        updated_learnings = []
        
        # Analyze interaction for learning opportunities
        learning_opportunities = self._identify_learning_opportunities(
            interaction_data, interaction_outcome, context
        )
        
        for opportunity in learning_opportunities:
            learning_type = opportunity['type']
            pattern_data = opportunity['pattern']
            success = opportunity.get('success', True)
            
            # Check if we already have a similar learning
            existing_learning = self._find_similar_learning(
                existing_learnings, learning_type, pattern_data
            )
            
            if existing_learning:
                # Reinforce existing learning
                existing_learning.reinforce(success=success, strength=opportunity.get('strength', 1.0))
                updated_learnings.append(existing_learning)
            else:
                # Create new learning
                new_learning = self._create_learning_memory(
                    learning_type, pattern_data, interaction_outcome, context
                )
                if new_learning:
                    new_learnings.append(new_learning)
        
        return new_learnings, updated_learnings

    def apply_learnings_to_decision(self,
                                   current_context: Dict[str, Any],
                                   available_actions: List[str],
                                   learnings: List[LearningMemory],
                                   base_preferences: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Apply learned patterns to influence decision making
        
        Args:
            current_context: Current situation context
            available_actions: Available actions/responses
            learnings: Relevant learned patterns
            base_preferences: Base preference scores for actions
            
        Returns:
            Modified preference scores incorporating learned patterns
        """
        if not learnings:
            return base_preferences or {action: 0.5 for action in available_actions}
        
        # Start with base preferences
        action_preferences = base_preferences.copy() if base_preferences else {action: 0.5 for action in available_actions}
        
        # Apply relevant learnings
        for learning in learnings:
            if learning.confidence_score < self.pattern_threshold:
                continue
            
            # Check if this learning is relevant to current context
            relevance_score = self._calculate_learning_relevance(learning, current_context)
            if relevance_score < 0.3:
                continue
            
            # Apply learning to action preferences
            learning_influence = self._extract_action_preferences(learning, available_actions)
            learning_strength = learning.strength * relevance_score * self.adaptation_strength
            
            for action, influence in learning_influence.items():
                if action in action_preferences:
                    current_pref = action_preferences[action]
                    modified_pref = current_pref + (influence * learning_strength)
                    action_preferences[action] = np.clip(modified_pref, 0.0, 1.0)
        
        return action_preferences

    def adapt_personality_from_learnings(self,
                                        base_trait_vector: np.ndarray,
                                        learnings: List[LearningMemory],
                                        adaptation_context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply long-term personality adaptations based on learned patterns
        
        This creates gradual personality shifts based on consistent behavioral learnings
        """
        adapted_vector = base_trait_vector.copy()
        
        # Group learnings by type for analysis
        learning_groups = {}
        for learning in learnings:
            if learning.learning_type not in learning_groups:
                learning_groups[learning.learning_type] = []
            learning_groups[learning.learning_type].append(learning)
        
        # Apply adaptations based on learning patterns
        for learning_type, type_learnings in learning_groups.items():
            trait_adaptations = self._analyze_trait_adaptations(learning_type, type_learnings)
            
            for trait_name, adaptation_strength in trait_adaptations.items():
                trait_index = self._get_trait_index(trait_name)
                if trait_index is not None:
                    # Apply gradual adaptation (very small changes over time)
                    adaptation_amount = adaptation_strength * 0.01  # Small adaptation rate
                    adapted_vector[trait_index] += adaptation_amount
        
        # Ensure traits stay within bounds
        adapted_vector = np.clip(adapted_vector, 0.0, 1.0)
        
        return adapted_vector

    def get_learning_summary(self, learnings: List[LearningMemory]) -> Dict[str, Any]:
        """Generate a summary of what the creature has learned"""
        if not learnings:
            return {"message": "No significant learnings yet", "total_learnings": 0}
        
        # Group by learning type
        learning_by_type = {}
        for learning in learnings:
            if learning.learning_type not in learning_by_type:
                learning_by_type[learning.learning_type] = []
            learning_by_type[learning.learning_type].append(learning)
        
        # Analyze learning patterns
        strongest_learnings = sorted(learnings, key=lambda l: l.strength, reverse=True)[:5]
        most_reinforced = sorted(learnings, key=lambda l: l.reinforcement_count, reverse=True)[:3]
        
        # Calculate learning statistics
        total_reinforcements = sum(l.reinforcement_count for l in learnings)
        average_confidence = sum(l.confidence_score for l in learnings) / len(learnings)
        
        # Identify learning trends
        recent_learnings = [l for l in learnings if (datetime.now() - l.created_at).days <= 7]
        learning_velocity = len(recent_learnings) / max(1, len(learnings))
        
        return {
            "total_learnings": len(learnings),
            "learning_by_type": {lt.value: len(ls) for lt, ls in learning_by_type.items()},
            "strongest_learnings": [
                {
                    "description": l.description,
                    "type": l.learning_type.value,
                    "strength": l.strength,
                    "confidence": l.confidence_score
                }
                for l in strongest_learnings
            ],
            "most_reinforced": [
                {
                    "description": l.description,
                    "reinforcements": l.reinforcement_count,
                    "success_rate": l.success_rate
                }
                for l in most_reinforced
            ],
            "learning_statistics": {
                "total_reinforcements": total_reinforcements,
                "average_confidence": average_confidence,
                "learning_velocity": learning_velocity,
                "stale_learnings": len([l for l in learnings if l.is_stale])
            },
            "learning_trends": self._analyze_learning_trends(learnings)
        }

    def cleanup_learnings(self, learnings: List[LearningMemory]) -> List[LearningMemory]:
        """Clean up old, weak, or redundant learnings"""
        cleaned_learnings = []
        
        # Group by type for cleanup
        by_type = {}
        for learning in learnings:
            if learning.learning_type not in by_type:
                by_type[learning.learning_type] = []
            by_type[learning.learning_type].append(learning)
        
        # Keep only the strongest learnings per type
        for learning_type, type_learnings in by_type.items():
            # Sort by strength and keep the strongest
            sorted_learnings = sorted(type_learnings, key=lambda l: l.strength, reverse=True)
            
            # Remove very weak learnings
            strong_learnings = [l for l in sorted_learnings if l.strength > 0.2]
            
            # Limit to max per type
            limited_learnings = strong_learnings[:self.max_learnings_per_type]
            
            cleaned_learnings.extend(limited_learnings)
        
        return cleaned_learnings

    def _identify_learning_opportunities(self,
                                       interaction_data: Dict[str, Any],
                                       outcome: Dict[str, Any],
                                       context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify what can be learned from this interaction"""
        opportunities = []
        
        # Analyze interaction success/failure patterns
        success_indicators = outcome.get('stats_delta', {})
        happiness_change = success_indicators.get('happiness', 0)
        overall_success = happiness_change > 0
        
        # User preference learning
        if 'user_intent' in interaction_data:
            opportunities.append({
                'type': LearningType.USER_PREFERENCE,
                'pattern': {
                    'user_intent': interaction_data['user_intent'],
                    'user_tone': interaction_data.get('user_tone', 'neutral'),
                    'outcome_success': overall_success,
                    'happiness_change': happiness_change
                },
                'success': overall_success,
                'strength': min(abs(happiness_change) / 20.0, 1.0)
            })
        
        # Behavioral pattern learning
        if 'action_style' in outcome.get('debug_info', {}):
            opportunities.append({
                'type': LearningType.BEHAVIORAL_PATTERN,
                'pattern': {
                    'context': interaction_data.get('context', {}),
                    'action_style': outcome['debug_info']['action_style'],
                    'outcome_success': overall_success,
                    'emotional_state': outcome.get('emotional_state', 'neutral')
                },
                'success': overall_success,
                'strength': 1.0
            })
        
        # Emotional pattern learning
        if 'primary_emotion' in interaction_data:
            opportunities.append({
                'type': LearningType.EMOTIONAL_PATTERN,
                'pattern': {
                    'trigger_emotion': interaction_data['primary_emotion'],
                    'context_type': interaction_data.get('type', 'unknown'),
                    'resulting_state': outcome.get('emotional_state', 'neutral'),
                    'satisfaction': overall_success
                },
                'success': overall_success,
                'strength': 0.8
            })
        
        # Contextual response learning
        if context and 'activity' in context:
            opportunities.append({
                'type': LearningType.CONTEXTUAL_RESPONSE,
                'pattern': {
                    'context_type': 'activity',
                    'specific_context': context['activity'],
                    'response_effectiveness': overall_success,
                    'emotional_result': outcome.get('emotional_state', 'neutral')
                },
                'success': overall_success,
                'strength': 0.9
            })
        
        return opportunities

    def _find_similar_learning(self,
                              existing_learnings: List[LearningMemory],
                              learning_type: LearningType,
                              pattern_data: Dict[str, Any]) -> Optional[LearningMemory]:
        """Find an existing learning that's similar to the new pattern"""
        for learning in existing_learnings:
            if learning.learning_type != learning_type:
                continue
            
            # Calculate similarity based on pattern overlap
            similarity = self._calculate_pattern_similarity(
                learning.trigger_conditions, pattern_data
            )
            
            if similarity > 0.7:  # High similarity threshold
                return learning
        
        return None

    def _create_learning_memory(self,
                               learning_type: LearningType,
                               pattern_data: Dict[str, Any],
                               outcome: Dict[str, Any],
                               context: Optional[Dict[str, Any]]) -> Optional[LearningMemory]:
        """Create a new learning memory from interaction data"""
        try:
            # Generate unique pattern ID
            pattern_id = f"{learning_type.value}_{hash(str(pattern_data))}"
            
            # Create description
            description = self._generate_learning_description(learning_type, pattern_data, outcome)
            
            # Extract learned response
            learned_response = self._extract_learned_response(pattern_data, outcome)
            
            # Determine initial confidence
            initial_confidence = self._calculate_initial_confidence(outcome)
            
            # Extract context tags
            context_tags = self._extract_context_tags(pattern_data, context)
            
            return LearningMemory(
                learning_type=learning_type,
                pattern_id=pattern_id,
                description=description,
                trigger_conditions=pattern_data,
                learned_response=learned_response,
                confidence_score=initial_confidence,
                context_tags=context_tags
            )
        except Exception as e:
            # Return None if learning creation fails
            return None

    def _calculate_learning_relevance(self, learning: LearningMemory, current_context: Dict[str, Any]) -> float:
        """Calculate how relevant a learning is to the current context"""
        relevance_score = 0.0
        
        # Check direct context matches
        trigger_conditions = learning.trigger_conditions
        for key, value in current_context.items():
            if key in trigger_conditions:
                if trigger_conditions[key] == value:
                    relevance_score += 0.3
                elif str(trigger_conditions[key]).lower() in str(value).lower():
                    relevance_score += 0.1
        
        # Check context tags
        context_tags = set(learning.context_tags)
        current_tags = set(current_context.get('tags', []))
        tag_overlap = len(context_tags.intersection(current_tags)) / max(len(context_tags), 1)
        relevance_score += tag_overlap * 0.4
        
        # Factor in learning strength
        relevance_score *= learning.strength
        
        return min(relevance_score, 1.0)

    def _extract_action_preferences(self, learning: LearningMemory, available_actions: List[str]) -> Dict[str, float]:
        """Extract action preferences from a learning"""
        preferences = {}
        learned_response = learning.learned_response
        
        # Extract preferences based on learning type
        if learning.learning_type == LearningType.BEHAVIORAL_PATTERN:
            preferred_style = learned_response.get('action_style')
            if preferred_style:
                # Map action styles to general actions
                style_to_action_map = {
                    'playful': {'play': 0.8, 'social': 0.6},
                    'nurturing': {'pet': 0.8, 'care': 0.7},
                    'curious': {'explore': 0.8, 'learn': 0.7},
                    'social': {'play': 0.7, 'interact': 0.8},
                    'independent': {'rest': 0.6, 'explore': 0.5}
                }
                
                action_prefs = style_to_action_map.get(preferred_style, {})
                for action in available_actions:
                    for mapped_action, pref in action_prefs.items():
                        if mapped_action in action.lower():
                            preferences[action] = pref
        
        elif learning.learning_type == LearningType.USER_PREFERENCE:
            # Apply user preference learnings
            success = learned_response.get('outcome_success', False)
            user_intent = learned_response.get('user_intent', '')
            
            preference_value = 0.7 if success else 0.3
            for action in available_actions:
                if any(intent_word in action.lower() for intent_word in user_intent.lower().split()):
                    preferences[action] = preference_value
        
        return preferences

    def _analyze_trait_adaptations(self, learning_type: LearningType, learnings: List[LearningMemory]) -> Dict[str, float]:
        """Analyze how learnings should influence personality traits"""
        trait_adaptations = {}
        
        if learning_type == LearningType.BEHAVIORAL_PATTERN:
            # Behavioral learnings might influence related traits
            for learning in learnings:
                if learning.strength > 0.7:  # Only strong learnings
                    action_style = learning.learned_response.get('action_style')
                    if action_style == 'social' and learning.success_rate > 0.7:
                        trait_adaptations['sociability'] = trait_adaptations.get('sociability', 0) + 0.1
                        trait_adaptations['extraversion'] = trait_adaptations.get('extraversion', 0) + 0.05
                    elif action_style == 'curious' and learning.success_rate > 0.7:
                        trait_adaptations['curiosity'] = trait_adaptations.get('curiosity', 0) + 0.1
                        trait_adaptations['openness'] = trait_adaptations.get('openness', 0) + 0.05
        
        elif learning_type == LearningType.EMOTIONAL_PATTERN:
            # Emotional learnings might influence emotional traits
            for learning in learnings:
                if learning.strength > 0.6:
                    resulting_state = learning.learned_response.get('resulting_state', 'neutral')
                    if resulting_state == 'happy' and learning.success_rate > 0.7:
                        trait_adaptations['optimism'] = trait_adaptations.get('optimism', 0) + 0.08
                        trait_adaptations['emotional_stability'] = trait_adaptations.get('emotional_stability', 0) + 0.05
        
        return trait_adaptations

    def _build_learning_templates(self) -> Dict[str, Any]:
        """Build templates for different types of learning"""
        return {
            "user_preference": {
                "pattern_keys": ["user_intent", "user_tone", "context_type"],
                "outcome_keys": ["happiness_change", "success"],
                "confidence_factors": ["outcome_magnitude", "consistency"]
            },
            "behavioral_pattern": {
                "pattern_keys": ["context", "action_style", "emotional_state"],
                "outcome_keys": ["effectiveness", "satisfaction"],
                "confidence_factors": ["repetition", "success_rate"]
            }
        }

    def _get_trait_index(self, trait_name: str) -> Optional[int]:
        """Get the index of a trait in the personality vector"""
        try:
            from .personality_system import TRAIT_NAME_TO_INDEX
            return TRAIT_NAME_TO_INDEX.get(trait_name)
        except ImportError:
            return None

    def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns"""
        common_keys = set(pattern1.keys()).intersection(set(pattern2.keys()))
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if pattern1[key] == pattern2[key]:
                matches += 1
            elif str(pattern1[key]).lower() == str(pattern2[key]).lower():
                matches += 0.5
        
        return matches / len(common_keys)

    def _generate_learning_description(self, learning_type: LearningType, pattern_data: Dict[str, Any], outcome: Dict[str, Any]) -> str:
        """Generate a human-readable description of what was learned"""
        if learning_type == LearningType.USER_PREFERENCE:
            intent = pattern_data.get('user_intent', 'interaction')
            success = pattern_data.get('outcome_success', False)
            return f"User {'enjoys' if success else 'dislikes'} {intent} interactions"
        
        elif learning_type == LearningType.BEHAVIORAL_PATTERN:
            style = pattern_data.get('action_style', 'unknown')
            success = pattern_data.get('outcome_success', False)
            return f"{'Effective' if success else 'Ineffective'} {style} behavior in this context"
        
        elif learning_type == LearningType.EMOTIONAL_PATTERN:
            trigger = pattern_data.get('trigger_emotion', 'neutral')
            result = pattern_data.get('resulting_state', 'neutral')
            return f"{trigger.title()} emotions lead to {result} responses"
        
        else:
            return f"Learned pattern for {learning_type.value}"

    def _extract_learned_response(self, pattern_data: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Extract what was learned from the interaction"""
        return {
            **pattern_data,
            'outcome_data': outcome,
            'learned_at': datetime.now().isoformat()
        }

    def _calculate_initial_confidence(self, outcome: Dict[str, Any]) -> float:
        """Calculate initial confidence for a new learning"""
        happiness_change = outcome.get('stats_delta', {}).get('happiness', 0)
        
        # Base confidence on outcome strength
        confidence = 0.5 + min(abs(happiness_change) / 40.0, 0.3)
        
        return min(confidence, 1.0)

    def _extract_context_tags(self, pattern_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> List[str]:
        """Extract relevant context tags for matching"""
        tags = []
        
        # Add tags from pattern data
        if 'user_intent' in pattern_data:
            tags.append(f"intent_{pattern_data['user_intent']}")
        
        if 'action_style' in pattern_data:
            tags.append(f"style_{pattern_data['action_style']}")
        
        # Add tags from context
        if context:
            if 'activity' in context:
                tags.append(f"activity_{context['activity']}")
            
            if 'mood' in context:
                tags.append(f"mood_{context['mood']}")
        
        return tags

    def _analyze_learning_trends(self, learnings: List[LearningMemory]) -> Dict[str, Any]:
        """Analyze trends in learning patterns"""
        if not learnings:
            return {"trend": "no_data"}
        
        # Group by time periods
        now = datetime.now()
        recent = [l for l in learnings if (now - l.created_at).days <= 7]
        older = [l for l in learnings if (now - l.created_at).days > 7]
        
        # Analyze learning velocity
        if len(older) > 0:
            recent_rate = len(recent) / 7.0  # learnings per day
            historical_rate = len(older) / max((now - min(l.created_at for l in older)).days, 1)
            
            if recent_rate > historical_rate * 1.5:
                trend = "accelerating_learning"
            elif recent_rate < historical_rate * 0.5:
                trend = "slowing_learning"
            else:
                trend = "steady_learning"
        else:
            trend = "new_learner"
        
        # Analyze learning quality
        avg_confidence = sum(l.confidence_score for l in learnings) / len(learnings)
        high_quality_learnings = len([l for l in learnings if l.confidence_score > 0.8])
        
        return {
            "trend": trend,
            "learning_quality": "high" if avg_confidence > 0.7 else ("medium" if avg_confidence > 0.4 else "low"),
            "high_confidence_learnings": high_quality_learnings,
            "learning_diversity": len(set(l.learning_type for l in learnings))
        }