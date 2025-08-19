"""
Context Manager for efficient prompt handling with dynamic context windows

Handles context compression, truncation, and optimization for different models
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ContextStats:
    """Statistics about context usage"""
    total_tokens: int
    system_tokens: int
    history_tokens: int
    current_tokens: int
    available_tokens: int
    compression_ratio: float = 0.0

class ContextManager:
    """Manages context windows efficiently for different models"""
    
    def __init__(self, max_context: int = 32768):
        self.max_context = max_context
        self.reserved_response_tokens = 1000  # Reserve space for response
        self.system_prompt_limit = 4000  # Max tokens for system prompts
        
        # Rough token estimation (more accurate would use tiktoken)
        self.chars_per_token = 4  # Conservative estimate
        
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation based on character count"""
        return max(1, len(text) // self.chars_per_token)
    
    def optimize_context(
        self,
        system_prompt: str,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        personality_data: Optional[str] = None
    ) -> Tuple[str, str, List[Dict[str, str]], ContextStats]:
        """
        Optimize context to fit within model limits
        Returns: (optimized_system_prompt, user_message, optimized_history, stats)
        """
        
        available_tokens = self.max_context - self.reserved_response_tokens
        
        # Estimate token usage
        system_tokens = self.estimate_tokens(system_prompt)
        user_tokens = self.estimate_tokens(user_message) 
        personality_tokens = self.estimate_tokens(personality_data or "")
        
        # Calculate tokens used by history
        history_tokens = 0
        optimized_history = chat_history or []
        
        if chat_history:
            history_tokens = sum(
                self.estimate_tokens(msg["content"]) 
                for msg in chat_history
            )
        
        total_tokens = system_tokens + user_tokens + personality_tokens + history_tokens
        
        logger.info(f"📊 Context analysis: {total_tokens:,}/{available_tokens:,} tokens")
        
        # If we're over the limit, optimize
        if total_tokens > available_tokens:
            logger.info("⚠️ Context exceeds limit, optimizing...")
            
            # Strategy 1: Compress system prompt if too long
            if system_tokens > self.system_prompt_limit:
                system_prompt = self._compress_system_prompt(system_prompt)
                system_tokens = self.estimate_tokens(system_prompt)
                logger.info(f"📝 Compressed system prompt: {system_tokens} tokens")
            
            # Strategy 2: Truncate/summarize history
            if total_tokens > available_tokens:
                optimized_history = self._optimize_history(
                    chat_history or [],
                    target_tokens=available_tokens - system_tokens - user_tokens - personality_tokens
                )
                history_tokens = sum(
                    self.estimate_tokens(msg["content"]) 
                    for msg in optimized_history
                )
                logger.info(f"💬 Optimized history: {len(optimized_history)} messages, {history_tokens} tokens")
        
        # Final stats
        final_tokens = system_tokens + user_tokens + personality_tokens + history_tokens
        compression_ratio = 1.0 - (final_tokens / max(1, total_tokens)) if total_tokens > available_tokens else 0.0
        
        stats = ContextStats(
            total_tokens=final_tokens,
            system_tokens=system_tokens,
            history_tokens=history_tokens,
            current_tokens=user_tokens,
            available_tokens=available_tokens - final_tokens,
            compression_ratio=compression_ratio
        )
        
        if compression_ratio > 0:
            logger.info(f"✂️ Context compressed by {compression_ratio:.1%}")
        
        return system_prompt, user_message, optimized_history, stats
    
    def _compress_system_prompt(self, prompt: str) -> str:
        """Compress system prompt while preserving key information"""
        
        # Remove excessive whitespace and newlines
        compressed = re.sub(r'\n\s*\n\s*', '\n\n', prompt)
        compressed = re.sub(r' +', ' ', compressed)
        
        # Keep critical sections but compress examples
        lines = compressed.split('\n')
        essential_lines = []
        
        skip_examples = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip verbose examples if we're running out of space
            if 'example:' in line.lower() or 'for example:' in line.lower():
                skip_examples = True
                continue
            elif skip_examples and (line.startswith('#') or line.isupper()):
                skip_examples = False
            
            if not skip_examples:
                essential_lines.append(line)
        
        result = '\n'.join(essential_lines)
        
        # If still too long, more aggressive compression
        if self.estimate_tokens(result) > self.system_prompt_limit:
            # Keep only the most critical parts
            critical_sections = []
            for line in essential_lines:
                if any(keyword in line.upper() for keyword in 
                      ['CRITICAL:', 'IMPORTANT:', 'MUST:', 'SPEECH STYLE', 'PERSONALITY']):
                    critical_sections.append(line)
                elif len(' '.join(critical_sections)) < self.system_prompt_limit * self.chars_per_token:
                    critical_sections.append(line)
            
            result = '\n'.join(critical_sections)
        
        return result
    
    def _optimize_history(
        self, 
        history: List[Dict[str, str]], 
        target_tokens: int
    ) -> List[Dict[str, str]]:
        """Optimize chat history to fit within token budget"""
        
        if not history:
            return []
        
        if target_tokens <= 0:
            logger.warning("No tokens available for history")
            return []
        
        # Strategy 1: Keep recent messages first (sliding window)
        optimized = []
        current_tokens = 0
        
        # Process from most recent backwards
        for msg in reversed(history):
            msg_tokens = self.estimate_tokens(msg["content"])
            
            if current_tokens + msg_tokens <= target_tokens:
                optimized.insert(0, msg)  # Insert at beginning to maintain order
                current_tokens += msg_tokens
            else:
                break
        
        # Strategy 2: If we have very little space, summarize older messages
        if len(optimized) < len(history) and len(optimized) > 2:
            # Keep first and last few messages, summarize middle
            if len(history) > 6:
                summary_msg = {
                    "role": "assistant",
                    "content": f"[Previous conversation covered: user questions, creature responses, relationship building - {len(history) - len(optimized)} messages summarized]"
                }
                
                # Try to fit summary
                summary_tokens = self.estimate_tokens(summary_msg["content"])
                if current_tokens + summary_tokens <= target_tokens:
                    optimized.insert(-2, summary_msg)  # Insert before last two messages
        
        if len(optimized) < len(history):
            logger.info(f"📚 History truncated: {len(optimized)}/{len(history)} messages kept")
        
        return optimized
    
    def get_context_utilization(self, text_length: int) -> Dict[str, Any]:
        """Get context window utilization stats"""
        estimated_tokens = self.estimate_tokens(" " * text_length)  
        utilization = estimated_tokens / self.max_context
        
        return {
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.max_context,
            "utilization_percent": utilization * 100,
            "available_tokens": self.max_context - estimated_tokens,
            "status": "optimal" if utilization < 0.7 else "high" if utilization < 0.9 else "critical"
        }
    
    def update_context_limit(self, new_limit: int):
        """Update context limit for different models"""
        old_limit = self.max_context
        self.max_context = new_limit
        logger.info(f"📏 Context limit updated: {old_limit:,} → {new_limit:,} tokens")
        
        # Adjust response token reservation for larger models
        if new_limit > 100000:  # 100k+ context models
            self.reserved_response_tokens = 2000
        elif new_limit > 50000:  # 50k+ context models  
            self.reserved_response_tokens = 1500
        else:
            self.reserved_response_tokens = 1000