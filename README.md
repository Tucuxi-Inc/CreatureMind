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

**For Linux users:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip git

# CentOS/RHEL
sudo yum install python3 python3-pip git
```

### Step 2: Get Your OpenAI API Key (Optional but Recommended)

**🆓 CreatureMind works without an API key** using intelligent mock responses, but real OpenAI gives much better results.

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to "API Keys" in your account
4. Create a new key (it starts with `sk-`)
5. **Keep this safe** - you can set it later via the web interface!

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
INFO: Uvicorn running on http://0.0.0.0:8000
```

**🎉 Success! CreatureMind is now running!**

### Step 6: Set Your API Key & Create Your First Creature

1. **Open your browser** and go to: `http://localhost:8000`
2. **Set your API key** (recommended):
   - Click the "🔑 API Key" button in the top navigation
   - Enter your OpenAI API key (starts with `sk-`)
   - Click "Save Key" - changes take effect immediately!
3. **Create your first creature**:
   - Click "Create Your First Creature"
   - Choose a creature type or create a custom template
   - Give it a name and personality
   - Click "Bring to Life"

**What's the difference between API modes?**
- **Without API Key**: Free, intelligent mock responses (great for testing)
- **With API Key**: Real OpenAI responses (~$0.01-0.05 per conversation, much more lifelike)

---

## 🐕 Available Creature Species

### 🏠 **Companion Creatures**
- **🐕 Dogs**: Loyal, playful, energetic companions with tail wagging and barking
- **🐱 Cats**: Independent, graceful felines with purring and elegant movements  
- **🐲 Dragons**: Wise, ancient beings with wing flutters and majestic roars
- **🧚 Fairies**: Delicate magical creatures with sparkling and ethereal chimes
- **👤 Humans**: Natural human companions with speech, gestures, and expressions

### 🏰 **Fantasy Adventures** *(Perfect for RPG games)*
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

## 🎮 Interacting with Your Creatures

### Basic Activities
All creatures support these standard activities through the web interface:

- **🍽️ Feed**: Satisfies hunger and increases happiness
- **🎾 Play**: Boosts happiness but uses energy  
- **❤️ Pet**: Shows affection and builds social connection
- **🚶 Walk**: Increases energy and provides stimulation

### Conversation System
- **Natural chat**: Talk to your creature in plain English
- **Species responses**: Get authentic creature language back
- **Mood-based translation**: Translation available when creature trusts you
- **Memory building**: Creatures remember your conversations

### Advanced Features
- **Personality evolution**: Watch traits change based on interactions
- **Learning system**: Creatures adapt to your preferences
- **Emotional states**: Real-time mood changes affect behavior
- **Custom templates**: Create your own creature types

---

## 🧬 Creating Custom Creatures

### Web Interface Method (Recommended)
1. Click "Create Template" in the web interface
2. Fill out the intuitive form:
   - **Species name** (e.g., "phoenix", "robot", "alien")
   - **Personality traits** and temperament
   - **Stats configuration** (happiness, energy, etc.)
   - **Language sounds** for different emotions
   - **Available activities** and their effects
3. Your template is instantly available for creature creation!

### Example Custom Template
```json
{
  "name": "Cosmic Phoenix",
  "species": "phoenix",
  "description": "A stellar bird that burns with the fire of distant suns",
  "activities": [
    {
      "name": "soar",
      "stat_effects": {"energy": 15, "happiness": 10},
      "description": "Soar through cosmic winds"
    }
  ],
  "language": {
    "sounds": {
      "happy": ["*stellar song*", "*aurora flames*"],
      "excited": ["*supernova cry*", "*solar flare*"]
    }
  }
}
```

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
  "archetype_weights": {
    "leonardo": 0.7,
    "einstein": 0.3
  },
  "trait_modifications": {
    "sociability": 0.8
  }
}
```

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

### Common Usage Issues

**Activities showing mock responses:**
- Make sure you set your API key via the web interface
- Create a new creature after setting the API key
- Check that your creature template includes the activity you're trying

**Translation not working:**
- Check creature's happiness and energy levels
- Try feeding, petting, or playing to improve stats
- Some species are more independent and translate less frequently

**Creatures showing wrong behaviors:**
- Make sure you're using the correct species template
- Human creatures should use human actions, not animal behaviors
- Create a fresh creature if switching between very different species

**Stats not updating:**
- Check the creature status page to verify stats are actually changing
- Web interface may have display lag - stats update on the server immediately
- Try refreshing the browser page

---

## 🐳 Docker Setup (Alternative Method)

### Quick Start with Docker Compose
```bash
git clone [repository-url] CreatureMind
cd CreatureMind
echo "OPENAI_API_KEY=your-api-key-here" > .env
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

## 🌐 API Reference

### Core Endpoints
- `POST /creatures/enhanced` - Create creature with personality system
- `POST /creatures/{id}/message` - Send message to creature
- `POST /creatures/{id}/activity` - Perform activity
- `GET /creatures/{id}/status` - Get creature status
- `GET /templates` - List available creature templates

### Personality System Endpoints
- `GET /personality/archetypes` - List famous personalities
- `GET /personality/traits` - List all 50 traits
- `POST /personality/simple` - Create simple personality
- `POST /personality/complex` - Create complex personality

### API Key Management
- `GET /api/status` - Check current API client status
- `POST /api/set_key` - Set OpenAI API key dynamically
- `POST /api/clear_key` - Revert to mock client

**Full API documentation available at:** `http://localhost:8000/docs`

---

## 🧪 Testing Your Setup

### Basic Functionality Test
```bash
# Test health endpoint
curl http://localhost:8000/health

# Create a test creature
curl -X POST "http://localhost:8000/creatures" \
  -H "Content-Type: application/json" \
  -d '{"name": "TestBuddy", "template_id": "loyal_dog"}'

# Send a test message
curl -X POST "http://localhost:8000/creatures/{creature_id}/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Personality System Test
```bash
# Create creature with Einstein personality
curl -X POST "http://localhost:8000/creatures/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Einstein",
    "template_id": "basic_human",
    "personality_mode": "complex",
    "complex_personality": {
      "mode": "archetype",
      "archetype_name": "einstein"
    }
  }'
```

---

## 📋 Recent Updates & Bug Fixes

### Version 1.4.0 (Latest) - Complete Species Support & Human Templates

#### 🎭 Universal Species Support
- **Added complete human template**: Full support for human characters with appropriate behaviors
- **Enhanced MockAIClient**: Now supports all species (human, elf, dwarf, gnome, sprite) 
- **Species-specific behaviors**: Each species uses authentic actions and sounds
- **Fixed animal behavior leakage**: Humans no longer show tail wagging or purring

#### 🔧 Critical Bug Fixes  
- **Fixed activity translation failures**: Added missing activities (pet, play, walk, feed) to human template
- **Fixed emoji mapping**: "Joyful" mood now shows 😄 instead of 😐
- **Enhanced translator agent**: Species-specific behavioral guidelines prevent cross-species contamination
- **Improved error messages**: Clear debugging information for missing activities

#### 🎯 User Experience Improvements
- **Strengthened AI safety**: Excellent handling of inappropriate requests with engaging but appropriate deflection
- **Better activity descriptions**: Human-friendly activity names and descriptions
- **Enhanced system prompts**: Explicit species behavior guidelines for consistent AI responses
- **Comprehensive template system**: All web interface activities supported for all species

#### 🧬 Technical Enhancements  
- **Enhanced MockAIClient species support**: 9 total species with authentic behavioral patterns
- **Improved translator prompts**: Species-specific examples and explicit behavior restrictions
- **Template persistence**: Human template now persists across server restarts
- **Better error handling**: Clear error messages for debugging activity and template issues

### Version 1.3.0 - Memory Integration & Frontend Stability

#### 🧠 Enhanced Memory & Context System
- **Long-term Memory Integration**: Creatures maintain conversation context across multiple interactions
- **Chat History Awareness**: All AI agents consider recent conversation history for coherent responses
- **Context-Aware Responses**: Memory agent analyzes both stored memories and chat history

#### 🔧 Critical Frontend Fixes
- **Fixed Web Interface Regression**: Resolved stats updates and activity translation display issues
- **Restored Activity Translations**: All activities properly display creature responses
- **Visual Stats Updates**: Fixed stat display to update correctly after interactions

### Version 1.2.0 - AI System Improvements

#### 🤖 Modern AI Integration
- **Upgraded to gpt-4.1-nano**: 90% cost reduction while maintaining response quality
- **Real OpenAI Integration**: Fixed mock client fallback system
- **Enhanced Mock Responses**: Improved fallback responses for testing without API key

### Version 1.1.0 - Production Stability

#### 🛠️ Critical Bug Fixes  
- **Fixed Pydantic Forward Reference Errors**: Resolved 500 errors during creature creation
- **Fixed Activity Stat Updates**: Activities now properly modify creature stats
- **Much More Communicative Creatures**: Relaxed translation requirements for better UX

#### 💡 Translation System Overhaul
- **User-Friendly Translation Rules**: Creatures communicate unless severely distressed
- **Helpful Translation Hints**: Specific guidance when translation unavailable
- **Better Emotional Context**: Mood-appropriate responses and state tracking

---

## 💰 Cost Information

### API Usage Costs (with OpenAI)
- **Conversations**: ~$0.01-0.05 per conversation
- **Activities**: ~$0.005-0.02 per activity  
- **gpt-4.1-nano model**: 90% cheaper than previous versions
- **Estimated monthly**: $1-10 for regular use

### Free Usage (without API)
- **Unlimited mock interactions**
- **All personality features**
- **Full template system**
- **Species-appropriate responses**

---

## 🎯 Next Steps & Learning Path

### For Beginners:
1. ✅ **Complete setup** following this guide
2. 🎮 **Create your first creature** with simple personality  
3. 💬 **Have conversations** and try activities
4. 🧬 **Watch personality evolution** over time

### For Intermediate Users:
1. 🎭 **Try personality archetypes** (Einstein, Leonardo, etc.)
2. 🔧 **Create custom creature templates**  
3. 📊 **Monitor learning and evolution systems**
4. 🎛️ **Experiment with complex personalities**

### For Advanced Users:
1. 🧠 **Build 50-dimensional personalities**
2. 🔌 **Integrate with external applications**
3. 🐳 **Deploy with Docker in production**
4. 🎮 **Create game integrations**

### For Developers:
- **Complete API Documentation**: `http://localhost:8000/docs`
- **Source Code**: Explore the `core/` directory
- **Integration Examples**: Check `examples/` for patterns
- **Custom Templates**: Build your own creature types

---

## 🌟 Origins & Innovation

CreatureMind evolved from **WiddlePupper**, an iOS virtual pet app that pioneered multi-agent creature consciousness. We've transformed this into the world's most sophisticated AI personality system.

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

1. ✅ **Follow the setup steps above**
2. 🎭 **Create your first enhanced creature**  
3. 🧬 **Watch them develop their unique personality**
4. 🚀 **Experience the future of AI companions**

*The journey of a thousand conversations begins with a single "hello" - but with CreatureMind, every conversation changes who your creature becomes...* 🧠✨

---

## 🆘 Getting Help

- **Documentation Issues**: Check the troubleshooting section above
- **API Problems**: Visit `http://localhost:8000/docs` for detailed API info
- **Installation Help**: Try the alternative commands provided for your system
- **Feature Questions**: Explore the `examples/` directory for working code

**Remember**: Most issues can be solved by trying `python3` instead of `python`, or creating a fresh creature after setting your API key!

---

## 📋 Quick Start Checklist

### Basic Setup (10 minutes)
- [ ] Install Python 3.11+ 
- [ ] Download CreatureMind and run `pip install -r requirements.txt`
- [ ] Start server with `python -m api.server` (or `python3 -m api.server`)
- [ ] Visit `http://localhost:8000` 
- [ ] Set API key via web interface (optional)
- [ ] Create your first creature

### Test Everything Works (5 minutes)
- [ ] Send a message to your creature
- [ ] Try all activities (feed, pet, play, walk)
- [ ] Check that stats update correctly
- [ ] Verify creature shows species-appropriate behaviors

### Advanced Features (20 minutes)
- [ ] Create creature with complex personality (try Einstein archetype)
- [ ] Monitor personality development and learning progress  
- [ ] Create a custom creature template
- [ ] Test different species and their unique behaviors

**Welcome to the future of AI personalities. Welcome to CreatureMind.** 🧠🚀