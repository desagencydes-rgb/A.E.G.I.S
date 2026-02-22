"""
Tool Executor Agent
Handles file operations, system commands, and dangerous operations
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from core.permissions import PermissionGate, PermissionLevel
from loguru import logger
import json
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

class ToolExecutorAgent(BaseAgent):
    """
    Agent responsible for executing file system and system operations
    with permission gating
    """
    
    def __init__(self):
        super().__init__(
            name="ToolExecutor",
            agent_type="tool_executor"
        )
        
        self.permission_gate = PermissionGate()
        logger.info("ToolExecutor initialized with permission gating")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a tool execution task
        
        Task format:
        {
            "tool": "read_file" | "write_file" | "delete_file" | etc.,
            "params": {...},
            "user_message": str  # For permission checking
        }
        """
        tool_name = task.get("tool")
        params = task.get("params", {})
        user_message = task.get("user_message", "")
        
        # Check permissions
        allowed, reason = self.permission_gate.check_permission(
            tool_name=tool_name,
            user_message=user_message,
            tool_params=params
        )
        
        if not allowed:
            return {
                "success": False,
                "error": reason,
                "permission_denied": True
            }
        
        # Execute tool
        try:
            if tool_name == "read_file":
                result = await self._read_file(params)
            elif tool_name == "write_file":
                result = await self._write_file(params)
            elif tool_name == "delete_file":
                result = await self._delete_file(params, user_message)
            elif tool_name == "list_directory":
                result = await self._list_directory(params)
            elif tool_name == "run_command":
                result = await self._run_command(params)
            elif tool_name == "check_file_exists":
                result = await self._check_file_exists(params)
            elif tool_name == "search_web":
                result = await self._search_web(params)
            elif tool_name == "read_url":
                result = await self._read_url(params)
            elif tool_name == "analyze_code":
                result = await self._analyze_code(params)
            elif tool_name == "run_tests":
                result = await self._run_tests(params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
            
            return {
                "success": True,
                "result": result,
                "tool": tool_name
            }
            
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    # Tool implementations
    
    async def _read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        path = Path(params["path"])
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        content = path.read_text(encoding="utf-8")
        
        return {
            "path": str(path.absolute()),
            "content": content,
            "size": len(content),
            "lines": content.count('\n') + 1
        }
    
    async def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file"""
        path = Path(params["path"])
        content = params["content"]
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        path.write_text(content, encoding="utf-8")
        
        logger.info(f"Wrote file: {path}")
        
        return {
            "path": str(path.absolute()),
            "size": len(content),
            "created": True
        }
    
    async def _delete_file(self, params: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Delete file with backup (containment protocol)"""
        path = Path(params["path"])
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Create backup first (containment protocol)
        backup_path = self.permission_gate.create_backup_path(str(path))
        shutil.copy2(path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        # Delete file
        path.unlink()
        logger.warning(f"Deleted file: {path}")
        
        return {
            "path": str(path.absolute()),
            "deleted": True,
            "backup": backup_path
        }
    
    async def _list_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents"""
        path = Path(params["path"])
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Not a directory: {path}")
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "path": str(item.absolute()),
                "is_file": item.is_file(),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None
            })
        
        return {
            "path": str(path.absolute()),
            "items": items,
            "count": len(items)
        }
    
    async def _run_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run system command"""
        command = params["command"]
        cwd = params.get("cwd", ".")
        
        logger.info(f"Running command: {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        
        return {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    
    async def _check_file_exists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if file exists"""
        path = Path(params["path"])
        
        return {
            "path": str(path.absolute()),
            "exists": path.exists(),
            "is_file": path.is_file() if path.exists() else None,
            "is_dir": path.is_dir() if path.exists() else None
        }

    async def _search_web(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search the web using DuckDuckGo HTML"""
        query = params["query"]
        logger.info(f"Searching web for: {query}")
        
        try:
            logger.info("creating session")
            async with aiohttp.ClientSession() as session:
                url = "https://html.duckduckgo.com/html/"
                data = {"q": query}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                
                logger.info(f"sending post request to {url}")
                async with session.post(url, data=data, headers=headers) as response:
                    logger.info(f"received response: {response.status}")
                    if response.status != 200:
                        raise Exception(f"Search failed with status {response.status}")
                    
                    html = await response.text()
                    logger.info(f"read html: {len(html)} bytes")
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    for result in soup.find_all('div', class_='result'):
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem and snippet_elem:
                            results.append({
                                "title": title_elem.get_text(strip=True),
                                "link": title_elem['href'],
                                "snippet": snippet_elem.get_text(strip=True)
                            })
                            
                    logger.info(f"found {len(results)} results")
                    return {
                        "query": query,
                        "results": results[:5],  # Return top 5
                        "count": len(results)
                    }
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    async def _read_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read content from a URL"""
        url = params["url"]
        logger.info(f"Reading URL: {url}")
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch URL with status {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                    
                text = soup.get_text(separator='\\n', strip=True)
                
                # Clean up text (simple version)
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\\n'.join(chunk for chunk in chunks if chunk)
                
                return {
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "content": text[:8000],  # Limit content size
                    "length": len(text)
                }

    async def _analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run pylint on a file"""
        path = str(Path(params["path"]).absolute())
        logger.info(f"Analyzing code: {path}")
        
        # Run pylint
        # We use strict flags to keep it focused on errors/warnings
        cmd = ["pylint", "--output-format=text", "--reports=n", path]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True
        )
        
        # Pylint returns non-zero for issues, which is fine
        return {
            "path": path,
            "output": result.stdout,
            "success": True, # The tool execution was successful even if lint errors found
            "exit_code": result.returncode
        }

    async def _run_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run pytest on a file or directory"""
        path = str(Path(params["path"]).absolute())
        logger.info(f"Running tests: {path}")
        
        cmd = ["pytest", path, "-v"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        return {
            "path": path,
            "output": result.stdout + "\\n" + result.stderr,
            "passed": result.returncode == 0,
            "exit_code": result.returncode
        }
