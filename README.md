# CreatureMind 🧠

**A universal AI system for creating believable companion creatures, mythical beasts, and interactive characters.**

Transform any idea into a living, breathing digital creature with authentic personality, emotions, and their own unique "language" that only translates when they're in the right mood.

## 🆕 **NEW: Custom Creature Creator**
**Create any creature type through our intuitive web interface!** Design robots, dragons, aliens, spirits, or any being you can imagine with custom stats, sounds, and behaviors.

---

## 🎯 What is CreatureMind?

CreatureMind creates **AI creature minds** that feel real and alive. Each creature:
- Has its own personality, emotions, and memory
- Speaks in their natural "language" (barks, roars, chirps, beeps, magic sounds)  
- Only translates to human language when they trust you
- Remembers your interactions and builds relationships
- Responds differently based on their mood and needs

**Think Tamagotchi meets ChatGPT, but for ANY creature you can imagine - and now you can create your own species!**

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

## 🐕 Create Your First Creature

### Option 1: Use the Web Interface (Recommended) 
1. **Open your browser** and go to: `http://localhost:8000`
2. **Click "Create Your First Creature"**
3. **Fill out the form**:
   - Enter a name for your creature
   - Choose a creature type (like "Loyal Dog")
   - Pick personality traits (optional)
   - Add custom description (optional)
4. **Click "Bring to Life"** and start chatting!

**🎉 That's it! You now have a beautiful web interface to interact with your creature!**

### Option 2: Use Simple Commands

**Create a dog named "Buddy":**
```bash
curl -X POST "http://localhost:8000/creatures" \
  -H "Content-Type: application/json" \
  -d '{"name": "Buddy", "template_id": "loyal_dog"}'
```

This returns your creature's ID. Copy it!

**Talk to your creature:**
```bash
# Replace CREATURE_ID with the ID from above
curl -X POST "http://localhost:8000/creatures/CREATURE_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello there!"}'
```

**Example response:**
```json
{
  "creature_language": "*tail wagging* *gentle approach* *soft woof*",
  "human_translation": "I'm happy to see you!",
  "can_translate": true,
  "emotional_state": "happy"
}
```

### Option 3: Use the Test Script

```bash
python examples/test_api.py
```

This automatically creates a creature and has a conversation!

---

## 🐲 Create Any Creature Type You Can Imagine

### Built-in Templates:
- **`loyal_dog`** - Faithful canine companion with hunger/energy needs
- **`independent_cat`** - Graceful feline with independent spirit
- **`ancient_dragon`** - Wise, territorial dragon with treasure satisfaction
- **`mystical_fairy`** - Magical forest dweller with nature connection

### 🎨 **NEW: Web-Based Custom Template Creator**

**Create any creature type directly through the web interface!**

1. **Click "Create Template"** in the web interface
2. **Fill out the intuitive form:**
   - Species name and description
   - Custom personality traits
   - Unique stat system (happiness, magic_power, treasure_lust, etc.)
   - Creature language sounds for different emotions
   - Translation conditions (when they'll "talk" to humans)
3. **Your template is instantly available** for creature creation!

**Examples of creatures you can create:**
- 🤖 **Robot Companion** - With battery life and processing power stats
- 🦄 **Unicorn** - With purity and magic essence stats  
- 👻 **Ghost Pet** - With ectoplasm energy and haunting ability
- 🐉 **Baby Dragon** - With growth potential and fire breath stats
- 🌟 **Star Being** - With cosmic energy and telepathy power
- 🧚‍♀️ **Garden Sprite** - With nature bond and seasonal mood cycles

### Advanced Custom Creation (File-Based):

For developers who prefer code, you can still create JSON templates:

```json
{
  "id": "cosmic_phoenix",
  "name": "Cosmic Phoenix",
  "species": "phoenix",
  "description": "A stellar bird that burns with the fire of distant suns",
  "stat_configs": {
    "stellar_energy": {"min_value": 0, "max_value": 100, "default_start": 80},
    "rebirth_cycle": {"min_value": 0, "max_value": 100, "default_start": 90},
    "cosmic_wisdom": {"min_value": 0, "max_value": 100, "default_start": 60}
  },
  "language": {
    "sounds": {
      "happy": ["*stellar song*", "*aurora flames*", "*cosmic trill*"],
      "powerful": ["*supernova cry*", "*solar flare*", "*galaxy spin*"],
      "peaceful": ["*nebula whisper*", "*starlight shimmer*", "*gentle orbit*"]
    },
    "translation_conditions": {
      "cosmic_wisdom": "> 40",
      "stellar_energy": "> 30"
    }
  }
}
```

Put it in the `examples/` folder and restart CreatureMind!

---

## 🎮 What Can You Do?

### Core Interactions:
- **💬 Chat**: Send messages and get authentic creature responses
- **🎯 Activities**: Feed, pet, play, or do species-specific activities
- **📊 Monitor**: Check your creature's mood, stats, and emotional state
- **🎨 **Create**: Design your own creature types with the template builder

### 🆕 **Template Creation Features:**
- **🧬 Custom Species**: Create any creature from robots to mythical beings
- **📈 Unique Stats**: Design custom stat systems (magic_power, battery_life, etc.)
- **🗣️ Language Design**: Create species-specific sounds and communication patterns
- **🔀 Translation Rules**: Set conditions for when creatures will translate to human language
- **⚡ Instant Integration**: Templates immediately become available for creature creation

### Advanced AI Features:
- **🧠 Memory System**: Creatures remember your interactions and build relationships
- **🌍 Cultural Adaptation**: Creature sounds adapt to different languages and cultures  
- **💭 Mood-Based Translation**: Earn your creature's trust to unlock translations
- **📈 Personality Evolution**: Creatures change based on how you treat them
- **🎭 Authentic Responses**: Each species responds with unique behavioral patterns

### Example Interactions:

```bash
# Different ways to interact:
{"message": "Want to play?"}
{"message": "I'm sorry I haven't visited in a while"}
{"message": "Good dragon! You're so wise!"}
{"message": "What do you think about treasure?"}
```

Each creature responds differently based on:
- Their species and personality
- Current mood and energy
- Your relationship history
- Cultural context

---

## 🛠️ Troubleshooting

### "Command not found" errors:
- **Mac**: Make sure you installed Python with Homebrew
- **Windows**: Make sure you checked "Add Python to PATH" during installation

### "Permission denied" errors:
- Try adding `python3` instead of `python`
- On Mac: `python3 -m api.server`

### API key errors:
- Make sure your OpenAI API key starts with `sk-`
- Check that you set the environment variable correctly
- Try restarting your terminal after setting the key

### Port already in use:
- Something else is using port 8000
- Change the port: `python -m api.server --port 8001`

### Getting help:
- Check the server logs in your terminal
- Try the basic test: `curl http://localhost:8000/health`
- Look at `examples/test_api.py` for working examples

---

## 🎯 What's Next?

### For Beginners:
1. Create your first creature
2. Have a conversation
3. Try feeding or playing with them
4. Watch how their mood changes

### For Advanced Users:
1. Create custom creature templates
2. Build applications that use the API
3. Deploy with Docker
4. Integrate with games or apps

### For Developers:
- **API Documentation**: Visit `http://localhost:8000/docs`
- **Source Code**: Explore the `core/` directory
- **Examples**: Check out `examples/` for integration patterns

---

## 🏗️ Architecture Overview

CreatureMind uses a **5-agent AI system** working together:

1. **Perception Agent** - Understands what you're saying
2. **Emotion Agent** - Determines how the creature feels
3. **Memory Agent** - Recalls relevant past interactions  
4. **Decision Agent** - Decides how to respond
5. **Translator Agent** - Creates creature language + optional translation

Each creature type has its own:
- **Personality traits** and **behavior patterns**
- **Language sounds** and **cultural variations**  
- **Stats system** (happiness, energy, species-specific needs)
- **Translation rules** (when they'll "talk" to humans)

---

## 🌟 Origins & Inspiration

CreatureMind was born from **WiddlePupper**, an iOS virtual pet app that pioneered multi-agent creature consciousness. We extracted and generalized that breakthrough AI architecture to work with any creature type.

**The magic of WiddlePupper** - authentic, believable creature personalities - is now available as a universal platform for developers, creators, and anyone who wants their own AI companion.

---

## 📜 License

MIT License - Use CreatureMind in your projects, commercial or personal!

---

## 🎉 Ready to Begin?

**Your creature is waiting to meet you!**

1. Follow the setup steps above
2. Create your first creature  
3. Start building a relationship
4. Watch them come to life

*The journey of a thousand conversations begins with a single "hello"...* 🐾