"""
Coding Agent
Handles code generation, refactoring, and file modifications
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from agents.tool_executor import ToolExecutorAgent
from memory.manager import MemoryManager
from loguru import logger
import json

class CodingAgent(BaseAgent):
    """
    Agent responsible for code generation and modification
    """
    
    def __init__(self):
        super().__init__(
            name="CodingAgent",
            agent_type="coding"
        )
        self.tool_executor = ToolExecutorAgent()
        self.memory = MemoryManager()
        self.backups = {}  # Track backups for rollback
        logger.info("CodingAgent initialized with Memory Integration and Multi-File Support")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a coding task
        
        Task format:
        {
            "instruction": str,  # What to do
            "file_path": str,    # Target file (optional)
            "test_file": str,    # Test file to run (optional)
            "context_files": [], # Additional context files to analyze/modify (optional)
            "check_code": bool,  # Whether to run static analysis (default: True for python)
            "enable_rollback": bool  # Create backups for rollback (default: True)
        }
        """
        instruction = task.get("instruction")
        file_path = task.get("file_path")
        test_file = task.get("test_file")
        context_files = task.get("context_files", [])
        check_code = task.get("check_code", True)
        enable_rollback = task.get("enable_rollback", True)
        
        if not instruction:
            return {
                "success": False,
                "error": "No instruction provided for coding task"
            }
            
        logger.info(f"Coding task: {instruction} on {file_path}")
        
        # 1. Read existing content if applicable
        current_content = ""
        if file_path:
            read_task = {
                "tool": "read_file",
                "params": {"path": file_path},
                "user_message": "Coding Agent reading file"
            }
            read_result = await self.tool_executor.process_task(read_task)
            if read_result["success"]:
                current_content = read_result["result"].get("content", "")
            else:
                logger.warning(f"Could not read file {file_path}, assuming new file.")

        # 2. Generate initial code
        code = await self._generate_code(instruction, current_content, file_path)
        
        if not code:
            return {"success": False, "error": "Failed to generate initial code"}

        # 3. Handle multi-file modifications if context_files provided
        if context_files:
            logger.info(f"Multi-file refactoring across {len(context_files) + 1} files")
            # Create backups first
            if enable_rollback:
                await self._create_backups([file_path] + context_files)
            
            try:
                # Modify all files
                for ctx_file in context_files:
                    ctx_code = await self._generate_code(
                        f"Related to: {instruction}\nModify {ctx_file} accordingly",
                        "", ctx_file
                    )
                    if ctx_code:
                        await self._write_to_file(ctx_file, ctx_code)
            except Exception as e:
                logger.error(f"Multi-file refactoring error: {e}")
                if enable_rollback:
                    await self._rollback_changes()
                return {"success": False, "error": str(e)}
        
        # 4. Write initial code to main file
        if file_path:
            if enable_rollback and file_path not in self.backups:
                await self._create_backups([file_path])
            
            if not await self._write_to_file(file_path, code):
                if enable_rollback:
                    await self._rollback_changes()
                return {"success": False, "error": "Failed to write file"}
            
            # 4. Self-Correction Loop (Static Analysis)
            # Only for Python files and if enabled
            if check_code and file_path.endswith(".py"):
                code = await self._run_analysis_loop(file_path, code, instruction)
                
            # 5. Test Execution Loop
            # If test file is provided, run tests and self-correct
            if test_file:
                 code = await self._run_test_loop(file_path, test_file, code, instruction)

            # 6. Save to Memory (Architecture Log)
            try:
                memory_content = f"Coding Task: {instruction}\nFile Modified: {file_path}\n"
                if "class " in code:
                    memory_content += f"Defined classes in {file_path}"
                
                await self.memory.add_memory(
                    role="assistant",
                    content=memory_content,
                    metadata={
                        "type": "coding_log",
                        "file": file_path,
                        "agent": "coding"
                    }
                )
                logger.info("Saved coding log to memory")
            except Exception as e:
                logger.error(f"Failed to save to memory: {e}")

            return {
                "success": True,
                "action": "wrote_file",
                "file": file_path,
                "test_file": test_file,
                "content_preview": code[:100] + "..."
            }
            
        return {
            "success": True,
            "action": "generated_code",
            "content": code
        }

    async def _generate_code(self, instruction: str, current_content: str, file_path: Optional[str], feedback: str = "") -> Optional[str]:
        """Generate code using LLM"""
        prompt = f"Instruction: {instruction}\n\n"
        
        if file_path:
            prompt += f"Target File: {file_path}\n"
            
        if current_content:
            prompt += f"Current Content:\n```\n{current_content}\n```\n\n"
        
        if feedback:
            prompt += f"Previous Attempt Feedback (FIX THESE ISSUES):\n{feedback}\n\n"
            prompt += "Please rewrite the FULL content strictly fixing the issues above.\n"
        
        if current_content and not feedback:
            prompt += "Please provide the FULL new content for this file. Output ONLY the code within a Markdown code block."
        else:
            prompt += "Generate the code. Output ONLY the code within a Markdown code block."

        response = await self.chat(prompt, stream=False)
        return self._extract_code(response)

    async def _write_to_file(self, file_path: str, content: str) -> bool:
        """Helper to write file"""
        write_task = {
            "tool": "write_file",
            "params": {
                "path": file_path,
                "content": content
            },
            "user_message": f"Coding Agent writing to {file_path}"
        }
        result = await self.tool_executor.process_task(write_task)
        return result["success"]

    async def _run_analysis_loop(self, file_path: str, current_code: str, instruction: str) -> str:
        """Run analysis and fix loop"""
        max_retries = 2
        
        for i in range(max_retries):
            logger.info(f"Running analysis iteration {i+1}")
            
            # Run analysis
            analyze_task = {
                "tool": "analyze_code",
                "params": {"path": file_path},
                "user_message": "Coding Agent checking code"
            }
            result = await self.tool_executor.process_task(analyze_task)
            
            if not result["success"]:
                logger.warning("Analysis tool failed to run")
                break
                
            analysis_result = result["result"]
            exit_code = analysis_result.get("exit_code", 0)
            output = analysis_result.get("output", "")
            
            if exit_code == 0:
                logger.info("Code analysis passed!")
                break
                
            logger.info(f"Analysis found issues: {output[:200]}...")
            
            # Attempt fix
            new_code = await self._generate_code(
                instruction=instruction,
                current_content=current_code,
                file_path=file_path,
                feedback=f"Static Analysis Output (Pylint):\n{output}"
            )
            
            if new_code:
                current_code = new_code
                if await self._write_to_file(file_path, current_code):
                    logger.info("Applied fix, verifying...")
                else:
                    logger.error("Failed to write fix")
                    break
            else:
                logger.warning("Failed to generate fix")
                break
                
        return current_code

    async def _run_test_loop(self, file_path: str, test_file: str, current_code: str, instruction: str) -> str:
        """Run tests and fix loop"""
        max_retries = 3
        
        for i in range(max_retries):
            logger.info(f"Running test iteration {i+1}")
            
            # Run tests
            test_task = {
                "tool": "run_tests",
                "params": {"path": test_file},
                "user_message": "Coding Agent running tests"
            }
            
            result = await self.tool_executor.process_task(test_task)
            
            if not result["success"]:
                 logger.warning(f"Test tool failed to run: {result.get('error')}")
                 break
            
            test_result = result["result"]
            passed = test_result.get("passed", False)
            output = test_result.get("output", "")
            
            if passed:
                logger.info("Tests passed!")
                break
                
            logger.info(f"Tests failed: {output[:200]}...")
            
            # Attempt fix
            new_code = await self._generate_code(
                instruction=instruction,
                current_content=current_code,
                file_path=file_path,
                feedback=f"Test Execution Failed:\nOutput:\n{output}"
            )
            
            if new_code:
                current_code = new_code
                if await self._write_to_file(file_path, current_code):
                    logger.info("Applied fix for tests, verifying...")
                else:
                    logger.error("Failed to write test fix")
                    break
            else:
                 logger.warning("Failed to generate test fix")
                 break
        
        return current_code

    def _extract_code(self, text: str) -> Optional[str]:
        """Extract code from markdown code blocks"""
        if not text: return None
        if "```" not in text:
            return text.strip()
            
        if "```python" in text:
            parts = text.split("```python")
            if len(parts) > 1:
                return parts[1].split("```")[0].strip()
                
        parts = text.split("```")
        if len(parts) > 1:
            content = parts[1]
            if "\n" in content:
                # Remove language identifier if present
                first_line = content.split("\n", 1)[0].strip()
                if first_line and " " not in first_line:
                     return content.split("\n", 1)[1].strip()
            return content.strip()
            
        return None
    
    async def _create_backups(self, file_paths: List[str]) -> None:
        """Create backups of files for rollback"""
        from datetime import datetime
        
        for file_path in file_paths:
            try:
                read_task = {
                    "tool": "read_file",
                    "params": {"path": file_path},
                    "user_message": "Creating backup"
                }
                result = await self.tool_executor.process_task(read_task)
                
                if result["success"]:
                    self.backups[file_path] = {
                        "content": result["result"].get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    logger.info(f"Backed up {file_path}")
            except Exception as e:
                logger.warning(f"Could not backup {file_path}: {e}")
    
    async def _rollback_changes(self) -> None:
        """Rollback all changes using backups"""
        logger.warning("Rolling back changes due to error")
        
        for file_path, backup in self.backups.items():
            try:
                await self._write_to_file(file_path, backup["content"])
                logger.info(f"Rolled back {file_path}")
            except Exception as e:
                logger.error(f"Failed to rollback {file_path}: {e}")
        
        self.backups.clear()
