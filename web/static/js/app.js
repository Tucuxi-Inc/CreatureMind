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
        document.getElementById('createTemplateBtn').addEventListener('click', () => this.showTemplateForm());
        document.getElementById('apiKeyBtn').addEventListener('click', () => this.showApiKeyModal());
        document.getElementById('cancelCreation').addEventListener('click', () => this.showWelcomeScreen());
        document.getElementById('cancelTemplate').addEventListener('click', () => this.showWelcomeScreen());

        // Form submission
        document.getElementById('creatureForm').addEventListener('submit', (e) => this.handleCreatureCreation(e));
        document.getElementById('customTemplateForm').addEventListener('submit', (e) => this.handleTemplateCreation(e));

        // Template builder event listeners
        document.getElementById('addTrait').addEventListener('click', () => this.addTraitInput());
        document.getElementById('addStat').addEventListener('click', () => this.addStatConfig());
        document.getElementById('addEmotion').addEventListener('click', () => this.addEmotionSound());
        document.getElementById('addCondition').addEventListener('click', () => this.addTranslationCondition());

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

        // API Key modal
        document.getElementById('closeApiKey').addEventListener('click', () => this.hideApiKeyModal());
        document.getElementById('toggleApiKeyVisibility').addEventListener('click', () => this.toggleApiKeyVisibility());
        document.getElementById('saveApiKey').addEventListener('click', () => this.saveApiKey());
        document.getElementById('clearApiKey').addEventListener('click', () => this.clearApiKey());

        // Enhanced personality system
        this.setupPersonalityEventListeners();
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

    // Note: handleCreatureCreation method moved to enhanced personality section

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

        // Add activity initiation message
        this.addMessage('activity', `🎮 ${activity.charAt(0).toUpperCase() + activity.slice(1)}ing your ${this.currentCreature.species}...`);

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
            
            // Update stats after activities - activities should always change stats
            await this.updateCreatureStats();

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
            // Use translation_hint if available, otherwise default message
            if (data.translation_hint) {
                unavailable.textContent = `💡 ${data.translation_hint}`;
            } else {
                unavailable.textContent = '🔒 Translation not available (creature needs to trust you more)';
            }
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
            
            // Update the stored creature data with fresh stats
            this.currentCreature.stats = status.stats;
            
            this.updateStatsDisplay(status.stats);
            this.updateMoodDisplay(status.mood);
            this.updateTranslationStatus(status.can_translate);
            
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
                
                if (fill) {
                    // Add animation class for visual feedback
                    fill.classList.add('stat-updating');
                    setTimeout(() => fill.classList.remove('stat-updating'), 500);
                    
                    fill.style.width = `${value}%`;
                }
                if (valueElement) {
                    // Show the change visually
                    const oldValue = parseInt(valueElement.textContent) || 0;
                    const newValue = Math.round(value);
                    valueElement.textContent = newValue;
                    
                    // Add visual indicator for changes
                    if (newValue !== oldValue) {
                        valueElement.classList.add('stat-changed');
                        setTimeout(() => valueElement.classList.remove('stat-changed'), 1000);
                    }
                }
                
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
                'joyful': '😄',
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
        document.getElementById('templateForm').classList.add('hidden');
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

    // Template Creation Methods
    showTemplateForm() {
        this.hideAllScreens();
        document.getElementById('templateForm').classList.remove('hidden');
        document.getElementById('templateName').focus();
        this.initializeTemplateForm();
    }

    initializeTemplateForm() {
        // Initialize with some default values
        this.updateConditionStatOptions();
    }

    addTraitInput() {
        const traitInputs = document.getElementById('traitInputs');
        const div = document.createElement('div');
        div.className = 'trait-input';
        div.innerHTML = `
            <input type="text" placeholder="e.g., brave, curious, magical" name="trait">
            <button type="button" class="remove-trait">×</button>
        `;
        traitInputs.appendChild(div);
        
        // Add remove event listener
        div.querySelector('.remove-trait').addEventListener('click', () => {
            div.remove();
        });
    }

    addStatConfig() {
        const statConfigs = document.getElementById('statConfigs');
        const div = document.createElement('div');
        div.className = 'stat-config';
        div.innerHTML = `
            <div class="stat-config-header">
                <input type="text" placeholder="Stat name (e.g., happiness)" name="stat_name" required>
                <button type="button" class="remove-stat">×</button>
            </div>
            <div class="stat-config-body">
                <div class="stat-inputs">
                    <label>Default Start:</label>
                    <input type="number" min="0" max="100" value="75" name="default_start">
                    <label>Max Value:</label>
                    <input type="number" min="1" value="100" name="max_value">
                    <label>Decay Rate:</label>
                    <input type="number" step="0.01" min="0" max="1" value="0.1" name="decay_rate">
                </div>
            </div>
        `;
        statConfigs.appendChild(div);
        
        // Add remove event listener
        div.querySelector('.remove-stat').addEventListener('click', () => {
            div.remove();
            this.updateConditionStatOptions();
        });

        // Add change listener to update translation conditions
        div.querySelector('input[name="stat_name"]').addEventListener('input', () => {
            this.updateConditionStatOptions();
        });
    }

    addEmotionSound() {
        const emotionSounds = document.getElementById('emotionSounds');
        const div = document.createElement('div');
        div.className = 'emotion-sound';
        div.innerHTML = `
            <div class="emotion-header">
                <input type="text" placeholder="Emotion (e.g., happy, sad)" name="emotion" required>
                <button type="button" class="remove-emotion">×</button>
            </div>
            <div class="sounds-list">
                <input type="text" placeholder="Sound 1 (e.g., *purr*)" name="sound">
                <input type="text" placeholder="Sound 2 (e.g., *content chirp*)" name="sound">
                <input type="text" placeholder="Sound 3 (e.g., *gentle nuzzle*)" name="sound">
            </div>
        `;
        emotionSounds.appendChild(div);
        
        // Add remove event listener
        div.querySelector('.remove-emotion').addEventListener('click', () => {
            div.remove();
        });
    }

    addTranslationCondition() {
        const translationConditions = document.getElementById('translationConditions');
        const div = document.createElement('div');
        div.className = 'translation-condition';
        div.innerHTML = `
            <select name="condition_stat" required>
                <option value="">Select stat...</option>
            </select>
            <select name="condition_operator" required>
                <option value="> ">Greater than</option>
                <option value="< ">Less than</option>
                <option value="= ">Equal to</option>
            </select>
            <input type="number" name="condition_value" placeholder="Value" required>
            <button type="button" class="remove-condition">×</button>
        `;
        translationConditions.appendChild(div);
        
        // Populate stat options
        this.populateConditionStatOptions(div.querySelector('select[name="condition_stat"]'));
        
        // Add remove event listener
        div.querySelector('.remove-condition').addEventListener('click', () => {
            div.remove();
        });
    }

    updateConditionStatOptions() {
        // Update all condition stat dropdowns
        document.querySelectorAll('select[name="condition_stat"]').forEach(select => {
            this.populateConditionStatOptions(select);
        });
    }

    populateConditionStatOptions(select) {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select stat...</option>';
        
        // Get all stat names
        document.querySelectorAll('input[name="stat_name"]').forEach(input => {
            if (input.value.trim()) {
                const option = document.createElement('option');
                option.value = input.value.trim();
                option.textContent = input.value.trim();
                select.appendChild(option);
            }
        });
        
        // Restore previous value if it still exists
        if (currentValue) {
            select.value = currentValue;
        }
    }

    async handleTemplateCreation(e) {
        e.preventDefault();
        
        this.showLoading('Creating custom template...');

        try {
            const templateData = this.collectTemplateData(e.target);
            
            const response = await fetch('/templates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(templateData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            this.hideLoading();
            
            // Reload templates to include the new one
            await this.loadTemplates();
            
            // Show success message and go back to welcome screen
            alert(`Template "${result.name}" created successfully! You can now use it to create creatures.`);
            this.showWelcomeScreen();
            
        } catch (error) {
            this.hideLoading();
            console.error('Template creation failed:', error);
            this.showError(`Failed to create template: ${error.message}`);
        }
    }

    collectTemplateData(form) {
        const formData = new FormData(form);
        
        // Collect basic info
        const templateData = {
            name: formData.get('name'),
            species: formData.get('species'),
            description: formData.get('description'),
            personality_traits: [],
            stat_configs: {},
            language_sounds: {},
            translation_conditions: {}
        };

        // Collect personality traits
        form.querySelectorAll('input[name="trait"]').forEach(input => {
            if (input.value.trim()) {
                templateData.personality_traits.push(input.value.trim());
            }
        });

        // Collect stat configurations
        form.querySelectorAll('.stat-config').forEach(statConfig => {
            const statName = statConfig.querySelector('input[name="stat_name"]').value.trim();
            if (statName) {
                templateData.stat_configs[statName] = {
                    min_value: 0,
                    max_value: parseInt(statConfig.querySelector('input[name="max_value"]').value) || 100,
                    decay_rate: parseFloat(statConfig.querySelector('input[name="decay_rate"]').value) || 0.1,
                    default_start: parseInt(statConfig.querySelector('input[name="default_start"]').value) || 75
                };
            }
        });

        // Collect language sounds
        form.querySelectorAll('.emotion-sound').forEach(emotionSound => {
            const emotion = emotionSound.querySelector('input[name="emotion"]').value.trim();
            if (emotion) {
                const sounds = [];
                emotionSound.querySelectorAll('input[name="sound"]').forEach(soundInput => {
                    if (soundInput.value.trim()) {
                        sounds.push(soundInput.value.trim());
                    }
                });
                if (sounds.length > 0) {
                    templateData.language_sounds[emotion] = sounds;
                }
            }
        });

        // Collect translation conditions
        form.querySelectorAll('.translation-condition').forEach(condition => {
            const stat = condition.querySelector('select[name="condition_stat"]').value;
            const operator = condition.querySelector('select[name="condition_operator"]').value;
            const value = condition.querySelector('input[name="condition_value"]').value;
            
            if (stat && operator && value) {
                templateData.translation_conditions[stat] = `${operator}${value}`;
            }
        });

        return templateData;
    }

    // Enhanced Personality System Methods
    setupPersonalityEventListeners() {
        // Personality mode selection
        document.querySelectorAll('input[name="personality_mode"]').forEach(radio => {
            radio.addEventListener('change', () => this.handlePersonalityModeChange());
        });

        // Method selection for complex personality
        document.querySelectorAll('input[name="personality_method"]').forEach(radio => {
            radio.addEventListener('change', () => this.handlePersonalityMethodChange());
        });

        // Trait modification controls
        document.getElementById('modifyTraitSelect').addEventListener('change', (e) => {
            this.handleTraitSelectChange(e);
        });

        document.getElementById('modifyTraitSlider').addEventListener('input', (e) => {
            document.getElementById('modifyTraitValue').textContent = parseFloat(e.target.value).toFixed(2);
        });

        document.getElementById('addModification').addEventListener('click', () => {
            this.addTraitModification();
        });

        // Slider controls
        document.getElementById('resetSliders').addEventListener('click', () => {
            this.resetTraitSliders();
        });

        document.getElementById('randomizeSliders').addEventListener('click', () => {
            this.randomizeTraitSliders();
        });

        // Blend controls
        document.getElementById('addBlendArchetype').addEventListener('click', () => {
            this.addBlendArchetype();
        });

        // Load initial data
        this.loadPersonalityData();
    }

    async loadPersonalityData() {
        try {
            // Load archetypes
            const archetypesResponse = await fetch('/personality/archetypes');
            this.archetypes = await archetypesResponse.json();

            // Load trait definitions
            const traitsResponse = await fetch('/personality/traits');
            this.traitDefinitions = await traitsResponse.json();

            // Populate UI elements
            this.populateArchetypeGrid();
            this.populateTraitSliders();
            this.populateTraitModificationSelect();

        } catch (error) {
            console.error('Failed to load personality data:', error);
        }
    }

    handlePersonalityModeChange() {
        const selectedMode = document.querySelector('input[name="personality_mode"]:checked').value;
        
        // Update visual state
        document.querySelectorAll('.mode-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-mode="${selectedMode}"]`).classList.add('active');

        // Show/hide appropriate panels
        if (selectedMode === 'simple') {
            document.getElementById('simplePersonalityPanel').classList.remove('hidden');
            document.getElementById('complexPersonalityPanel').classList.add('hidden');
        } else {
            document.getElementById('simplePersonalityPanel').classList.add('hidden');
            document.getElementById('complexPersonalityPanel').classList.remove('hidden');
        }
    }

    handlePersonalityMethodChange() {
        const selectedMethod = document.querySelector('input[name="personality_method"]:checked').value;
        
        // Update visual state
        document.querySelectorAll('.method-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-method="${selectedMethod}"]`).classList.add('active');

        // Show/hide appropriate panels
        document.querySelectorAll('.method-panel').forEach(panel => {
            panel.classList.add('hidden');
        });

        if (selectedMethod === 'archetype') {
            document.getElementById('archetypePanel').classList.remove('hidden');
        } else if (selectedMethod === 'custom') {
            document.getElementById('customTraitsPanel').classList.remove('hidden');
        } else if (selectedMethod === 'blend') {
            document.getElementById('blendPanel').classList.remove('hidden');
        }

        this.updatePersonalityPreview();
    }

    populateArchetypeGrid() {
        const grid = document.getElementById('archetypeGrid');
        grid.innerHTML = '';

        this.archetypes.archetypes.forEach(archetype => {
            const card = document.createElement('div');
            card.className = 'archetype-card';
            card.dataset.archetype = archetype.id;
            
            const iconMap = {
                'leonardo': '🎨',
                'einstein': '🔬', 
                'montessori': '👩‍🏫',
                'socrates': '🤔',
                'rogers': '🤗',
                'yoda': '👴'
            };

            card.innerHTML = `
                <div class="archetype-header">
                    <div class="archetype-icon">${iconMap[archetype.id] || '⭐'}</div>
                    <div class="archetype-name">${archetype.name}</div>
                </div>
                <div class="archetype-description">${archetype.description}</div>
                <div class="archetype-traits">Famous for their unique personality traits</div>
            `;

            card.addEventListener('click', () => this.selectArchetype(archetype.id));
            grid.appendChild(card);
        });
    }

    selectArchetype(archetypeId) {
        // Update visual selection
        document.querySelectorAll('.archetype-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-archetype="${archetypeId}"]`).classList.add('selected');

        this.selectedArchetype = archetypeId;
        this.updatePersonalityPreview();
    }

    populateTraitSliders() {
        const container = document.getElementById('traitSliders');
        container.innerHTML = '';

        this.traitDefinitions.traits.forEach(trait => {
            const slider = document.createElement('div');
            slider.className = 'trait-slider';
            
            slider.innerHTML = `
                <div class="trait-label">
                    ${trait.name.replace(/_/g, ' ')}
                    <span class="trait-description">${trait.description}</span>
                </div>
                <input type="range" class="trait-range" min="0" max="1" step="0.01" value="0.5" data-trait="${trait.name}">
                <span class="trait-value">0.50</span>
            `;

            const range = slider.querySelector('.trait-range');
            const valueDisplay = slider.querySelector('.trait-value');

            range.addEventListener('input', () => {
                valueDisplay.textContent = parseFloat(range.value).toFixed(2);
                this.updatePersonalityPreview();
            });

            container.appendChild(slider);
        });
    }

    populateTraitModificationSelect() {
        const select = document.getElementById('modifyTraitSelect');
        select.innerHTML = '<option value="">Select a trait to modify...</option>';

        this.traitDefinitions.traits.forEach(trait => {
            const option = document.createElement('option');
            option.value = trait.name;
            option.textContent = trait.name.replace(/_/g, ' ');
            select.appendChild(option);
        });
    }

    handleTraitSelectChange(e) {
        const slider = document.getElementById('modifyTraitSlider');
        const button = document.getElementById('addModification');
        
        if (e.target.value) {
            slider.disabled = false;
            button.disabled = false;
        } else {
            slider.disabled = true;
            button.disabled = true;
        }
    }

    addTraitModification() {
        const select = document.getElementById('modifyTraitSelect');
        const slider = document.getElementById('modifyTraitSlider');
        const traitName = select.value;
        const traitValue = parseFloat(slider.value);

        if (!traitName) return;

        // Check if modification already exists
        const existing = document.querySelector(`[data-modification-trait="${traitName}"]`);
        if (existing) {
            existing.remove();
        }

        // Add modification
        const container = document.getElementById('activeModifications');
        const item = document.createElement('div');
        item.className = 'modification-item';
        item.dataset.modificationTrait = traitName;
        
        item.innerHTML = `
            <div class="modification-info">
                <span class="modification-trait">${traitName.replace(/_/g, ' ')}</span>
                <span class="modification-value">${traitValue.toFixed(2)}</span>
            </div>
            <button type="button" class="remove-modification">×</button>
        `;

        item.querySelector('.remove-modification').addEventListener('click', () => {
            item.remove();
            this.updatePersonalityPreview();
        });

        container.appendChild(item);

        // Reset controls
        select.value = '';
        slider.value = 0.5;
        document.getElementById('modifyTraitValue').textContent = '0.50';
        slider.disabled = true;
        document.getElementById('addModification').disabled = true;

        this.updatePersonalityPreview();
    }

    resetTraitSliders() {
        document.querySelectorAll('.trait-range').forEach(range => {
            range.value = 0.5;
            range.nextElementSibling.textContent = '0.50';
        });
        this.updatePersonalityPreview();
    }

    randomizeTraitSliders() {
        document.querySelectorAll('.trait-range').forEach(range => {
            const value = Math.random();
            range.value = value;
            range.nextElementSibling.textContent = value.toFixed(2);
        });
        this.updatePersonalityPreview();
    }

    addBlendArchetype() {
        const container = document.getElementById('blendControls');
        const item = document.createElement('div');
        item.className = 'blend-item';
        
        const archetypeOptions = this.archetypes.archetypes.map(arch => 
            `<option value="${arch.id}">${arch.name}</option>`
        ).join('');

        item.innerHTML = `
            <select class="blend-archetype">
                <option value="">Select personality...</option>
                ${archetypeOptions}
            </select>
            <input type="range" class="blend-weight" min="0" max="1" step="0.1" value="0.5">
            <span class="blend-weight-display">0.5</span>
            <button type="button" class="remove-blend">×</button>
        `;

        const weightSlider = item.querySelector('.blend-weight');
        const weightDisplay = item.querySelector('.blend-weight-display');

        weightSlider.addEventListener('input', () => {
            weightDisplay.textContent = weightSlider.value;
            this.updatePersonalityPreview();
        });

        item.querySelector('.blend-archetype').addEventListener('change', () => {
            this.updatePersonalityPreview();
        });

        item.querySelector('.remove-blend').addEventListener('click', () => {
            item.remove();
            this.updatePersonalityPreview();
        });

        container.appendChild(item);
    }

    updatePersonalityPreview() {
        // This is a simplified preview - in practice you'd want to call the API
        const previewTraits = document.getElementById('previewTopTraits');
        const previewDescription = document.getElementById('previewDescription');

        const method = document.querySelector('input[name="personality_method"]:checked')?.value;
        
        if (method === 'archetype' && this.selectedArchetype) {
            const archetype = this.archetypes.archetypes.find(a => a.id === this.selectedArchetype);
            previewTraits.innerHTML = `Selected: <strong>${archetype.name}</strong>`;
            previewDescription.textContent = archetype.description;
            
        } else if (method === 'custom') {
            // Show top 5 traits from sliders
            const traits = Array.from(document.querySelectorAll('.trait-range')).map(slider => ({
                name: slider.dataset.trait,
                value: parseFloat(slider.value)
            })).sort((a, b) => b.value - a.value).slice(0, 5);

            previewTraits.innerHTML = traits.map(trait => 
                `<span class="trait-score">${trait.name.replace(/_/g, ' ')}: ${trait.value.toFixed(2)}</span>`
            ).join('');
            previewDescription.textContent = 'Custom personality with manually adjusted traits';
            
        } else if (method === 'blend') {
            const blendItems = Array.from(document.querySelectorAll('.blend-item')).map(item => {
                const archetype = item.querySelector('.blend-archetype').value;
                const weight = parseFloat(item.querySelector('.blend-weight').value);
                return { archetype, weight };
            }).filter(item => item.archetype);

            if (blendItems.length > 0) {
                const archetypeNames = blendItems.map(item => {
                    const arch = this.archetypes.archetypes.find(a => a.id === item.archetype);
                    return `${arch?.name} (${(item.weight * 100).toFixed(0)}%)`;
                });
                previewTraits.innerHTML = `Blend: ${archetypeNames.join(', ')}`;
                previewDescription.textContent = 'Custom blend of multiple famous personalities';
            } else {
                previewTraits.textContent = 'Add personalities to create a blend';
                previewDescription.textContent = 'Select archetypes and adjust weights to create a unique blend';
            }
        } else {
            previewTraits.textContent = 'Select a personality configuration to see preview';
            previewDescription.textContent = 'This creature will have a unique personality based on your selections';
        }
    }

    // Update creature creation to handle enhanced personality
    async handleCreatureCreation(e) {
        e.preventDefault();
        
        this.showLoading('Bringing your creature to life...');

        try {
            const creatureData = this.collectCreatureData(e.target);
            
            // Use enhanced endpoint if personality system is complex
            const personalityMode = document.querySelector('input[name="personality_mode"]:checked').value;
            const endpoint = personalityMode === 'complex' ? '/creatures/enhanced' : '/creatures';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(creatureData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            this.hideLoading();
            this.currentCreature = result;
            this.showCreatureInterface();
            this.updateCreatureDisplay();
            
            // Send welcome message
            this.addMessage('system', `🎉 ${result.name} has come to life! Say hello to your new companion.`);
            
        } catch (error) {
            this.hideLoading();
            console.error('Creature creation failed:', error);
            this.showError(`Failed to create creature: ${error.message}`);
        }
    }

    collectCreatureData(form) {
        const formData = new FormData(form);
        const personalityMode = formData.get('personality_mode');
        
        const creatureData = {
            name: formData.get('name'),
            template_id: formData.get('template_id'),
            personality_mode: personalityMode
        };

        if (personalityMode === 'simple') {
            // Collect simple personality data
            const traits = Array.from(document.querySelectorAll('.trait-option.selected')).map(el => el.textContent);
            
            creatureData.simple_personality = {
                traits: traits,
                custom_description: formData.get('custom_personality') || '',
                base_temperament: formData.get('base_temperament') || 'neutral'
            };
            
            // Legacy support
            creatureData.personality_traits = traits;
            creatureData.custom_personality = formData.get('custom_personality') || '';
            
        } else if (personalityMode === 'complex') {
            // Collect complex personality data
            const method = document.querySelector('input[name="personality_method"]:checked').value;
            
            const complexPersonality = {
                mode: method
            };

            if (method === 'archetype') {
                complexPersonality.archetype_name = this.selectedArchetype;
                
            } else if (method === 'custom') {
                const traitValues = {};
                document.querySelectorAll('.trait-range').forEach(slider => {
                    traitValues[slider.dataset.trait] = parseFloat(slider.value);
                });
                complexPersonality.trait_values = traitValues;
                
            } else if (method === 'blend') {
                const archetypeWeights = {};
                document.querySelectorAll('.blend-item').forEach(item => {
                    const archetype = item.querySelector('.blend-archetype').value;
                    const weight = parseFloat(item.querySelector('.blend-weight').value);
                    if (archetype) {
                        archetypeWeights[archetype] = weight;
                    }
                });
                complexPersonality.archetype_weights = archetypeWeights;
            }

            // Collect trait modifications
            const modifications = {};
            document.querySelectorAll('.modification-item').forEach(item => {
                const trait = item.dataset.modificationTrait;
                const value = parseFloat(item.querySelector('.modification-value').textContent);
                modifications[trait] = value;
            });
            
            if (Object.keys(modifications).length > 0) {
                complexPersonality.trait_modifications = modifications;
            }

            creatureData.complex_personality = complexPersonality;
        }

        return creatureData;
    }

    // API Key Management Methods
    async showApiKeyModal() {
        document.getElementById('apiKeyModal').classList.remove('hidden');
        await this.updateApiKeyStatus();
    }

    hideApiKeyModal() {
        document.getElementById('apiKeyModal').classList.add('hidden');
        // Clear the input for security
        document.getElementById('apiKeyInput').value = '';
    }

    async updateApiKeyStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            const statusElement = document.getElementById('apiKeyStatus');
            
            if (status.has_api_key) {
                statusElement.className = 'status-indicator connected';
                statusElement.innerHTML = `<i class="fas fa-circle-check"></i><span>API key configured - using ${status.model} model</span>`;
            } else {
                statusElement.className = 'status-indicator disconnected';
                statusElement.innerHTML = '<i class="fas fa-circle-xmark"></i><span>No API key set - using mock responses</span>';
            }
        } catch (error) {
            console.error('Failed to get API status:', error);
        }
    }

    toggleApiKeyVisibility() {
        const input = document.getElementById('apiKeyInput');
        const icon = document.querySelector('#toggleApiKeyVisibility i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.className = 'fas fa-eye-slash';
        } else {
            input.type = 'password';
            icon.className = 'fas fa-eye';
        }
    }

    async saveApiKey() {
        const apiKey = document.getElementById('apiKeyInput').value.trim();
        
        if (!apiKey) {
            alert('Please enter an API key');
            return;
        }
        
        if (!apiKey.startsWith('sk-')) {
            alert('Invalid API key format. OpenAI API keys start with "sk-"');
            return;
        }
        
        try {
            const response = await fetch('/api/set_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ api_key: apiKey })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to set API key');
            }

            const result = await response.json();
            
            await this.updateApiKeyStatus();
            
            alert(`API key set successfully! Now using ${result.model} model for real AI responses.`);
            
            this.hideApiKeyModal();
            
        } catch (error) {
            console.error('Failed to save API key:', error);
            alert(`Failed to save API key: ${error.message}`);
        }
    }

    async clearApiKey() {
        if (confirm('Are you sure you want to clear the API key? This will revert to mock responses.')) {
            try {
                const response = await fetch('/api/clear_key', {
                    method: 'POST'
                });

                if (!response.ok) {
                    throw new Error('Failed to clear API key');
                }

                await this.updateApiKeyStatus();
                alert('API key cleared. Now using mock responses.');
                
            } catch (error) {
                console.error('Failed to clear API key:', error);
                alert(`Failed to clear API key: ${error.message}`);
            }
        }
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