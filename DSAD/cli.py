#!/usr/bin/env python3
"""
DoS Attack Detector - CLI entry point.
"""

import os
import re
import shutil
import sys
import signal
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dos_detector import DoSDetector


def check_root_permissions():
    """Check if running with root/administrator privileges"""
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:  # Unix/Linux/Mac
        return os.geteuid() == 0

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


def _wrap_line(line, max_len):
    """Wrap een regel op woordgrenzen tot max_len tekens per regel."""
    if len(line) <= max_len:
        return [line] if line.strip() else []
    out = []
    while line:
        line = line.strip()
        if not line:
            break
        if len(line) <= max_len:
            out.append(line)
            break
        chunk = line[: max_len + 1]
        last_space = chunk.rfind(' ')
        if last_space > 0:
            out.append(line[:last_space])
            line = line[last_space:]
        else:
            out.append(line[:max_len])
            line = line[max_len:]
    return out


def print_boxed_message(message, color=Colors.OKGREEN):
    """Print a message in a centered box. Lange regels worden in de box omgebroken."""
    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 80
    box_width = min(75, max(40, term_width - 4))
    box_padding = max(0, (term_width - box_width) // 2)
    border_line = "═" * (box_width - 2)
    content_width = box_width - 2
    max_text_len = content_width - 2  # spatie links en rechts van de tekst
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    wrapped = []
    for line in str(message).split('\n'):
        wrapped.extend(_wrap_line(line, max_text_len))
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    for line in wrapped:
        if not line.strip():
            continue
        msg_with_colors = f"{color}{Colors.BOLD}{line}{Colors.ENDC}"
        msg_clean = ansi_escape.sub('', msg_with_colors)
        msg_padding = max(0, content_width - len(msg_clean) - 1)
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {msg_with_colors}{' ' * msg_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def print_progress(message):
    """Print progress message centered"""
    progress_msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKCYAN}{message}{Colors.ENDC}"
    centered = center_text(progress_msg)
    print(centered)


# Global detector instance
detector_instance = None
# Flag to indicate Ctrl+C was pressed
_ctrl_c_requested = False


# Custom exception for returning to menu
class ReturnToMenuException(Exception):
    """Exception to return to main menu"""
    pass

# Suppress traceback for ReturnToMenuException using custom exception hook
# This prevents tracebacks when ReturnToMenuException is raised
_original_excepthook = sys.excepthook

def _custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception hook to suppress traceback for ReturnToMenuException"""
    # Check if this is ReturnToMenuException or KeyboardInterrupt that should be suppressed
    if exc_type == ReturnToMenuException:
        # Suppress traceback for ReturnToMenuException - just return silently
        return
    # Also suppress KeyboardInterrupt tracebacks when _ctrl_c_requested is True
    if exc_type == KeyboardInterrupt:
        global _ctrl_c_requested
        if _ctrl_c_requested:
            # Suppress traceback for KeyboardInterrupt when Ctrl+C was requested
            return
    _original_excepthook(exc_type, exc_value, exc_traceback)

# Set custom exception hook AFTER ReturnToMenuException is defined
sys.excepthook = _custom_excepthook


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global detector_instance, _ctrl_c_requested
    _ctrl_c_requested = True
    if detector_instance:
        detector_instance.stop()
    # Don't raise exception here - it causes traceback when called from signal handler
    # Set flag and let KeyboardInterrupt be raised naturally by Python


def get_primary_local_ip():
    """Bepaal een lokaal IP (niet 127.0.0.1) zodat testverkeer op de interface zichtbaar is voor sniff."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip if ip and ip != "0.0.0.0" else "127.0.0.1"
    except Exception:
        return "127.0.0.1"


def get_network_interfaces():
    """Get list of available network interfaces"""
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        return interfaces
    except ImportError:
        # Fallback: try to get interfaces from system
        try:
            import subprocess
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if ': ' in line and 'lo:' not in line:
                    parts = line.split(': ')
                    if len(parts) > 1:
                        interfaces.append(parts[1].split('@')[0].strip())
            return interfaces if interfaces else ['eth0', 'wlan0']
        except:
            return ['eth0', 'wlan0']


def configure_detector():
    """Configure detector settings"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Start configuration box
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Detector Configuratie{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Collect input with prompts shown in box
    try:
        interfaces = get_network_interfaces()
        if interfaces:
            interfaces_info = f" {Colors.DIM}Beschikbare interfaces: {', '.join(interfaces[:5])}{Colors.ENDC}"
            interfaces_info_clean = ansi_escape.sub('', interfaces_info)
            interfaces_info_padding = max(0, content_width - len(interfaces_info_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{interfaces_info}{' ' * interfaces_info_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            prompt_text = f" {Colors.BOLD}Network interface (Enter voor alle):{Colors.ENDC} "
            prompt_clean = ansi_escape.sub('', prompt_text)
            prompt_padding = max(0, content_width - len(prompt_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{prompt_text}{' ' * prompt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
            # Input will appear on next line (unavoidable)
            interface_input = input(center_text("")).strip()
            interface = interface_input if interface_input else None
            # Show value in reopened box
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            value_text = f" {Colors.BOLD}Interface:{Colors.ENDC} {interface or 'Alle'}"
            value_clean = ansi_escape.sub('', value_text)
            value_padding = max(0, content_width - len(value_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{value_text}{' ' * value_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        else:
            interface = None
        
        # Thresholds section
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        thresholds_header = f" {Colors.BOLD}Thresholds:{Colors.ENDC}"
        thresholds_header_clean = ansi_escape.sub('', thresholds_header)
        thresholds_header_padding = max(0, content_width - len(thresholds_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{thresholds_header}{' ' * thresholds_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        # SYN
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        syn_prompt = f" {Colors.BOLD}SYN Flood threshold (standaard 100):{Colors.ENDC} "
        syn_prompt_clean = ansi_escape.sub('', syn_prompt)
        syn_prompt_padding = max(0, content_width - len(syn_prompt_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{syn_prompt}{' ' * syn_prompt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
        syn_input = input(center_text("")).strip()
        syn_threshold = int(syn_input) if syn_input else 100
        
        # UDP
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        syn_value_text = f"   {Colors.DIM}- SYN Flood:{Colors.ENDC} {syn_threshold}"
        syn_value_clean = ansi_escape.sub('', syn_value_text)
        syn_value_padding = max(0, content_width - len(syn_value_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{syn_value_text}{' ' * syn_value_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        udp_prompt = f" {Colors.BOLD}UDP Flood threshold (standaard 200):{Colors.ENDC} "
        udp_prompt_clean = ansi_escape.sub('', udp_prompt)
        udp_prompt_padding = max(0, content_width - len(udp_prompt_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{udp_prompt}{' ' * udp_prompt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
        udp_input = input(center_text("")).strip()
        udp_threshold = int(udp_input) if udp_input else 200
        
        # ICMP
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        udp_value_text = f"   {Colors.DIM}- UDP Flood:{Colors.ENDC} {udp_threshold}"
        udp_value_clean = ansi_escape.sub('', udp_value_text)
        udp_value_padding = max(0, content_width - len(udp_value_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{udp_value_text}{' ' * udp_value_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        icmp_prompt = f" {Colors.BOLD}ICMP Flood threshold (standaard 150):{Colors.ENDC} "
        icmp_prompt_clean = ansi_escape.sub('', icmp_prompt)
        icmp_prompt_padding = max(0, content_width - len(icmp_prompt_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{icmp_prompt}{' ' * icmp_prompt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
        icmp_input = input(center_text("")).strip()
        icmp_threshold = int(icmp_input) if icmp_input else 150
        
        # HTTP
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        icmp_value_text = f"   {Colors.DIM}- ICMP Flood:{Colors.ENDC} {icmp_threshold}"
        icmp_value_clean = ansi_escape.sub('', icmp_value_text)
        icmp_value_padding = max(0, content_width - len(icmp_value_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{icmp_value_text}{' ' * icmp_value_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        http_prompt = f" {Colors.BOLD}HTTP Flood threshold (standaard 300):{Colors.ENDC} "
        http_prompt_clean = ansi_escape.sub('', http_prompt)
        http_prompt_padding = max(0, content_width - len(http_prompt_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{http_prompt}{' ' * http_prompt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
        http_input = input(center_text("")).strip()
        http_threshold = int(http_input) if http_input else 300
        
        # Time window
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        http_value_text = f"   {Colors.DIM}- HTTP Flood:{Colors.ENDC} {http_threshold}"
        http_value_clean = ansi_escape.sub('', http_value_text)
        http_value_padding = max(0, content_width - len(http_value_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{http_value_text}{' ' * http_value_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        time_window_prompt = f" {Colors.BOLD}Time window in seconden (standaard 10):{Colors.ENDC} "
        time_window_prompt_clean = ansi_escape.sub('', time_window_prompt)
        time_window_prompt_padding = max(0, content_width - len(time_window_prompt_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{time_window_prompt}{' ' * time_window_prompt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
        time_window_input = input(center_text("")).strip()
        time_window = int(time_window_input) if time_window_input else 10
        
        # Final summary
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        time_window_value_text = f" {Colors.BOLD}Time Window:{Colors.ENDC} {time_window} seconden"
        time_window_value_clean = ansi_escape.sub('', time_window_value_text)
        time_window_value_padding = max(0, content_width - len(time_window_value_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{time_window_value_text}{' ' * time_window_value_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
    except (ValueError, KeyboardInterrupt) as e:
        if isinstance(e, KeyboardInterrupt):
            # Close box and return silently
            try:
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            except:
                pass
            raise ReturnToMenuException()
        # Invalid input, use defaults
        interface = None
        syn_threshold = 100
        udp_threshold = 200
        icmp_threshold = 150
        http_threshold = 300
        time_window = 10
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    
    return {
        'interface': interface,
        'syn_threshold': syn_threshold,
        'udp_threshold': udp_threshold,
        'icmp_threshold': icmp_threshold,
        'http_threshold': http_threshold,
        'time_window': time_window
    }


def start_monitoring(config):
    """Start monitoring with configured settings"""
    global detector_instance
    
    # Set up signal handler for Ctrl+C - must be done before any operations
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create detector with callbacks for CLI output
    def stats_callback(stats):
        """Callback for statistics updates"""
        # Could print stats here if needed
        pass
    
    def alert_callback(attack_type, src_ip, count, threshold, rate):
        """Callback for alerts"""
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        print(f"\n{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        alert_header = f" {Colors.BOLD}ATTACK GEDETECTEERD!{Colors.ENDC}"
        alert_header_clean = ansi_escape.sub('', alert_header)
        alert_header_padding = max(0, content_width - len(alert_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{alert_header}{' ' * alert_header_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        
        attack_line = f" {Colors.BOLD}Type:{Colors.ENDC} {Colors.BRIGHT_RED}{attack_type}{Colors.ENDC}"
        attack_clean = ansi_escape.sub('', attack_line)
        attack_padding = max(0, content_width - len(attack_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{attack_line}{' ' * attack_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        ip_line = f" {Colors.BOLD}Source IP:{Colors.ENDC} {src_ip}"
        ip_clean = ansi_escape.sub('', ip_line)
        ip_padding = max(0, content_width - len(ip_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{ip_line}{' ' * ip_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        count_line = f" {Colors.BOLD}Packet Count:{Colors.ENDC} {Colors.BRIGHT_RED}{count}{Colors.ENDC} (Threshold: {threshold})"
        count_clean = ansi_escape.sub('', count_line)
        count_padding = max(0, content_width - len(count_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{count_line}{' ' * count_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        rate_line = f" {Colors.BOLD}Attack Rate:{Colors.ENDC} {Colors.BRIGHT_RED}{rate:.2f} packets/sec{Colors.ENDC}"
        rate_clean = ansi_escape.sub('', rate_line)
        rate_padding = max(0, content_width - len(rate_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{rate_line}{' ' * rate_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    
    detector_instance = DoSDetector(
        syn_threshold=config['syn_threshold'],
        udp_threshold=config['udp_threshold'],
        icmp_threshold=config['icmp_threshold'],
        http_threshold=config['http_threshold'],
        time_window=config['time_window'],
        interface=config['interface'],
        stats_callback=stats_callback,
        alert_callback=alert_callback
    )
    
    # Show monitoring configuration in a box
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
    config_header = f" {Colors.BOLD}Monitoring Configuratie{Colors.ENDC}"
    config_header_clean = ansi_escape.sub('', config_header)
    config_header_padding = max(0, content_width - len(config_header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{config_header}{' ' * config_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    interface_line = f" {Colors.BOLD}Interface:{Colors.ENDC} {config['interface'] or 'Alle'}"
    interface_clean = ansi_escape.sub('', interface_line)
    interface_padding = max(0, content_width - len(interface_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{interface_line}{' ' * interface_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    time_window_line = f" {Colors.BOLD}Time Window:{Colors.ENDC} {config['time_window']} seconden"
    time_window_clean = ansi_escape.sub('', time_window_line)
    time_window_padding = max(0, content_width - len(time_window_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{time_window_line}{' ' * time_window_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    thresholds_header = f" {Colors.BOLD}Thresholds:{Colors.ENDC}"
    thresholds_header_clean = ansi_escape.sub('', thresholds_header)
    thresholds_header_padding = max(0, content_width - len(thresholds_header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{thresholds_header}{' ' * thresholds_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    syn_line = f"   {Colors.DIM}- SYN Flood:{Colors.ENDC} {config['syn_threshold']} packets/{config['time_window']}s"
    syn_clean = ansi_escape.sub('', syn_line)
    syn_padding = max(0, content_width - len(syn_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{syn_line}{' ' * syn_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    udp_line = f"   {Colors.DIM}- UDP Flood:{Colors.ENDC} {config['udp_threshold']} packets/{config['time_window']}s"
    udp_clean = ansi_escape.sub('', udp_line)
    udp_padding = max(0, content_width - len(udp_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{udp_line}{' ' * udp_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    icmp_line = f"   {Colors.DIM}- ICMP Flood:{Colors.ENDC} {config['icmp_threshold']} packets/{config['time_window']}s"
    icmp_clean = ansi_escape.sub('', icmp_line)
    icmp_padding = max(0, content_width - len(icmp_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{icmp_line}{' ' * icmp_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    http_line = f"   {Colors.DIM}- HTTP Flood:{Colors.ENDC} {config['http_threshold']} requests/{config['time_window']}s"
    http_clean = ansi_escape.sub('', http_line)
    http_padding = max(0, content_width - len(http_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{http_line}{' ' * http_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    
    # Check for root permissions before starting
    has_root = check_root_permissions()
    
    if not has_root:
        # Show warning in a yellow box
        print(f"\n{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        warning_header = f" {Colors.BOLD}WAARSCHUWING{Colors.ENDC}"
        warning_header_clean = ansi_escape.sub('', warning_header)
        warning_header_padding = max(0, content_width - len(warning_header_clean))
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}{warning_header}{' ' * warning_header_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        
        warning_line1 = f" {Colors.WARNING}Packet capture vereist root/administrator rechten.{Colors.ENDC}"
        warning_line1_clean = ansi_escape.sub('', warning_line1)
        warning_line1_padding = max(0, content_width - len(warning_line1_clean))
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}{warning_line1}{' ' * warning_line1_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}")
        
        if os.name == 'nt':  # Windows
            solution_line = f" {Colors.DIM}Run als Administrator of gebruik een tool met admin rechten.{Colors.ENDC}"
        else:  # Linux/Mac
            solution_line = f" {Colors.DIM}Run met: sudo python3 jacops.py{Colors.ENDC}"
        
        solution_clean = ansi_escape.sub('', solution_line)
        solution_padding = max(0, content_width - len(solution_clean))
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}{solution_line}{' ' * solution_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}")
        
        continue_line = f" {Colors.DIM}Doorgaan zonder root rechten kan tot fouten leiden.{Colors.ENDC}"
        continue_clean = ansi_escape.sub('', continue_line)
        continue_padding = max(0, content_width - len(continue_clean))
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}{continue_line}{' ' * continue_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}")
        
        continue_prompt = f" {Colors.WARNING}{Colors.BOLD}→{Colors.ENDC} {Colors.BOLD}Doorgaan? (j/n):{Colors.ENDC} "
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}{continue_prompt}", end="")
        user_choice = input().strip().lower()
        prompt_clean = ansi_escape.sub('', continue_prompt)
        pad = max(0, content_width - len(prompt_clean) - len(user_choice))
        print(f"{' ' * pad}{Colors.WARNING}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.WARNING}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
        
        if user_choice not in ['j', 'y', 'ja', 'yes']:
            print_boxed_message("Monitoring geannuleerd.", Colors.OKGREEN)
            return
    
    print_boxed_message("Monitoring gestart. Druk Ctrl+C om te stoppen.", Colors.OKGREEN)
    print()
    
    try:
        # Use gui_mode=True to suppress the default output from dos_detector.py
        detector_instance.start_monitoring(gui_mode=True)
    except ReturnToMenuException:
        # Already handled, re-raise
        raise
    except KeyboardInterrupt:
        # Ctrl+C - don't show error, just return silently
        global _ctrl_c_requested
        _ctrl_c_requested = True
        if detector_instance:
            detector_instance.stop()
        # Raise ReturnToMenuException to return to menu
        # This will be caught by main() and handled gracefully
        raise ReturnToMenuException()
    except PermissionError as e:
        # Show permission error in a red box with detailed solutions
        print(f"\n{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        error_header = f" {Colors.BOLD}PERMISSIE FOUT{Colors.ENDC}"
        error_header_clean = ansi_escape.sub('', error_header)
        error_header_padding = max(0, content_width - len(error_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{error_header}{' ' * error_header_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        
        error_line = f" {Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Operation not permitted{Colors.ENDC}"
        error_clean = ansi_escape.sub('', error_line)
        error_padding = max(0, content_width - len(error_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{error_line}{' ' * error_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        
        solution_header = f" {Colors.BOLD}Oplossing:{Colors.ENDC}"
        solution_header_clean = ansi_escape.sub('', solution_header)
        solution_header_padding = max(0, content_width - len(solution_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{solution_header}{' ' * solution_header_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        if os.name == 'nt':  # Windows
            sol_line1 = f"   {Colors.DIM}1. Run als Administrator{Colors.ENDC}"
            sol_line2 = f"   {Colors.DIM}2. Of gebruik een tool met admin rechten{Colors.ENDC}"
        else:  # Linux/Mac
            sol_line1 = f"   {Colors.DIM}1. Run met: sudo python3 jacops.py{Colors.ENDC}"
            sol_line2 = f"   {Colors.DIM}2. Of: sudo python3 DSAD/cli.py{Colors.ENDC}"
        
        for sol_line in [sol_line1, sol_line2]:
            sol_clean = ansi_escape.sub('', sol_line)
            sol_padding = max(0, content_width - len(sol_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{sol_line}{' ' * sol_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    except Exception as e:
        # FIRST: Check if this is actually a KeyboardInterrupt wrapped in another exception
        # Check multiple ways KeyboardInterrupt might be wrapped - MUST be first!
        if isinstance(e, KeyboardInterrupt):
            if detector_instance:
                detector_instance.stop()
            raise ReturnToMenuException()
        if hasattr(e, '__cause__') and isinstance(e.__cause__, KeyboardInterrupt):
            if detector_instance:
                detector_instance.stop()
            raise ReturnToMenuException()
        if hasattr(e, '__context__') and isinstance(e.__context__, KeyboardInterrupt):
            if detector_instance:
                detector_instance.stop()
            raise ReturnToMenuException()
        
        # Check error message for KeyboardInterrupt indicators BEFORE getting error_str
        # This must be done before any string operations to catch Ctrl+C early
        error_str = str(e)
        
        # Check for KeyboardInterrupt in error message (must be before error box)
        if 'keyboardinterrupt' in error_str.lower() or 'interrupted' in error_str.lower() or 'ctrl+c' in error_str.lower():
            if detector_instance:
                detector_instance.stop()
            raise ReturnToMenuException()
        
        # Only show error box for real errors (not Ctrl+C)
        is_permission_error = 'permission' in error_str.lower() or 'not permitted' in error_str.lower() or 'errno 1' in error_str.lower()
        
        print(f"\n{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        error_header = f" {Colors.BOLD}FOUT{Colors.ENDC}"
        error_header_clean = ansi_escape.sub('', error_header)
        error_header_padding = max(0, content_width - len(error_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{error_header}{' ' * error_header_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        
        error_line = f" {Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}{error_str}{Colors.ENDC}"
        error_clean = ansi_escape.sub('', error_line)
        error_padding = max(0, content_width - len(error_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{error_line}{' ' * error_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        if is_permission_error:
            print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            note_line = f" {Colors.DIM}Packet capture vereist root/administrator rechten.{Colors.ENDC}"
            note_clean = ansi_escape.sub('', note_line)
            note_padding = max(0, content_width - len(note_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{note_line}{' ' * note_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
            
            if os.name != 'nt':
                solution_line = f" {Colors.DIM}Probeer: sudo python3 jacops.py{Colors.ENDC}"
                solution_clean = ansi_escape.sub('', solution_line)
                solution_padding = max(0, content_width - len(solution_clean))
                print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{solution_line}{' ' * solution_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
        
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def run_dos_test():
    """
    Start monitoring, voer een gesimuleerde DoS-test uit en toon of de detector reageert.
    Gebruikt loopback (127.0.0.1) zodat alleen lokaal verkeer wordt gegenereerd.
    """
    global detector_instance

    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 80
    box_width = min(75, max(40, term_width - 4))
    box_padding = max(0, (term_width - box_width) // 2)
    border_line = "═" * (box_width - 2)
    content_width = box_width - 2
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # Sub-menu: kies type test
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    test_header = f" {Colors.BOLD}DoS Test (simulatie){Colors.ENDC}"
    test_header_clean = ansi_escape.sub('', test_header)
    test_header_padding = max(0, content_width - len(test_header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{test_header}{' ' * test_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    opts = [
        f" {Colors.OKCYAN}[1]{Colors.ENDC}  SYN flood test",
        f" {Colors.OKCYAN}[2]{Colors.ENDC}  UDP flood test",
        f" {Colors.OKCYAN}[3]{Colors.ENDC}  ICMP flood test",
        f" {Colors.OKCYAN}[4]{Colors.ENDC}  Alle types (kort)",
    ]
    for line in opts:
        line_clean = ansi_escape.sub('', line)
        pad = max(0, content_width - len(line_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{line}{' ' * pad}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    prompt = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Type test (1-4):{Colors.ENDC} "
    choice = input(center_text(prompt)).strip()
    type_map = {"1": "syn", "2": "udp", "3": "icmp", "4": "all"}
    test_type = type_map.get(choice, "syn")

    # Test injecteert pakketten in de detector (geen netwerk/sudo nodig voor de test zelf)
    # Luister op alle interfaces (None)
    config = {
        "interface": None,
        "syn_threshold": 50,
        "udp_threshold": 80,
        "icmp_threshold": 60,
        "http_threshold": 300,
        "time_window": 10,
    }

    signal.signal(signal.SIGINT, signal_handler)
    detector_instance = DoSDetector(
        syn_threshold=config["syn_threshold"],
        udp_threshold=config["udp_threshold"],
        icmp_threshold=config["icmp_threshold"],
        http_threshold=config["http_threshold"],
        time_window=config["time_window"],
        interface=config["interface"],
        stats_callback=lambda s: None,  # Geen [STATS]-regel tijdens test
        alert_callback=lambda at, ip, cnt, th, rate, ts: _alert_callback(at, ip, cnt, th, rate),
    )

    def monitor_thread():
        try:
            detector_instance.start_monitoring(gui_mode=True)
        except (ReturnToMenuException, KeyboardInterrupt):
            pass

    print_boxed_message(
        "Monitoring gestart. DoS-test start over 3 seconden... (voer uit met sudo als je geen alerts ziet)",
        Colors.OKGREEN,
    )
    thread = threading.Thread(target=monitor_thread, daemon=True)
    thread.start()
    time.sleep(3.0)

    # Injecteer testpakketten direct in de detector (geen netwerk nodig), zodat alerts gegarandeerd verschijnen
    try:
        from scapy.all import IP, TCP, UDP, ICMP
    except ImportError:
        print_boxed_message("Scapy vereist voor DoS-test.", Colors.FAIL)
        if detector_instance:
            detector_instance.stop()
        return
    try:
        src = "127.0.0.1"
        counts = {"syn": 60, "udp": 90, "icmp": 70}  # Boven thresholds 50, 80, 60
        if test_type == "syn":
            for i in range(counts["syn"]):
                if not detector_instance or not detector_instance.running:
                    break
                pkt = IP(src=src, dst=src) / TCP(flags="S", sport=40000 + i, dport=80)
                detector_instance.process_packet(pkt)
                time.sleep(0.02)
        elif test_type == "udp":
            for i in range(counts["udp"]):
                if not detector_instance or not detector_instance.running:
                    break
                pkt = IP(src=src, dst=src) / UDP(sport=50000 + i, dport=53)
                detector_instance.process_packet(pkt)
                time.sleep(0.02)
        elif test_type == "icmp":
            for i in range(counts["icmp"]):
                if not detector_instance or not detector_instance.running:
                    break
                pkt = IP(src=src, dst=src) / ICMP(id=i % 65535, seq=i)
                detector_instance.process_packet(pkt)
                time.sleep(0.02)
        elif test_type == "all":
            for i in range(counts["syn"]):
                if not detector_instance or not detector_instance.running:
                    break
                pkt = IP(src=src, dst=src) / TCP(flags="S", sport=40000 + i, dport=80)
                detector_instance.process_packet(pkt)
                time.sleep(0.01)
            for i in range(counts["udp"]):
                if not detector_instance or not detector_instance.running:
                    break
                pkt = IP(src=src, dst=src) / UDP(sport=50000 + i, dport=53)
                detector_instance.process_packet(pkt)
                time.sleep(0.01)
            for i in range(counts["icmp"]):
                if not detector_instance or not detector_instance.running:
                    break
                pkt = IP(src=src, dst=src) / ICMP(id=i % 65535, seq=i)
                detector_instance.process_packet(pkt)
                time.sleep(0.01)
    finally:
        if detector_instance:
            detector_instance.stop()
        time.sleep(0.8)
    sys.stdout.flush()
    sys.stderr.flush()

    print_boxed_message(
        "Test afgerond. Zie hierboven de rode alert-boxen als er aanvallen zijn gedetecteerd.",
        Colors.OKGREEN,
    )


def _alert_callback(attack_type, src_ip, count, threshold, rate, _timestamp=None):
    """Callback voor alerts tijdens DoS-test (zelfde box-stijl als start_monitoring)."""
    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 80
    box_width = min(75, max(40, term_width - 4))
    box_padding = max(0, (term_width - box_width) // 2)
    border_line = "═" * (box_width - 2)
    content_width = box_width - 2
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    alert_header = f" {Colors.BOLD}ATTACK GEDETECTEERD!{Colors.ENDC}"
    alert_header_clean = ansi_escape.sub('', alert_header)
    alert_header_padding = max(0, content_width - len(alert_header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{alert_header}{' ' * alert_header_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    attack_line = f" {Colors.BOLD}Type:{Colors.ENDC} {Colors.BRIGHT_RED}{attack_type}{Colors.ENDC}"
    ip_line = f" {Colors.BOLD}Source IP:{Colors.ENDC} {src_ip}"
    count_line = f" {Colors.BOLD}Packet Count:{Colors.ENDC} {Colors.BRIGHT_RED}{count}{Colors.ENDC} (Threshold: {threshold})"
    rate_line = f" {Colors.BOLD}Attack Rate:{Colors.ENDC} {Colors.BRIGHT_RED}{rate:.2f} packets/sec{Colors.ENDC}"
    for line in (attack_line, ip_line, count_line, rate_line):
        line_clean = ansi_escape.sub('', line)
        pad = max(0, content_width - len(line_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{line}{' ' * pad}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    sys.stdout.flush()
    sys.stderr.flush()


def main():
    """Main CLI function"""
    try:
        while True:
            # Show menu
            try:
                term_width = shutil.get_terminal_size().columns
            except Exception:
                term_width = 80
            box_width = min(75, max(40, term_width - 4))
            box_padding = max(0, (term_width - box_width) // 2)
            border_line = "═" * (box_width - 2)
            content_width = box_width - 2
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            menu_title = f" {Colors.BOLD}DoS Attack Detector{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub('', menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Monitoring (met configuratie)"
            option1_clean = ansi_escape.sub('', option1)
            option1_padding = max(0, content_width - len(option1_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option2 = f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  Monitoring (standaard)"
            option2_clean = ansi_escape.sub('', option2)
            option2_padding = max(0, content_width - len(option2_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option3 = f" {Colors.OKCYAN}{Colors.BOLD}[3]{Colors.ENDC}  DoS test (simulatie)"
            option3_clean = ansi_escape.sub('', option3)
            option3_padding = max(0, content_width - len(option3_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option3}{' ' * option3_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option4 = f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten"
            option4_clean = ansi_escape.sub('', option4)
            option4_padding = max(0, content_width - len(option4_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option4}{' ' * option4_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            prompt_text = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} "
            choice = input(center_text(prompt_text)).strip().lower()
            
            if choice == "1":
                try:
                    config = configure_detector()
                    start_monitoring(config)
                except ReturnToMenuException:
                    raise
                except KeyboardInterrupt:
                    raise ReturnToMenuException()
            elif choice == "2":
                try:
                    config = {
                        'interface': None,
                        'syn_threshold': 100,
                        'udp_threshold': 200,
                        'icmp_threshold': 150,
                        'http_threshold': 300,
                        'time_window': 10
                    }
                    start_monitoring(config)
                except ReturnToMenuException:
                    raise
                except KeyboardInterrupt:
                    raise ReturnToMenuException()
            elif choice == "3":
                try:
                    run_dos_test()
                except ReturnToMenuException:
                    raise
                except KeyboardInterrupt:
                    raise ReturnToMenuException()
            elif choice == "q":
                print_boxed_message("Afsluiten...", Colors.OKGREEN)
                break
            else:
                # Show error in a box
                print(f"\n{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                error_msg = f" {Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze! Kies 1, 2, 3 of q.{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = max(0, content_width - len(error_clean))
                print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{error_msg}{' ' * error_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
                print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    
    except KeyboardInterrupt:
        # Ctrl+C pressed - return to menu silently
        # Convert to ReturnToMenuException to avoid traceback
        raise ReturnToMenuException()
    except ReturnToMenuException:
        # ReturnToMenuException - just re-raise, will be caught by jacops.py
        raise


if __name__ == "__main__":
    main()
