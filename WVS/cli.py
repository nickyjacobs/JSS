#!/usr/bin/env python3
"""
Web Vulnerability Scanner - CLI entry point.
"""

import os
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scanner import VulnerabilityScanner

# ANSI color codes voor terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'
    BRIGHT_CYAN = '\033[1;96m'
    BRIGHT_GREEN = '\033[1;92m'
    BRIGHT_RED = '\033[1;91m'


def center_text(text, width=None):
    """Center text in terminal, ignoring ANSI color codes"""
    if width is None:
        try:
            width = shutil.get_terminal_size().columns
        except:
            width = 80
    
    # Remove ANSI codes to get actual text length
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text_without_codes = ansi_escape.sub('', text)
    text_length = len(text_without_codes)
    
    # Calculate padding
    padding = (width - text_length) // 2
    return ' ' * padding + text


def print_boxed_message(message, color=Colors.OKGREEN):
    """Print a message in a centered box"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Handle multi-line messages
    lines = str(message).split('\n')
    
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    
    for line in lines:
        if not line.strip():
            continue
        msg_with_colors = f"{color}{Colors.BOLD}{line}{Colors.ENDC}"
        msg_clean = ansi_escape.sub('', msg_with_colors)
        # Account for the space after ║
        msg_padding = max(0, content_width - len(msg_clean) - 1)
        # Ensure total length matches exactly
        total_length = 1 + len(msg_clean) + msg_padding
        if total_length != content_width:
            msg_padding = max(0, content_width - len(msg_clean) - 1)
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {msg_with_colors}{' ' * msg_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def print_progress(message):
    """Print progress message centered"""
    progress_msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKCYAN}{message}{Colors.ENDC}"
    centered = center_text(progress_msg)
    print(centered)


def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    severity_lower = severity.lower()
    if severity_lower == 'critical':
        return Colors.BRIGHT_RED
    elif severity_lower == 'high':
        return Colors.FAIL
    elif severity_lower == 'medium':
        return Colors.WARNING
    elif severity_lower == 'low':
        return Colors.OKCYAN
    else:
        return Colors.DIM


def print_scan_results(vulnerabilities: list):
    """Print scan results in a formatted box"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    if not vulnerabilities:
        print_boxed_message("Geen kwetsbaarheden gevonden!", Colors.OKGREEN)
        return
    
    # Count by severity
    severity_count = {}
    for vuln in vulnerabilities:
        sev = vuln.get('severity', 'unknown').lower()
        severity_count[sev] = severity_count.get(sev, 0) + 1
    
    # Header
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Scan Resultaten ({len(vulnerabilities)} gevonden){Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Summary
    summary_parts = []
    for sev in ['critical', 'high', 'medium', 'low']:
        if sev in severity_count:
            color = get_severity_color(sev)
            summary_parts.append(f"{color}{sev.upper()}: {severity_count[sev]}{Colors.ENDC}")
    
    if summary_parts:
        summary_line = f" {Colors.BOLD}Samenvatting:{Colors.ENDC} {', '.join(summary_parts)}"
        summary_clean = ansi_escape.sub('', summary_line)
        summary_padding = max(0, content_width - len(summary_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{summary_line}{' ' * summary_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Vulnerabilities
    for i, vuln in enumerate(vulnerabilities, 1):
        severity = vuln.get('severity', 'unknown')
        severity_color = get_severity_color(severity)
        
        # Title
        title_line = f" {Colors.DIM}{i}.{Colors.ENDC} {severity_color}{Colors.BOLD}[{severity.upper()}]{Colors.ENDC} {vuln.get('title', 'Unknown')}"
        title_clean = ansi_escape.sub('', title_line)
        if len(title_clean) > content_width:
            title_line = f" {Colors.DIM}{i}.{Colors.ENDC} {severity_color}{Colors.BOLD}[{severity.upper()}]{Colors.ENDC} {vuln.get('title', 'Unknown')[:50]}..."
            title_clean = ansi_escape.sub('', title_line)
        title_padding = max(0, content_width - len(title_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{title_line}{' ' * title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        # Description
        desc = vuln.get('description', '')
        if desc:
            desc_line = f"    {desc}"
            desc_clean = ansi_escape.sub('', desc_line)
            if len(desc_clean) > content_width:
                desc_line = f"    {desc[:content_width - 4]}..."
                desc_clean = ansi_escape.sub('', desc_line)
            desc_padding = max(0, content_width - len(desc_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{desc_line}{' ' * desc_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        # URL
        url = vuln.get('url', '')
        if url:
            url_line = f"    {Colors.DIM}URL:{Colors.ENDC} {url[:60]}"
            if len(url) > 60:
                url_line = f"    {Colors.DIM}URL:{Colors.ENDC} {url[:57]}..."
            url_clean = ansi_escape.sub('', url_line)
            url_padding = max(0, content_width - len(url_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{url_line}{' ' * url_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        if i < len(vulnerabilities):
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def run_scan():
    """Run a vulnerability scan"""
    url_input = input(f"{center_text('Voer URL in om te scannen: ')}").strip()
    
    if not url_input:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen URL opgegeven!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    # Validate URL
    if not url_input.startswith(('http://', 'https://')):
        url_input = 'http://' + url_input
    
    # Select scan types
    print()
    print(center_text(f"{Colors.BOLD}Selecteer scan types:{Colors.ENDC}"))
    print(center_text("[1] Alle scans"))
    print(center_text("[2] SQL Injection"))
    print(center_text("[3] XSS (Cross-Site Scripting)"))
    print(center_text("[4] Directory Traversal"))
    print(center_text("[5] Command Injection"))
    print(center_text("[6] File Upload"))
    print()
    
    scan_choice = input(f"{center_text('Keuze (1-6, meerdere met komma): ')}").strip()
    
    scan_types = []
    if scan_choice == "1" or not scan_choice:
        scan_types = ['all']
    else:
        choices = scan_choice.split(',')
        type_map = {
            '2': 'sql',
            '3': 'xss',
            '4': 'directory',
            '5': 'command',
            '6': 'file_upload'
        }
        for choice in choices:
            choice = choice.strip()
            if choice in type_map:
                scan_types.append(type_map[choice])
    
    if not scan_types:
        scan_types = ['all']
    
    # Run scan
    print_progress(f"Scannen van {url_input}...")
    try:
        scanner = VulnerabilityScanner(url_input)
        vulnerabilities = scanner.scan(scan_types)
        print_scan_results(vulnerabilities)
    except Exception as e:
        error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij scannen: {str(e)}{Colors.ENDC}"
        print(center_text(error_msg))


def main():
    """Main CLI function"""
    try:
        while True:
            # Show menu
            try:
                term_width = shutil.get_terminal_size().columns
            except:
                term_width = 80
            
            box_width = 75
            box_padding = (term_width - box_width) // 2
            border_line = "═" * 73
            content_width = 73
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            menu_title = f" {Colors.BOLD}Web Vulnerability Scanner{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub('', menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Scan website"
            option1_clean = ansi_escape.sub('', option1)
            option1_padding = max(0, content_width - len(option1_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option2 = f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten"
            option2_clean = ansi_escape.sub('', option2)
            option2_padding = max(0, content_width - len(option2_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
            
            # Get user choice
            print()
            choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} ").strip().lower()
            
            if choice == "1":
                run_scan()
            elif choice == "q":
                print_boxed_message("Afsluiten...", Colors.OKGREEN)
                break
            else:
                error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze!{Colors.ENDC}"
                print(center_text(error_msg))
    
    except KeyboardInterrupt:
        print()
        print_boxed_message("Afsluiten...", Colors.OKGREEN)


if __name__ == "__main__":
    main()
