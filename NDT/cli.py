#!/usr/bin/env python3
"""
Network Device Scanner - CLI entry point.
"""

import os
import re
import shutil
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app import detect_local_subnet
from scanner.network_scan import scan_network
from scanner.storage import save_scan_with_history, get_note
from scanner.port_scan import scan_common_ports, get_service_name
from scanner.osint_lookup import enrich_device_with_osint

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


def print_scan_progress(message):
    """Print scan progress message centered"""
    progress_msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKCYAN}{message}{Colors.ENDC}"
    centered = center_text(progress_msg)
    print(centered)


def print_device_table(devices):
    """Print devices in a formatted table"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    if not devices:
        print_boxed_message("Geen apparaten gevonden.", Colors.WARNING)
        return
    
    # Table header - adjust column widths to fit content_width (73)
    # IP: 15, MAC: 17, Hostname: 20, Vendor: 15 = 67 + 3 spaces = 70 chars
    header = f"{'IP-adres':<15} {'MAC-adres':<17} {'Hostname':<20} {'Vendor':<15}"
    header_with_colors = f" {Colors.BOLD}{header}{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header_with_colors)
    # Calculate padding: content_width (73) - length of header_with_colors (including space)
    # header_with_colors = " " + BOLD + header + ENDC
    # After stripping ANSI: " " + header = 1 + 70 = 71 chars
    header_padding = max(0, content_width - len(header_clean))
    # Ensure total length matches exactly: space(1) + header(70) + padding = 73
    total_length = len(header_clean) + header_padding
    if total_length != content_width:
        header_padding = max(0, content_width - len(header_clean))
    
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header_with_colors}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Table rows
    for device in devices:
        # Get values and ensure they're strings, not None
        ip = device.get("ip") or "N/A"
        mac = device.get("mac") or "N/A"
        hostname = device.get("hostname") or "N/A"
        vendor = device.get("vendor") or "N/A"
        
        # Convert to strings to be safe
        ip = str(ip)
        mac = str(mac)
        hostname = str(hostname)
        vendor = str(vendor)
        
        # Truncate long strings to fit column widths
        if len(ip) > 15:
            ip = ip[:12] + "..."
        if len(mac) > 17:
            mac = mac[:14] + "..."
        if len(hostname) > 20:
            hostname = hostname[:17] + "..."
        if len(vendor) > 15:
            vendor = vendor[:12] + "..."
        
        row = f"{ip:<15} {mac:<17} {hostname:<20} {vendor:<15}"
        row_with_colors = f" {Colors.OKGREEN}{row}{Colors.ENDC}"
        row_clean = ansi_escape.sub('', row_with_colors)
        # Calculate padding: content_width (73) - length of row_with_colors (including space)
        # row_with_colors = " " + OKGREEN + row + ENDC
        # After stripping ANSI: " " + row = 1 + 70 = 71 chars
        row_padding = max(0, content_width - len(row_clean))
        # Ensure total length matches exactly: space(1) + row(70) + padding = 73
        total_length = len(row_clean) + row_padding
        if total_length != content_width:
            row_padding = max(0, content_width - len(row_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{row_with_colors}{' ' * row_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
    
    # Summary
    summary = f"Totaal: {len(devices)} apparaat(en) gevonden."
    summary_with_colors = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}{summary}{Colors.ENDC}"
    summary_centered = center_text(summary_with_colors)
    print(f"\n{summary_centered}\n")


def print_device_details(device):
    """Print detailed information about a device"""
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
    
    # Device info - ensure all values are strings
    ip_val = str(device.get('ip') or 'N/A')
    mac_val = str(device.get('mac') or 'N/A')
    hostname_val = str(device.get('hostname') or 'N/A')
    vendor_val = str(device.get('vendor') or 'N/A')
    
    info_lines = [
        f"IP-adres:     {ip_val}",
        f"MAC-adres:    {mac_val}",
        f"Hostname:     {hostname_val}",
        f"Vendor:       {vendor_val}"
    ]
    
    # Open ports - add as separate section with wrapping
    if device.get("open_ports"):
        ports = device.get("open_ports", [])
        services = device.get("services", [])
        ports_list = [f'{p} ({s})' for p, s in zip(ports, services)]
        info_lines.append("")  # Empty line separator
        # Wrap ports string to fit within box (content_width = 73 chars)
        # "Open poorten: " is 15 chars, so we have 58 chars for content on first line
        # Continuation lines should align with the content (not the label), so indent by 15 chars
        ports_str = ', '.join(ports_list)
        max_first_line = 58  # First line: "Open poorten: " (15) + content (58) = 73
        max_continuation_line = 73 - 15  # Continuation lines: indent (15) + content (58) = 73
        
        if len(ports_str) <= max_first_line:
            info_lines.append(f"Open poorten: {ports_str}")
        else:
            # Split into multiple lines with proper alignment
            info_lines.append("Open poorten:")
            current_line = ""
            for port_item in ports_list:
                if current_line:
                    test_line = current_line + ", " + port_item
                else:
                    # First continuation line: align with content after "Open poorten: "
                    # Values like "10.120.1.1" start at column 14 (after "IP-adres:     " which is 15 chars including space)
                    # "Open poorten:" is 15 chars, so we need 14 spaces to align with values
                    test_line = "              " + port_item  # 14 spaces to align with content
                
                if len(test_line) <= max_continuation_line:
                    current_line = test_line
                else:
                    if current_line:
                        info_lines.append(current_line)
                    # Start new continuation line with proper indent
                    # Values like "10.120.1.1" start at column 14 (after "IP-adres:     " which is 15 chars including space)
                    # "Open poorten:" is 15 chars, so we need 14 spaces to align with values
                    current_line = "              " + port_item  # 14 spaces to align with content
            
            if current_line:
                info_lines.append(current_line)
    
    # OSINT data - add as separate section
    if device.get("osint"):
        osint = device.get("osint", {})
        info_lines.append("")  # Empty line separator
        info_lines.append("OSINT Data:")
        if osint.get("virustotal"):
            vt = osint["virustotal"]
            info_lines.append(f"  VirusTotal: {vt.get('reputation', 'N/A')} reputation")
        if osint.get("abuseipdb"):
            abuse = osint["abuseipdb"]
            info_lines.append(f"  AbuseIPDB:  {abuse.get('confidence', 'N/A')}% confidence")
        if osint.get("ipinfo"):
            ipinfo = osint["ipinfo"]
            info_lines.append(f"  IPinfo:     {ipinfo.get('city', 'N/A')}, {ipinfo.get('country', 'N/A')}")
    
    # Note
    mac = device.get("mac")
    if mac:
        note = get_note(mac)
        if note:
            info_lines.append("")  # Empty line separator
            info_lines.append(f"Notitie:      {note}")
    
    # Print all lines in box
    for line in info_lines:
        if not line.strip():  # Empty line - print empty box line
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{' ' * content_width}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            continue
        
        line_with_colors = f" {Colors.OKGREEN}{line}{Colors.ENDC}"
        line_clean = ansi_escape.sub('', line_with_colors)
        # Calculate padding: content_width (73) - length of line_with_colors (including space)
        # line_with_colors = " " + OKGREEN + line + ENDC
        # After stripping ANSI: " " + line
        line_padding = max(0, content_width - len(line_clean))
        # Ensure total length matches exactly: space(1) + line + padding = 73
        total_length = len(line_clean) + line_padding
        if total_length != content_width:
            line_padding = max(0, content_width - len(line_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{line_with_colors}{' ' * line_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def main():
    """Main CLI function"""
    # Detect subnet
    print_scan_progress("Detecteren van lokaal subnet...")
    subnet = detect_local_subnet()
    
    if not subnet:
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        box_padding = (term_width - 75) // 2
        
        print_boxed_message("Kon geen subnet detecteren. Voer handmatig in (bijv. 192.168.1.0/24)", Colors.WARNING)
        subnet_input = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Subnet:{Colors.ENDC} ").strip()
        if not subnet_input:
            print_boxed_message("Geen subnet opgegeven. Afbreken.", Colors.FAIL)
            return
        subnet = subnet_input
    
    print_boxed_message(f"Subnet gedetecteerd: {subnet}", Colors.OKGREEN)
    
    # Ask for options
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    box_padding = (term_width - 75) // 2
    
    # Center "Scan opties:" header
    scan_opties_header = f"{Colors.BOLD}Scan opties:{Colors.ENDC}"
    print(center_text(scan_opties_header))
    
    # Center input prompts
    portscan_prompt = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Port scanning inschakelen? (j/n):{Colors.ENDC} "
    enable_portscan = input(center_text(portscan_prompt)).strip().lower() == 'j'
    
    osint_prompt = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}OSINT enrichment inschakelen? (j/n):{Colors.ENDC} "
    enable_osint = input(center_text(osint_prompt)).strip().lower() == 'j'
    
    # Run scan
    print_boxed_message(f"Scan gestart voor subnet: {subnet}\nDit kan even duren...", Colors.OKCYAN)
    
    try:
        devices = scan_network(subnet)
        print_boxed_message(f"Scan voltooid. {len(devices)} apparaten gevonden.", Colors.OKGREEN)
        
        # Port scanning
        if enable_portscan:
            print_scan_progress("Port scanning gestart...")
            for i, device in enumerate(devices, 1):
                ip = device.get("ip")
                if ip:
                    try:
                        progress_msg = f"{Colors.DIM}[{i}/{len(devices)}] Scannen van {ip}...{Colors.ENDC}"
                        print(center_text(progress_msg), end="\r")
                        open_ports = scan_common_ports(ip, timeout=0.5)
                        device["open_ports"] = open_ports
                        device["services"] = [get_service_name(p) for p in open_ports]
                        if open_ports:
                            result_msg = f"{Colors.OKGREEN}[{i}/{len(devices)}] {ip}: {len(open_ports)} open poort(en) gevonden{Colors.ENDC}"
                            print(center_text(result_msg))
                        else:
                            result_msg = f"{Colors.DIM}[{i}/{len(devices)}] {ip}: Geen open poorten gevonden{Colors.ENDC}"
                            print(center_text(result_msg))
                    except Exception as e:
                        error_msg = f"{Colors.WARNING}[{i}/{len(devices)}] Fout bij {ip}: {e}{Colors.ENDC}"
                        print(center_text(error_msg))
            print_boxed_message("Port scanning voltooid.", Colors.OKGREEN)
        
        # OSINT enrichment
        if enable_osint:
            print_scan_progress("OSINT enrichment gestart...")
            for i, device in enumerate(devices, 1):
                ip = device.get("ip")
                if ip:
                    try:
                        progress_msg = f"{Colors.DIM}[{i}/{len(devices)}] Verrijken van {ip}...{Colors.ENDC}"
                        print(center_text(progress_msg), end="\r")
                        enrich_device_with_osint(device)
                        result_msg = f"{Colors.OKGREEN}[{i}/{len(devices)}] {ip}: OSINT data opgehaald{Colors.ENDC}"
                        print(center_text(result_msg))
                        time.sleep(0.2)  # Rate limiting
                    except Exception as e:
                        error_msg = f"{Colors.WARNING}[{i}/{len(devices)}] Fout bij {ip}: {e}{Colors.ENDC}"
                        print(center_text(error_msg))
            print_boxed_message("OSINT enrichment voltooid.", Colors.OKGREEN)
        
        # Save scan
        try:
            new_devices, removed_devices = save_scan_with_history(devices, selected_network=None)
            if new_devices:
                print_boxed_message(f"{len(new_devices)} nieuwe apparaten gevonden", Colors.OKGREEN)
            if removed_devices:
                print_boxed_message(f"{len(removed_devices)} apparaten verdwenen", Colors.WARNING)
        except Exception as e:
            print_boxed_message(f"Fout bij opslaan scan: {e}", Colors.FAIL)
        
        # Display results
        print_device_table(devices)
        
        # Ask for details
        if devices:
            detail_prompt = "Voor details over een apparaat, voer het IP-adres in (of 'q' om terug te gaan):"
            detail_prompt_centered = center_text(f"{Colors.BOLD}{detail_prompt}{Colors.ENDC}")
            print(detail_prompt_centered)
            while True:
                ip_prompt = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}IP-adres:{Colors.ENDC} "
                ip_input = input(center_text(ip_prompt)).strip()
                if ip_input.lower() == 'q':
                    break
                
                device = next((d for d in devices if d.get("ip") == ip_input), None)
                if device:
                    print_device_details(device)
                else:
                    error_msg = f"Apparaat met IP {ip_input} niet gevonden."
                    print_boxed_message(error_msg, Colors.WARNING)
    
    except KeyboardInterrupt:
        print_boxed_message("Scan geannuleerd door gebruiker.", Colors.WARNING)
    except Exception as e:
        print_boxed_message(f"Fout bij scan: {e}", Colors.FAIL)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
