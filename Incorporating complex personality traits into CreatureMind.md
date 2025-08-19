Incorporating complex personality traits into CreatureMind

## **Integration Instructions for 50-Trait Personality System**

### **1\. Data Model Extensions**

First, extend your creature models to support trait vectors:

\# In creature.py or creature\_state.py  
class CreatureState:  
    def \_\_init\_\_(self, ...):  
        \# Add trait vector  
        self.trait\_vector: np.ndarray \= np.zeros(50)  \# Default neutral  
        self.trait\_labels \= \[  
            "openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism",  
            "curiosity", "creativity", "adaptability", "resilience", "empathy",  
            \# ... all 50 traits from the document  
        \]

### **2\. Add Utility Model to Decision Agent**

Create a new utility computation module:

\# New file: agents/utility\_model.py  
import numpy as np  
from typing import Dict, List

class TraitUtilityModel:  
    def \_\_init\_\_(self, trait\_dim: int \= 50):  
        self.trait\_dim \= trait\_dim  
        \# Define action styles relevant to creatures  
        self.actions \= \[  
            "playful", "cautious", "assertive", "nurturing",   
            "curious", "defensive", "social", "independent",  
            "energetic", "calm", "analytical", "emotional"  
        \]  
        \# Initialize weight matrices (could be loaded from config)  
        self.W \= {a: np.random.randn(trait\_dim, 25\) \* 0.1 for a in self.actions}  
        self.b \= {a: 0.0 for a in self.actions}  
      
    def compute\_utilities(self, trait\_vector: np.ndarray, context\_vector: np.ndarray) \-\> Dict\[str, float\]:  
        """Compute utility scores for each action style given traits and context"""  
        utilities \= {}  
        for action in self.actions:  
            utility \= float(trait\_vector.T @ self.W\[action\] @ context\_vector \+ self.b\[action\])  
            utilities\[action\] \= utility  
        return utilities  
      
    def select\_action\_style(self, utilities: Dict\[str, float\], temperature: float \= 0.3) \-\> str:  
        """Select action style using softmax with temperature"""  
        \# Implementation of softmax selection  
        values \= np.array(list(utilities.values()))  
        probs \= np.exp(values / temperature) / np.sum(np.exp(values / temperature))  
        return np.random.choice(list(utilities.keys()), p=probs)

### **3\. Modify Decision Agent**

Update the decision agent to use trait-based decision making:

\# In decision\_agent.py  
from .utility\_model import TraitUtilityModel

class DecisionAgent:  
    def \_\_init\_\_(self, ai\_client: AIClient):  
        self.ai\_client \= ai\_client  
        self.utility\_model \= TraitUtilityModel()  
      
    async def decide(self, perception\_data, emotion\_data, memory\_data,   
                     creature\_state, template):  
        \# NEW: Extract context vector from agent inputs  
        context\_vector \= self.\_build\_context\_vector(  
            perception\_data, emotion\_data, memory\_data, creature\_state  
        )  
          
        \# NEW: Compute utilities and select action style  
        utilities \= self.utility\_model.compute\_utilities(  
            creature\_state.trait\_vector, context\_vector  
        )  
        action\_style \= self.utility\_model.select\_action\_style(utilities)  
          
        \# Modify system prompt to include trait influence  
        system\_prompt \= self.\_build\_trait\_aware\_prompt(  
            creature\_state, template, action\_style, utilities  
        )  
          
        \# Continue with existing logic...  
      
    def \_build\_context\_vector(self, perception\_data, emotion\_data,   
                             memory\_data, creature\_state) \-\> np.ndarray:  
        """Convert agent data into context vector for utility computation"""  
        \# Map various inputs to a 25-dimensional context vector  
        context \= np.zeros(25)  
          
        \# Example mappings (customize based on your needs):  
        \# Emotional intensity (0-4)  
        emotion\_map \= {"happy": 0.8, "sad": 0.6, "angry": 0.9, "neutral": 0.3}  
        context\[0\] \= emotion\_map.get(emotion\_data.get("primary\_emotion", "neutral"), 0.5)  
          
        \# User intent mappings (5-9)  
        intent\_map \= {"greet": 0.8, "play": 0.9, "feed": 0.7, "command": 0.4}  
        context\[5\] \= intent\_map.get(perception\_data.get("user\_intent", "unknown"), 0.5)  
          
        \# Relationship quality (10-14)  
        relationship\_map \= {"strong": 0.9, "developing": 0.6, "new": 0.3, "strained": 0.2}  
        context\[10\] \= relationship\_map.get(memory\_data.get("relationship", "neutral"), 0.5)  
          
        \# Physical state (15-19)  
        context\[15\] \= creature\_state.stats.get("energy", 50\) / 100  
        context\[16\] \= creature\_state.stats.get("happiness", 50\) / 100  
        context\[17\] \= creature\_state.stats.get("hunger", 50\) / 100  
          
        \# Normalize  
        return context / np.linalg.norm(context)  
      
    def \_build\_trait\_aware\_prompt(self, creature\_state, template,   
                                 action\_style, utilities):  
        """Build prompt that incorporates trait-driven action style"""  
        \# Get top 5 traits for this creature  
        trait\_indices \= np.argsort(creature\_state.trait\_vector)\[-5:\]  
        top\_traits \= \[creature\_state.trait\_labels\[i\] for i in trait\_indices\]  
          
        prompt \= f"""You are the Decision Making Agent for a {creature\_state.species}.

TRAIT-DRIVEN PERSONALITY:  
\- Dominant traits: {', '.join(top\_traits)}  
\- Selected action style: {action\_style}  
\- Style confidence: {utilities\[action\_style\]:.2f}

Your response MUST align with the {action\_style} style, which means:  
{self.\_get\_style\_guidance(action\_style)}

\[Rest of existing prompt...\]  
"""  
        return prompt  
      
    def \_get\_style\_guidance(self, action\_style: str) \-\> str:  
        """Provide specific guidance for each action style"""  
        style\_guides \= {  
            "playful": "Be energetic, fun-loving, and spontaneous. Use bouncy movements and happy sounds.",  
            "cautious": "Be careful, observant, and measured. Move slowly and assess before acting.",  
            "assertive": "Be confident, direct, and decisive. Stand tall and communicate clearly.",  
            "nurturing": "Be caring, gentle, and protective. Use soft sounds and comforting gestures.",  
            \# ... etc  
        }  
        return style\_guides.get(action\_style, "Act naturally according to your species.")

### **4\. Add Archetype Presets**

Create a preset manager for the personality archetypes:

\# New file: models/personality\_archetypes.py  
import numpy as np

class PersonalityArchetypes:  
    """Preset personality vectors from the trait model document"""  
      
    ARCHETYPES \= {  
        "leonardo": {  
            "name": "Leonardo da Vinci",  
            "description": "Curious, creative, and endlessly inventive",  
            "vector": \[0.98,0.75,0.60,0.70,0.30,0.99,0.97,0.80,0.70,0.65,  
                      0.50,0.65,0.90,0.72,0.55,0.85,0.88,0.45,0.85,0.99,  
                      0.30,0.55,0.75,0.65,0.40,0.96,0.60,0.50,0.95,0.50,  
                      0.80,0.78,0.90,0.95,0.65,0.92,0.85,0.60,0.85,0.85,  
                      0.90,0.80,0.88,0.75,0.50,0.30,0.80,0.50,0.70,0.92\]  
        },  
        "einstein": {  
            "name": "Albert Einstein",  
            "description": "Deeply thoughtful, intellectually curious, and independent",  
            "vector": \[0.95,0.70,0.55,0.60,0.25,0.98,0.94,0.85,0.65,0.60,  
                      0.45,0.60,0.88,0.70,0.50,0.80,0.75,0.40,0.88,0.98,  
                      0.30,0.55,0.65,0.70,0.35,0.95,0.58,0.55,0.70,0.50,  
                      0.65,0.62,0.82,0.90,0.58,0.85,0.80,0.60,0.95,0.90,  
                      0.88,0.75,0.48,0.30,0.78,0.82,0.40,0.90,0.55,0.80\]  
        },  
        \# ... add all other archetypes  
    }  
      
    @classmethod  
    def get\_archetype(cls, name: str) \-\> np.ndarray:  
        """Get archetype vector by name"""  
        if name in cls.ARCHETYPES:  
            return np.array(cls.ARCHETYPES\[name\]\["vector"\])  
        return None  
      
    @classmethod  
    def create\_custom\_blend(cls, archetype\_weights: Dict\[str, float\]) \-\> np.ndarray:  
        """Blend multiple archetypes with weights"""  
        result \= np.zeros(50)  
        total\_weight \= sum(archetype\_weights.values())  
          
        for archetype\_name, weight in archetype\_weights.items():  
            if archetype\_name in cls.ARCHETYPES:  
                vector \= np.array(cls.ARCHETYPES\[archetype\_name\]\["vector"\])  
                result \+= vector \* (weight / total\_weight)  
          
        return np.clip(result, 0.0, 1.0)

### **5\. Integration with Creature Templates**

Extend creature templates to include personality configuration:

\# In creature\_template.py  
class CreatureTemplate:  
    def \_\_init\_\_(self, ...):  
        \# Add personality configuration  
        self.personality\_config \= {  
            "base\_archetype": "einstein",  \# Optional preset  
            "trait\_modifiers": {},  \# Specific trait overrides  
            "randomization\_factor": 0.1  \# How much to vary from base  
        }

### **6\. Usage Example**

When creating a creature:

\# In creature initialization  
from models.personality\_archetypes import PersonalityArchetypes

\# Option 1: Use a preset  
creature.trait\_vector \= PersonalityArchetypes.get\_archetype("yoda")

\# Option 2: Blend archetypes  
creature.trait\_vector \= PersonalityArchetypes.create\_custom\_blend({  
    "einstein": 0.6,  
    "rogers": 0.4  
})

\# Option 3: Custom traits  
creature.trait\_vector \= np.array(\[0.7, 0.8, 0.3, ...\])  \# 50 values

### **7\. Key Implementation Notes for Co-pilot**

1. **Context Vector Design**: The context vector should capture relevant aspects of the current situation. Consider including:

   * Emotional state (from emotion agent)  
   * User intent (from perception agent)  
   * Physical needs (from creature stats)  
   * Social context (from memory agent)  
   * Environmental factors  
2. **Weight Matrix Initialization**: Start with small random weights and consider training them using:

   * Supervised learning from desired creature behaviors  
   * Reinforcement learning from user feedback  
   * Manual tuning for specific personality effects  
3. **Action Style Mapping**: Map the abstract action styles to concrete creature behaviors:

   * "playful" → bouncing, tail wagging, excited sounds  
   * "cautious" → slow movements, quiet observation  
   * "assertive" → direct gaze, firm stance, clear vocalizations  
4. **Trait Influence Strength**: Add a "trait\_influence\_strength" parameter (0-1) to control how much personality affects decisions vs. immediate context.

5. **Debugging**: Add trait vector visualization and utility scores to debug\_info for understanding why certain behaviors were chosen.

This integration preserves your existing multi-agent architecture while adding a sophisticated personality layer that influences decision-making in a mathematically principled way.

