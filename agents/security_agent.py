"""
AEGIS Security Agent - HAT Mode
Advanced security testing and vulnerability analysis
"""

import re
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from loguru import logger
from agents.base_agent import BaseAgent
from core.config import config


class VulnerabilityCategory:
    """Common vulnerability categories"""
    SQL_INJECTION = "SQL Injection"
    XSS = "Cross-Site Scripting"
    CSRF = "Cross-Site Request Forgery"
    RCE = "Remote Code Execution"
    PATH_TRAVERSAL = "Path Traversal"
    INSECURE_DESERIALIZATION = "Insecure Deserialization"
    BROKEN_AUTH = "Broken Authentication"
    SENSITIVE_DATA = "Sensitive Data Exposure"
    XXE = "XML External Entities"
    SECURITY_MISCONFIG = "Security Misconfiguration"
    CRYPTO_FAILURE = "Cryptographic Failure"
    SSRF = "Server-Side Request Forgery"
    DEPENDENCY_VULN = "Vulnerable Dependency"


class Severity:
    """CVSS-based severity levels"""
    CRITICAL = "CRITICAL"  # 9.0-10.0
    HIGH = "HIGH"          # 7.0-8.9
    MEDIUM = "MEDIUM"      # 4.0-6.9
    LOW = "LOW"            # 0.1-3.9
    INFO = "INFO"          # 0.0


class SecurityFinding:
    """Represents a security vulnerability or issue"""
    
    def __init__(
        self,
        category: str,
        severity: str,
        title: str,
        description: str,
        location: str,
        evidence: str,
        remediation: str,
        cwe_id: Optional[str] = None,
        cvss_score: Optional[float] = None
    ):
        self.category = category
        self.severity = severity
        self.title = title
        self.description = description
        self.location = location
        self.evidence = evidence
        self.remediation = remediation
        self.cwe_id = cwe_id
        self.cvss_score = cvss_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score
        }


class SecurityAgent(BaseAgent):
    """
    Advanced Security Agent for vulnerability detection and penetration testing
    """
    
    def __init__(self):
        super().__init__("SecurityAgent", "security_agent")
        
        # Vulnerability patterns (static analysis)
        self.vuln_patterns = self._init_vulnerability_patterns()
        
        # Dangerous functions by language
        self.dangerous_functions = self._init_dangerous_functions()
        
        # Secrets and sensitive data patterns
        self.secret_patterns = self._init_secret_patterns()
        
        logger.info("Security Agent initialized in HAT mode")
    
    def _get_system_prompt(self) -> str:
        """Override to use HAT mode system prompt"""
        return config.system_prompt
    
    def _init_vulnerability_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize vulnerability detection patterns"""
        return {
            "sql_injection": [
                {
                    "pattern": r'(?:execute|query|executemany)\s*\(\s*["\'].*?%s.*?["\']',
                    "description": "String formatting in SQL query",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-89"
                },
                {
                    "pattern": r'(?:execute|query)\s*\(\s*.*?\+\s*',
                    "description": "String concatenation in SQL query",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-89"
                },
                {
                    "pattern": r'f["\'].*?(?:SELECT|INSERT|UPDATE|DELETE).*?\{.*?\}',
                    "description": "F-string interpolation in SQL",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-89"
                }
            ],
            "command_injection": [
                {
                    "pattern": r'(?:os\.system|subprocess\.call|subprocess\.run|exec|eval)\s*\(\s*.*?\+',
                    "description": "Command injection via concatenation",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-78"
                },
                {
                    "pattern": r'(?:os\.system|subprocess\.call)\s*\(\s*f["\']',
                    "description": "Command injection via f-string",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-78"
                },
                {
                    "pattern": r'shell\s*=\s*True',
                    "description": "Shell=True in subprocess (dangerous)",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-78"
                }
            ],
            "path_traversal": [
                {
                    "pattern": r'open\s*\(\s*.*?\+\s*.*?\)',
                    "description": "Path traversal in file open",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-22"
                },
                {
                    "pattern": r'os\.path\.join\s*\(.*?request\.',
                    "description": "User input in path construction",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-22"
                }
            ],
            "deserialization": [
                {
                    "pattern": r'pickle\.loads?\s*\(',
                    "description": "Unsafe deserialization with pickle",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-502"
                },
                {
                    "pattern": r'yaml\.load\s*\([^,)]*\)',
                    "description": "Unsafe YAML deserialization (use safe_load)",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-502"
                }
            ],
            "xss": [
                {
                    "pattern": r'\.innerHTML\s*=\s*.*?(?:req|input|params)',
                    "description": "XSS via innerHTML with user input",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-79"
                },
                {
                    "pattern": r'document\.write\s*\(\s*.*?(?:req|input|params)',
                    "description": "XSS via document.write",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-79"
                }
            ],
            "crypto_issues": [
                {
                    "pattern": r'hashlib\.(?:md5|sha1)\s*\(',
                    "description": "Weak cryptographic hash (MD5/SHA1)",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-327"
                },
                {
                    "pattern": r'Random\s*\(\s*\)',
                    "description": "Insecure random number generator",
                    "severity": Severity.MEDIUM,
                    "cwe": "CWE-338"
                }
            ]
        }
    
    def _init_dangerous_functions(self) -> Dict[str, List[str]]:
        """Functions that are commonly misused or dangerous"""
        return {
            "python": [
                "eval", "exec", "compile", "__import__",
                "os.system", "subprocess.call", "subprocess.run",
                "pickle.loads", "pickle.load",
                "yaml.load", "shelve.open"
            ],
            "javascript": [
                "eval", "Function", "setTimeout", "setInterval",
                "innerHTML", "document.write", "execScript"
            ],
            "php": [
                "eval", "assert", "system", "exec", "shell_exec",
                "passthru", "proc_open", "unserialize"
            ]
        }
    
    def _init_secret_patterns(self) -> Dict[str, str]:
        """Patterns for detecting secrets and credentials"""
        return {
            "AWS Access Key": r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
            "AWS Secret Key": r'(?i)aws(.{0,20})?[\'\"][0-9a-zA-Z\/+]{40}[\'\"]',
            "GitHub Token": r'ghp_[0-9a-zA-Z]{36}',
            "Generic API Key": r'(?i)(?:api[_-]?key|apikey)[\'\"]?\s*[:=]\s*[\'\"]?([0-9a-zA-Z\-_]{20,})[\'\"]?',
            "Generic Secret": r'(?i)(?:secret|password|passwd|pwd)[\'\"]?\s*[:=]\s*[\'\"]?([^\s\'\";]{8,})[\'\"]?',
            "Private Key": r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
            "JWT Token": r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
            "Database Connection": r'(?i)(?:mysql|postgres|mongodb):\/\/[^\s\'"]+',
            "Generic Password": r'(?i)password\s*=\s*["\'](?!.*\$\{)([^"\']{4,})["\']'
        }
    
    async def scan_code(self, code: str, file_path: str = "unknown") -> List[SecurityFinding]:
        """
        Scan code for security vulnerabilities
        
        Args:
            code: Source code to analyze
            file_path: Path to the file (for reporting)
            
        Returns:
            List of security findings
        """
        findings = []
        
        # 1. Pattern-based static analysis
        findings.extend(self._scan_vulnerability_patterns(code, file_path))
        
        # 2. Secret detection
        findings.extend(self._scan_secrets(code, file_path))
        
        # 3. Dangerous function usage
        findings.extend(self._scan_dangerous_functions(code, file_path))
        
        logger.info(f"Code scan complete: {len(findings)} findings in {file_path}")
        
        return findings
    
    def _scan_vulnerability_patterns(self, code: str, file_path: str) -> List[SecurityFinding]:
        """Scan for vulnerability patterns"""
        findings = []
        
        for category, patterns in self.vuln_patterns.items():
            for pattern_def in patterns:
                pattern = pattern_def["pattern"]
                matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Get line number
                    line_num = code[:match.start()].count('\n') + 1
                    
                    # Extract evidence (matched code)
                    evidence = match.group(0).strip()
                    
                    finding = SecurityFinding(
                        category=category.replace("_", " ").title(),
                        severity=pattern_def["severity"],
                        title=pattern_def["description"],
                        description=f"Potential {category.replace('_', ' ')} vulnerability detected",
                        location=f"{file_path}:line {line_num}",
                        evidence=evidence,
                        remediation=self._get_remediation(category),
                        cwe_id=pattern_def.get("cwe")
                    )
                    
                    findings.append(finding)
        
        return findings
    
    def _scan_secrets(self, code: str, file_path: str) -> List[SecurityFinding]:
        """Scan for hardcoded secrets and credentials"""
        findings = []
        
        for secret_type, pattern in self.secret_patterns.items():
            matches = re.finditer(pattern, code, re.MULTILINE)
            
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                
                # Redact the actual secret for safety
                evidence = match.group(0)
                if len(evidence) > 20:
                    evidence = evidence[:10] + "***REDACTED***" + evidence[-5:]
                
                finding = SecurityFinding(
                    category=VulnerabilityCategory.SENSITIVE_DATA,
                    severity=Severity.HIGH,
                    title=f"Hardcoded {secret_type} Detected",
                    description=f"Code contains what appears to be a hardcoded {secret_type}",
                    location=f"{file_path}:line {line_num}",
                    evidence=evidence,
                    remediation="Use environment variables or secure secret management (e.g., AWS Secrets Manager, HashiCorp Vault)",
                    cwe_id="CWE-798"
                )
                
                findings.append(finding)
        
        return findings
    
    def _scan_dangerous_functions(self, code: str, file_path: str) -> List[SecurityFinding]:
        """Scan for usage of dangerous functions"""
        findings = []
        
        # Detect language (simple heuristic)
        lang = self._detect_language(code)
        
        if lang in self.dangerous_functions:
            for func in self.dangerous_functions[lang]:
                # Create pattern to match function calls
                pattern = rf'\b{re.escape(func)}\s*\('
                matches = re.finditer(pattern, code)
                
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    
                    # Get context (full line)
                    line_start = code.rfind('\n', 0, match.start()) + 1
                    line_end = code.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(code)
                    evidence = code[line_start:line_end].strip()
                    
                    finding = SecurityFinding(
                        category=VulnerabilityCategory.SECURITY_MISCONFIG,
                        severity=Severity.MEDIUM,
                        title=f"Dangerous Function Usage: {func}",
                        description=f"The function '{func}' can be dangerous if used with untrusted input",
                        location=f"{file_path}:line {line_num}",
                        evidence=evidence,
                        remediation=f"Avoid using '{func}' with user-controlled input. Use safer alternatives.",
                        cwe_id="CWE-676"
                    )
                    
                    findings.append(finding)
        
        return findings
    
    def _detect_language(self, code: str) -> str:
        """Simple language detection"""
        if "def " in code or "import " in code:
            return "python"
        elif "function " in code or "const " in code or "let " in code:
            return "javascript"
        elif "<?php" in code:
            return "php"
        return "unknown"
    
    def _get_remediation(self, category: str) -> str:
        """Get remediation advice for vulnerability category"""
        remediation_map = {
            "sql_injection": "Use parameterized queries or prepared statements. Never concatenate user input into SQL queries.",
            "command_injection": "Avoid shell=True. Use argument lists instead of string commands. Validate and sanitize all input.",
            "path_traversal": "Validate file paths against a whitelist. Use os.path.abspath() and check if result is within allowed directory.",
            "deserialization": "Use safe deserialization methods (e.g., yaml.safe_load). Avoid pickle with untrusted data.",
            "xss": "Sanitize and encode all user input before rendering. Use Content Security Policy (CSP).",
            "crypto_issues": "Use SHA-256 or stronger. Use secrets module for random numbers in security contexts."
        }
        
        return remediation_map.get(category, "Review code for security implications and apply defense-in-depth principles.")
    
    def generate_report(self, findings: List[SecurityFinding]) -> str:
        """Generate a comprehensive security report"""
        # Group by severity
        by_severity = {
            Severity.CRITICAL: [],
            Severity.HIGH: [],
            Severity.MEDIUM: [],
            Severity.LOW: [],
            Severity.INFO: []
        }
        
        for finding in findings:
            by_severity[finding.severity].append(finding)
        
        # Build report
        report_lines = [
            "# Security Scan Report",
            "",
            f"## Summary",
            f"- **Total Findings**: {len(findings)}",
            f"- **Critical**: {len(by_severity[Severity.CRITICAL])} [CRITICAL]",
            f"- **High**: {len(by_severity[Severity.HIGH])} [HIGH]",
            f"- **Medium**: {len(by_severity[Severity.MEDIUM])} [MEDIUM]",
            f"- **Low**: {len(by_severity[Severity.LOW])} [LOW]",
            f"- **Info**: {len(by_severity[Severity.INFO])} [INFO]",
            "",
            "---",
            ""
        ]
        
        # Add detailed findings by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            if by_severity[severity]:
                report_lines.append(f"## {severity} Severity Findings")
                report_lines.append("")
                
                for i, finding in enumerate(by_severity[severity], 1):
                    report_lines.extend([
                        f"### {i}. {finding.title}",
                        f"**Category**: {finding.category}",
                        f"**Location**: `{finding.location}`",
                        f"**CWE**: {finding.cwe_id or 'N/A'}",
                        "",
                        f"**Description**: {finding.description}",
                        "",
                        "**Evidence**:",
                        "```",
                        finding.evidence,
                        "```",
                        "",
                        f"**Remediation**: {finding.remediation}",
                        "",
                        "---",
                        ""
                    ])
        
        return "\n".join(report_lines)
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process security-related task"""
        task_type = task.get("type")
        
        if task_type == "scan_code":
            code = task.get("code", "")
            file_path = task.get("file_path", "unknown")
            findings = await self.scan_code(code, file_path)
            
            return {
                "status": "complete",
                "findings": [f.to_dict() for f in findings],
                "report": self.generate_report(findings)
            }
        
        elif task_type == "scan_directory":
            directory = Path(task.get("directory"))
            all_findings = []
            
            # Scan all code files
            for ext in ['.py', '.js', '.php', '.java', '.go']:
                for file_path in directory.rglob(f'*{ext}'):
                    try:
                        code = file_path.read_text(encoding='utf-8')
                        findings = await self.scan_code(code, str(file_path))
                        all_findings.extend(findings)
                    except Exception as e:
                        logger.error(f"Error scanning {file_path}: {e}")
            
            return {
                "status": "complete",
                "findings": [f.to_dict() for f in all_findings],
                "report": self.generate_report(all_findings)
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
