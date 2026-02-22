"""
Tool Definitions for Ollama
JSON Schemas for all available tools
"""

from typing import List, Dict, Any

# Tool definitions in the format expected by Ollama
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the specified path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content directly to a file at the specified path. Creates directories if needed. Use this for simple file creation when you know the exact content to write. For complex code generation or analysis, use delegate_coding instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List contents of a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the directory"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a system command in the terminal. Use with caution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Current working directory for execution (optional)"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file. Requires permission code for dangerous operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file to delete"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_file_exists",
            "description": "Check if a file or directory exists",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information using DuckDuckGo",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Read the content of a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to read"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delegate_research",
            "description": "Delegate a research task to the specialized Research Agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The research query or topic"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delegate_coding",
            "description": "Delegate a COMPLEX coding task to the specialized Coding Agent. Use this for: code generation with analysis/testing, refactoring existing code, or multi-file changes. For SIMPLE file creation with known content, use write_file directly instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instruction": {
                        "type": "string", 
                        "description": "What code to write or modify"
                    },
                    "file_path": {
                        "type": "string", 
                        "description": "Target file path (optional)"
                    }
                },
                "required": ["instruction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delegate_security",
            "description": "Delegate a security task to the Security Agent (HAT mode). Use for vulnerability scanning, security analysis, penetration testing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["scan_code", "scan_directory"],
                        "description": "Type of security task: scan_code for inline code or scan_directory for file system scanning"
                    },
                    "code": {
                        "type": "string",
                        "description": "Source code to scan (required for scan_code type)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "File path for reporting (optional for scan_code, required for scan_directory)"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory path to scan (required for scan_directory type)"
                    }
                },
                "required": ["type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delegate_feature_dev",
            "description": "Start a comprehensive 7-phase feature development workflow (Discovery, Exploration, Clarification, Architecture, Implementation, Review, Summary). Use for complex features that require architectural design.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feature_request": {
                        "type": "string",
                        "description": "Detailed description of the feature to build"
                    }
                },
                "required": ["feature_request"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_code",
            "description": "Run static code analysis (Pylint) on a python file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the python file to analyze"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run tests using pytest on a specific file or directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the test file or directory"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get all tool definitions"""
    return TOOLS
