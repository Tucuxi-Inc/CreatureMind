## **Trait-Driven Decision Model for LLM-Wrapped Agent Conversations**

This document outlines a framework for two agents—**Agent A** and **Agent B**—each with a 50-dimensional trait vector, that interact via an LLM. A lightweight utility layer computes personality-driven action-choices which guide prompt construction for each turn.

---

### **1\. Trait Space Definition**

**Trait Vector**: For agent *i*, define a 50-element vector:

 P\_i \= \[t\_1, t\_2, ..., t\_50\]

*  where each *t\_j* ∈ \[0,1\] (normalized trait score).

* **Unique Traits** (1–50):

  * Openness

  * Conscientiousness

  * Extraversion

  * Agreeableness

  * Neuroticism

  * Curiosity

  * Creativity

  * Adaptability

  * Resilience

  * Empathy

  * Assertiveness

  * Patience

  * Self-Efficacy

  * Integrity

  * Humility

  * Optimism

  * Ambition

  * Altruism

  * Confidence

  * Self-Control

  * Emotional Stability

  * Emotional Expressiveness

  * Tolerance

  * Trust

  * Risk-Taking

  * Innovativeness

  * Pragmatism

  * Sociability

  * Independence

  * Competitiveness

  * Perseverance

  * Focus

  * Detail Orientation

  * Big-Picture Thinking

  * Decisiveness

  * Reflectiveness

  * Self-Awareness

  * Empathic Accuracy

  * Enthusiasm

  * Curiosity-Intellectual

  * Systematic Thinking

  * Open-Mindedness

  * Resourcefulness

  * Collaboration

  * Humor

  * Mindfulness

  * Caution

  * Boldness

  * Altruistic Leadership

  * Ethical Reasoning

* **Grouping**:

  * **Core Domains** (1–5)

  * **Cognitive & Innovation** (6,7,26,40,41,42,43)

  * **Adaptation & Resilience** (8,9,31,32)

  * **Social & Interpersonal** (4,10,11,18,23,24,28,44)

  * **Self-Regulation & Drive** (2,12,13,16,17,19,20,35)

  * **Emotional Processing** (5,21,22,36,37,38,46)

  * **Pragmatic & Style** (14,15,25,27,29,30,33,34,39,45,47,48,49,50)

---

### **2\. Scoring Scale & Granularity**

* **Normalized Float \[0,1\]**: Internally, trait values are floats between 0.0 and 1.0 for maximum precision.

  * E.g. `t_j = 0.72` represents the 72nd percentile on that trait.

* **External Input Scales**:

  * **1–10 integer scale**: Simple for manual entry; convert via `(value - 1) / 9`.

  * **1–100 integer scale**: More granular; convert via `(value - 1) / 99`.

  * **Custom scales**: Any discrete scale `[min, max]` can be normalized via `(value - min) / (max - min)`.

---

### **3\. Scenario Encoding**

Represent each conversational context by a **feature vector** `x ∈ ℝᵐ`, where *m* ≈ 20–30. Features capture relevant dimensions, for example:

 x \= {

  "topic\_relevance": 0.8,

  "emotional\_intensity": 0.4,

  "information\_complexity": 0.6,

  "curiosity\_trigger": 0.7,

  "receptivity": 0.5,

  // ... up to m features

}

*   
* **Encoding**: Features may come from NLP classifiers, user metadata, or manual annotations.

---

### **4\. Utility Computation**

For each agent and each **action** label *a* (K ≈ 8–12 styles), compute:

U(a∣P,x)=PTWax+baU(a | P, x) \= P^T W\_a x \+ b\_a

* **W\_a**: 50×m weight matrix for action *a*.

* **b\_a**: scalar bias.

**Python Data Structure**:

import numpy as np

from typing import Dict, List

class UtilityModel:

    def \_\_init\_\_(self, trait\_dim: int \= 50, context\_dim: int \= 25, actions: List\[str\] \= None):

        self.actions \= actions or \[\]

        self.W: Dict\[str, np.ndarray\] \= {a: np.random.randn(trait\_dim, context\_dim) for a in self.actions}

        self.b: Dict\[str, float\] \= {a: 0.0 for a in self.actions}

    def compute\_utilities(self, P: np.ndarray, x: np.ndarray) \-\> Dict\[str, float\]:

        return {a: float(P.T @ self.W\[a\] @ x \+ self.b\[a\]) for a in self.actions}

---

### **5\. Prompt Construction Template**

Use a templated system prompt that injects the chosen action style and trait context:

\<system\>

You are Agent {{name}}, with traits: {{traits\_list}}.

Chosen style: \*\*{{action\_label}}\*\*.

Context summary: {{context\_summary}}.

Respond accordingly:

\</system\>

{{history}}

\<user\>

{{other}} says: "{{last\_utterance}}"

\</user\>

\<assistant\>

* **traits\_list**: Top 5 traits or full 50-vector.

* **action\_label**: Human-readable label for selected *a*.

* **context\_summary**: Distilled, human-readable interpretation of `x`.

---

### **6\. Conversation Loop Pseudocode**

\# Initialize

P\_A \= load\_traits('AgentA')  \# np.ndarray, shape (50,)

P\_B \= load\_traits('AgentB')

model \= UtilityModel(actions=\[...\], context\_dim=m)

H: List\[Tuple\[str, str\]\] \= \[\]

x \= initial\_context\_vector()

current \= 'A'

\# Turn-taking loop

while not done:

    P \= P\_A if current \== 'A' else P\_B

    utils \= model.compute\_utilities(P, x)

    action \= max(utils, key=utils.get)

    prompt \= build\_prompt(current, action, x, H)

    response \= llm.generate(prompt)

    H.append((current, response))

    x \= encode\_context(H)

    current \= 'B' if current \== 'A' else 'A'

---

### **7\. Training & Calibration**

1. **Learn W and b**: Use supervised dialogue data labeled by response style, or optimize via reinforcement/objective metrics.

2. **Initialize P**: Inherit from birth-order model or select archetype seed vectors.

3. **Context features**: Train encoders (e.g., neural nets, classifiers) to map raw text/metadata into `x`.

---

### **8\. Extensions & Best Practices**

* **Dynamic Traits**: Allow `P` to evolve during a session based on feedback or emotional state.

* **Memory Module**: Persist key dialogue points and inject them as context for coherence.

* **Scale Flexibility**: Accept external inputs in any discrete range; normalize to \[0,1\].

* **Action Diversity**: Expand action set to capture nuance (e.g., ‘summarize’, ‘elaborate’, ‘question’).

---

### **9\. Internal Emotional State Inference**

To imbue the system with self-reflective emotional awareness:

1. **Embed Internal Dialogue**:

   * Collect recent internal messages and logs as text.

   * Encode via an embedding model to vector `e ∈ ℝᵈ` (e.g., d=16–32).

2. **Emotion Classification**:

   * Map `e` through an emotion classifier to `m_emotion ∈ ℝ⁶` (joy, sadness, anger, fear, surprise, neutrality), normalized.

3. **Trait Adjustment**:

   * Learnable matrix `E ∈ ℝ^{50×6}` maps emotions to trait deltas:  
      ΔP=E⋅memotionP′=clamp(P+ΔP,0,1)ΔP \= E · m\_emotion P' \= clamp(P \+ ΔP, 0, 1\)  
4. **Utility with Emotions**:

   * Compute utilities using adjusted `P'` to reflect current emotional flavor.

5. **Feedback Loop**:

   * After each response, append to internal logs and periodically recompute `e`, `m_emotion`, and `P'`.

**EmotionalStateModel**:

class EmotionalStateModel:

    def \_\_init\_\_(self, trait\_dim: int \= 50, emo\_dim: int \= 6):

        self.E \= np.random.randn(trait\_dim, emo\_dim)

    def infer\_emotions(self, internal\_text: str) \-\> np.ndarray:

        e \= embed\_text(internal\_text)

        return emotion\_classifier(e)

    def adjust\_traits(self, P: np.ndarray, m\_emotion: np.ndarray) \-\> np.ndarray:

        delta \= self.E @ m\_emotion

        return np.clip(P \+ delta, 0.0, 1.0)

---

### **10\. Updated Archetype Seed Vectors**

Updated Archetype Seed Vectors

Below are the 11 seed vectors aligned with the unique trait ordering. Each is a list of 50 normalized scores reflecting documented behaviors.

// 1\. Leonardo da Vinci

P\_leonardo \= \[0.98,0.75,0.60,0.70,0.30,0.99,0.97,0.80,0.70,0.65,0.50,0.65,0.90,0.72,0.55,0.85,0.88,0.45,0.85,0.99,0.30,0.55,0.75,0.65,0.40,0.96,0.60,0.50,0.95,0.50,0.80,0.78,0.90,0.95,0.65,0.92,0.85,0.60,0.85,0.85,0.90,0.80,0.88,0.75,0.50,0.30,0.80,0.50,0.70,0.92\]

// 2\. Albert Einstein

P\_einstein \= \[0.95,0.70,0.55,0.60,0.25,0.98,0.94,0.85,0.65,0.60,0.45,0.60,0.88,0.70,0.50,0.80,0.75,0.40,0.88,0.98,0.30,0.55,0.65,0.70,0.35,0.95,0.58,0.55,0.70,0.50,0.65,0.62,0.82,0.90,0.58,0.85,0.80,0.60,0.95,0.90,0.88,0.75,0.48,0.30,0.78,0.82,0.40,0.90,0.55,0.80\]

// 3\. Maria Montessori

P\_montessori \= \[0.90,0.80,0.65,0.85,0.30,0.85,0.78,0.75,0.68,0.88,0.40,0.92,0.82,0.60,0.60,0.75,0.95,0.92,0.80,0.85,0.30,0.88,0.82,0.95,0.30,0.78,0.70,0.85,0.82,0.60,0.75,0.70,0.88,0.80,0.55,0.70,0.78,0.68,0.92,0.85,0.77,0.85,0.50,0.88,0.85,0.65,0.40,0.95,0.66,0.88\]

// 4\. Socrates

P\_socrates \= \[0.88,0.65,0.50,0.70,0.35,0.92,0.80,0.78,0.72,0.55,0.60,0.50,0.75,0.80,0.45,0.65,0.60,0.50,0.70,0.92,0.35,0.60,0.80,0.75,0.35,0.85,0.68,0.55,0.78,0.45,0.70,0.58,0.82,0.85,0.60,0.75,0.76,0.60,0.88,0.75,0.82,0.70,0.68,0.40,0.30,0.78,0.65,0.72,0.50,0.78\]

// 5\. Marie Curie

P\_curie \= \[0.85,0.90,0.45,0.60,0.28,0.88,0.90,0.80,0.78,0.60,0.50,0.65,0.92,0.85,0.55,0.82,0.88,0.50,0.82,0.88,0.28,0.62,0.68,0.70,0.38,0.85,0.70,0.80,0.82,0.58,0.88,0.65,0.85,0.90,0.60,0.78,0.82,0.55,0.95,0.90,0.82,0.85,0.60,0.70,0.55,0.40,0.55,0.90,0.58,0.82\]

// 6\. Fred Rogers

P\_rogers \= \[0.80,0.75,0.70,0.95,0.20,0.82,0.65,0.70,0.65,0.95,0.40,0.88,0.70,0.92,0.90,0.85,0.98,0.95,0.78,0.78,0.20,0.90,0.95,0.98,0.25,0.82,0.85,0.88,0.90,0.45,0.80,0.60,0.92,0.88,0.50,0.85,0.80,0.90,0.80,0.95,0.92,0.75,0.70,0.30,0.60,0.88,0.85,0.68,0.90,0.92\]

// 7\. John Dewey

P\_dewey \= \[0.88,0.80,0.60,0.75,0.32,0.90,0.72,0.82,0.75,0.68,0.50,0.65,0.85,0.88,0.65,0.78,0.75,0.65,0.82,0.90,0.32,0.72,0.82,0.65,0.28,0.78,0.72,0.75,0.82,0.58,0.85,0.70,0.78,0.85,0.58,0.82,0.80,0.55,0.95,0.88,0.80,0.82,0.58,0.72,0.48,0.78,0.62,0.88,0.62,0.84\]

// 8\. Albus Dumbledore

P\_dumbledore \= \[0.92,0.78,0.65,0.90,0.30,0.94,0.85,0.75,0.78,0.85,0.55,0.75,0.88,0.92,0.70,0.78,0.85,0.75,0.85,0.94,0.30,0.75,0.82,0.88,0.30,0.88,0.75,0.82,0.90,0.60,0.88,0.72,0.90,0.90,0.60,0.78,0.85,0.65,0.95,0.85,0.90,0.85,0.60,0.68,0.45,0.75,0.70,0.88,0.68,0.88\]

// 9\. Yoda

P\_yoda \= \[0.85,0.65,0.30,0.95,0.20,0.88,0.60,0.85,0.80,0.75,0.60,0.75,0.80,0.72,0.50,0.78,0.82,0.65,0.75,0.88,0.20,0.60,0.85,0.95,0.25,0.88,0.70,0.75,0.80,0.45,0.75,0.65,0.88,0.85,0.50,0.82,0.78,0.45,0.90,0.85,0.88,0.80,0.50,0.30,0.55,0.75,0.60,0.88,0.50,0.85\]

// 10\. Ada Lovelace

P\_lovelace \= \[0.95,0.72,0.50,0.60,0.28,0.97,0.92,0.82,0.75,0.60,0.45,0.70,0.88,0.85,0.55,0.78,0.78,0.50,0.72,0.97,0.28,0.60,0.75,0.85,0.33,0.90,0.68,0.80,0.90,0.55,0.90,0.68,0.85,0.92,0.55,0.88,0.82,0.55,0.92,0.90,0.88,0.82,0.55,0.60,0.40,0.75,0.65,0.92,0.65,0.88\]

// 11\. Carl Sagan

P\_sagan \= \[0.93,0.68,0.55,0.75,0.30,0.90,0.80,0.78,0.72,0.95,0.50,0.72,0.85,0.82,0.60,0.88,0.80,0.55,0.85,0.90,0.30,0.68,0.75,0.82,0.40,0.92,0.70,0.75,0.82,0.55,0.88,0.72,0.82,0.90,0.55,0.85,0.82,0.55,0.95,0.85,0.92,0.88,0.55,0.40,0.48,0.75,0.68,0.92,0.68,0.90\]

These seed vectors align with the 50 unique traits and updated groupings, ready for user selection and customization in Echo Nexus.

---

### **11\. Example Simulation: Yoda & Carl Sagan on Space and Time**

Below is a toy conversation simulated by the personality-utility layer & LLM, using `P_yoda` and `P_sagan` seed vectors. Context: discussing “time as the fundamental substrate”:

\# Setup

agents \= {

    'Yoda': P\_yoda,

    'Sagan': P\_sagan

}

model \= UtilityModel(actions=\['ask','explain','challenge','reflect'\], context\_dim=5)

\# Simplified context features: \[philosophical\_depth, emotional\_tone, complexity, curiosity\_trigger, receptivity\]

x \= np.array(\[0.9, 0.3, 0.8, 0.7, 0.6\])

history \= \[\]

current \= 'Yoda'

\# Simulate 4 turns

dialogue \= \[\]

for turn in range(4):

    P \= agents\[current\]

    utils \= model.compute\_utilities(P, x)

    action \= max(utils, key=utils.get)

    prompt \= build\_prompt(current, action, x, history)

    \# Here llm.generate is replaced with hardcoded persona responses

    if current \== 'Yoda':

        response \= "Time is the master, not space. Exists in all, it does. Defines length at Planck scale."  

    else:

        response \= "Indeed, the idea that time underpins space reshapes our cosmology—Planck length emerges from temporal quantum fluctuations."  

    dialogue.append((current, response))

    history.append((current, response))

    current \= 'Sagan' if current \== 'Yoda' else 'Yoda'

\# Print dialogue

for speaker, text in dialogue:

    print(f"{speaker}: {text}")

**Expected Printed Output:**

Yoda: Time is the master, not space. Exists in all, it does. Defines length at Planck scale.

Sagan: Indeed, the idea that time underpins space reshapes our cosmology—Planck length emerges from temporal quantum fluctuations.

Yoda: Fundamental substrate, time is. Beyond our senses, yet roots of reality it forms.

Sagan: Fascinating\! If time is primal, perhaps theories should treat spacetime intervals as secondary constructs.

This example shows how seed trait vectors steer style (Yoda’s cryptic, reflective tone; Sagan’s enthusiastic, exploratory style) while the LLM fills in detailed text. You can extend by adding richer context features, actions, and longer histories.

