#!/usr/bin/env python3
"""
Live Threat Intelligence Dashboard - CLI entry point.
"""

import os
import re
import shutil
import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Add virtual environment to path if it exists
venv_site_packages = Path(__file__).parent / ".venv" / "lib" / "python3.13" / "site-packages"
if not venv_site_packages.exists():
    import glob
    venv_lib = Path(__file__).parent / ".venv" / "lib"
    if venv_lib.exists():
        python_dirs = glob.glob(str(venv_lib / "python*"))
        if python_dirs:
            venv_site_packages = Path(python_dirs[0]) / "site-packages"

if venv_site_packages.exists():
    sys.path.insert(0, str(venv_site_packages))

from aggregator import ThreatAggregator
from config import Config

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
    severity_colors = {
        "Critical": Colors.FAIL,
        "High": Colors.WARNING,
        "Medium": Colors.OKCYAN,
        "Low": Colors.OKGREEN,
        "Info": Colors.DIM,
    }
    return severity_colors.get(severity, Colors.ENDC)


def format_timestamp(ts: str) -> str:
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts


def print_summary(data: dict):
    """Print summary view of threat data"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    aggregate = data.get("aggregate", {})
    sources = data.get("sources", {})
    timestamp = data.get("timestamp", "")
    
    # Header
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Live Threat Intelligence - Overzicht{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Total threats
    total = aggregate.get("total_threats", 0)
    total_line = f" {Colors.BOLD}Totaal threats:{Colors.ENDC} {Colors.BRIGHT_GREEN}{total}{Colors.ENDC}"
    total_clean = ansi_escape.sub('', total_line)
    total_padding = max(0, content_width - len(total_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{total_line}{' ' * total_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Last update
    if timestamp:
        update_time = format_timestamp(timestamp)
        update_line = f" {Colors.BOLD}Laatste update:{Colors.ENDC} {Colors.DIM}{update_time}{Colors.ENDC}"
        update_clean = ansi_escape.sub('', update_line)
        update_padding = max(0, content_width - len(update_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{update_line}{' ' * update_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Sources status
    by_source = aggregate.get("by_source", {})
    source_names = {
        "abuseipdb": "AbuseIPDB",
        "otx": "AlienVault OTX",
        "virustotal": "VirusTotal"
    }
    
    for source_key, source_name in source_names.items():
        source_data = sources.get(source_key, {})
        count = by_source.get(source_key, 0)
        
        if source_data.get("error"):
            status_color = Colors.FAIL
            status_text = f"✗ {source_data['error'][:40]}"
        else:
            status_color = Colors.OKGREEN
            status_text = f"✓ {count} threats"
        
        source_line = f" {Colors.BOLD}{source_name}:{Colors.ENDC} {status_color}{status_text}{Colors.ENDC}"
        source_clean = ansi_escape.sub('', source_line)
        source_padding = max(0, content_width - len(source_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{source_line}{' ' * source_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Top threats
    top_threats = aggregate.get("top_threats", [])[:10]
    if top_threats:
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        top_header = f" {Colors.BOLD}Top 10 Threats:{Colors.ENDC}"
        top_header_clean = ansi_escape.sub('', top_header)
        top_header_padding = max(0, content_width - len(top_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{top_header}{' ' * top_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        for i, threat in enumerate(top_threats, 1):
            indicator = threat.get("indicator", "N/A")
            risk_score = threat.get("risk_score", 0)
            severity = threat.get("severity", "Unknown")
            severity_color = get_severity_color(severity)
            
            threat_line = f" {Colors.DIM}{i:2}.{Colors.ENDC} {indicator[:25]:<25} {severity_color}{severity:<8}{Colors.ENDC} {Colors.BOLD}Score:{Colors.ENDC} {risk_score}"
            threat_clean = ansi_escape.sub('', threat_line)
            if len(threat_clean) > content_width:
                threat_line = f" {Colors.DIM}{i:2}.{Colors.ENDC} {indicator[:20]:<20} {severity_color}{severity:<8}{Colors.ENDC} {Colors.BOLD}Score:{Colors.ENDC} {risk_score}"
                threat_clean = ansi_escape.sub('', threat_line)
            threat_padding = max(0, content_width - len(threat_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{threat_line}{' ' * threat_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def print_details(data: dict):
    """Print detailed view of all threats"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    aggregate = data.get("aggregate", {})
    threats = aggregate.get("top_threats", [])
    
    if not threats:
        print_boxed_message("Geen threats gevonden", Colors.WARNING)
        return
    
    # Header
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Threat Details ({len(threats)} total){Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Table header
    table_header = f" {Colors.BOLD}{'Indicator':<25} {'Type':<10} {'Severity':<10} {'Score':<6} {'Country':<6}{Colors.ENDC}"
    table_header_clean = ansi_escape.sub('', table_header)
    table_header_padding = max(0, content_width - len(table_header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{table_header}{' ' * table_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Threats
    for threat in threats:
        indicator = str(threat.get("indicator", "N/A"))[:24]
        threat_type = str(threat.get("type", "N/A"))[:9]
        severity = str(threat.get("severity", "Unknown"))[:9]
        risk_score = threat.get("risk_score", 0)
        country = str(threat.get("country", "N/A"))[:5] if threat.get("country") != "XX" else "N/A"
        
        severity_color = get_severity_color(severity)
        
        threat_line = f" {indicator:<25} {threat_type:<10} {severity_color}{severity:<10}{Colors.ENDC} {risk_score:<6} {country:<6}"
        threat_clean = ansi_escape.sub('', threat_line)
        threat_padding = max(0, content_width - len(threat_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{threat_line}{' ' * threat_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def refresh_data(aggregator: ThreatAggregator) -> dict:
    """Refresh threat data"""
    print_progress("Ophalen van threat data... Dit kan even duren...")
    try:
        data = aggregator.fetch_all()
        aggregator.save(data)
        return data
    except Exception as e:
        print_boxed_message(f"Fout bij ophalen data: {str(e)[:60]}", Colors.FAIL)
        # Try to load cached data
        cached = aggregator.load()
        if cached:
            return cached
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "aggregate": {"total_threats": 0, "by_source": {}, "top_threats": []},
            "sources": {},
        }


def main():
    """Main CLI function"""
    aggregator = ThreatAggregator()
    
    # Load initial data
    data = aggregator.load()
    if not data:
        print_boxed_message("Geen cached data gevonden. Ophalen van nieuwe data...", Colors.WARNING)
        data = refresh_data(aggregator)
    else:
        print_progress("Geladen van cached data. Druk 'r' om te refreshen.")
    
    # Real-time update thread
    update_interval = 60  # seconds
    stop_updates = threading.Event()
    last_data = data
    
    def update_loop():
        """Background thread for periodic updates"""
        while not stop_updates.is_set():
            time.sleep(update_interval)
            if not stop_updates.is_set():
                try:
                    new_data = aggregator.fetch_all()
                    aggregator.save(new_data)
                    nonlocal last_data
                    last_data = new_data
                except:
                    pass
    
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()
    
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
            menu_title = f" {Colors.BOLD}Live Threat Intelligence Dashboard{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub('', menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Overzicht (Summary)"
            option1_clean = ansi_escape.sub('', option1)
            option1_padding = max(0, content_width - len(option1_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option2 = f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  Details (Volledige lijst)"
            option2_clean = ansi_escape.sub('', option2)
            option2_padding = max(0, content_width - len(option2_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option3 = f" {Colors.OKCYAN}{Colors.BOLD}[r]{Colors.ENDC}  Refresh data"
            option3_clean = ansi_escape.sub('', option3)
            option3_padding = max(0, content_width - len(option3_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option3}{' ' * option3_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option4 = f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten"
            option4_clean = ansi_escape.sub('', option4)
            option4_padding = max(0, content_width - len(option4_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option4}{' ' * option4_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
            
            # Check for updates
            if last_data != data:
                data = last_data
                print_progress("Data bijgewerkt!")
            
            # Get user choice
            print()
            choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} ").strip().lower()
            
            if choice == "1":
                print_summary(data)
            elif choice == "2":
                print_details(data)
            elif choice == "r":
                data = refresh_data(aggregator)
                last_data = data
            elif choice == "q":
                stop_updates.set()
                print_boxed_message("Afsluiten...", Colors.OKGREEN)
                break
            else:
                error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze!{Colors.ENDC}"
                print(center_text(error_msg))
                time.sleep(1)
    
    except KeyboardInterrupt:
        stop_updates.set()
        print_boxed_message("Afsluiten...", Colors.OKGREEN)


if __name__ == "__main__":
    main()
