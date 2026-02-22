"""
Base Agent Class
Foundation for all specific agent implementations
"""

import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import ollama
from loguru import logger
from core.config import config, Mode

class BaseAgent(ABC):
    """
    Abstract base class for all AEGIS agents
    Handles interaction with Ollama and basic state management
    """
    
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self.agent_config = config.get_agent_config(agent_type)
        self.model = self.agent_config.get("model", "hermes3:8b")
        self.context: List[Dict[str, Any]] = []
        self.system_prompt = self._get_system_prompt()
        
        logger.info(f"Agent '{name}' initialized with model '{self.model}'")

    def _get_system_prompt(self) -> str:
        """Get system prompt - can be overridden by subclasses"""
        # Default to global system prompt if not overridden
        return config.system_prompt

    async def chat(
        self, 
        user_message: str, 
        stream: bool = True,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None] | str:
        """
        Send message to agent and get response
        """
        # Prepare messages
        messages = self._prepare_messages(user_message)
        
        # Use agent-specific config or fallback to defaults
        options = {
            "num_ctx": self.agent_config.get("context_window", config.max_context),
            "temperature": temperature or self.agent_config.get("temperature", 0.7)
        }
        
        # Add keep_alive if specified in agent config
        if "keep_alive" in self.agent_config:
            options["keep_alive"] = self.agent_config["keep_alive"]
        
        try:
            if stream:
                return self._chat_stream(messages, options)
            else:
                return await self._chat_sync(messages, options)
                
        except Exception as e:
            logger.error(f"Error in chat with {self.name}: {e}")
            raise

    async def _chat_stream(
        self, 
        messages: List[Dict[str, Any]], 
        options: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Handle streaming chat"""
        client = ollama.AsyncClient(host=config.ollama_host)
        
        async for part in await client.chat(
            model=self.model,
            messages=messages,
            options=options,
            stream=True
        ):
            if 'message' in part and 'content' in part['message']:
                yield part['message']['content']

    async def _chat_sync(
        self, 
        messages: List[Dict[str, Any]], 
        options: Dict[str, Any]
    ) -> str:
        """Handle synchronous chat"""
        client = ollama.AsyncClient(host=config.ollama_host)
        
        response = await client.chat(
            model=self.model,
            messages=messages,
            options=options,
            stream=False
        )
        
        return response['message']['content']

    def _prepare_messages(self, user_message: str) -> List[Dict[str, Any]]:
        """Prepare message history with system prompt"""
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ]
        
        # Add history (this is a simple implementation, will be enhanced with MemoryManager)
        messages.extend(self.context)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        return messages

    def update_context(self, role: str, content: str):
        """Update agent's short-term context"""
        self.context.append({"role": role, "content": content})
        # TODO: Implement sliding window or token limit check here

    def clear_context(self):
        """Clear short-term context context"""
        self.context = []

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a specific task delegated to this agent
        Must be implemented by subclasses
        """
        pass
