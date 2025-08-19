"""
CreatureMind API Server

REST API for the CreatureMind service - provides endpoints for creating and
interacting with creature minds.
"""

import os
import json
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from core.models.creature import Creature
from core.models.creature_template import CreatureTemplate
from core.models.personality_system import (
    PersonalityMode, EnhancedPersonality, PersonalityArchetypes, 
    TRAIT_DEFINITIONS, TRAIT_NAME_TO_INDEX
)
from core.agents.creature_mind_system import CreatureMindSystem
from core.agents.ai_client import create_ai_client


# Pydantic models for API requests/responses
class CreateCreatureRequest(BaseModel):
    name: str
    template_id: str
    personality_traits: Optional[list] = None
    custom_personality: Optional[str] = ""


class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ActivityRequest(BaseModel):
    activity: str
    parameters: Optional[Dict[str, Any]] = None


class CreateTemplateRequest(BaseModel):
    name: str
    species: str
    description: str
    personality_traits: List[str]
    stat_configs: Dict[str, Dict[str, Any]]
    language_sounds: Dict[str, List[str]]
    translation_conditions: Dict[str, str]
    activities: Optional[List[Dict[str, Any]]] = None


# Enhanced personality API models
class CreateSimplePersonalityRequest(BaseModel):
    """Request for creating a simple personality (3-5 traits)"""
    traits: List[str]
    custom_description: Optional[str] = ""
    base_temperament: str = "neutral"


class CreateComplexPersonalityRequest(BaseModel):
    """Request for creating a complex personality (50-dimensional)"""
    mode: str = "archetype"  # "archetype", "custom", "blend"
    
    # For archetype mode
    archetype_name: Optional[str] = None
    
    # For custom mode
    trait_values: Optional[Dict[str, float]] = None  # trait_name -> value (0.0-1.0)
    
    # For blend mode  
    archetype_weights: Optional[Dict[str, float]] = None  # archetype -> weight
    
    # Optional trait modifications for any mode
    trait_modifications: Optional[Dict[str, float]] = None


class CreateCreatureWithPersonalityRequest(BaseModel):
    """Enhanced creature creation with personality options"""
    name: str
    template_id: str
    
    # Personality configuration
    personality_mode: str = "simple"  # "simple" or "complex"
    simple_personality: Optional[CreateSimplePersonalityRequest] = None
    complex_personality: Optional[CreateComplexPersonalityRequest] = None
    
    # Legacy support
    personality_traits: Optional[List[str]] = None
    custom_personality: Optional[str] = ""


class PersonalityInfoResponse(BaseModel):
    """Response with personality information"""
    mode: str
    simple_traits: Optional[List[str]] = None
    dominant_traits: Optional[List[tuple]] = None  # (trait_name, score) pairs
    archetype_base: Optional[str] = None
    trait_modifications: Optional[Dict[str, float]] = None


class CreatureResponse(BaseModel):
    creature_language: str
    human_translation: Optional[str] = None
    can_translate: bool
    translation_hint: Optional[str] = None  # Helpful hint when translation isn't available
    emotional_state: str
    stats_delta: Dict[str, float]
    debug_info: Optional[Dict[str, Any]] = None


# Global storage (in production, use proper database)
creatures: Dict[str, Creature] = {}
creature_minds: Dict[str, CreatureMindSystem] = {}
templates: Dict[str, CreatureTemplate] = {}


# Initialize FastAPI app
app = FastAPI(
    title="CreatureMind API",
    description="Multi-agent AI system for believable creature companions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
web_templates = Jinja2Templates(directory="web/templates")


@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    # Load creature templates
    await load_templates()
    
    # Create AI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("🚨 Warning: No OpenAI API key found. Using mock client.")
        print("   Set OPENAI_API_KEY environment variable to enable real AI responses.")
        print("   Mock responses are limited and not realistic.")
        client_type = "mock"
    else:
        print("✅ OpenAI API key found. Using real AI client with gpt-4.1-nano model.")
        client_type = "openai"
    
    global ai_client
    ai_client = create_ai_client(client_type, api_key=api_key)


async def load_templates():
    """Load creature templates from examples directory"""
    import glob
    
    template_files = glob.glob("examples/*.json")
    for file_path in template_files:
        try:
            with open(file_path, 'r') as f:
                template_data = json.load(f)
                template = CreatureTemplate(**template_data)
                templates[template.id] = template
                print(f"Loaded template: {template.id}")
        except Exception as e:
            print(f"Error loading template {file_path}: {e}")


@app.get("/", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Serve the web interface"""
    return web_templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def get_favicon():
    """Serve favicon"""
    from fastapi.responses import FileResponse
    return FileResponse("web/static/favicon.ico")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/templates")
async def list_templates():
    """List available creature templates"""
    return {
        "templates": [
            {
                "id": template.id,
                "name": template.name,
                "species": template.species,
                "description": template.description
            }
            for template in templates.values()
        ]
    }


@app.post("/creatures")
async def create_creature(request: CreateCreatureRequest):
    """Create a new creature"""
    if request.template_id not in templates:
        raise HTTPException(status_code=400, detail=f"Template {request.template_id} not found")
    
    template = templates[request.template_id]
    
    # Create creature with template defaults
    creature = Creature(
        name=request.name,
        species=template.species,
        template_id=request.template_id
    )
    
    # Set up stats from template
    from core.models.creature import StatConfig
    for stat_name, config_dict in template.stat_configs.items():
        # Convert dict to StatConfig object
        stat_config = StatConfig(**config_dict)
        creature.stats.configs[stat_name] = stat_config
        creature.stats.set_stat(stat_name, config_dict.get("default_start", 75))
    
    # Set personality
    if request.personality_traits:
        creature.personality.traits = request.personality_traits
    else:
        creature.personality.traits = template.default_personality_traits.copy()
    
    if request.custom_personality:
        creature.personality.custom_description = request.custom_personality
    
    # Store creature and create mind system
    creature_id = str(creature.id)
    creatures[creature_id] = creature
    creature_minds[creature_id] = CreatureMindSystem(creature, template, ai_client)
    
    return {
        "creature_id": creature_id,
        "name": creature.name,
        "species": creature.species,
        "template": request.template_id,
        "stats": {name: creature.stats.get_stat(name) for name in creature.stats.configs.keys()}
    }


@app.post("/creatures/{creature_id}/message")
async def send_message(creature_id: str, request: MessageRequest) -> CreatureResponse:
    """Send a message to a creature"""
    if creature_id not in creature_minds:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    mind = creature_minds[creature_id]
    response = await mind.process_message(request.message, request.context)
    
    return CreatureResponse(
        creature_language=response.creature_language,
        human_translation=response.human_translation,
        can_translate=response.can_translate,
        translation_hint=response.translation_hint,
        emotional_state=response.emotional_state,
        stats_delta=response.stats_delta,
        debug_info=response.debug_info
    )


@app.post("/creatures/{creature_id}/activity")
async def perform_activity(creature_id: str, request: ActivityRequest) -> CreatureResponse:
    """Have a creature perform an activity"""
    if creature_id not in creature_minds:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    mind = creature_minds[creature_id]
    response = await mind.process_activity(request.activity, request.parameters)
    
    return CreatureResponse(
        creature_language=response.creature_language,
        human_translation=response.human_translation,
        can_translate=response.can_translate,
        translation_hint=response.translation_hint,
        emotional_state=response.emotional_state,
        stats_delta=response.stats_delta,
        debug_info=response.debug_info
    )


@app.get("/creatures/{creature_id}/status")
async def get_creature_status(creature_id: str):
    """Get creature status"""
    if creature_id not in creature_minds:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    mind = creature_minds[creature_id]
    return mind.get_creature_status()


@app.get("/creatures")
async def list_creatures():
    """List all creatures"""
    return {
        "creatures": [
            {
                "id": str(creature.id),
                "name": creature.name,
                "species": creature.species,
                "template": creature.template_id,
                "created_at": creature.created_at.isoformat()
            }
            for creature in creatures.values()
        ]
    }


@app.post("/templates")
async def create_custom_template(request: CreateTemplateRequest):
    """Create a custom creature template"""
    from core.models.creature_template import CreatureTemplate, LanguageConfig, ActivityConfig
    
    # Generate a unique template ID
    template_id = f"custom_{request.species}_{len(templates) + 1}"
    
    # Create language configuration
    language_config = LanguageConfig(
        sounds=request.language_sounds,
        translation_conditions=request.translation_conditions,
        behavioral_patterns=[]
    )
    
    # Create activity configurations
    activity_configs = []
    if request.activities:
        for activity_data in request.activities:
            activity_config = ActivityConfig(
                name=activity_data["name"],
                stat_effects=activity_data.get("stat_effects", {}),
                energy_cost=activity_data.get("energy_cost", 0),
                description=activity_data.get("description", ""),
                required_stats=activity_data.get("required_stats", {})
            )
            activity_configs.append(activity_config)
    
    # Create the template
    template = CreatureTemplate(
        id=template_id,
        name=request.name,
        species=request.species,
        description=request.description,
        default_personality_traits=request.personality_traits,
        stat_configs=request.stat_configs,
        language=language_config,
        activities=activity_configs
    )
    
    # Store the template
    templates[template_id] = template
    
    return {
        "template_id": template_id,
        "name": template.name,
        "species": template.species,
        "description": template.description,
        "message": "Custom template created successfully!"
    }


# Enhanced personality endpoints
@app.get("/personality/archetypes")
async def list_personality_archetypes():
    """List all available personality archetypes"""
    return {
        "archetypes": PersonalityArchetypes.list_archetypes()
    }


@app.get("/personality/traits")  
async def list_personality_traits():
    """List all 50 personality traits with descriptions"""
    return {
        "traits": [
            {
                "index": trait.index,
                "name": trait.name,
                "description": trait.description,
                "category": trait.category,
                "low_description": trait.low_description,
                "high_description": trait.high_description
            }
            for trait in TRAIT_DEFINITIONS
        ]
    }


@app.post("/personality/simple")
async def create_simple_personality(request: CreateSimplePersonalityRequest):
    """Create a simple personality configuration"""
    personality = EnhancedPersonality(
        mode=PersonalityMode.SIMPLE,
        simple_traits=request.traits,
        custom_description=request.custom_description,
        base_temperament=request.base_temperament
    )
    
    return {
        "personality_id": "temp_" + str(hash(str(request.traits))),  # Temporary ID
        "mode": personality.mode.value,
        "traits": personality.simple_traits,
        "description": personality.custom_description,
        "temperament": personality.base_temperament
    }


@app.post("/personality/complex")
async def create_complex_personality(request: CreateComplexPersonalityRequest):
    """Create a complex (50-dimensional) personality configuration"""
    
    personality = EnhancedPersonality(mode=PersonalityMode.COMPLEX)
    
    if request.mode == "archetype" and request.archetype_name:
        # Use preset archetype
        archetype_vector = PersonalityArchetypes.get_archetype(request.archetype_name)
        if archetype_vector is None:
            raise HTTPException(status_code=400, detail=f"Unknown archetype: {request.archetype_name}")
        
        personality.archetype_base = request.archetype_name
        personality.trait_vector = archetype_vector.tolist()
        
    elif request.mode == "custom" and request.trait_values:
        # Use custom trait values
        trait_vector = [0.5] * 50  # Start with neutral
        
        for trait_name, value in request.trait_values.items():
            if trait_name in TRAIT_NAME_TO_INDEX:
                idx = TRAIT_NAME_TO_INDEX[trait_name]
                trait_vector[idx] = max(0.0, min(1.0, value))  # Clamp to [0,1]
        
        personality.trait_vector = trait_vector
        
    elif request.mode == "blend" and request.archetype_weights:
        # Blend multiple archetypes
        blended_vector = PersonalityArchetypes.create_custom_blend(request.archetype_weights)
        personality.trait_vector = blended_vector.tolist()
        
    else:
        raise HTTPException(status_code=400, detail="Invalid personality creation mode or missing parameters")
    
    # Apply trait modifications if provided
    if request.trait_modifications and personality.trait_vector:
        for trait_name, value in request.trait_modifications.items():
            if trait_name in TRAIT_NAME_TO_INDEX:
                idx = TRAIT_NAME_TO_INDEX[trait_name]
                personality.trait_vector[idx] = max(0.0, min(1.0, value))
        
        personality.trait_modifications = request.trait_modifications
    
    # Get dominant traits for response
    dominant_traits = personality.get_dominant_traits(5)
    
    return {
        "personality_id": "temp_complex_" + str(hash(str(personality.trait_vector))),
        "mode": personality.mode.value,
        "archetype_base": personality.archetype_base,
        "dominant_traits": [{"trait": trait, "score": score} for trait, score in dominant_traits],
        "trait_modifications": personality.trait_modifications
    }


@app.post("/creatures/enhanced")
async def create_creature_with_personality(request: CreateCreatureWithPersonalityRequest):
    """Create a creature with enhanced personality configuration"""
    
    if request.template_id not in templates:
        raise HTTPException(status_code=400, detail=f"Template {request.template_id} not found")
    
    template = templates[request.template_id]
    
    # Create creature with template defaults
    creature = Creature(
        name=request.name,
        species=template.species,
        template_id=request.template_id
    )
    
    # Set up stats from template
    from core.models.creature import StatConfig
    for stat_name, config_dict in template.stat_configs.items():
        stat_config = StatConfig(**config_dict)
        creature.stats.configs[stat_name] = stat_config
        creature.stats.set_stat(stat_name, config_dict.get("default_start", 75))
    
    # Configure personality based on mode
    if request.personality_mode == "complex" and request.complex_personality:
        # Create enhanced personality
        complex_req = request.complex_personality
        enhanced_personality = EnhancedPersonality(mode=PersonalityMode.COMPLEX)
        
        if complex_req.mode == "archetype" and complex_req.archetype_name:
            archetype_vector = PersonalityArchetypes.get_archetype(complex_req.archetype_name)
            if archetype_vector is None:
                raise HTTPException(status_code=400, detail=f"Unknown archetype: {complex_req.archetype_name}")
            
            enhanced_personality.archetype_base = complex_req.archetype_name
            enhanced_personality.trait_vector = archetype_vector.tolist()
            
        elif complex_req.mode == "custom" and complex_req.trait_values:
            trait_vector = [0.5] * 50
            for trait_name, value in complex_req.trait_values.items():
                if trait_name in TRAIT_NAME_TO_INDEX:
                    idx = TRAIT_NAME_TO_INDEX[trait_name]
                    trait_vector[idx] = max(0.0, min(1.0, value))
            enhanced_personality.trait_vector = trait_vector
            
        elif complex_req.mode == "blend" and complex_req.archetype_weights:
            blended_vector = PersonalityArchetypes.create_custom_blend(complex_req.archetype_weights)
            enhanced_personality.trait_vector = blended_vector.tolist()
        
        # Apply modifications
        if complex_req.trait_modifications and enhanced_personality.trait_vector:
            for trait_name, value in complex_req.trait_modifications.items():
                if trait_name in TRAIT_NAME_TO_INDEX:
                    idx = TRAIT_NAME_TO_INDEX[trait_name]
                    enhanced_personality.trait_vector[idx] = max(0.0, min(1.0, value))
            enhanced_personality.trait_modifications = complex_req.trait_modifications
        
        creature.personality.enhanced_personality = enhanced_personality
        
    elif request.personality_mode == "simple" and request.simple_personality:
        # Create simple personality
        simple_req = request.simple_personality
        enhanced_personality = EnhancedPersonality(
            mode=PersonalityMode.SIMPLE,
            simple_traits=simple_req.traits,
            custom_description=simple_req.custom_description,
            base_temperament=simple_req.base_temperament
        )
        creature.personality.enhanced_personality = enhanced_personality
        creature.personality.traits = simple_req.traits
        
    else:
        # Legacy mode - use simple traits
        if request.personality_traits:
            creature.personality.traits = request.personality_traits
        else:
            creature.personality.traits = template.default_personality_traits.copy()
        
        if request.custom_personality:
            creature.personality.custom_description = request.custom_personality
    
    # Store creature and create mind system
    creature_id = str(creature.id)
    creatures[creature_id] = creature
    creature_minds[creature_id] = CreatureMindSystem(creature, template, ai_client)
    
    # Build response with personality information
    personality_info = None
    if creature.personality.enhanced_personality:
        enhanced = creature.personality.enhanced_personality
        if enhanced.mode == PersonalityMode.COMPLEX:
            dominant_traits = enhanced.get_dominant_traits(5)
            personality_info = {
                "mode": enhanced.mode.value,
                "archetype_base": enhanced.archetype_base,
                "dominant_traits": [{"trait": trait, "score": score} for trait, score in dominant_traits],
                "trait_modifications": enhanced.trait_modifications
            }
        else:
            personality_info = {
                "mode": enhanced.mode.value,
                "simple_traits": enhanced.simple_traits,
                "description": enhanced.custom_description,
                "temperament": enhanced.base_temperament
            }
    
    return {
        "creature_id": creature_id,
        "name": creature.name,
        "species": creature.species,
        "template": request.template_id,
        "stats": {name: creature.stats.get_stat(name) for name in creature.stats.configs.keys()},
        "personality": personality_info
    }


@app.get("/creatures/{creature_id}/personality")
async def get_creature_personality(creature_id: str):
    """Get detailed personality information for a creature"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if creature.personality.enhanced_personality:
        enhanced = creature.personality.enhanced_personality
        
        if enhanced.mode == PersonalityMode.COMPLEX:
            dominant_traits = enhanced.get_dominant_traits(10)
            return PersonalityInfoResponse(
                mode=enhanced.mode.value,
                dominant_traits=[(trait, score) for trait, score in dominant_traits],
                archetype_base=enhanced.archetype_base,
                trait_modifications=enhanced.trait_modifications
            )
        else:
            return PersonalityInfoResponse(
                mode=enhanced.mode.value,
                simple_traits=enhanced.simple_traits
            )
    else:
        # Legacy personality
        return PersonalityInfoResponse(
            mode="simple",
            simple_traits=creature.personality.traits
        )


@app.get("/creatures/{creature_id}/personality/development")
async def get_personality_development(creature_id: str):
    """Get personality development analysis for a creature"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if not (hasattr(creature.personality, 'enhanced_personality') and creature.personality.enhanced_personality):
        raise HTTPException(status_code=400, detail="Creature does not have enhanced personality system")
    
    enhanced = creature.personality.enhanced_personality
    development_analysis = enhanced.get_personality_development_analysis()
    
    if development_analysis is None:
        return {
            "message": "No personality development data available yet",
            "evolution_enabled": enhanced.evolution_enabled,
            "shifts_count": len(enhanced.personality_shifts)
        }
    
    return {
        "development_analysis": development_analysis,
        "evolution_enabled": enhanced.evolution_enabled,
        "active_shifts": len([s for s in enhanced.personality_shifts if not s.is_expired]),
        "total_shifts": len(enhanced.personality_shifts),
        "current_emotional_state": enhanced.current_emotional_state.primary_emotion if enhanced.current_emotional_state else None
    }


@app.post("/creatures/{creature_id}/personality/evolution/toggle")
async def toggle_personality_evolution(creature_id: str, enable: bool):
    """Enable or disable personality evolution for a creature"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if not (hasattr(creature.personality, 'enhanced_personality') and creature.personality.enhanced_personality):
        raise HTTPException(status_code=400, detail="Creature does not have enhanced personality system")
    
    enhanced = creature.personality.enhanced_personality
    enhanced.evolution_enabled = enable
    
    return {
        "message": f"Personality evolution {'enabled' if enable else 'disabled'}",
        "evolution_enabled": enhanced.evolution_enabled
    }


@app.post("/creatures/{creature_id}/personality/evolution/reset")
async def reset_personality_evolution(creature_id: str, keep_shifts: bool = False):
    """Reset personality evolution to baseline"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if not (hasattr(creature.personality, 'enhanced_personality') and creature.personality.enhanced_personality):
        raise HTTPException(status_code=400, detail="Creature does not have enhanced personality system")
    
    enhanced = creature.personality.enhanced_personality
    enhanced.reset_personality_evolution(keep_shifts=keep_shifts)
    
    return {
        "message": "Personality evolution reset to baseline",
        "shifts_kept": keep_shifts,
        "current_shifts": len(enhanced.personality_shifts)
    }


@app.get("/creatures/{creature_id}/learning")
async def get_creature_learning(creature_id: str):
    """Get learning and adaptation information for a creature"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if not (hasattr(creature.personality, 'enhanced_personality') and creature.personality.enhanced_personality):
        raise HTTPException(status_code=400, detail="Creature does not have enhanced personality system")
    
    enhanced = creature.personality.enhanced_personality
    learning_summary = enhanced.get_learning_summary()
    
    if learning_summary is None:
        return {
            "message": "No learning data available yet",
            "learning_enabled": enhanced.learning_enabled,
            "learned_patterns_count": len(enhanced.learned_patterns)
        }
    
    return {
        "learning_summary": learning_summary,
        "learning_enabled": enhanced.learning_enabled,
        "adaptation_rate": enhanced.adaptation_rate,
        "learned_patterns_count": len(enhanced.learned_patterns)
    }


@app.post("/creatures/{creature_id}/learning/toggle")
async def toggle_creature_learning(creature_id: str, enable: bool):
    """Enable or disable learning for a creature"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if not (hasattr(creature.personality, 'enhanced_personality') and creature.personality.enhanced_personality):
        raise HTTPException(status_code=400, detail="Creature does not have enhanced personality system")
    
    enhanced = creature.personality.enhanced_personality
    enhanced.learning_enabled = enable
    
    return {
        "message": f"Learning {'enabled' if enable else 'disabled'}",
        "learning_enabled": enhanced.learning_enabled
    }


@app.post("/creatures/{creature_id}/learning/reset")
async def reset_creature_learning(creature_id: str, keep_strong_learnings: bool = True):
    """Reset learned patterns for a creature"""
    if creature_id not in creatures:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures[creature_id]
    
    if not (hasattr(creature.personality, 'enhanced_personality') and creature.personality.enhanced_personality):
        raise HTTPException(status_code=400, detail="Creature does not have enhanced personality system")
    
    enhanced = creature.personality.enhanced_personality
    patterns_before = len(enhanced.learned_patterns)
    enhanced.reset_learning(keep_strong_learnings=keep_strong_learnings)
    patterns_after = len(enhanced.learned_patterns)
    
    return {
        "message": "Learning patterns reset",
        "patterns_removed": patterns_before - patterns_after,
        "patterns_kept": patterns_after,
        "strong_learnings_kept": keep_strong_learnings
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)