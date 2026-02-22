"""
Test script for AEGIS HAT mode security capabilities
"""

import sys
import asyncio
from pathlib import Path

# Configure logger to avoid Unicode errors on Windows
from loguru import logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

from core.config import config, Mode
from agents.security_agent import SecurityAgent
from tools.security_tools import SecurityToolkit
from core.adaptive_security import EvolutionaryFuzzer, FuzzTestCase


# Sample vulnerable code for testing
VULNERABLE_CODE_SAMPLES = {
    "sql_injection.py": """
import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # VULNERABLE: SQL injection via string formatting
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    return cursor.fetchone()

def login(username, password):
    # VULNERABLE: String concatenation in SQL
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()
""",
    "command_injection.py": """
import os
import subprocess

def ping_host(hostname):
    # VULNERABLE: Command injection  
    os.system(f"ping -c 1 {hostname}")

def backup_file(filename):
    # VULNERABLE: Shell=True with user input
    subprocess.run(f"tar -czf backup.tar.gz {filename}", shell=True)
""",
    "secrets.py": """
# VULNERABLE: Hardcoded credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

DATABASE_URL = "mysql://admin:password123@localhost/mydb"

api_key = "sk-1234567890abcdef1234567890abcdef"
""",
    "xss_vuln.js": """
function displayComment(comment) {
    // VULNERABLE: XSS via innerHTML
    document.getElementById('comments').innerHTML = comment;
}

function showMessage(msg) {
    // VULNERABLE: document.write with user input
    document.write("<p>" + msg + "</p>");
}
""",
    "deserialization.py": """
import pickle
import yaml

def load_user_data(data):
    # VULNERABLE: Unsafe deserialization
    user = pickle.loads(data)
    return user

def load_config(config_str):
    # VULNERABLE: yaml.load instead of safe_load
    config = yaml.load(config_str)
    return config
"""
}


async def test_vulnerability_scanner():
    """Test the vulnerability scanner"""
    logger.info("=" * 60)
    logger.info("Testing Vulnerability Scanner")
    logger.info("=" * 60)
    
    security_agent = SecurityAgent()
    
    for filename, code in VULNERABLE_CODE_SAMPLES.items():
        logger.info(f"\n[SCAN] Scanning {filename}...")
        
        findings = await security_agent.scan_code(code, filename)
        
        logger.info(f"[OK] Found {len(findings)} vulnerabilities")
        
        for finding in findings:
            logger.warning(
                f"  [{finding.severity}] {finding.title} "
                f"at {finding.location}"
            )
    
    # Generate comprehensive report
    all_findings = []
    for filename, code in VULNERABLE_CODE_SAMPLES.items():
        findings = await security_agent.scan_code(code, filename)
        all_findings.extend(findings)
    
    report = security_agent.generate_report(all_findings)
    
    # Save report
    report_path = Path("data/security_scan_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    
    logger.success(f"[REPORT] Report saved to {report_path}")
    
    return all_findings


async def test_security_toolkit():
    """Test the security toolkit (use with caution!)"""
    logger.info("=" * 60)
    logger.info("Testing Security Toolkit")
    logger.info("=" * 60)
    
    toolkit = SecurityToolkit()
    
    # Test header scanning (safe)
    logger.info("\n[WEB] Testing HTTP header scanner...")
    try:
        results = toolkit.web_scanner.scan_headers("https://example.com")
        logger.info(f"Missing headers: {results.get('missing_headers', [])}")
        logger.info(f"Issues found: {len(results.get('issues', []))}")
    except Exception as e:
        logger.error(f"Header scan error: {e}")
    
    # Test TLS analyzer (safe)
    logger.info("\n[TLS] Testing TLS analyzer...")
    try:
        tls_results = toolkit.tls_analyzer.analyze_tls("example.com")
        logger.info(f"TLS Version: {tls_results.get('tls_version')}")
        logger.info(f"Cipher: {tls_results.get('cipher')}")
        logger.info(f"Issues: {len(tls_results.get('issues', []))}")
    except Exception as e:
        logger.error(f"TLS analysis error: {e}")


def test_evolutionary_fuzzer():
    """Test the evolutionary fuzzer"""
    logger.info("=" * 60)
    logger.info("Testing Evolutionary Fuzzer")
    logger.info("=" * 60)
    
    fuzzer = EvolutionaryFuzzer(population_size=20)
    
    # Seed payloads
    seeds = [
        "test",
        "admin",
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "; ls",
        "../../etc/passwd"
    ]
    
    fuzzer.initialize_population(seeds)
    
    # Mock test function (simulates application testing)
    def mock_test_function(payload: str) -> tuple:
        """Simulate testing a payload"""
        interesting = False
        behavior = "normal response"
        
        # Simulate interesting responses
        if "error" in payload.lower() or "'" in payload:
            interesting = True
            behavior = "SQL error: syntax error near..."
        elif "<script>" in payload:
            interesting = True
            behavior = "Rendered in DOM without sanitization"
        elif len(payload) > 50:
            interesting = True
            behavior = "Long payload caused buffer issues"
        
        return interesting, behavior
    
    # Evolve for multiple generations
    logger.info("\n[EVOLUTION] Starting evolution...")
    for gen in range(5):
        fuzzer.evolve_generation(mock_test_function)
        
        best = fuzzer.get_best_test_cases(3)
        logger.info(f"\nGeneration {gen + 1} - Top 3 test cases:")
        for i, tc in enumerate(best, 1):
            logger.info(
                f"  {i}. Fitness: {tc.fitness_score:.1f} | "
                f"Payload: {tc.payload[:50]}..."
            )
    
    logger.success("\n[OK] Evolution complete!")
    logger.info(f"Best test case: {fuzzer.get_best_test_cases(1)[0].payload}")


async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("AEGIS HAT Mode - Security Testing Suite")
    logger.info("=" * 60)
    
    # Switch to HAT mode
    config.switch_mode(Mode.HAT)
    logger.info(f"[OK] Switched to {config.current_mode.value.upper()} mode")
    
    # Test 1: Vulnerability Scanner
    await test_vulnerability_scanner()
    
    # Test 2: Security Toolkit
    await test_security_toolkit()
    
    # Test 3: Evolutionary Fuzzer
    test_evolutionary_fuzzer()
    
    logger.success("\n" + "=" * 60)
    logger.success("All tests complete!")
    logger.success("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
