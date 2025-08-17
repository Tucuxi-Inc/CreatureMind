"""
CreatureMind API Server

REST API for the CreatureMind service - provides endpoints for creating and
interacting with creature minds.
"""

import os
import json
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.models.creature import Creature
from core.models.creature_template import CreatureTemplate
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


class CreatureResponse(BaseModel):
    creature_language: str
    human_translation: Optional[str] = None
    can_translate: bool
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


@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    # Load creature templates
    await load_templates()
    
    # Create AI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: No OpenAI API key found. Using mock client.")
        client_type = "mock"
    else:
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)