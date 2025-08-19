"""
Local AI Manager for Apple Silicon using llama.cpp

Manages llama-server lifecycle and provides optimized inference for CreatureMind
using the Gemma-3-270M model with 32k context window.
"""

import asyncio
import os
import subprocess
import time
import signal
import aiohttp
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LocalAIConfig:
    """Configuration for local AI inference"""
    server_port: int = 8081
    host: str = "127.0.0.1"
    ctx_size: int = 32768   # Context size for gemma-3-270m model
    threads: int = 8       # Optimized for Apple Silicon
    gpu_layers: int = 99   # Use Metal GPU acceleration
    batch_size: int = 512  # Optimized batch size
    temperature: float = 0.7
    timeout: int = 600     # 10 minute timeout
    model_name: str = "gemma-3-270m-it-F16.gguf"  # Default model - lightweight 270M parameter model


class LocalAIManager:
    """Manages llama-server for local AI inference on Apple Silicon"""
    
    # Model specifications with context windows
    MODEL_SPECS = {
        "gemma-3-270m": {"ctx_size": 32768, "size": "270M", "family": "gemma3"},
        "gemma-3-2b": {"ctx_size": 32768, "size": "2B", "family": "gemma3"}, 
        "gemma-3-4b": {"ctx_size": 128000, "size": "4B", "family": "gemma3"},
        "gemma-3-9b": {"ctx_size": 128000, "size": "9B", "family": "gemma3"},
        "gemma-3-27b": {"ctx_size": 128000, "size": "27B", "family": "gemma3"},
        # Future models can be added here
        "llama-3.2-1b": {"ctx_size": 32768, "size": "1B", "family": "llama3"},
        "llama-3.2-3b": {"ctx_size": 32768, "size": "3B", "family": "llama3"},
        "llama-3.3-70b": {"ctx_size": 128000, "size": "70B", "family": "llama3"}
    }
    
    def __init__(self, base_dir: str = None, model_name: Optional[str] = None):
        self.base_dir = Path(base_dir or os.getcwd())
        
        # Model detection and configuration
        self.available_models = self._scan_available_models()
        self.current_model = model_name or self._select_default_model()
        
        # Create config with detected model
        self.config = LocalAIConfig(
            model_name=self.current_model,
            ctx_size=self._get_model_context_size(self.current_model)
        )
        
        # Paths
        self.bin_dir = self.base_dir / "localai" / "bin"
        self.models_dir = self.base_dir / "localai" / "models"
        self.server_binary = self.bin_dir / "llama-server"
        self.model_path = self.models_dir / self.current_model
        
        # Process management
        self.server_process: Optional[subprocess.Popen] = None
        self.is_running = False
        
        # Validate paths
        self._validate_setup()
    
    def _scan_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Scan models directory for available models"""
        models_dir = self.base_dir / "localai" / "models"
        available = {}
        
        if not models_dir.exists():
            logger.warning(f"Models directory not found: {models_dir}")
            return {}
        
        for model_file in models_dir.glob("*.gguf"):
            model_name = model_file.name
            
            # Try to match against known model specs
            model_key = self._identify_model(model_name)
            if model_key:
                spec = self.MODEL_SPECS[model_key].copy()
                spec["file_name"] = model_name
                spec["file_size"] = model_file.stat().st_size
                spec["file_path"] = model_file
                available[model_name] = spec
            else:
                # Unknown model - use conservative defaults
                available[model_name] = {
                    "ctx_size": 32768,  # Conservative default
                    "size": "Unknown",
                    "family": "unknown",
                    "file_name": model_name,
                    "file_size": model_file.stat().st_size,
                    "file_path": model_file
                }
        
        logger.info(f"📁 Found {len(available)} models: {list(available.keys())}")
        return available
    
    def _identify_model(self, filename: str) -> Optional[str]:
        """Identify model type from filename"""
        filename_lower = filename.lower()
        
        for model_key in self.MODEL_SPECS:
            # Check for model name patterns
            if "gemma" in filename_lower and "270m" in filename_lower:
                return "gemma-3-270m"
            elif "gemma" in filename_lower and "2b" in filename_lower:
                return "gemma-3-2b" 
            elif "gemma" in filename_lower and "4b" in filename_lower:
                return "gemma-3-4b"
            elif "gemma" in filename_lower and "9b" in filename_lower:
                return "gemma-3-9b"
            elif "gemma" in filename_lower and "27b" in filename_lower:
                return "gemma-3-27b"
            # Add more patterns as needed
        
        return None
    
    def _select_default_model(self) -> str:
        """Select the best available model as default"""
        if not self.available_models:
            return "gemma-3-270m-it-F16.gguf"  # Fallback to 270M model
        
        # Priority order: try to find gemma-3-270m first (lightweight default)
        for filename in self.available_models:
            if "270m" in filename.lower():
                return filename
        
        # Fallback to 4B model if 270M not available
        for filename in self.available_models:
            if "4b" in filename.lower():
                return filename
        
        # If not found, return the first available model
        return next(iter(self.available_models))
    
    def _get_model_context_size(self, model_name: str) -> int:
        """Get context size for a model"""
        if model_name in self.available_models:
            return self.available_models[model_name]["ctx_size"]
        
        # Default conservative context size
        return 32768
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available models with their specs"""
        return self.available_models.copy()
    
    async def switch_model(self, model_name: str) -> bool:
        """Switch to a different model (requires server restart)"""
        if model_name not in self.available_models:
            logger.error(f"Model {model_name} not found in available models")
            return False
        
        if self.is_running:
            logger.info("🔄 Stopping current server to switch models...")
            await self.stop_server()
        
        # Update configuration
        self.current_model = model_name
        self.model_path = self.models_dir / model_name
        self.config.model_name = model_name
        self.config.ctx_size = self._get_model_context_size(model_name)
        
        logger.info(f"🔄 Switched to model: {model_name} (context: {self.config.ctx_size:,} tokens)")
        
        # Restart server with new model
        logger.info("🚀 Starting server with new model...")
        restart_success = await self.start_server()
        if restart_success:
            logger.info(f"✅ Successfully switched to model: {model_name}")
            return True
        else:
            logger.error(f"❌ Failed to restart server with model: {model_name}")
            return False
    
    def _validate_setup(self):
        """Validate that all required files exist"""
        if not self.server_binary.exists():
            raise FileNotFoundError(f"llama-server binary not found at {self.server_binary}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Gemma model not found at {self.model_path}")
        
        # Make binary executable
        os.chmod(self.server_binary, 0o755)
        
        logger.info(f"✅ Found llama-server: {self.server_binary}")
        logger.info(f"✅ Found Gemma model: {self.model_path} ({self.model_path.stat().st_size // (1024*1024)}MB)")
    
    async def start_server(self) -> bool:
        """Start the llama-server with Apple Silicon optimizations"""
        if self.is_running:
            logger.warning("Server already running")
            return True
        
        try:
            # Build command with optimizations
            cmd = [
                str(self.server_binary),
                "--model", str(self.model_path),
                "--host", self.config.host,
                "--port", str(self.config.server_port),
                "--ctx-size", str(self.config.ctx_size),
                "--threads", str(self.config.threads),
                "--gpu-layers", str(self.config.gpu_layers),
                "--batch-size", str(self.config.batch_size),
                "--timeout", str(self.config.timeout),
                "--cont-batching",  # Enable continuous batching
                "--flash-attn",     # Enable flash attention
                "--mlock",          # Keep model in RAM
                "--no-mmap",        # Don't memory map (better for Apple Silicon)
                "--chat-template", "gemma",  # Use Gemma chat template
                "--log-disable"     # Reduce noise
            ]
            
            logger.info("🚀 Starting llama-server with Apple Silicon optimizations...")
            logger.info(f"   Model: {self.model_path.name}")
            logger.info(f"   Context: {self.config.ctx_size:,} tokens")
            logger.info(f"   Port: {self.config.server_port}")
            
            # Start process
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.bin_dir
            )
            
            # Wait for server to be ready
            if await self._wait_for_server():
                self.is_running = True
                logger.info("✅ Local AI server ready!")
                return True
            else:
                logger.error("❌ Server failed to start properly")
                await self.stop_server()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    async def _wait_for_server(self, max_wait: int = 30) -> bool:
        """Wait for server to be ready"""
        health_url = f"http://{self.config.host}:{self.config.server_port}/health"
        completion_url = f"http://{self.config.host}:{self.config.server_port}/completion"
        
        for i in range(max_wait):
            try:
                async with aiohttp.ClientSession() as session:
                    # Check health endpoint
                    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                        if response.status == 200:
                            # Also test completion endpoint with minimal payload
                            test_payload = {"prompt": "test", "max_tokens": 1}
                            async with session.post(completion_url, json=test_payload, timeout=aiohttp.ClientTimeout(total=5)) as comp_response:
                                if comp_response.status == 200:
                                    logger.info(f"   ✅ Both health and completion endpoints ready")
                                    return True
                                else:
                                    logger.info(f"   ⏳ Health OK but completion not ready ({comp_response.status})")
            except Exception as e:
                if i % 5 == 0:
                    logger.info(f"   ⏳ Waiting for endpoints... ({i}/{max_wait}s) - {e}")
            
            await asyncio.sleep(1)
        
        return False
    
    async def stop_server(self):
        """Stop the llama-server"""
        if not self.server_process:
            return
        
        logger.info("🛑 Stopping local AI server...")
        
        try:
            # Graceful shutdown
            self.server_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.server_process.kill()
                self.server_process.wait()
            
            self.server_process = None
            self.is_running = False
            logger.info("✅ Server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health and get status"""
        try:
            url = f"http://{self.config.host}:{self.config.server_port}/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Update internal state if server is actually running
                        if not self.is_running:
                            logger.info("🔄 Detected running server, updating internal state")
                            self.is_running = True
                        
                        return {
                            "status": "healthy",
                            "model": self.model_path.name,
                            "context_size": self.config.ctx_size,
                            "server_info": data
                        }
                    else:
                        return {"status": "unhealthy", "http_status": response.status}
        except Exception as e:
            # Server is not reachable
            if self.is_running:
                logger.warning("🔄 Server not reachable, updating internal state")
                self.is_running = False
            return {"status": "stopped", "error": str(e)}
    
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using the local server"""
        # Check server health first (which will update internal state if needed)
        health = await self.health_check()
        if health.get("status") != "healthy":
            raise RuntimeError(f"Local AI server not available: {health.get('error', 'Unknown error')}")
        
        # Prepare request
        payload = {
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stop": kwargs.get("stop", []),
            "stream": False,
            "cache_prompt": True,  # Cache for efficiency
        }
        
        try:
            url = f"http://{self.config.host}:{self.config.server_port}/completion"
            logger.info(f"🌐 Making request to: {url}")
            logger.info(f"📦 Payload: {payload}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    logger.info(f"📡 Response status: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Success: {len(str(result))} chars")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error response: {error_text}")
                        raise RuntimeError(f"Server error {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"Completion error: {e}")
            raise
    
    async def generate_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion using OpenAI-compatible endpoint with Gemma chat template"""
        # Check server health first (which will update internal state if needed)
        health = await self.health_check()
        if health.get("status") != "healthy":
            raise RuntimeError(f"Local AI server not available: {health.get('error', 'Unknown error')}")
        
        # Prepare request for OpenAI-compatible chat completions
        payload = {
            "model": "gpt-3.5-turbo",  # Placeholder, server will use configured model
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": False,
        }
        
        try:
            url = f"http://{self.config.host}:{self.config.server_port}/v1/chat/completions"
            logger.info(f"🌐 Making chat completion request to: {url}")
            logger.info(f"📦 Messages: {len(messages)} messages")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    logger.info(f"📡 Response status: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Chat completion success: {len(str(result))} chars")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Chat completion error response: {error_text}")
                        raise RuntimeError(f"Server error {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise
    
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.server_process and self.is_running:
            try:
                self.server_process.terminate()
            except:
                pass


# Global instance
_local_ai_manager = None

def get_local_ai_manager() -> LocalAIManager:
    """Get the global LocalAIManager instance"""
    global _local_ai_manager
    if _local_ai_manager is None:
        _local_ai_manager = LocalAIManager()
    return _local_ai_manager


async def ensure_local_ai_running() -> bool:
    """Ensure local AI server is running"""
    manager = get_local_ai_manager()
    if not manager.is_running:
        return await manager.start_server()
    return True


async def cleanup_local_ai():
    """Cleanup local AI resources"""
    global _local_ai_manager
    if _local_ai_manager:
        await _local_ai_manager.stop_server()
        _local_ai_manager = None