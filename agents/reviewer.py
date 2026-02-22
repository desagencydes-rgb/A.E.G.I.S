"""
Reviewer Agent
Performs code review, style checking, and security analysis
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from agents.tool_executor import ToolExecutorAgent
from loguru import logger
import re


class ReviewerAgent(BaseAgent):
    """Agent responsible for code review and quality checks"""
    
    def __init__(self):
        super().__init__(
            name="Reviewer",
            agent_type="reviewer"
        )
        self.tool_executor = ToolExecutorAgent()
        logger.info("ReviewerAgent initialized")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review  code and provide feedback
        
        Task format:
        {
            "file_path": str,      # File to review
            "review_type": str,    # "style", "security", "performance", "all"
            "auto_fix": bool       # Attempt to auto-fix issues (default: False)
        }
        """
        file_path = task.get("file_path")
        review_type = task.get("review_type", "all")
        auto_fix = task.get("auto_fix", False)
        
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        
        logger.info(f"Reviewing {file_path} for {review_type} issues")
        
        # Read the file
        read_task = {
            "tool": "read_file",
            "params": {"path": file_path},
            "user_message": "Reviewer reading file"
        }
        read_result = await self.tool_executor.process_task(read_task)
        
        if not read_result["success"]:
            return {"success": False, "error": "Could not read file"}
        
        content = read_result["result"].get("content", "")
        
        # Perform reviews based on type
        issues = []
        
        if review_type in ["style", "all"]:
            issues.extend(await self._check_style(file_path, content))
        
        if review_type in ["security", "all"]:
            issues.extend(self._check_security(content))
        
        if review_type in ["performance", "all"]:
            issues.extend(self._check_performance(content))
        
        return {
            "success": True,
            "file": file_path,
            "issues": issues,
            "issue_count": len(issues),
            "severity_breakdown": self._categorize_issues(issues)
        }
    
    async def _check_style(self, file_path: str, content: str) -> List[Dict]:
        """Check code style using static analysis"""
        issues = []
        
        if file_path.endswith(".py"):
            # Run flake8 or pylint if available
            analyze_task = {
                "tool": "analyze_code",
                "params": {"path": file_path},
                "user_message": "Reviewer checking style"
            }
            result = await self.tool_executor.process_task(analyze_task)
            
            if result["success"]:
                output = result["result"].get("output", "")
                # Parse pylint/flake8 output
                for line in output.split("\n"):
                    if line.strip():
                        issues.append({
                            "type": "style",
                            "severity": "medium",
                            "message": line.strip()
                        })
        
        return issues
    
    def _check_security(self, content: str) -> List[Dict]:
        """Check for common security issues"""
        issues = []
        
        # Check for common security anti-patterns
        patterns = [
            (r"eval\(", "Use of eval() is dangerous"),
            (r"exec\(", "Use of exec() is dangerous"),
            (r"pickle\.loads", "Pickle deserialization can be unsafe"),
            (r"shell=True", "shell=True in subprocess is risky"),
            (r"password\s*=\s*['\"]", "Hardcoded password detected")
        ]
        
        for pattern, message in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "message": message,
                    "line": content[:match.start()].count("\n") + 1
                })
        
        return issues
    
    def _check_performance(self, content: str) -> List[Dict]:
        """Check for performance issues"""
        issues = []
        
        # Check for O(n²) patterns
        if "for " in content and content.count("for ") > 1:
            # Nested loops detected (might be O(n²))
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "for " in line:
                    # Check if there's another for inside
                    indent = len(line) - len(line.lstrip())
                    for j in range(i+1, min(i+20, len(lines))):
                        next_line = lines[j]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent <= indent:
                            break
                        if "for " in next_line:
                            issues.append({
                                "type": "performance",
                                "severity": "medium",
                                "message": f"Potential O(n²) detected: nested loops at line {i+1}",
                                "line": i+1
                            })
                            break
        
        return issues
    
    def _categorize_issues(self, issues: List[Dict]) -> Dict[str, int]:
        """Categorize issues by severity"""
        breakdown = {"high": 0, "medium": 0, "low": 0}
        
        for issue in issues:
            severity = issue.get("severity", "medium")
            breakdown[severity] = breakdown.get(severity, 0) + 1
        
        return breakdown


if __name__ == "__main__":
    import asyncio
    
    async def test():
        reviewer = ReviewerAgent()
        result = await reviewer.process_task({
            "file_path": "test.py",
            "review_type": "all"
        })
        print(result)
    
    asyncio.run(test())
