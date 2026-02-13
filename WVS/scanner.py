"""
Core vulnerability scanning functionality
"""
import re
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    DEFAULT_TIMEOUT, MAX_CONCURRENT_REQUESTS, USER_AGENT,
    ENABLE_SQL_INJECTION, ENABLE_XSS, ENABLE_DIRECTORY_TRAVERSAL,
    ENABLE_COMMAND_INJECTION, ENABLE_FILE_UPLOAD
)


class VulnerabilityScanner:
    """Web vulnerability scanner"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        self.vulnerabilities = []
    
    def scan(self, scan_types: List[str] = None) -> List[Dict]:
        """Run vulnerability scan"""
        if scan_types is None:
            scan_types = ['all']
        
        self.vulnerabilities = []
        
        # Get initial page
        try:
            response = self.session.get(self.target_url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            return [{
                'type': 'error',
                'severity': 'high',
                'title': 'Cannot connect to target',
                'description': str(e),
                'url': self.target_url
            }]
        
        # Parse forms and links
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        links = soup.find_all('a', href=True)
        
        # Scan based on types
        if 'all' in scan_types or 'sql' in scan_types:
            if ENABLE_SQL_INJECTION:
                self._scan_sql_injection(forms, links)
        
        if 'all' in scan_types or 'xss' in scan_types:
            if ENABLE_XSS:
                self._scan_xss(forms, links)
        
        if 'all' in scan_types or 'directory' in scan_types:
            if ENABLE_DIRECTORY_TRAVERSAL:
                self._scan_directory_traversal(links)
        
        if 'all' in scan_types or 'command' in scan_types:
            if ENABLE_COMMAND_INJECTION:
                self._scan_command_injection(forms)
        
        if 'all' in scan_types or 'file_upload' in scan_types:
            if ENABLE_FILE_UPLOAD:
                self._scan_file_upload(forms)
        
        return self.vulnerabilities
    
    def _scan_sql_injection(self, forms: List, links: List):
        """Scan for SQL injection vulnerabilities"""
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' AND '1'='1",
        ]
        
        # Test forms
        for form in forms:
            form_action = form.get('action', '')
            form_method = form.get('method', 'get').lower()
            form_url = urljoin(self.target_url, form_action)
            
            inputs = form.find_all(['input', 'textarea'])
            for payload in sql_payloads:
                data = {}
                for inp in inputs:
                    name = inp.get('name')
                    if name:
                        data[name] = payload
                
                try:
                    if form_method == 'post':
                        response = self.session.post(form_url, data=data, timeout=DEFAULT_TIMEOUT)
                    else:
                        response = self.session.get(form_url, params=data, timeout=DEFAULT_TIMEOUT)
                    
                    # Check for SQL error patterns
                    error_patterns = [
                        r"SQL syntax.*MySQL",
                        r"Warning.*\Wmysql_",
                        r"MySQLSyntaxErrorException",
                        r"valid MySQL result",
                        r"PostgreSQL.*ERROR",
                        r"Warning.*\Wpg_",
                        r"PostgreSQL query failed",
                        r"SQLite.*error",
                        r"SQLiteException",
                        r"Warning.*\Wsqlite_",
                        r"Microsoft Access.*error",
                        r"ODBC.*error",
                        r"ORA-\d{5}",
                        r"Oracle.*error",
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            self.vulnerabilities.append({
                                'type': 'sql_injection',
                                'severity': 'high',
                                'title': 'Potential SQL Injection',
                                'description': f'SQL error detected with payload: {payload}',
                                'url': form_url,
                                'payload': payload,
                                'method': form_method.upper()
                            })
                            break
                
                except requests.RequestException:
                    continue
        
        # Test URL parameters
        parsed = urlparse(self.target_url)
        params = parse_qs(parsed.query)
        if params:
            for param_name, param_values in params.items():
                for payload in sql_payloads:
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?" + \
                              "&".join([f"{k}={v[0]}" for k, v in test_params.items()])
                    
                    try:
                        response = self.session.get(test_url, timeout=DEFAULT_TIMEOUT)
                        for pattern in [
                            r"SQL syntax.*MySQL",
                            r"Warning.*\Wmysql_",
                            r"PostgreSQL.*ERROR",
                            r"SQLite.*error",
                        ]:
                            if re.search(pattern, response.text, re.IGNORECASE):
                                self.vulnerabilities.append({
                                    'type': 'sql_injection',
                                    'severity': 'high',
                                    'title': 'Potential SQL Injection in URL parameter',
                                    'description': f'SQL error detected in parameter "{param_name}"',
                                    'url': test_url,
                                    'payload': payload,
                                    'parameter': param_name
                                })
                                break
                    except requests.RequestException:
                        continue
    
    def _scan_xss(self, forms: List, links: List):
        """Scan for XSS vulnerabilities"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
        ]
        
        # Test forms
        for form in forms:
            form_action = form.get('action', '')
            form_method = form.get('method', 'get').lower()
            form_url = urljoin(self.target_url, form_action)
            
            inputs = form.find_all(['input', 'textarea'])
            for payload in xss_payloads:
                data = {}
                for inp in inputs:
                    name = inp.get('name')
                    if name:
                        data[name] = payload
                
                try:
                    if form_method == 'post':
                        response = self.session.post(form_url, data=data, timeout=DEFAULT_TIMEOUT)
                    else:
                        response = self.session.get(form_url, params=data, timeout=DEFAULT_TIMEOUT)
                    
                    # Check if payload is reflected
                    if payload in response.text:
                        self.vulnerabilities.append({
                            'type': 'xss',
                            'severity': 'medium',
                            'title': 'Potential XSS (Cross-Site Scripting)',
                            'description': f'XSS payload reflected in response',
                            'url': form_url,
                            'payload': payload,
                            'method': form_method.upper()
                        })
                
                except requests.RequestException:
                    continue
        
        # Test URL parameters
        parsed = urlparse(self.target_url)
        params = parse_qs(parsed.query)
        if params:
            for param_name, param_values in params.items():
                for payload in xss_payloads:
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?" + \
                              "&".join([f"{k}={v[0]}" for k, v in test_params.items()])
                    
                    try:
                        response = self.session.get(test_url, timeout=DEFAULT_TIMEOUT)
                        if payload in response.text:
                            self.vulnerabilities.append({
                                'type': 'xss',
                                'severity': 'medium',
                                'title': 'Potential XSS in URL parameter',
                                'description': f'XSS payload reflected in parameter "{param_name}"',
                                'url': test_url,
                                'payload': payload,
                                'parameter': param_name
                            })
                    except requests.RequestException:
                        continue
    
    def _scan_directory_traversal(self, links: List):
        """Scan for directory traversal vulnerabilities"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        for link in links[:10]:  # Limit to first 10 links
            href = link.get('href', '')
            if not href or href.startswith('#'):
                continue
            
            full_url = urljoin(self.target_url, href)
            parsed = urlparse(full_url)
            
            for payload in traversal_payloads:
                test_path = f"{parsed.path}/{payload}"
                test_url = f"{parsed.scheme}://{parsed.netloc}{test_path}"
                
                try:
                    response = self.session.get(test_url, timeout=DEFAULT_TIMEOUT)
                    # Check for common file contents
                    if 'root:' in response.text or '[boot loader]' in response.text:
                        self.vulnerabilities.append({
                            'type': 'directory_traversal',
                            'severity': 'high',
                            'title': 'Potential Directory Traversal',
                            'description': f'System file content detected',
                            'url': test_url,
                            'payload': payload
                        })
                        break
                except requests.RequestException:
                    continue
    
    def _scan_command_injection(self, forms: List):
        """Scan for command injection vulnerabilities"""
        cmd_payloads = [
            "; ls",
            "| whoami",
            "& id",
            "`whoami`",
            "$(id)",
        ]
        
        for form in forms:
            form_action = form.get('action', '')
            form_method = form.get('method', 'get').lower()
            form_url = urljoin(self.target_url, form_action)
            
            inputs = form.find_all(['input', 'textarea'])
            for payload in cmd_payloads:
                data = {}
                for inp in inputs:
                    name = inp.get('name')
                    if name:
                        data[name] = payload
                
                try:
                    if form_method == 'post':
                        response = self.session.post(form_url, data=data, timeout=DEFAULT_TIMEOUT)
                    else:
                        response = self.session.get(form_url, params=data, timeout=DEFAULT_TIMEOUT)
                    
                    # Check for command output patterns
                    if any(pattern in response.text for pattern in ['uid=', 'gid=', 'groups=', 'root:x:']):
                        self.vulnerabilities.append({
                            'type': 'command_injection',
                            'severity': 'critical',
                            'title': 'Potential Command Injection',
                            'description': f'Command output detected in response',
                            'url': form_url,
                            'payload': payload,
                            'method': form_method.upper()
                        })
                
                except requests.RequestException:
                    continue
    
    def _scan_file_upload(self, forms: List):
        """Scan for insecure file upload vulnerabilities"""
        for form in forms:
            form_action = form.get('action', '')
            form_method = form.get('method', 'get').lower()
            form_url = urljoin(self.target_url, form_action)
            
            # Check if form has file input
            file_inputs = form.find_all('input', {'type': 'file'})
            if not file_inputs:
                continue
            
            # Check for missing security headers
            try:
                response = self.session.get(form_url, timeout=DEFAULT_TIMEOUT)
                headers = response.headers
                
                issues = []
                if 'Content-Security-Policy' not in headers:
                    issues.append('Missing Content-Security-Policy header')
                if 'X-Content-Type-Options' not in headers:
                    issues.append('Missing X-Content-Type-Options header')
                
                if issues:
                    self.vulnerabilities.append({
                        'type': 'file_upload',
                        'severity': 'medium',
                        'title': 'Insecure File Upload Form',
                        'description': '; '.join(issues),
                        'url': form_url,
                        'method': form_method.upper()
                    })
            except requests.RequestException:
                continue
