"""
Core configuration management for AEGIS
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from enum import Enum

class Mode(Enum):
    """Operational modes"""
    NORMAL = "normal"
    MONSTER = "monster"  # Protocol 666
    HAT = "hat"  # Hacking & Attack Testing

class Config:
    """Central configuration management"""
    
    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Use .env.example as fallback
            load_dotenv(Path(__file__).parent.parent / ".env.example")
        
        self.config_dir = Path(__file__).parent.parent / "config"
        self.data_dir = Path(__file__).parent.parent / "data"
        
        # Core settings from environment
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.ollama_proxy_port = int(os.getenv("OLLAMA_PROXY_PORT", "11435"))
        self.dangerous_code = os.getenv("DANGEROUS_PERMISSION_CODE", "yesyesyes45")
        self.max_context = int(os.getenv("MAX_CONTEXT_TOKENS", "16384"))
        
        # Paths
        self.chromadb_path = Path(os.getenv("CHROMADB_PATH", "./data/vector_db"))
        self.sqlite_path = Path(os.getenv("SQLITE_DB_PATH", "./data/aegis.db"))
        self.log_file = Path(os.getenv("LOG_FILE", "./data/memory/logs/aegis.log"))
        
        # Model configs
        self.models = self._load_toml("models.toml")
        
        # Current mode
        self._current_mode = Mode(os.getenv("DEFAULT_MODE", "normal"))
        self.mode_config = self._load_mode_config(self._current_mode)
    
    def _load_toml(self, filename: str) -> Dict[str, Any]:
        """Load TOML configuration file"""
        path = self.config_dir / filename
        if path.exists():
            return toml.load(path)
        return {}
    
    def _load_mode_config(self, mode: Mode) -> Dict[str, Any]:
        """Load mode-specific configuration"""
        if mode == Mode.NORMAL:
            return self._load_toml("normal_mode.toml")
        elif mode == Mode.MONSTER:
            return self._load_toml("protocol_666.toml")
        elif mode == Mode.HAT:
            return self._load_toml("hat_mode.toml")
        else:
            return self._load_toml("normal_mode.toml")
    
    def switch_mode(self, new_mode: Mode):
        """Switch operational mode"""
        self._current_mode = new_mode
        self.mode_config = self._load_mode_config(new_mode)
    
    @property
    def current_mode(self) -> Mode:
        """Get current operational mode"""
        return self._current_mode
    
    @property
    def system_prompt(self) -> str:
        """Get system prompt for current mode"""
        return self.mode_config.get("prompts", {}).get("system_prompt", "")
    
    @property
    def orchestrator_model(self) -> str:
        """Get orchestrator model for current mode"""
        if self._current_mode == Mode.NORMAL:
            return self.models.get("orchestrator", {}).get("normal_model", "hermes3:8b")
        else:
            return self.models.get("orchestrator", {}).get("monster_model", "dolphin-llama3:8b")
    
    def get_agent_model(self, agent_name: str) -> str:
        """Get model for specific agent"""
        return self.models.get(agent_name, {}).get("model", "hermes3:8b")
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get full configuration for specific agent"""
        return self.models.get(agent_name, {})
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            self.chromadb_path,
            self.sqlite_path.parent,
            self.log_file.parent,
            self.data_dir / "memory" / "conversations",
            self.data_dir / "memory" / "knowledge",
            self.data_dir / "memory" / "logs",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

# Global config instance
config = Config()
