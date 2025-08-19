"""
Local AI Client for CreatureMind

Provides OpenAI-compatible interface using local llama.cpp server with Gemma-3-270M.
Optimized for Apple Silicon with 32k context support.
"""

import logging
from typing import Optional, List, Dict, Any
from .ai_client import AIClient
from .local_ai_manager import get_local_ai_manager, ensure_local_ai_running

logger = logging.getLogger(__name__)


class LocalAIClient(AIClient):
    """Local AI client using llama.cpp server with dynamic model support"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.manager = get_local_ai_manager()
        
        # Update model name dynamically
        self.model_name = self.manager.current_model
        self.max_context_tokens = self.manager.config.ctx_size
        self.max_response_tokens = min(4000, self.max_context_tokens // 8)  # Reserve space for context
        
        logger.info(f"🧠 LocalAIClient initialized - Model: {self.model_name}, Context: {self.max_context_tokens:,}")
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using chat completions endpoint with Gemma chat template"""
        try:
            # Check if server is running, start only if needed
            health = await self.manager.health_check()
            if health.get("status") != "healthy":
                logger.info("🔄 Local AI server not healthy, attempting to start...")
                if not await self.manager.start_server():
                    raise RuntimeError("Failed to start local AI server")
            
            # Build messages for chat completions API
            messages = []
            
            # Add system message if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add chat history
            if chat_history:
                messages.extend(chat_history)
            
            # Add current user message
            if user_message:
                messages.append({"role": "user", "content": user_message})
            
            logger.info(f"🧠 LocalAI generating response ({len(messages)} messages)")
            
            # Generate response using chat completions endpoint
            response = await self.manager.generate_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response content
            if response and "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                logger.info(f"✅ LocalAI response generated ({len(content)} chars)")
                return content.strip()
            else:
                raise RuntimeError("No response content in server response")
                
        except Exception as e:
            logger.error(f"LocalAI generation error: {e}")
            # Re-raise to let the smart client handle fallback
            raise
    
    def _build_gemma_prompt(self, system_prompt: str, user_message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Build Gemma3 formatted prompt with full context"""
        prompt_parts = ["<bos>"]
        
        # Add system prompt if provided
        if system_prompt:
            prompt_parts.extend([
                "<start_of_turn>system",
                system_prompt,
                "<end_of_turn>"
            ])
        
        # Add chat history (leverage full 32k context!)
        if chat_history:
            for msg in chat_history:
                role = "user" if msg["role"] == "user" else "model"
                prompt_parts.extend([
                    f"<start_of_turn>{role}",
                    msg["content"],
                    "<end_of_turn>"
                ])
        
        # Add current user message
        if user_message:
            prompt_parts.extend([
                "<start_of_turn>user",
                user_message,
                "<end_of_turn>"
            ])
        
        # Start model response
        prompt_parts.append("<start_of_turn>model")
        
        return "\n".join(prompt_parts)
    
    def is_available(self) -> bool:
        """Check if local AI is available"""
        try:
            return self.manager.is_running
        except Exception:
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of local AI"""
        return await self.manager.health_check()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the local model"""
        return {
            "model": self.model_name,
            "type": "local",
            "provider": "llama.cpp",
            "context_window": self.max_context_tokens,
            "max_response_tokens": self.max_response_tokens,
            "hardware": "Apple Silicon",
            "features": [
                "32k context window",
                "Metal GPU acceleration", 
                "Offline inference",
                "Zero API costs",
                "Flash attention",
                "Continuous batching"
            ]
        }
    
    async def start(self):
        """Start the local AI server"""
        logger.info("🚀 Starting LocalAIClient...")
        success = await ensure_local_ai_running()
        if success:
            logger.info("✅ LocalAIClient ready!")
        else:
            logger.error("❌ Failed to start LocalAIClient")
        return success
    
    async def stop(self):
        """Stop the local AI server"""
        logger.info("🛑 Stopping LocalAIClient...")
        await self.manager.stop_server()
        logger.info("✅ LocalAIClient stopped")


class SmartAIClient(AIClient):
    """Smart AI client with intelligent fallback chain"""
    
    def __init__(self, openai_client: Optional[AIClient] = None, mock_client: Optional[AIClient] = None):
        self.openai_client = openai_client
        self.local_client = LocalAIClient()
        self.mock_client = mock_client
        
        # Fallback preferences
        self.prefer_local = False  # Can be toggled by user
        
        logger.info("🤖 SmartAIClient initialized with fallback chain:")
        logger.info("   1. OpenAI API (if available)")
        logger.info("   2. Local Gemma-3-270M (32k context)")
        logger.info("   3. Mock responses (fallback)")
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using smart fallback chain"""
        
        # Determine which client to try first
        clients_to_try = []
        
        if self.prefer_local:
            # Local-first mode
            clients_to_try = [
                ("Local AI", self.local_client),
                ("OpenAI", self.openai_client),
                ("Mock", self.mock_client)
            ]
        else:
            # Cloud-first mode (default)
            clients_to_try = [
                ("OpenAI", self.openai_client),
                ("Local AI", self.local_client),
                ("Mock", self.mock_client)
            ]
        
        # Try each client in order
        for name, client in clients_to_try:
            if client is None:
                continue
                
            try:
                logger.info(f"🤖 Trying {name}...")
                
                # Special handling for local AI startup
                if name == "Local AI" and not client.is_available():
                    logger.info("   Starting local AI server...")
                    await client.start()
                
                response = await client.generate_response(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    chat_history=chat_history,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                logger.info(f"✅ {name} generated response successfully")
                return response
                
            except Exception as e:
                logger.warning(f"⚠️ {name} failed: {e}")
                continue
        
        # If all else fails
        raise RuntimeError("All AI clients failed to generate response")
    
    def get_current_client_status(self) -> Dict[str, Any]:
        """Get status of all available clients"""
        status = {}
        
        # OpenAI status
        if self.openai_client:
            status["openai"] = {
                "available": True,
                "type": "cloud",
                "cost": "~$0.01-0.05/conversation"
            }
        else:
            status["openai"] = {
                "available": False,
                "reason": "No API key configured"
            }
        
        # Local AI status
        status["local"] = {
            "available": self.local_client.is_available(),
            "type": "local",
            "cost": "$0 (free)",
            "model": self.local_client.model_name,
            "context": f"{self.local_client.max_context_tokens:,} tokens"
        }
        
        # Mock status
        status["mock"] = {
            "available": self.mock_client is not None,
            "type": "fallback",
            "cost": "$0 (limited)"
        }
        
        return status
    
    async def start_local_ai(self) -> bool:
        """Manually start local AI"""
        return await self.local_client.start()
    
    async def stop_local_ai(self):
        """Manually stop local AI"""
        await self.local_client.stop()
    
    def set_prefer_local(self, prefer: bool):
        """Set whether to prefer local AI over cloud"""
        self.prefer_local = prefer
        mode = "local-first" if prefer else "cloud-first"
        logger.info(f"🔄 Switching to {mode} mode")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get comprehensive health check"""
        health = {}
        
        # Check each client
        if self.openai_client:
            try:
                # Simple test - would need to implement in actual OpenAI client
                health["openai"] = {"status": "available"}
            except:
                health["openai"] = {"status": "error"}
        else:
            health["openai"] = {"status": "not_configured"}
        
        # Local AI health
        health["local"] = await self.local_client.health_check()
        
        # Mock health
        health["mock"] = {"status": "available" if self.mock_client else "not_configured"}
        
        return health