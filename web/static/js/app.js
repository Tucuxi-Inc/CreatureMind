// CreatureMind Web Interface JavaScript

class CreatureMindApp {
    constructor() {
        this.currentCreature = null;
        this.apiBase = '';
        this.templates = [];
        this.messageHistory = [];
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadTemplates();
        this.showWelcomeScreen();
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('getStartedBtn').addEventListener('click', () => this.showCreationForm());
        document.getElementById('newCreatureBtn').addEventListener('click', () => this.showCreationForm());
        document.getElementById('cancelCreation').addEventListener('click', () => this.showWelcomeScreen());

        // Form submission
        document.getElementById('creatureForm').addEventListener('submit', (e) => this.handleCreatureCreation(e));

        // Chat
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        document.getElementById('sendButton').addEventListener('click', () => this.sendMessage());

        // Activity buttons
        document.querySelectorAll('.activity-btn').forEach(btn => {
            btn.addEventListener('click', () => this.performActivity(btn.dataset.activity));
        });

        // Error modal
        document.getElementById('closeError').addEventListener('click', () => this.hideError());
        document.getElementById('errorOkBtn').addEventListener('click', () => this.hideError());
    }

    async loadTemplates() {
        try {
            const response = await fetch('/templates');
            const data = await response.json();
            this.templates = data.templates;
            this.populateTemplateSelector();
        } catch (error) {
            console.error('Failed to load templates:', error);
            this.showError('Failed to load creature templates. Please refresh the page.');
        }
    }

    populateTemplateSelector() {
        const select = document.getElementById('creatureTemplate');
        select.innerHTML = '<option value="">Choose a creature type...</option>';
        
        this.templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = `${template.name} (${template.species})`;
            select.appendChild(option);
        });

        // Add change listener to update personality traits
        select.addEventListener('change', () => this.updatePersonalityTraits());
    }

    updatePersonalityTraits() {
        const selectedTemplate = document.getElementById('creatureTemplate').value;
        const traitOptions = document.getElementById('traitOptions');
        
        traitOptions.innerHTML = '';

        if (selectedTemplate) {
            const template = this.templates.find(t => t.id === selectedTemplate);
            if (template && template.description) {
                // Create personality trait options based on template
                const commonTraits = [
                    'loyal', 'playful', 'energetic', 'calm', 'friendly', 'protective',
                    'curious', 'intelligent', 'affectionate', 'independent', 'social',
                    'brave', 'gentle', 'mischievous', 'wise', 'patient'
                ];

                commonTraits.forEach(trait => {
                    const traitTag = document.createElement('div');
                    traitTag.className = 'trait-tag';
                    traitTag.textContent = trait;
                    traitTag.addEventListener('click', () => this.toggleTrait(traitTag));
                    traitOptions.appendChild(traitTag);
                });
            }
        }
    }

    toggleTrait(traitElement) {
        traitElement.classList.toggle('selected');
    }

    getSelectedTraits() {
        const selectedTraits = [];
        document.querySelectorAll('.trait-tag.selected').forEach(tag => {
            selectedTraits.push(tag.textContent);
        });
        return selectedTraits;
    }

    async handleCreatureCreation(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const creatureData = {
            name: formData.get('name'),
            template_id: formData.get('template_id'),
            personality_traits: this.getSelectedTraits(),
            custom_personality: formData.get('custom_personality')
        };

        this.showLoading('Creating your creature...');

        try {
            const response = await fetch('/creatures', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(creatureData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const creature = await response.json();
            this.currentCreature = creature;
            
            this.hideLoading();
            this.showCreatureInterface();
            this.updateCreatureDisplay();
            
            // Send welcome message
            this.addMessage('system', `🎉 ${creature.name} has come to life! Say hello to your new companion.`);
            
        } catch (error) {
            this.hideLoading();
            console.error('Failed to create creature:', error);
            this.showError('Failed to create your creature. Please try again.');
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || !this.currentCreature) return;

        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';

        // Show typing indicator
        this.addMessage('creature', '...', 'typing');

        try {
            const response = await fetch(`/creatures/${this.currentCreature.creature_id}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add creature response
            this.addCreatureMessage(data);
            
            // Update stats if they changed
            if (data.stats_delta && Object.keys(data.stats_delta).length > 0) {
                await this.updateCreatureStats();
            }

        } catch (error) {
            this.removeTypingIndicator();
            console.error('Failed to send message:', error);
            this.addMessage('system', '❌ Failed to send message. Please try again.');
        }
    }

    async performActivity(activity) {
        if (!this.currentCreature) return;

        this.addMessage('activity', `🎮 Performing activity: ${activity}`);

        try {
            const response = await fetch(`/creatures/${this.currentCreature.creature_id}/activity`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ activity })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Add creature response to activity
            this.addCreatureMessage(data);
            
            // Update stats
            if (data.stats_delta && Object.keys(data.stats_delta).length > 0) {
                await this.updateCreatureStats();
            }

        } catch (error) {
            console.error('Failed to perform activity:', error);
            this.addMessage('system', '❌ Failed to perform activity. Please try again.');
        }
    }

    addMessage(type, text, className = '') {
        const messagesContainer = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type} ${className}`.trim();
        
        if (type === 'user') {
            messageElement.textContent = text;
        } else if (type === 'system' || type === 'activity') {
            messageElement.textContent = text;
        } else {
            messageElement.innerHTML = text;
        }
        
        messageElement.classList.add('fade-in');
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addCreatureMessage(data) {
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message creature fade-in';
        
        // Creature language (always shown)
        const creatureLanguage = document.createElement('div');
        creatureLanguage.className = 'creature-language';
        creatureLanguage.textContent = data.creature_language;
        messageContainer.appendChild(creatureLanguage);
        
        // Human translation (if available)
        if (data.can_translate && data.human_translation) {
            const translation = document.createElement('div');
            translation.className = 'translation';
            translation.textContent = `💭 ${data.human_translation}`;
            messageContainer.appendChild(translation);
        } else if (!data.can_translate) {
            const unavailable = document.createElement('div');
            unavailable.className = 'translation';
            unavailable.textContent = '🔒 Translation not available (creature needs to trust you more)';
            messageContainer.appendChild(unavailable);
        }
        
        // Emotion indicator
        if (data.emotional_state) {
            const emotion = document.createElement('div');
            emotion.className = 'emotion-indicator';
            emotion.textContent = `😊 Feeling: ${data.emotional_state}`;
            messageContainer.appendChild(emotion);
        }
        
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.appendChild(messageContainer);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Update translation status
        this.updateTranslationStatus(data.can_translate);
    }

    removeTypingIndicator() {
        const typingIndicator = document.querySelector('.message.typing');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    updateTranslationStatus(canTranslate) {
        const status = document.getElementById('translationStatus');
        const icon = status.querySelector('i');
        const text = status.querySelector('span');
        
        if (canTranslate) {
            status.className = 'translation-status available';
            icon.className = 'fas fa-language';
            text.textContent = 'Translation Available';
        } else {
            status.className = 'translation-status unavailable';
            icon.className = 'fas fa-lock';
            text.textContent = 'Translation Locked';
        }
    }

    async updateCreatureStats() {
        try {
            const response = await fetch(`/creatures/${this.currentCreature.creature_id}/status`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            
            const status = await response.json();
            this.updateStatsDisplay(status.stats);
            this.updateMoodDisplay(status.mood);
            
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    updateCreatureDisplay() {
        if (!this.currentCreature) return;

        document.getElementById('creature-name-text').textContent = this.currentCreature.name;
        document.getElementById('creature-species').textContent = this.currentCreature.species;
        
        // Set creature emoji based on species
        const emoji = this.getCreatureEmoji(this.currentCreature.species);
        document.getElementById('creature-emoji').textContent = emoji;
        
        // Update stats
        this.updateStatsDisplay(this.currentCreature.stats);
    }

    getCreatureEmoji(species) {
        const emojiMap = {
            'dog': '🐕',
            'cat': '🐱',
            'dragon': '🐉',
            'fairy': '🧚',
            'bird': '🐦',
            'rabbit': '🐰',
            'fox': '🦊'
        };
        return emojiMap[species] || '🐾';
    }

    updateStatsDisplay(stats) {
        Object.entries(stats).forEach(([statName, value]) => {
            const statElement = document.getElementById(`stat-${statName}`);
            if (statElement) {
                const fill = statElement.querySelector('.stat-fill');
                const valueElement = statElement.querySelector('.stat-value');
                
                if (fill) fill.style.width = `${value}%`;
                if (valueElement) valueElement.textContent = Math.round(value);
                
                // Update color based on value
                if (fill) {
                    if (value < 30) {
                        fill.style.background = '#ef4444';
                    } else if (value < 60) {
                        fill.style.background = '#f59e0b';
                    } else {
                        fill.style.background = 'linear-gradient(90deg, #10b981, #6366f1)';
                    }
                }
            }
        });
    }

    updateMoodDisplay(mood) {
        const moodText = document.getElementById('mood-text');
        const moodEmoji = document.getElementById('mood-emoji');
        
        if (moodText) moodText.textContent = mood;
        
        if (moodEmoji) {
            const moodEmojiMap = {
                'happy': '😊',
                'excited': '🤩',
                'sad': '😢',
                'tired': '😴',
                'angry': '😠',
                'curious': '🤔',
                'content': '😌',
                'playful': '😄',
                'hungry': '🤤',
                'neutral': '😐'
            };
            moodEmoji.textContent = moodEmojiMap[mood] || '😐';
        }
    }

    showWelcomeScreen() {
        this.hideAllScreens();
        document.getElementById('welcomeScreen').classList.remove('hidden');
    }

    showCreationForm() {
        this.hideAllScreens();
        document.getElementById('creationForm').classList.remove('hidden');
        document.getElementById('creatureName').focus();
    }

    showCreatureInterface() {
        this.hideAllScreens();
        document.getElementById('creatureInterface').classList.remove('hidden');
        document.getElementById('messageInput').focus();
    }

    hideAllScreens() {
        document.getElementById('welcomeScreen').classList.add('hidden');
        document.getElementById('creationForm').classList.add('hidden');
        document.getElementById('creatureInterface').classList.add('hidden');
    }

    showLoading(text = 'Loading...') {
        document.getElementById('loadingText').textContent = text;
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorModal').classList.remove('hidden');
    }

    hideError() {
        document.getElementById('errorModal').classList.add('hidden');
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CreatureMindApp();
});

// Add some utility functions for better UX
function formatTime(date) {
    return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}