#!/usr/bin/env python3
"""
Test script for speech styles integration
Tests both single archetype and blended personality speech styles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models.personality_system import EnhancedPersonality, PersonalityMode, PersonalityArchetypes
from core.agents.decision_agent import DecisionAgent
from core.agents.ai_client import MockAIClient
import numpy as np

def test_single_archetype_speech_style():
    """Test speech style extraction for single archetype personality"""
    print("🧪 Testing Single Archetype Speech Style (Yoda)")
    
    # Create an enhanced personality with Yoda archetype
    personality = EnhancedPersonality(
        mode=PersonalityMode.COMPLEX,
        archetype_base="yoda"
    )
    
    # Create decision agent
    ai_client = MockAIClient()
    agent = DecisionAgent(ai_client)
    
    # Test speech style extraction
    speech_style_data = agent._get_speech_style_guidance(personality)
    
    if speech_style_data:
        print("✅ Speech style data extracted successfully!")
        print(f"   Type: {speech_style_data['type']}")
        print(f"   Archetype: {speech_style_data.get('archetype_name', 'N/A')}")
        
        speech_style = speech_style_data['speech_style']
        print(f"   Tone: {speech_style['tone']}")
        print(f"   Sample phrases: {speech_style['common_phrases'][:3]}")
        print(f"   Key quirks: {speech_style['speech_quirks'][:2]}")
        
        # Test prompt formatting
        formatted_prompt = agent._format_speech_style_prompt(speech_style_data)
        print(f"   Formatted prompt length: {len(formatted_prompt)} characters")
        print("   ✅ Prompt formatting successful")
    else:
        print("❌ No speech style data extracted")
    
    print()

def test_blended_archetype_speech_style():
    """Test speech style blending for mixed personalities"""
    print("🧪 Testing Blended Archetype Speech Style (Socrates + Yoda)")
    
    # Create an enhanced personality with blended archetypes
    blend_weights = {
        "socrates": 0.6,
        "yoda": 0.4
    }
    
    personality = EnhancedPersonality(
        mode=PersonalityMode.COMPLEX,
        archetype_blend=blend_weights
    )
    
    # Create decision agent
    ai_client = MockAIClient()
    agent = DecisionAgent(ai_client)
    
    # Test speech style extraction
    speech_style_data = agent._get_speech_style_guidance(personality)
    
    if speech_style_data:
        print("✅ Blended speech style data extracted successfully!")
        print(f"   Type: {speech_style_data['type']}")
        
        speech_style = speech_style_data['speech_style']
        print(f"   Blended tone: {speech_style['tone']}")
        print(f"   Combined patterns: {len(speech_style['patterns'])} patterns")
        print(f"   Mixed phrases: {len(speech_style['common_phrases'])} phrases")
        print(f"   Sample phrases: {speech_style['common_phrases'][:3]}")
        
        # Test prompt formatting
        formatted_prompt = agent._format_speech_style_prompt(speech_style_data)
        print(f"   Formatted prompt length: {len(formatted_prompt)} characters")
        print("   ✅ Blended prompt formatting successful")
    else:
        print("❌ No blended speech style data extracted")
    
    print()

def test_archetype_availability():
    """Test that all archetypes have speech style data"""
    print("🧪 Testing Archetype Speech Style Availability")
    
    archetypes = PersonalityArchetypes.list_archetypes()
    print(f"   Found {len(archetypes)} archetypes")
    
    missing_speech_styles = []
    
    for archetype in archetypes:
        archetype_id = archetype['id']
        archetype_info = PersonalityArchetypes.get_archetype_info(archetype_id)
        
        if not archetype_info or 'speech_style' not in archetype_info:
            missing_speech_styles.append(archetype_id)
        else:
            speech_style = archetype_info['speech_style']
            required_keys = ['tone', 'patterns', 'common_phrases', 'speech_quirks']
            
            for key in required_keys:
                if key not in speech_style:
                    missing_speech_styles.append(f"{archetype_id} (missing {key})")
                    break
    
    if not missing_speech_styles:
        print("   ✅ All archetypes have complete speech style data!")
    else:
        print(f"   ❌ Missing speech styles: {missing_speech_styles}")
    
    print()

def test_simple_personality_fallback():
    """Test that simple personalities don't break the system"""
    print("🧪 Testing Simple Personality Fallback")
    
    # Create a simple personality
    personality = EnhancedPersonality(
        mode=PersonalityMode.SIMPLE,
        simple_traits=["friendly", "curious", "playful"]
    )
    
    # Create decision agent
    ai_client = MockAIClient()
    agent = DecisionAgent(ai_client)
    
    # Test speech style extraction (should return None)
    speech_style_data = agent._get_speech_style_guidance(personality)
    
    if speech_style_data is None:
        print("   ✅ Simple personality correctly returns no speech style data")
    else:
        print("   ❌ Simple personality unexpectedly returned speech style data")
    
    print()

def main():
    """Run all speech style tests"""
    print("🎭 CreatureMind Speech Style Integration Tests\n")
    
    test_archetype_availability()
    test_single_archetype_speech_style()
    test_blended_archetype_speech_style()
    test_simple_personality_fallback()
    
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main()