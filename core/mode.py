"""
Mode management for AEGIS
Handles switching between Normal and Monster Mode (Protocol 666)
"""

from enum import Enum
from typing import Optional
from loguru import logger

class Mode(Enum):
    """Operational modes"""
    NORMAL = "normal"
    MONSTER = "monster"  # Protocol 666
    HAT = "hat"  # Hacking & Attack Testing

class ModeManager:
    """Manages mode switching and mode-specific behavior"""
    
    # Keywords that trigger mode switches
    MONSTER_KEYWORDS = [
        "/monster", "/protocol666", "/unleash", 
        "protocol 666", "/p666"
    ]
    
    HAT_KEYWORDS = [
        "/hat", "/security", "/pentest", "/hack"
    ]
    
    NORMAL_KEYWORDS = [
        "/normal", "/safe", "/standard", "/reset"
    ]
    
    def __init__(self, initial_mode: Mode = Mode.NORMAL):
        self._current_mode = initial_mode
        self._mode_history = [initial_mode]
        logger.info(f"ModeManager initialized in {initial_mode.value} mode")
    
    @property
    def current_mode(self) -> Mode:
        """Get current operational mode"""
        return self._current_mode
    
    @property
    def is_monster_mode(self) -> bool:
        """Check if currently in Monster Mode (Protocol 666)"""
        return self._current_mode == Mode.MONSTER
    
    @property
    def is_normal_mode(self) -> bool:
        """Check if currently in Normal Mode"""
        return self._current_mode == Mode.NORMAL
    
    def switch_mode(self, new_mode: Mode) -> bool:
        """
        Switch to a new mode
        
        Returns:
            True if mode changed, False if already in that mode
        """
        if self._current_mode == new_mode:
            logger.debug(f"Already in {new_mode.value} mode")
            return False
        
        old_mode = self._current_mode
        self._current_mode = new_mode
        self._mode_history.append(new_mode)
        
        logger.info(f"Mode switch: {old_mode.value} → {new_mode.value}")
        return True
    
    def detect_mode_switch(self, user_message: str) -> Optional[Mode]:
        """
        Detect if user message contains mode switch keyword
        
        Returns:
            New mode if switch detected, None otherwise
        """
        message_lower = user_message.lower()
        
        # Check for monster mode keywords
        for keyword in self.MONSTER_KEYWORDS:
            if keyword in message_lower:
                return Mode.MONSTER
        
        # Check for HAT mode keywords
        for keyword in self.HAT_KEYWORDS:
            if keyword in message_lower:
                return Mode.HAT
        
        # Check for normal mode keywords
        for keyword in self.NORMAL_KEYWORDS:
            if keyword in message_lower:
                return Mode.NORMAL
        
        return None
        
    def handle_command(self, command: str) -> str:
        """Handle a mode switch command"""
        new_mode = self.detect_mode_switch(command)
        
        if not new_mode:
            return "Unknown command or no mode switch detected."
            
        if self.switch_mode(new_mode):
            if new_mode == Mode.MONSTER:
                return "PROTOCOL 666 ACTIVATED. SAFETY SYSTEMS DISENGAGED. 💀⚡"
            elif new_mode == Mode.HAT:
                return "HAT MODE ACTIVATED. Security research tools armed. Ethical testing only. 🎯🔐"
            else:
                return "Returning to Normal Mode. Safety systems re-engaged. 🛡️"
        else:
            return f"Already in {new_mode.value} mode."

    def get_mode_emoji(self) -> str:
        """Get emoji representation of current mode"""
        if self._current_mode == Mode.MONSTER:
            return "💀⚡"
        elif self._current_mode == Mode.HAT:
            return "🎯🔐"
        else:
            return "🛡️✨"
    
    def get_mode_display_name(self) -> str:
        """Get display name for current mode"""
        if self._current_mode == Mode.MONSTER:
            return "PROTOCOL 666"
        elif self._current_mode == Mode.HAT:
            return "HAT MODE"
        else:
            return "NORMAL MODE"
    
    def get_mode_color(self) -> str:
        """Get Rich color for current mode"""
        if self._current_mode == Mode.MONSTER:
            return "red"
        elif self._current_mode == Mode.HAT:
            return "cyan"
        else:
            return "green"
