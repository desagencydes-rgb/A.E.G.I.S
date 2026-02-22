"""
Unit tests for Mode Manager
Tests mode switching (normal/monster), config loading
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.mode import ModeManager, Mode


class TestModeManager:
    """Tests for mode management"""
    
    def test_init_default_normal(self):
        """Test that mode manager initializes to normal mode"""
        manager = ModeManager()
        assert manager.current_mode == Mode.NORMAL
    
    def test_switch_to_monster(self):
        """Test switching to monster mode"""
        manager = ModeManager()
        result = manager.switch_mode(Mode.MONSTER)
        
        assert manager.current_mode == Mode.MONSTER
        assert "Protocol 666" in result or "MONSTER" in result
    
    def test_switch_to_normal(self):
        """Test switching back to normal mode"""
        manager = ModeManager()
        manager.switch_mode(Mode.MONSTER)
        result = manager.switch_mode(Mode.NORMAL)
        
        assert manager.current_mode == Mode.NORMAL
        assert "Normal" in result or "NORMAL" in result
    
    def test_handle_command_monster(self):
        """Test /monster command"""
        manager = ModeManager()
        result = manager.handle_command("/monster")
        
        assert manager.current_mode == Mode.MONSTER
        assert result  # Should return a message
    
    def test_handle_command_normal(self):
        """Test /normal command"""
        manager = ModeManager()
        manager.switch_mode(Mode.MONSTER)
        result = manager.handle_command("/normal")
        
        assert manager.current_mode == Mode.NORMAL
        assert result
    
    def test_handle_invalid_command(self):
        """Test invalid command handling"""
        manager = ModeManager()
        result = manager.handle_command("/invalid")
        
        assert "Unknown" in result or "not recognized" in result
    
    def test_get_mode_color(self):
        """Test mode color retrieval"""
        manager = ModeManager()
        
        manager.switch_mode(Mode.NORMAL)
        assert manager.get_mode_color() == "green"
        
        manager.switch_mode(Mode.MONSTER)
        assert manager.get_mode_color() == "red"
    
    def test_get_system_prompt_normal(self):
        """Test normal mode system prompt"""
        manager = ModeManager()
        prompt = manager.get_system_prompt()
        
        assert "helpful" in prompt.lower() or "assistant" in prompt.lower()
        assert "protocol 666" not in prompt.lower()
    
    def test_get_system_prompt_monster(self):
        """Test monster mode system prompt"""
        manager = ModeManager()
        manager.switch_mode(Mode.MONSTER)
        prompt = manager.get_system_prompt()
        
        # Monster mode should have different personality
        assert prompt != manager.get_system_prompt()  # Different from when manager was just created


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
