# CreatureMind 🧠

**The most advanced AI companion system ever created - featuring 50-dimensional evolving personalities, emotional intelligence, and learning adaptation.**

Transform any idea into a living, breathing digital creature with authentic personality, emotions, and their own unique "language" that only translates when they're in the right mood. Watch your creatures grow, learn, and develop unique relationships with you over time.

## 🆕 **BREAKTHROUGH: Enhanced Evolving Personality System**
**The world's first 50-dimensional AI personality system with real-time evolution, emotional influence, and learning adaptation!** Your creatures don't just have personalities - they develop them through your interactions, creating truly unique companions that feel genuinely alive.

### 🌟 **What Makes This Revolutionary?**

| Traditional AI | CreatureMind Enhanced |
|----------------|----------------------|
| Static responses | Dynamic personality evolution |
| Fixed behavior patterns | Learns from every interaction |
| No emotional depth | Real-time emotional influences |
| One-size-fits-all | 50-dimensional trait customization |
| Forgets interactions | Builds lasting relationships |

---

## 🎯 What is CreatureMind?

CreatureMind creates **AI creature minds** with unprecedented sophistication. Each creature:

- **🧬 Evolving Personality**: 50-dimensional trait vectors that change based on experiences
- **💭 Emotional Intelligence**: Real-time emotional states that influence behavior  
- **📚 Learning & Adaptation**: Creatures learn your preferences and adapt over time
- **🗣️ Natural Communication**: Speaks in their species "language" with mood-based translation
- **🧠 Persistent Memory**: Remembers all interactions and builds deep relationships
- **🎭 Authentic Behavior**: Each species responds with unique, believable patterns

**Think Tamagotchi meets advanced psychology research, powered by cutting-edge AI - for ANY creature you can imagine!**

---

## 🚀 Complete Setup Guide (Start from Zero)

### Step 1: Install Required Software

**For Mac users:**

1. **Install Homebrew** (if you don't have it):
   - Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)
   - Copy and paste this command, then press Enter:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.11**:
   ```bash
   brew install python@3.11
   ```

**For Windows users:**

1. **Install Python**:
   - Go to [python.org](https://python.org/downloads/)
   - Download Python 3.11 or newer
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Install Git**:
   - Go to [git-scm.com](https://git-scm.com/download/win)
   - Download and install Git

### Step 2: Get Your OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to "API Keys" in your account
4. Create a new key (it starts with `sk-`)
5. **Keep this safe** - you'll need it in Step 4!

### Step 3: Download CreatureMind

**Option A: Download ZIP (Easiest)**
1. Download the CreatureMind folder
2. Put it somewhere easy to find (like your Desktop)

**Option B: Use Git (if you have it)**
```bash
git clone [repository-url] CreatureMind
cd CreatureMind
```

### Step 4: Set Up CreatureMind

1. **Open Terminal/Command Prompt** in the CreatureMind folder:
   - **Mac**: Right-click the CreatureMind folder → "New Terminal at Folder"
   - **Windows**: Shift+Right-click in the folder → "Open PowerShell window here"

2. **Install CreatureMind**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your API key**:
   - **Mac/Linux**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   - **Windows**:
   ```bash
   set OPENAI_API_KEY=your-api-key-here
   ```

### Step 5: Start CreatureMind! 🎉

```bash
python -m api.server
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

**🎉 Success! CreatureMind is now running!**

---

## 🐳 Docker Setup (Alternative Method)

### Option A: Quick Start with Docker Compose (Recommended)

**Prerequisites**: Docker and Docker Compose installed

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tucuxi-Inc/CreatureMind.git
   cd CreatureMind
   ```

2. **Set up environment:**
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Open your browser:** `http://localhost:8000`

**🎉 CreatureMind is now running in Docker!**

### Option B: Docker Build and Run

1. **Build the image:**
   ```bash
   docker build -t creaturemind .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name creaturemind \
     -p 8000:8000 \
     -e OPENAI_API_KEY="your-api-key-here" \
     creaturemind
   ```

3. **Open your browser:** `http://localhost:8000`

### 🌐 Cloud Deployment Options

**Deploy to any cloud platform that supports Docker:**

**🚀 Railway (Easiest):**
1. Fork this repository on GitHub
2. Connect Railway to your GitHub account
3. Deploy with one click from your forked repo
4. Add `OPENAI_API_KEY` environment variable in Railway dashboard

**☁️ Google Cloud Run:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/[PROJECT-ID]/creaturemind

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/[PROJECT-ID]/creaturemind --platform managed
```

**🔷 Azure Container Instances:**
```bash
# Build and push to Azure Container Registry
az acr build --registry [REGISTRY-NAME] --image creaturemind .

# Deploy to Container Instances
az container create --resource-group [RESOURCE-GROUP] \
  --name creaturemind --image [REGISTRY].azurecr.io/creaturemind:latest
```

**🟠 AWS ECS/Fargate:**
1. Push image to Amazon ECR
2. Create ECS task definition
3. Deploy to Fargate cluster

### Docker Management Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart with updates
docker-compose down && docker-compose up -d

# View running containers
docker ps

# Access container shell
docker exec -it creaturemind bash
```

---

## 🧠 Enhanced Personality System Overview

### The Four Pillars of Advanced Personalities

**1. 🧬 50-Dimensional Trait System**
- Scientifically-grounded personality traits based on psychological research
- Each trait affects behavior in realistic, measurable ways
- Choose from simple (3-5 traits) or complex (50-dimensional) modes

**2. 🌱 Personality Evolution** 
- Creatures change based on experiences and interactions
- 10 evolution triggers: achievements, failures, learning, bonding, stress, etc.
- Real personality development that you can track over time

**3. 💭 Emotional State Influence**
- Current emotions temporarily modify personality traits
- 12 emotion types with realistic behavioral impacts
- Natural decay and realistic emotional patterns

**4. 📚 Learning & Adaptation**
- Creatures learn your preferences and behavioral patterns
- 7 learning types: user preferences, emotional patterns, interaction outcomes
- Adaptive responses that improve relationship quality over time

### Famous Personality Archetypes

Start with scientifically-crafted personalities based on historical figures:

- **🎨 Leonardo da Vinci** - Creative genius (high creativity, curiosity, innovativeness)
- **🔬 Albert Einstein** - Analytical thinker (high systematic thinking, intellectual curiosity)  
- **👩‍🏫 Maria Montessori** - Nurturing educator (high empathy, patience, altruism)
- **🤔 Socrates** - Wise philosopher (high wisdom, curiosity, humility)
- **🤗 Fred Rogers** - Gentle soul (high empathy, kindness, emotional stability)
- **👴 Yoda** - Ancient wisdom (high wisdom, patience, mindfulness)

---

## 🐕 Create Your First Enhanced Creature

### Option 1: Web Interface with Enhanced Personalities (Recommended)

1. **Open your browser** and go to: `http://localhost:8000`
2. **Click "Create Your First Creature"**
3. **Choose your personality mode**:

   **Simple Mode (Beginner-Friendly):**
   - Pick 3-5 key traits like "playful", "loyal", "curious"
   - Choose a base temperament
   - Add custom description

   **Complex Mode (Advanced):**
   - **Archetype**: Start with Leonardo, Einstein, etc.
   - **Custom**: Set all 50 traits individually  
   - **Blend**: Combine multiple archetypes
   - **Fine-tune**: Modify specific traits

4. **Watch your creature come to life!**

### Option 2: Terminal Commands

**Create a creature with simple personality:**
```bash
curl -X POST "http://localhost:8000/creatures/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buddy",
    "template_id": "loyal_dog",
    "personality_mode": "simple",
    "simple_personality": {
      "traits": ["playful", "loyal", "energetic"],
      "base_temperament": "energetic"
    }
  }'
```

**Create a creature with Einstein's personality:**
```bash
curl -X POST "http://localhost:8000/creatures/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Einstein",
    "template_id": "loyal_dog", 
    "personality_mode": "complex",
    "complex_personality": {
      "mode": "archetype",
      "archetype_name": "einstein"
    }
  }'
```

**Create a custom personality blend:**
```bash
curl -X POST "http://localhost:8000/creatures/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Creative Scientist",
    "template_id": "loyal_dog",
    "personality_mode": "complex", 
    "complex_personality": {
      "mode": "blend",
      "archetype_weights": {
        "leonardo": 0.7,
        "einstein": 0.3
      },
      "trait_modifications": {
        "sociability": 0.8
      }
    }
  }'
```

### Option 3: Use the Test Script

```bash
python examples/test_api.py
```

This automatically creates a creature and demonstrates the personality system!

---

## 🎮 Interacting with Enhanced Creatures

### Basic Interactions

**Send a message:**
```bash
curl -X POST "http://localhost:8000/creatures/CREATURE_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello there!"}'
```

**Example responses based on personality:**

**High Extraversion Creature:**
```json
{
  "creature_language": "*bounds forward eagerly* *excited barking* *tail wagging intensely*",
  "human_translation": "Hello there! I'm so excited to meet you!",
  "can_translate": true,
  "emotional_state": "excited"
}
```

**Low Extraversion Creature:**
```json
{
  "creature_language": "*cautious approach* *quiet sniff* *reserved posture*",
  "human_translation": "Oh... hello. I need a moment to get comfortable.",
  "can_translate": true,
  "emotional_state": "cautious"
}
```

### Watch Personality Evolution

**Check personality development:**
```bash
curl -X GET "http://localhost:8000/creatures/CREATURE_ID/personality/development"
```

**Example response:**
```json
{
  "development_analysis": {
    "total_personality_change": 0.18,
    "most_influenced_traits": [
      {"trait": "confidence", "change": 0.15},
      {"trait": "trust", "change": 0.12},
      {"trait": "sociability", "change": 0.08}
    ],
    "development_summary": "Developed stronger confidence and trust through positive interactions"
  },
  "evolution_enabled": true,
  "active_shifts": 3,
  "total_shifts": 12
}
```

### Monitor Learning Progress

**Check what your creature has learned:**
```bash
curl -X GET "http://localhost:8000/creatures/CREATURE_ID/learning"
```

**Example response:**
```json
{
  "learning_summary": {
    "total_learnings": 23,
    "learning_by_type": {
      "user_preference": 8,
      "behavioral_pattern": 7,
      "emotional_pattern": 5
    },
    "strongest_learnings": [
      {
        "description": "User enjoys playful interactions",
        "type": "user_preference",
        "strength": 0.89,
        "confidence": 0.85
      }
    ],
    "learning_statistics": {
      "average_confidence": 0.72,
      "learning_velocity": 0.15,
      "total_reinforcements": 89
    }
  }
}
```

---

## 🔧 Complete API Reference

### Enhanced Creature Creation

**Create creature with enhanced personality:**
```http
POST /creatures/enhanced
Content-Type: application/json

{
  "name": "My Creature",
  "template_id": "loyal_dog",
  "personality_mode": "complex",
  "complex_personality": {
    "mode": "archetype",
    "archetype_name": "leonardo",
    "trait_modifications": {
      "sociability": 0.8
    }
  }
}
```

### Personality Management

**Get personality information:**
```http
GET /creatures/{creature_id}/personality
```

**Get development analysis:**
```http
GET /creatures/{creature_id}/personality/development
```

**Control evolution:**
```http
POST /creatures/{creature_id}/personality/evolution/toggle?enable=true
POST /creatures/{creature_id}/personality/evolution/reset?keep_shifts=false
```

### Learning Management

**Get learning data:**
```http
GET /creatures/{creature_id}/learning
```

**Control learning:**
```http
POST /creatures/{creature_id}/learning/toggle?enable=true
POST /creatures/{creature_id}/learning/reset?keep_strong_learnings=true
```

### Personality System Endpoints

**List available archetypes:**
```http
GET /personality/archetypes
```

**List all 50 traits:**
```http
GET /personality/traits
```

**Create personality configurations:**
```http
POST /personality/simple
POST /personality/complex
```

### Enhanced Status Monitoring

**Get comprehensive creature status:**
```http
GET /creatures/{creature_id}/status
```

**Example enhanced status response:**
```json
{
  "creature_id": "abc123",
  "name": "Leonardo",
  "species": "dog",
  "stats": {"happiness": 85, "energy": 70},
  "personality": {
    "mode": "complex",
    "evolution_enabled": true,
    "active_shifts": 3,
    "total_shifts": 12,
    "current_emotional_state": "content",
    "development_analysis": {
      "total_personality_change": 0.18,
      "personality_stability": 0.82,
      "evolution_trajectory": "steady_evolution"
    }
  }
}
```

---

## 🐲 Creature Templates & Custom Creation

### Built-in Templates

**🏠 Companion Creatures:**
- **`loyal_dog`** - Faithful canine companion with hunger/energy needs
- **`independent_cat`** - Graceful feline with independent spirit
- **`ancient_dragon`** - Wise, territorial dragon with treasure satisfaction
- **`mystical_fairy`** - Magical forest dweller with nature connection

**🏰 Dungeon Exploration Specialists** *(Perfect for RPG games)*:
- **🧝‍♀️ `dungeon_elf_scout`** - Perceptive guide with stealth and ancient knowledge
- **🪓 `dungeon_dwarf_warrior`** - Fearless protector with stone expertise and battle courage
- **🔧 `dungeon_gnome_tinkerer`** - Brilliant inventor and puzzle-solving master
- **✨ `dungeon_sprite_guide`** - Magical being with dungeon secrets and mystical powers

### Custom Template Creation

**Web Interface Method:**
1. Click "Create Template" in the web interface
2. Fill out the intuitive form
3. Your template is instantly available!

**API Method:**
```http
POST /templates
Content-Type: application/json

{
  "name": "Cosmic Phoenix",
  "species": "phoenix",
  "description": "A stellar bird that burns with the fire of distant suns",
  "personality_traits": ["curious", "wise", "energetic"],
  "stat_configs": {
    "stellar_energy": {"min_value": 0, "max_value": 100, "default_start": 80},
    "cosmic_wisdom": {"min_value": 0, "max_value": 100, "default_start": 60}
  },
  "language_sounds": {
    "happy": ["*stellar song*", "*aurora flames*"],
    "powerful": ["*supernova cry*", "*solar flare*"]
  },
  "translation_conditions": {
    "cosmic_wisdom": "> 40",
    "stellar_energy": "> 30"
  }
}
```

---

## 🧬 The Science Behind Enhanced Personalities

### Psychological Foundation

CreatureMind's personality system is based on decades of psychological research:

**The Big Five Model (OCEAN)**
- Established in 1980s-1990s by researchers like Lewis Goldberg
- Scientifically validated across cultures and languages
- Foundation traits: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism

**Extended Trait Framework**
- 50 scientifically-grounded traits across 10 categories
- Based on contemporary personality psychology research
- Real correlations between traits and behaviors

### Mathematical Framework

**Trait Vector Mathematics:**
```
Personality Vector P = [t1, t2, t3, ..., t50] where ti ∈ [0,1]
Evolved Vector E = P + Σ(evolution_shifts) + emotional_influences
```

**Utility Computation:**
```
Action Utility U(a|P,x) = P^T * W_a * x + b_a

Where:
- P = personality trait vector
- W_a = weight matrix for action a  
- x = context vector
- b_a = bias term for action a
```

**Learning Adaptation:**
```
Confidence(t+1) = Confidence(t) + α * (outcome - expected)
Where α is the learning rate
```

---

## 🎯 Advanced Usage Examples

### Game Development Integration

**RPG Companion that evolves based on player choices:**
```javascript
class AdaptiveCompanion {
  async updateFromPlayerAction(action, outcome) {
    const interactionData = {
      type: action.type,
      emotional_impact: outcome.satisfaction,
      primary_emotion: outcome.emotion,
      context: { 
        location: action.location,
        difficulty: action.difficulty,
        success: outcome.success
      }
    };
    
    // Creature learns and evolves from this action
    await this.sendInteraction(interactionData);
  }
}
```

### Educational Application

**Tutoring companion that adapts to learning style:**
```javascript
class LearningCompanion {
  async adaptToStudentResponse(question, studentAnswer, isCorrect) {
    const interactionData = {
      type: 'learning_experience',
      emotional_impact: isCorrect ? 0.6 : -0.2,
      primary_emotion: isCorrect ? 'proud' : 'encouraging',
      context: {
        subject: question.subject,
        difficulty: question.level,
        learning_occurred: true,
        success: isCorrect
      }
    };
    
    // Companion becomes more encouraging or challenging
    await this.updatePersonality(interactionData);
  }
}
```

### Business Applications

**Customer service bot that adapts to customer personality:**
```javascript
const serviceBotData = {
  type: 'user_preference',
  emotional_impact: customerSatisfactionScore,
  context: {
    customer_type: detectCustomerPersonality(),
    issue_complexity: analyzeIssueComplexity(),
    interaction_history: getCustomerHistory()
  }
};
```

---

## 🏗️ Enhanced Architecture Overview

CreatureMind uses a **6-agent AI system** with advanced personality integration:

1. **Perception Agent** - Understands what you're saying and extracts emotional context
2. **Emotion Agent** - Determines creature's emotional state and influences
3. **Memory Agent** - Recalls relevant past interactions and learned patterns
4. **Personality Agent** - Applies 50-dimensional personality traits to decision making
5. **Decision Agent** - Decides how to respond using trait-driven utility computation
6. **Translator Agent** - Creates species language with personality-aware translation

### Enhanced Features per Creature:

**🧠 Personality System:**
- 50-dimensional trait vectors or simple 3-5 trait mode
- Famous personality archetypes or custom configurations
- Real-time personality evolution based on interactions

**💭 Emotional Intelligence:**
- Current emotional state tracking
- Emotional influences on trait expression
- Natural emotional decay and realistic patterns

**📚 Learning & Memory:**
- Persistent interaction memory
- Behavioral pattern learning
- User preference adaptation
- Long-term relationship building

**🗣️ Communication:**
- Species-specific language sounds
- Mood and personality-based translation
- Cultural variations and context awareness

---

## 🛠️ Troubleshooting

### Common Issues

**"Command not found" errors:**
- **Mac**: Make sure you installed Python with Homebrew
- **Windows**: Make sure you checked "Add Python to PATH" during installation

**"Permission denied" errors:**
- Try adding `python3` instead of `python`
- On Mac: `python3 -m api.server`

**API key errors:**
- Make sure your OpenAI API key starts with `sk-`
- Check that you set the environment variable correctly
- Try restarting your terminal after setting the key

**Port already in use:**
- Something else is using port 8000
- Change the port: `python -m api.server --port 8001`

**Personality system not working:**
- Check that numpy is installed: `pip install numpy`
- Verify API is running: `curl http://localhost:8000/health`
- Check creature has enhanced personality: `GET /creatures/{id}/personality`

### Getting Help

- Check the server logs in your terminal
- Try the basic test: `curl http://localhost:8000/health`
- Look at `examples/test_api.py` for working examples
- Visit the comprehensive guide: `ENHANCED_PERSONALITY_GUIDE.md`

---

## 🎯 Next Steps & Learning Path

### For Beginners:
1. Create your first creature with simple personality
2. Have conversations and watch emotional responses
3. Try different activities and see how personality affects reactions
4. Observe personality evolution over several interactions

### For Intermediate Users:
1. Experiment with personality archetypes (Leonardo, Einstein, etc.)
2. Create custom personality blends
3. Monitor learning progress and personality development
4. Try controlling evolution and learning settings

### For Advanced Users:
1. Create fully custom 50-dimensional personalities
2. Build applications using the enhanced API
3. Deploy with Docker in production environments
4. Integrate personality evolution into games or apps

### For Developers:
- **Complete API Documentation**: Visit `http://localhost:8000/docs`
- **Enhanced Personality Guide**: Read `ENHANCED_PERSONALITY_GUIDE.md`
- **Source Code**: Explore the `core/` directory
- **Integration Examples**: Check out `examples/` for patterns

---

## 🌟 Origins & Innovation

CreatureMind was born from **WiddlePupper**, an iOS virtual pet app that pioneered multi-agent creature consciousness. We've now evolved this into the world's most sophisticated AI personality system.

### What Makes This Groundbreaking:

**🔬 Scientific Foundation**: Based on 50+ years of personality psychology research
**🧬 Dynamic Evolution**: First AI system where personalities truly change over time  
**📚 Persistent Learning**: Creatures build lasting relationships through memory and adaptation
**💡 Practical Applications**: Ready for games, education, therapy, customer service, and more
**🛠️ Developer-Friendly**: Complete API access with comprehensive documentation

The magic isn't just in the complexity - it's in how all these systems work together to create authentic, believable characters that feel genuinely alive and develop unique relationships with each user.

---

## 📜 License

MIT License - Use CreatureMind in your projects, commercial or personal!

---

## 🎉 Ready to Create Truly Alive AI Companions?

**Your evolving creature is waiting to meet you!**

1. Follow the setup steps above
2. Create your first enhanced creature
3. Watch them develop their unique personality
4. Experience the future of AI companions

*The journey of a thousand conversations begins with a single "hello" - but with CreatureMind, every conversation changes who your creature becomes...* 🧠✨

---

## 📋 Quick Start Checklist

### Basic Setup (10 minutes)
- [ ] Install Python 3.11+ and get OpenAI API key
- [ ] Download CreatureMind and run `pip install -r requirements.txt`
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Start server with `python -m api.server`
- [ ] Visit `http://localhost:8000` to create your first creature

### Enhanced Personality Features (20 minutes)  
- [ ] Create creature with complex personality using an archetype
- [ ] Send several different types of messages (happy, sad, excited)
- [ ] Check personality development: `GET /creatures/{id}/personality/development`
- [ ] Monitor learning progress: `GET /creatures/{id}/learning`
- [ ] Observe how emotional state affects responses

### Advanced Features (30 minutes)
- [ ] Create custom personality with trait sliders
- [ ] Create personality blend combining multiple archetypes
- [ ] Experiment with evolution controls (enable/disable/reset)
- [ ] Test learning controls and pattern recognition
- [ ] Build simple application using the enhanced API

**Welcome to the future of AI personalities. Welcome to CreatureMind.** 🧠🚀