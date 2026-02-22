"""
Advanced Security Tools for AEGIS HAT Mode
Network scanning, web testing, and threat intelligence
"""

import socket
import ssl
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from loguru import logger
from pathlib import Path


class PortScanner:
    """Network port scanner with service detection"""
    
    COMMON_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        6379: "Redis",
        8080: "HTTP-Alt",
        8443: "HTTPS-Alt",
        27017: "MongoDB"
    }
    
    @staticmethod
    def scan_port(host: str, port: int, timeout: float = 1.0) -> Dict[str, Any]:
        """
        Scan a single port
        
        Args:
            host: Target host
            port: Port number  
            timeout: Connection timeout
            
        Returns:
            Dict with port info
        """
        result = {
            "port": port,
            "service": PortScanner.COMMON_PORTS.get(port, "Unknown"),
            "state": "closed",
            "banner": None
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Try to connect
            connection_result = sock.connect_ex((host, port))
            
            if connection_result == 0:
                result["state"] = "open"
                
                # Try banner grabbing
                try:
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        result["banner"] = banner[:200]  # Limit banner length
                except:
                    pass
            
            sock.close()
            
        except socket.timeout:
            result["state"] = "filtered"
        except Exception as e:
            logger.debug(f"Error scanning {host}:{port} - {e}")
        
        return result
    
    @staticmethod
    def scan_ports(host: str, ports: List[int], timeout: float = 1.0) -> List[Dict[str, Any]]:
        """
        Scan multiple ports
        
        Args:
            host: Target host
            ports: List of ports to scan
            timeout: Connection timeout per port
            
        Returns:
            List of port scan results
        """
        results = []
        
        logger.info(f"Scanning {len(ports)} ports on {host}")
        
        for port in ports:
            result = PortScanner.scan_port(host, port, timeout)
            if result["state"] != "closed":
                results.append(result)
                logger.info(f"Found open port: {port} ({result['service']})")
        
        return results


class TLSAnalyzer:
    """Analyze TLS/SSL configuration"""
    
    @staticmethod
    def analyze_tls(hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Analyze TLS configuration
        
        Args:
            hostname: Target hostname
            port: HTTPS port
            
        Returns:
            TLS configuration analysis
        """
        result = {
            "hostname": hostname,
            "port": port,
            "tls_version": None,
            "cipher": None,
            "certificate": {},
            "issues": []
        }
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get TLS version
                    result["tls_version"] = ssock.version()
                    
                    # Get cipher
                    result["cipher"] = ssock.cipher()[0]
                    
                    # Get certificate info
                    cert = ssock.getpeercert()
                    result["certificate"] = {
                        "subject": dict(x[0] for x in cert.get('subject', [])),
                        "issuer": dict(x[0] for x in cert.get('issuer', [])),
                        "version": cert.get('version'),
                        "serialNumber": cert.get('serialNumber'),
                        "notBefore": cert.get('notBefore'),
                        "notAfter": cert.get('notAfter')
                    }
                    
                    # Check for issues
                    if result["tls_version"] in ["TLSv1", "TLSv1.1", "SSLv2", "SSLv3"]:
                        result["issues"].append({
                            "severity": "HIGH",
                            "title": f"Outdated TLS version: {result['tls_version']}",
                            "remediation": "Upgrade to TLS 1.2 or higher"
                        })
                    
                    # Check weak ciphers
                    weak_ciphers = ["RC4", "DES", "3DES", "MD5"]
                    if any(weak in result["cipher"] for weak in weak_ciphers):
                        result["issues"].append({
                            "severity": "MEDIUM",
                            "title": f"Weak cipher suite: {result['cipher']}",
                            "remediation": "Use strong cipher suites (AES-GCM, ChaCha20)"
                        })
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"TLS analysis failed for {hostname}:{port} - {e}")
        
        return result


class WebSecurityScanner:
    """Basic web application security scanner"""
    
    @staticmethod
    def scan_headers(url: str) -> Dict[str, Any]:
        """
        Analyze HTTP security headers
        
        Args:
            url: Target URL
            
        Returns:
            Security header analysis
        """
        result = {
            "url": url,
            "present_headers": {},
            "missing_headers": [],
            "issues": []
        }
        
        # Security headers to check
        security_headers = {
            "Strict-Transport-Security": "HSTS not enabled",
            "Content-Security-Policy": "CSP not configured",
            "X-Frame-Options": "Clickjacking protection missing",
            "X-Content-Type-Options": "MIME-sniffing protection missing",
            "X-XSS-Protection": "XSS protection header missing",
            "Referrer-Policy": "Referrer policy not set",
            "Permissions-Policy": "Permissions policy not configured"
        }
        
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            # Check for security headers
            for header, issue in security_headers.items():
                if header in response.headers:
                    result["present_headers"][header] = response.headers[header]
                else:
                    result["missing_headers"].append(header)
                    result["issues"].append({
                        "severity": "MEDIUM",
                        "title": issue,
                        "header": header,
                        "remediation": f"Add '{header}' header to HTTP responses"
                    })
            
            # Check for information disclosure
            info_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
            for header in info_headers:
                if header in response.headers:
                    result["issues"].append({
                        "severity": "LOW",
                        "title": f"Information disclosure via '{header}' header",
                        "value": response.headers[header],
                        "remediation": f"Remove or obfuscate '{header}' header"
                    })
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Header scan failed for {url} - {e}")
        
        return result
    
    @staticmethod
    def test_http_methods(url: str) -> Dict[str, Any]:
        """
        Test which HTTP methods are allowed
        
        Args:
            url: Target URL
            
        Returns:
            HTTP methods analysis
        """
        result = {
            "url": url,
            "allowed_methods": [],
            "issues": []
        }
        
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE"]
        
        try:
            for method in methods:
                try:
                    response = requests.request(method, url, timeout=5)
                    if response.status_code != 405:  # Method Not Allowed
                        result["allowed_methods"].append(method)
                except:
                    pass
            
            # Check for dangerous methods
            dangerous = ["PUT", "DELETE", "TRACE"]
            enabled_dangerous = [m for m in dangerous if m in result["allowed_methods"]]
            
            if enabled_dangerous:
                result["issues"].append({
                    "severity": "MEDIUM",
                    "title": f"Dangerous HTTP methods enabled: {', '.join(enabled_dangerous)}",
                    "remediation": "Disable unnecessary HTTP methods on production servers"
                })
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"HTTP method test failed for {url} - {e}")
        
        return result


class ThreatIntelligence:
    """Threat intelligence lookup (CVE, CWE databases)"""
    
    @staticmethod
    def lookup_cve(cve_id: str) -> Optional[Dict[str, Any]]:
        """
        Look up CVE information
        
        Args:
            cve_id: CVE identifier (e.g., CVE-2021-44228)
            
        Returns:
            CVE information or None
        """
        try:
            # Using NIST NVD API
            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("vulnerabilities"):
                    vuln = data["vulnerabilities"][0]["cve"]
                    
                    return {
                        "id": cve_id,
                        "description": vuln.get("descriptions", [{}])[0].get("value"),
                        "published": vuln.get("published"),
                        "lastModified": vuln.get("lastModified"),
                        "cvss_v3": vuln.get("metrics", {}).get("cvssMetricV3", [{}])[0],
                        "references": [ref.get("url") for ref in vuln.get("references", [])]
                    }
        
        except Exception as e:
            logger.error(f"CVE lookup failed for {cve_id} - {e}")
        
        return None
    
    @staticmethod
    def get_cwe_info(cwe_id: str) -> Dict[str, str]:
        """
        Get CWE (Common Weakness Enumeration) information
        
        Args:
            cwe_id: CWE identifier (e.g., CWE-89)
            
        Returns:
            Basic CWE info (static mapping)
        """
        cwe_db = {
            "CWE-78": {
                "name": "OS Command Injection",
                "description": "Improper neutralization of special elements used in an OS command"
            },
            "CWE-79": {
                "name": "Cross-site Scripting (XSS)",
                "description": "Improper neutralization of input during web page generation"
            },
            "CWE-89": {
                "name": "SQL Injection",
                "description": "Improper neutralization of special elements used in an SQL command"
            },
            "CWE-22": {
                "name": "Path Traversal",
                "description": "Improper limitation of a pathname to a restricted directory"
            },
            "CWE-502": {
                "name": "Deserialization of Untrusted Data",
                "description": "Application deserializes untrusted data without verification"
            },
            "CWE-798": {
                "name": "Use of Hard-coded Credentials",
                "description": "Software contains hard-coded credentials"
            },
            "CWE-327": {
                "name": "Use of a Broken or Risky Cryptographic Algorithm",
                "description": "Use of weak cryptographic algorithm"
            },
            "CWE-338": {
                "name": "Use of Cryptographically Weak PRNG",
                "description": "Use of insufficiently random values in security context"
            },
            "CWE-676": {
                "name": "Use of Potentially Dangerous Function",
                "description": "Program invokes potentially dangerous function"
            }
        }
        
        return cwe_db.get(cwe_id, {
            "name": "Unknown",
            "description": f"CWE ID: {cwe_id}"
        })


class SecurityToolkit:
    """Main toolkit interface for all security tools"""
    
    def __init__(self):
        self.port_scanner = PortScanner()
        self.tls_analyzer = TLSAnalyzer()
        self.web_scanner = WebSecurityScanner()
        self.threat_intel = ThreatIntelligence()
        logger.info("Security Toolkit initialized")
    
    def run_comprehensive_scan(self, target: str) -> Dict[str, Any]:
        """
        Run comprehensive security scan on target
        
        Args:
            target: Target URL or hostname
            
        Returns:
            Comprehensive scan results
        """
        results = {
            "target": target,
            "scans": {}
        }
        
        # Parse target
        parsed = urlparse(target if "://" in target else f"http://{target}")
        hostname = parsed.hostname or target
        
        try:
            # 1. Port scan (common ports only)
            logger.info(f"Starting port scan on {hostname}")
            common_ports = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080, 8443]
            results["scans"]["port_scan"] = self.port_scanner.scan_ports(hostname, common_ports)
        except Exception as e:
            results["scans"]["port_scan"] = {"error": str(e)}
        
        try:
            # 2. TLS analysis (if HTTPS)
            if parsed.scheme == "https" or 443 in [p["port"] for p in results["scans"].get("port_scan", [])]:
                logger.info(f"Analyzing TLS configuration for {hostname}")
                results["scans"]["tls_analysis"] = self.tls_analyzer.analyze_tls(hostname)
        except Exception as e:
            results["scans"]["tls_analysis"] = {"error": str(e)}
        
        try:
            # 3. HTTP header analysis
            if parsed.scheme in ["http", "https"]:
                logger.info(f"Scanning HTTP headers for {target}")
                results["scans"]["header_scan"] = self.web_scanner.scan_headers(target)
                results["scans"]["http_methods"] = self.web_scanner.test_http_methods(target)
        except Exception as e:
            results["scans"]["header_scan"] = {"error": str(e)}
        
        return results
