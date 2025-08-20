# CreatureMind 🧠

**The most advanced AI companion system with FREE local AI inference and developer-friendly API controls.**

Transform any idea into a living, breathing digital creature with authentic personality, emotions, and their own unique "language" that only translates when they're in the right mood. Each creature develops a unique relationship with you through natural conversation.

## 🆕 **REVOLUTIONARY: 100% Local AI + Developer Control**
**The world's first local AI creature system with complete developer control!** No API keys required - your creatures run completely on your computer with fast, private responses. Plus a comprehensive API for external applications to control every aspect of creature behavior.

### 🌟 **What Makes This Special?**

| Traditional AI Chatbots | CreatureMind |
|------------------------|-------------|
| Requires expensive APIs | **FREE Local AI inference** |
| Generic responses | **Species-specific authentic behavior** |
| No memory | **Persistent conversation memory** |
| Human-like only | **Any creature type imaginable** |
| Static personalities | **Evolving personality traits** |
| Cloud-dependent | **Runs completely offline** |
| No developer control | **Complete API control over stats & behavior** |

---

## 🎯 What is CreatureMind?

CreatureMind creates **AI creature minds** with unprecedented authenticity. Each creature:

- **🏠 100% Local & Free**: Runs completely on your computer with no API costs
- **⚡ Multiple AI Models**: Choose from fast (Gemma-3-270M) to intelligent (GPT-OSS-20B, Qwen3-0.6B)
- **🎭 Species-Specific Intelligence**: Dogs bark and wag tails, cats purr and act aloof, dragons roar majestically
- **💭 Emotional Intelligence**: Real-time emotional states that influence behavior  
- **🗣️ Authentic Communication**: Each species speaks in their own "language" with mood-based translation
- **🧠 Persistent Memory**: Remembers all interactions and builds relationships over time
- **🔧 Developer API**: Complete programmatic control over stats, thresholds, and behavior
- **🔒 Privacy First**: All AI processing happens locally - conversations stay private

**Think sophisticated virtual pets meets psychology research, powered by FREE local AI - for ANY creature you can imagine!**

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

**For Linux users:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip git

# CentOS/RHEL
sudo yum install python3 python3-pip git
```

### Step 2: Download CreatureMind

**Option A: Download ZIP (Easiest)**
1. Download the CreatureMind folder from the repository
2. Extract it somewhere easy to find (like your Desktop)

**Option B: Use Git (Recommended)**
```bash
git clone [repository-url] CreatureMind
cd CreatureMind
```

### Step 3: Set Up CreatureMind

1. **Open Terminal/Command Prompt** in the CreatureMind folder:
   - **Mac**: Right-click the CreatureMind folder → "New Terminal at Folder"
   - **Windows**: Shift+Right-click in the folder → "Open PowerShell window here"
   - **Linux**: Right-click → "Open Terminal Here"

2. **Install CreatureMind dependencies**:
   ```bash
   # Most systems:
   pip install -r requirements.txt
   
   # If above doesn't work, try:
   pip3 install -r requirements.txt
   
   # Or on some Linux systems:
   python3 -m pip install -r requirements.txt
   ```

### Step 4: Download AI Models (First Time Only)

CreatureMind needs AI model files to work. You'll need to download them separately:

1. **Create the models directory**:
   ```bash
   mkdir -p localai/models
   ```

2. **Download models** (choose one or more):
   
   **Fast & Lightweight (Recommended for most users):**
   - **Gemma-3-270M**: `gemma-3-270m-it-F16.gguf` (~540MB)
   - **Qwen3-0.6B**: `qwen3-0.6b-instruct-q4_k_m.gguf` (~400MB)
   
   **More Intelligent (Requires more RAM):**
   - **GPT-OSS-20B**: `gpt-oss-20b-Q4_0.gguf` (~12GB)
   
   Download from [Hugging Face](https://huggingface.co) or other GGUF model repositories and place in `localai/models/`

3. **Verify setup**:
   ```bash
   # Check that you have at least one model file:
   ls localai/models/
   # Should show your .gguf files
   ```

### Step 5: Start CreatureMind! 🎉

```bash
# Most systems (including Mac/Linux):
python -m api.server

# If above doesn't work, try:
python3 -m api.server

# Alternative method:
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

You should see:
```
🧠 Using LocalAI only for fast, free inference with Gemma-3-270M
🚀 Starting Local AI server...
   Model: gemma-3-270m-it-F16.gguf
   Family: gemma3
   Context: 32,768 tokens
   🔷 Gemma optimizations: Gemma chat template enabled
✅ Local AI server ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

**🎉 Success! CreatureMind is now running with Local AI!**

### Step 6: Create Your First Creature & Start Chatting!

1. **Open your browser** and go to: `http://localhost:8000`
2. **Create your first creature**:
   - Click "Create Your First Creature"
   - Choose a creature type (dog, cat, dragon, fairy, etc.)
   - Give it a name and personality
   - Click "Bring to Life"
3. **Start chatting immediately!**
   - Your creature will respond using Local AI
   - Each species has unique behaviors and sounds
   - Natural conversation with species-appropriate responses

---

## 🐕 Available Creature Species

### 🏠 **Companion Creatures**
- **🐕 Dogs**: Loyal, playful, energetic companions with tail wagging and barking
- **🐱 Cats**: Independent, graceful felines with purring and elegant movements  
- **👤 Humans**: Natural human companions with speech, gestures, and expressions

### 🏰 **Fantasy Adventures** *(Perfect for RPG games)*
- **🐲 Dragons**: Wise, ancient beings with wing flutters and majestic roars
- **🧚 Fairies**: Delicate magical creatures with sparkling and ethereal chimes
- **🧝‍♀️ Elves**: Graceful scouts with keen perception and melodic voices
- **🪓 Dwarves**: Sturdy warriors with hearty laughs and determined stances
- **🔧 Gnomes**: Brilliant tinkerers with curious muttering and inventive gestures
- **✨ Sprites**: Quick, mischievous beings with tiny voices and shimmering movements

Each species has:
- **Unique sounds** and vocalizations
- **Species-specific behaviors** and actions
- **Authentic movement** patterns
- **Cultural variations** and language sounds

---

## 🤖 AI Model System

### 🔄 **Multiple Model Support**
CreatureMind supports multiple Local AI models with seamless switching:

**🚀 Available Model Types:**
- **Gemma-3-270M** (Default) - Fast, lightweight responses (1-3 seconds, ~1GB RAM)
- **Gemma-3-270M-UD** - Ultra Dense variant for better quality responses
- **Qwen3-0.6B** - Alternative small model with 40K context window
- **GPT-OSS-20B** - Large, intelligent responses (20+ seconds, 8GB+ RAM)
- **Custom Models** - Add any compatible GGUF model to the models folder

**⚡ Web Interface Model Switching:**
1. Click the "🧠 AI Model" button in the web interface
2. Select from available models with performance information
3. Switch models instantly - server restarts automatically
4. Different models for different needs: speed vs. intelligence

**📁 Adding New Models:**
1. Download any compatible GGUF model file
2. Place in `localai/models/` directory  
3. Restart CreatureMind - new model appears in selection
4. Switch to new model via web interface

**🎯 Model Recommendations:**
- **270M/0.6B**: Great for quick interactions, basic conversations
- **20B+**: Better for complex personalities, nuanced responses, detailed dialogue
- **Custom**: Experiment with different model sizes and types

---

## 🗣️ Conversation System

### Natural Chat Experience
- **Species-Appropriate Responses**: Dogs bark and wag tails, cats purr and act aloof
- **Emotional Intelligence**: Creatures respond based on their current emotional state
- **Memory Persistence**: Creatures remember previous conversations and build relationships
- **Translation System**: Creatures speak in their "language" - translation available when they trust you

### How Translation Works
- **Happiness/Energy/Hunger at 50+**: Creature trusts you enough to translate
- **Below thresholds**: You get authentic creature sounds with "Translation not available"
- **Developer Control**: Adjust translation thresholds via API for your application's needs

### Example Conversations

**Dog (Happy):**
- *Action*: tail wagging enthusiastically, ears perked up
- *Sound*: excited bark  
- *Translation*: "Woof! I'm so happy to see you!"

**Cat (Content):**
- *Action*: slow blink, gentle purr, stretching paws
- *Sound*: content purr
- *Translation*: "I suppose you're acceptable company today."

**Dragon (Wise):**
- *Action*: majestic head raise, wings rustling softly
- *Sound*: low rumbling growl
- *Translation*: "Mortal, you seek wisdom. I shall consider your words."

---

## 🧬 Creating Custom Creatures

### Web Interface Method (Recommended)
1. Click "Create Template" in the web interface
2. Fill out the intuitive form:
   - **Species name** (e.g., "phoenix", "robot", "alien")
   - **Personality traits** and temperament
   - **Stats configuration** (happiness, energy, hunger)
   - **Language sounds** for different emotions
   - **Available activities** and their effects
3. Your template is instantly available for creature creation!

### Example Custom Template
```json
{
  \"name\": \"Cosmic Phoenix\",
  \"species\": \"phoenix\",
  \"description\": \"A stellar bird that burns with the fire of distant suns\",
  \"stat_configs\": {
    \"happiness\": {\"min_value\": 0, \"max_value\": 100, \"decay_rate\": 0, \"default_start\": 75},
    \"energy\": {\"min_value\": 0, \"max_value\": 100, \"decay_rate\": 0, \"default_start\": 75},
    \"hunger\": {\"min_value\": 0, \"max_value\": 100, \"decay_rate\": 0, \"default_start\": 75}
  },
  \"language\": {
    \"sounds\": {
      \"happy\": [\"*stellar song*\", \"*aurora flames*\"],
      \"excited\": [\"*supernova cry*\", \"*solar flare*\"]
    },
    \"translation_conditions\": {
      \"happiness\": \"> 50\",
      \"energy\": \"> 50\",
      \"hunger\": \"> 50\"
    }
  }
}
```

---

## 🔧 Developer API Reference

### 🎮 **Complete Programmatic Control**
CreatureMind provides a comprehensive API for developers to integrate creatures into their applications:

### Core Creature Management
```bash
# Create a new creature
POST /creatures/enhanced
{
  \"name\": \"Buddy\",
  \"template_id\": \"loyal_dog\",
  \"personality_mode\": \"simple\",
  \"personality_traits\": [\"loyal\", \"playful\", \"energetic\"]
}

# Send a message to your creature
POST /creatures/{creature_id}/message
{
  \"message\": \"How are you feeling today?\",
  \"context\": {\"environment\": \"park\", \"time\": \"morning\"}
}

# Get creature status
GET /creatures/{creature_id}/status
```

### 📊 **Stat Management APIs**

**Direct Stat Control:**
```bash
# Set specific stat values (0-100, automatically clamped)
POST /creatures/{creature_id}/stats
{
  \"stats\": {
    \"happiness\": 85,
    \"energy\": 60,
    \"hunger\": 90
  }
}
```

**Configuration Management:**
```bash
# Adjust decay rates and translation thresholds
POST /creatures/{creature_id}/config
{
  \"decay_rates\": {
    \"happiness\": 0.1,
    \"energy\": 0.2,
    \"hunger\": 0.15
  },
  \"thresholds\": {
    \"happiness\": 60,
    \"energy\": 50,
    \"hunger\": 40
  }
}
```

**Translation Threshold Control:**
```bash
# Adjust when translation becomes available
POST /creatures/{creature_id}/thresholds
{
  \"thresholds\": {
    \"happiness\": 30,
    \"energy\": 40,
    \"hunger\": 50
  }
}
```

### 🎮 **Usage Examples for Games & Apps**

**Feeding System:**
```bash
# Player feeds creature - increase hunger and happiness
curl -X POST \"/creatures/123/stats\" \\
  -d '{\"stats\": {\"hunger\": 95, \"happiness\": 80}}'
```

**Exercise/Battle System:**
```bash
# After battle - decrease energy, but increase happiness for victory
curl -X POST \"/creatures/123/stats\" \\
  -d '{\"stats\": {\"energy\": 40, \"happiness\": 90}}'
```

**Sleep/Rest System:**
```bash
# After rest - restore energy
curl -X POST \"/creatures/123/stats\" \\
  -d '{\"stats\": {\"energy\": 100}}'
```

**Dynamic Difficulty:**
```bash
# Make creature more/less talkative based on game state
curl -X POST \"/creatures/123/thresholds\" \\
  -d '{\"thresholds\": {\"happiness\": 20, \"energy\": 20, \"hunger\": 20}}'
```

### 📝 **API Response Format**
Every creature interaction returns:
```json
{
  \"creature_language\": \"*tail wagging* Woof!\",
  \"human_translation\": \"I'm so excited to see you!\",
  \"can_translate\": true,
  \"emotional_state\": \"excited\",
  \"stats_delta\": {\"happiness\": 0, \"energy\": 0, \"hunger\": 0},
  \"debug_info\": {
    \"decision\": {
      \"action\": \"tail wagging enthusiastically\",
      \"vocalization\": \"excited bark\",
      \"intention\": \"showing excitement and joy\",
      \"energy_level\": \"high\"
    },
    \"perception\": {\"user_intent\": \"greeting\", \"user_tone\": \"friendly\"},
    \"emotion\": {\"primary_emotion\": \"excited\", \"impact_score\": 0.8},
    \"memory\": {\"relevant_memories\": \"Previous positive interactions\"}
  }
}
```

**Developer Benefits:**
- **Complete Control**: Manage all aspects of creature behavior programmatically
- **Rich Debug Info**: Access to all AI agent outputs for analysis
- **Flexible Integration**: Use only the features you need
- **Real-time Updates**: Changes take effect immediately
- **No Surprises**: Stats only change when you explicitly modify them

---

## 🧠 Advanced Personality System

### Simple Mode (Beginner-Friendly)
- Choose 3-5 key traits like "playful", "loyal", "curious"
- Select base temperament (calm, energetic, gentle, bold)
- Add custom personality description

### Complex Mode (Advanced)
Choose from several configuration methods:

**🎓 Famous Personalities**
Start with scientifically-crafted personalities:
- **🎨 Leonardo da Vinci** - Creative genius (high creativity, curiosity)
- **🔬 Albert Einstein** - Analytical thinker (high systematic thinking)
- **👩‍🏫 Maria Montessori** - Nurturing educator (high empathy, patience)
- **🤔 Socrates** - Wise philosopher (high wisdom, humility)
- **🤗 Fred Rogers** - Gentle soul (high empathy, emotional stability)
- **👴 Yoda** - Ancient wisdom (high wisdom, mindfulness)

**🎛️ Custom 50-Dimensional Traits**
Fine-tune all 50 personality dimensions:
- **Core Traits**: Extraversion, agreeableness, conscientiousness
- **Emotional**: Optimism, emotional stability, empathy
- **Cognitive**: Intelligence, creativity, curiosity, wisdom
- **Social**: Sociability, trust, cooperation, leadership
- **Behavioral**: Energy, persistence, risk-taking, organization

**🎭 Personality Blending**
Combine multiple famous personalities:
```json
{
  \"archetype_weights\": {
    \"leonardo\": 0.7,
    \"einstein\": 0.3
  },
  \"trait_modifications\": {
    \"sociability\": 0.8
  }
}
```

### 🗣️ **Authentic Speech Styles**
Each famous personality speaks with their authentic voice patterns:

- **🎨 Leonardo da Vinci**: *"Fascinating! I observe that... Art is never finished, only abandoned."*
- **🔬 Einstein**: *"Let me think about this... Imagination is more important than knowledge."*  
- **👩‍🏫 Montessori**: *"How wonderful! Let us discover... Help me to do it myself."*
- **🤔 Socrates**: *"What is...? But consider... I know that I know nothing."*
- **🤗 Fred Rogers**: *"You are special just the way you are. How does that make you feel?"*
- **👴 Yoda**: *"Strong with the Force, you are. Much to learn, you have. Hmm."*

---

## 🔧 Troubleshooting

### Common Installation Issues

**"Command not found" errors:**
- **Mac**: Make sure you installed Python with Homebrew
- **Windows**: Make sure you checked "Add Python to PATH" during installation
- **All systems**: Try using `python3` instead of `python`

**"Permission denied" errors:**
```bash
# Try these alternatives in order:
python3 -m api.server
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000
sudo python3 -m api.server  # Last resort on Linux
```

**Package installation issues:**
```bash
# Try these alternatives:
pip3 install -r requirements.txt
python3 -m pip install -r requirements.txt
pip install --user -r requirements.txt
```

**Port already in use:**
```bash
# Use a different port:
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8001
# Then visit http://localhost:8001
```

**No AI models found:**
- Check that you have `.gguf` files in `localai/models/`
- Download at least one model (Gemma-3-270M recommended)
- Verify file permissions allow reading the model files

### Common Usage Issues

**Creatures giving repetitive responses:**
- Try switching to a larger AI model (GPT-OSS-20B)
- Smaller models (270M, 0.6B) may repeat responses with simple prompts
- Larger models provide more varied and intelligent responses

**Translation not working:**
- Check creature's happiness, energy, and hunger levels via `/status` endpoint
- Default threshold is 50 for all stats
- Use the API to adjust thresholds: `POST /creatures/{id}/thresholds`

**Stats not updating:**
- Stats are now controlled entirely via API - no automatic decay
- Use `POST /creatures/{id}/stats` to modify stats
- Check the creature status page to verify current stat values

**AI model switching issues:**
- Model switching restarts the server (takes 10-30 seconds)
- Make sure the new model file exists in `localai/models/`
- Check terminal output for model loading errors

---

## 🐳 Docker Setup (Alternative Method)

### Quick Start with Docker Compose
```bash
# Clone repository
git clone [repository-url] CreatureMind
cd CreatureMind

# Add your AI models to localai/models/ directory
# (Download GGUF files and place them there)

# Start with Local AI
docker-compose up -d
```

Visit `http://localhost:8000` - CreatureMind is now running in Docker!

### Docker Management
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart with updates
docker-compose down && docker-compose up -d
```

---

## 🧪 Testing Your Setup

### Basic Functionality Test
```bash
# Test health endpoint
curl http://localhost:8000/health

# Create a test creature (dog)
curl -X POST \"http://localhost:8000/creatures/enhanced\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"name\": \"TestBuddy\", \"template_id\": \"loyal_dog\"}'

# Send a test message (expect dog-like response with Local AI)
curl -X POST \"http://localhost:8000/creatures/{creature_id}/message\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"message\": \"Want to play fetch?\"}'

# Expected response: dog behaviors like tail wagging, excited bark, \"Woof!\"
```

### Developer API Test
```bash
# Test stat modification
curl -X POST \"http://localhost:8000/creatures/{creature_id}/stats\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"stats\": {\"happiness\": 95, \"energy\": 60, \"hunger\": 80}}'

# Test threshold adjustment  
curl -X POST \"http://localhost:8000/creatures/{creature_id}/thresholds\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"thresholds\": {\"happiness\": 30, \"energy\": 30, \"hunger\": 30}}'

# Verify changes
curl \"http://localhost:8000/creatures/{creature_id}/status\"
```

### Multi-Species Test
```bash
# Test different species get different responses
curl -X POST \"http://localhost:8000/creatures/enhanced\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"name\": \"Whiskers\", \"template_id\": \"independent_cat\"}'

# Cat should respond with purrs, slow blinks, aloof but affectionate behavior
curl -X POST \"http://localhost:8000/creatures/{cat_id}/message\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"message\": \"Here kitty, want treats?\"}'
```

---

## 💰 Cost Information

### Local AI (Default - FREE)
- **🆓 Completely Free**: No costs for any interactions
- **⚡ Unlimited conversations**: Chat as much as you want
- **🏠 Runs locally**: No data leaves your computer
- **🚀 Fast responses**: Optimized for your hardware
- **📱 One-time setup**: Download model files once

### Hardware Requirements
- **Minimum**: 4GB RAM, 2GB free disk space
- **Recommended**: 8GB RAM, 5GB free disk space
- **Optimal**: 16GB+ RAM for larger models

**Total cost: $0 forever!**

---

## 🎯 Next Steps & Learning Path

### For Beginners:
1. ✅ **Complete setup** following this guide
2. 🎮 **Create your first creature** with simple personality  
3. 💬 **Have conversations** and explore species differences
4. 🧬 **Watch how personalities affect responses**

### For Developers:
1. 🔌 **Explore the API** at `http://localhost:8000/docs`
2. 📊 **Test stat manipulation** endpoints
3. 🎛️ **Integrate with your application**
4. 🧠 **Experiment with different AI models**

### For Game Developers:
1. 🎮 **Plan creature integration** into game mechanics
2. 📊 **Map game events** to creature stat changes
3. 🗣️ **Design conversation systems** around creature responses
4. 🎭 **Create custom species** for your game world

### For Advanced Users:
1. 🧠 **Build custom AI models** and add to CreatureMind
2. 🔧 **Create complex creature templates**
3. 🐳 **Deploy with Docker** in production
4. 🌐 **Build web applications** around the API

---

## 🔌 Integration Examples

### Game Integration
```python
import requests

class CreatureCompanion:
    def __init__(self, creature_id):
        self.creature_id = creature_id
        self.base_url = \"http://localhost:8000\"
    
    def feed(self):
        # Player feeds creature
        response = requests.post(f\"{self.base_url}/creatures/{self.creature_id}/stats\", 
                               json={\"stats\": {\"hunger\": 95, \"happiness\": 85}})
        return response.json()
    
    def battle_result(self, won=True):
        # After battle - tired but happy if won
        happiness = 90 if won else 60
        response = requests.post(f\"{self.base_url}/creatures/{self.creature_id}/stats\",
                               json={\"stats\": {\"energy\": 40, \"happiness\": happiness}})
        return response.json()
    
    def chat(self, message):
        # Natural conversation
        response = requests.post(f\"{self.base_url}/creatures/{self.creature_id}/message\",
                               json={\"message\": message})
        return response.json()

# Usage
companion = CreatureCompanion(\"creature-123\")
companion.feed()
result = companion.chat(\"How do you feel after that meal?\")
print(result[\"human_translation\"])  # \"That was delicious! Thank you!\"
```

### Educational App Integration
```python
class StudyBuddy:
    def __init__(self, creature_id):
        self.creature_id = creature_id
        
    def study_session_complete(self, success_rate):
        # Adjust creature mood based on study performance
        happiness = 70 + (success_rate * 30)  # 70-100 based on 0-1 success rate
        energy = max(30, 75 - (success_rate * 20))  # More effort = less energy
        
        requests.post(f\"http://localhost:8000/creatures/{self.creature_id}/stats\",
                     json={\"stats\": {\"happiness\": happiness, \"energy\": energy}})
    
    def encourage_student(self):
        response = requests.post(f\"http://localhost:8000/creatures/{self.creature_id}/message\",
                               json={\"message\": \"How are you feeling about studying today?\"})
        return response.json()[\"human_translation\"]
```

---

## 🌟 What Makes CreatureMind Revolutionary

### 🔬 **Scientific Foundation**
Built on decades of personality psychology research with authentic behavioral modeling for each species.

### 🎮 **Developer-First Design**  
Complete API control means you can integrate creatures into ANY application - games, education, customer service, therapy apps, and more.

### 🏠 **Privacy & Control**
Your creatures and conversations stay on your computer. No cloud dependency, no data collection, no privacy concerns.

### 🆓 **Truly Free**
No hidden costs, no API fees, no subscriptions. Download once, use forever.

### 🧬 **Infinite Possibilities**
Create any creature type imaginable with custom templates, stats, behaviors, and personalities.

**The magic isn't just in the AI - it's in how CreatureMind gives you complete control to create authentic, believable characters that fit perfectly into YOUR vision.**

---

## 📜 License

MIT License - Use CreatureMind in your projects, commercial or personal!

---

## 🎉 Ready to Create Truly Alive AI Companions?

**Your creature is waiting to meet you!**

1. ✅ **Follow the setup steps above**
2. 🤖 **Download an AI model** (Gemma-3-270M recommended)
3. 🎭 **Create your first creature**  
4. 💬 **Start chatting and see the magic**
5. 🔧 **Explore the API** for your own applications

*Every creature is unique. Every conversation matters. Every interaction shapes who they become.* 🧠✨

---

## 🆘 Getting Help

- **Installation Issues**: Check the troubleshooting section above
- **API Documentation**: Visit `http://localhost:8000/docs` for detailed API info
- **Model Problems**: Ensure you have `.gguf` files in `localai/models/`
- **Feature Questions**: Explore the `examples/` directory for working code

**Remember**: Most issues can be solved by ensuring you have AI model files and trying `python3` instead of `python`!

---

## 📋 Quick Start Checklist

### Basic Setup (15 minutes)
- [ ] Install Python 3.11+ 
- [ ] Download CreatureMind and run `pip install -r requirements.txt`
- [ ] Download at least one AI model to `localai/models/`
- [ ] Start server with `python -m api.server` (or `python3 -m api.server`)
- [ ] Visit `http://localhost:8000` 
- [ ] Create your first creature

### Test Everything Works (5 minutes)
- [ ] Send a message to your creature
- [ ] Verify creature shows species-appropriate behaviors  
- [ ] Check translation works when creature is happy
- [ ] Test different species respond differently

### Developer Features (10 minutes)
- [ ] Explore API documentation at `http://localhost:8000/docs`
- [ ] Test stat modification endpoints
- [ ] Test threshold adjustment endpoints
- [ ] Try the debug_info in API responses

**Welcome to the future of AI companions. Welcome to CreatureMind.** 🧠🚀