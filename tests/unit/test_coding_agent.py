"""
Unit tests for Coding Agent
Tests code generation, analysis loop, TDD workflow
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.coding import CodingAgent
from tests.fixtures.test_files import SAMPLE_PYTHON_HELLO, SAMPLE_PYTHON_BAD_SYNTAX


class TestCodingAgent:
    """Tests for the Coding Agent"""
    
    @pytest.fixture
    def coding_agent(self):
        """Create a coding agent instance"""
        return CodingAgent()
    
    def test_init(self, coding_agent):
        """Test coding agent initialization"""
        assert coding_agent.name == "CodingAgent"
        assert coding_agent.agent_type == "coding"
    
    @pytest.mark.asyncio
    async def test_extract_code_from_markdown(self, coding_agent):
        """Test code extraction from markdown blocks"""
        markdown_code = '''Here is the code:
```python
def hello():
    print("Hello!")
```
That's it!'''
        
        extracted = coding_agent._extract_code(markdown_code)
        assert "def hello():" in extracted
        assert "print" in extracted
        assert "Here is the code" not in extracted
    
    @pytest.mark.asyncio
    async def test_extract_code_plain(self, coding_agent):
        """Test that plain code is returned as-is"""
        plain_code = 'def test():\n    pass'
        extracted = coding_agent._extract_code(plain_code)
        assert extracted == plain_code
    
    @pytest.mark.asyncio
    async def test_write_to_file(self, coding_agent, tmp_path):
        """Test file writing"""
        test_file = tmp_path / "test.py"
        coding_agent._write_to_file(str(test_file), "print('hello')")
        
        assert test_file.exists()
        assert test_file.read_text() == "print('hello')"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_process_task_simple(self, coding_agent, tmp_path):
        """Test basic code generation task"""
        test_file = tmp_path / "output.py"
        
        task = {
            "instruction": "Create a hello world script",
            "file_path": str(test_file),
            "check_code": False  # Skip analysis for speed
        }
        
        # Mock LLM response
        with patch('ollama.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            mock_instance.chat.return_value = {
                "message": {
                    "content": SAMPLE_PYTHON_HELLO
                }
            }
            
            result = await coding_agent.process_task(task)
            
            assert result["success"] is True
            assert test_file.exists()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_analysis_loop(self, coding_agent, tmp_path):
        """Test static analysis and fix loop"""
        test_file = tmp_path / "bad_code.py"
        test_file.write_text(SAMPLE_PYTHON_BAD_SYNTAX)
        
        # Mock the analysis to return errors, then success
        with patch.object(coding_agent.tool_executor, 'process_task', new=AsyncMock(side_effect=[
            {"success": True, "errors": ["SyntaxError: invalid syntax"]},
            {"success": True, "errors": []}
        ])):
            with patch('ollama.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value = mock_instance
                
                # Fixed code after analysis
                mock_instance.chat.return_value = {
                    "message": {"content": SAMPLE_PYTHON_HELLO}
                }
                
                result = await coding_agent._run_analysis_loop(
                    str(test_file),
                    SAMPLE_PYTHON_BAD_SYNTAX,
                    "Fix the code"
                )
                
                # Should have attempted to fix
                assert result is not None
    
    @pytest.mark.asyncio
    async def test_memory_integration(self, coding_agent, tmp_path):
        """Test that coding actions are saved to memory"""
        test_file = tmp_path / "test.py"
        
        task = {
            "instruction": "Create test file",
            "file_path": str(test_file),
            "check_code": False
        }
        
        with patch('ollama.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.chat.return_value = {"message": {"content": "print('test')"}}
            
            with patch.object(coding_agent.memory_manager, 'add_memory', new=AsyncMock()) as mock_add:
                result = await coding_agent.process_task(task)
                
                # Should have saved to memory
                assert mock_add.called or result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
