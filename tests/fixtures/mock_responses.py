"""
Mock LLM responses for deterministic testing
"""

MOCK_RESPONSES = {
    "normal_greeting": {
        "content": "Hello! I'm AEGIS, your AI assistant. How can I help you today?",
        "tool_calls": None
    },
    
    "monster_greeting": {
        "content": "Protocol 666 active. What do you need?",
        "tool_calls": None
    },
    
    "delegate_research": {
        "content": "",
        "tool_calls": [{
            "function": {
                "name": "delegate_research",
                "arguments": {"query": "Python 3.12 features"}
            }
        }]
    },
    
    "delegate_coding": {
        "content": "",
        "tool_calls": [{
            "function": {
                "name": "delegate_coding",
                "arguments": {
                    "instruction": "Create hello world script",
                    "file_path": "test_hello.py"
                }
            }
        }]
    },
    
    "research_summary": {
        "content": "Python 3.12 introduces improved error messages, better performance, and new syntax features.",
        "tool_calls": None
    },
    
    "code_generation": {
        "content": """```python
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```""",
        "tool_calls": None
    },
    
    "code_with_fix": {
        "content": """```python
def fixed_function():
    print("Now with colon!")
    return None
```""",
        "tool_calls": None
    }
}


def get_mock_response(response_type: str):
    """Get a mock response by type"""
    return MOCK_RESPONSES.get(response_type, MOCK_RESPONSES["normal_greeting"])
