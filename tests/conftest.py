"""
Pytest fixtures and configuration for AEGIS tests
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Config for ChromaDB to avoid issues
os.environ["CHROMA_SERVER_NOFILE"] = "65535"


@pytest.fixture
def temp_test_dir(tmp_path):
    """Provide a temporary directory for test files"""
    test_dir = tmp_path / "aegis_test"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def mock_llm_response():
    """Factory for creating mock LLM responses"""
    def _create_response(content: str, tool_calls: list = None):
        response = {
            "message": {
                "role": "assistant",
                "content": content
            }
        }
        if tool_calls:
            response["message"]["tool_calls"] = tool_calls
        return response
    return _create_response


@pytest.fixture
def sample_code_python():
    """Sample Python code for testing"""
    return '''
def hello_world():
    """Print a greeting"""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
'''


@pytest.fixture
def sample_code_with_errors():
    """Sample Python code with intentional errors"""
    return '''
def broken_function()
    print("Missing colon"
    return None
'''


@pytest.fixture
def mock_research_results():
    """Mock web search results"""
    return {
        "success": True,
        "results": [
            {"title": "Python 3.12 Features", "url": "https://example.com/py312", "snippet": "New features include..."},
            {"title": "What's New", "url": "https://docs.python.org/3.12", "snippet": "Python 3.12 adds..."}
        ],
        "summary": "Python 3.12 introduces several new features including improved error messages and performance enhancements."
    }


@pytest.fixture
def mock_tool_call():
    """Factory for creating mock tool calls"""
    def _create_tool_call(function_name: str, arguments: Dict[str, Any]):
        return {
            "function": {
                "name": function_name,
                "arguments": arguments
            }
        }
    return _create_tool_call


@pytest.fixture
async def cleanup_test_files():
    """Cleanup fixture that runs after tests"""
    test_files = []
    
    def register(filepath):
        test_files.append(filepath)
    
    yield register
    
    # Cleanup
    for filepath in test_files:
        if os.path.exists(filepath):
            os.remove(filepath)
