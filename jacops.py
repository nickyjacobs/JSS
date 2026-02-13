#!/usr/bin/env python3
"""
JacOps Security Suite v.1.0
Een uitgebreide cybersecurity multitool suite met verschillende professionele security tools.
"""

import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from typing import Optional


class ReturnToMenuException(Exception):
    """Custom exception to signal return to main menu"""
    pass

# Try to import readline for tab completion
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

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


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


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


def print_banner():
    """Print the JacOps Security Suite banner"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    # ASCII art lines for JacOps - original format
    ascii_lines = [
        "     _             ___            ",
        "    | | __ _  ___ / _ \\ _ __  ___ ",
        " _  | |/ _` |/ __| | | | '_ \\/ __|",
        "| |_| | (_| | (__| |_| | |_) \\__ \\",
        " \\___/ \\__,_|\\___|\\___/| .__/|___/",
        "                       |_|        "
    ]
    
    # Center each ASCII art line
    centered_ascii = []
    for line in ascii_lines:
        centered_ascii.append(center_text(line, term_width))
    
    # Create banner - all elements centered
    banner = f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}{chr(10).join(centered_ascii)}{Colors.ENDC}
{center_text(Colors.OKCYAN + Colors.BOLD + "════════════════════════════════════════" + Colors.ENDC, term_width)}
{center_text(Colors.BRIGHT_CYAN + Colors.BOLD + "Security Suite v.1.0" + Colors.ENDC, term_width)}
{center_text(Colors.OKCYAN + Colors.BOLD + "════════════════════════════════════════" + Colors.ENDC, term_width)}
{center_text(Colors.DIM + "10 Professional Security Tools" + Colors.ENDC, term_width)}
"""
    print(banner)


def print_menu():
    """Print the main menu"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    menu_items = [
        ("[1]", "", "File Type Identifier (Magic Numbers)"),
        ("[2]", "", "Phishing Email Simulator"),
        ("[3]", "", "Network Device Scanner"),
        ("[4]", "", "Live Threat Intelligence Dashboard"),
        ("[5]", "", "Password Policy Analyzer"),
        ("[6]", "", "Caesar Cipher Frequency Analyzer"),
        ("[7]", "", "DoS Attack Detector"),
        ("[8]", "", "Secure File Sharing System"),
        ("[9]", "", "Intrusion Detection Monitor"),
        ("[10]", "", "Web Vulnerability Scanner"),
    ]
    
    # Menu box width - make it wider for better alignment
    box_width = 75  # Increased from 61 to 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73  # 75 - 2 border chars
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    content_width = 73  # Fixed content width inside box (box_width - 2 border chars)
    
    # Top border - ensure perfect alignment
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    # Header line - fixed width formatting
    header_text = "Selecteer een tool:"
    header_with_colors = f" {Colors.BOLD}{header_text}{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header_with_colors)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header_with_colors}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    for number, icon, description in menu_items:
        # Normalize number formatting: [1]-[9] get extra space to match [10]
        if len(number) == 3:  # [1] through [9]
            formatted_number = f"{Colors.OKCYAN}{Colors.BOLD}{number}{Colors.ENDC} "
        else:  # [10]
            formatted_number = f"{Colors.OKCYAN}{Colors.BOLD}{number}{Colors.ENDC} "
        
        # Build content string - no emojis, simpler formatting
        # Format: " [number] description"
        content = f" {formatted_number}{description}"
        
        # Remove ANSI codes to get actual display width
        content_clean = ansi_escape.sub('', content)
        
        # Calculate exact padding to fill content_width exactly
        padding_needed = content_width - len(content_clean)
        
        # Ensure padding is non-negative and correct
        if padding_needed < 0:
            padding_needed = 0
        
        # Print with exact padding - right border will always align perfectly
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{content}{' ' * padding_needed}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    # Exit option - fixed width formatting
    exit_content = f" {Colors.OKCYAN}{Colors.BOLD}[0]{Colors.ENDC}  {Colors.BRIGHT_RED}{Colors.BOLD}Exit{Colors.ENDC}"
    exit_clean = ansi_escape.sub('', exit_content)
    exit_padding = max(0, content_width - len(exit_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{exit_content}{' ' * exit_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")


def get_user_choice() -> str:
    """Get user's menu choice"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    # Center the prompt - align with menu box
    box_width = 75  # Increased from 61 to 75
    box_padding = (term_width - box_width) // 2
    
    # Prompt starts at same position as menu box content
    print()
    choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Select a tool:{Colors.ENDC} ").strip()
    return choice


def ask_cli_or_gui(tool_name: str) -> str:
    """Ask user if they want CLI or GUI version"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    # Use same box dimensions as main menu
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73  # 75 - 2 border chars
    content_width = 73  # Fixed content width inside box
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Title line
    title_with_colors = f" {Colors.BOLD}{tool_name}{Colors.ENDC}"
    title_clean = ansi_escape.sub('', title_with_colors)
    title_padding = max(0, content_width - len(title_clean))
    
    # Option 1: CLI versie
    option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  CLI versie"
    option1_clean = ansi_escape.sub('', option1)
    option1_padding = max(0, content_width - len(option1_clean))
    
    # Option 2: GUI versie
    option2 = f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  GUI versie"
    option2_clean = ansi_escape.sub('', option2)
    option2_padding = max(0, content_width - len(option2_clean))
    
    # Print centered box
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{title_with_colors}{' ' * title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
    
    # Prompt aligned with box
    print()
    choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze (1-2):{Colors.ENDC} ").strip()
    return choice


def print_fti_result(result_data):
    """Print File Type Identifier result in a nice formatted box"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    if "error" in result_data:
        error_msg = f"Error: {result_data['error']} — {result_data.get('filepath', '')}"
        error_clean = ansi_escape.sub('', error_msg)
        error_padding = max(0, content_width - len(error_clean))
        
        print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.BRIGHT_RED}{Colors.BOLD}{error_msg}{Colors.ENDC}{' ' * error_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
        return
    
    # Title
    title = "File Type Identifier - Resultaten"
    title_with_colors = f" {Colors.BOLD}{title}{Colors.ENDC}"
    title_clean = ansi_escape.sub('', title_with_colors)
    title_padding = max(0, content_width - len(title_clean))
    
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{title_with_colors}{' ' * title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # File path
    filepath_line = f" {Colors.OKCYAN}File:{Colors.ENDC} {result_data.get('filepath', '—')}"
    filepath_clean = ansi_escape.sub('', filepath_line)
    filepath_padding = max(0, content_width - len(filepath_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{filepath_line}{' ' * filepath_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Size
    size_line = f" {Colors.OKCYAN}Size:{Colors.ENDC} {result_data.get('file_size_formatted', '—')}"
    size_clean = ansi_escape.sub('', size_line)
    size_padding = max(0, content_width - len(size_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{size_line}{' ' * size_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Raw hex
    hex_line = f" {Colors.OKCYAN}Raw hex:{Colors.ENDC} {result_data.get('raw_hex', '—')}"
    hex_clean = ansi_escape.sub('', hex_line)
    hex_padding = max(0, content_width - len(hex_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{hex_line}{' ' * hex_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Detected type
    detected_line = f" {Colors.OKCYAN}Detected:{Colors.ENDC} {Colors.BRIGHT_GREEN}{result_data.get('detected_type', '—')}{Colors.ENDC}"
    detected_clean = ansi_escape.sub('', detected_line)
    detected_padding = max(0, content_width - len(detected_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{detected_line}{' ' * detected_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # File extension
    ext_line = f" {Colors.OKCYAN}File extension:{Colors.ENDC} {result_data.get('file_extension', '—')}"
    ext_clean = ansi_escape.sub('', ext_line)
    ext_padding = max(0, content_width - len(ext_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{ext_line}{' ' * ext_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Mismatch warning
    if result_data.get('mismatch'):
        mismatch_line = f" {Colors.BRIGHT_RED}{Colors.BOLD}⚠ Warning:{Colors.ENDC} {Colors.WARNING}Extension mismatch detected!{Colors.ENDC}"
        mismatch_clean = ansi_escape.sub('', mismatch_line)
        mismatch_padding = max(0, content_width - len(mismatch_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{mismatch_line}{' ' * mismatch_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Additional info if available
    if result_data.get('md5'):
        md5_line = f" {Colors.OKCYAN}MD5:{Colors.ENDC} {result_data['md5']}"
        md5_clean = ansi_escape.sub('', md5_line)
        md5_padding = max(0, content_width - len(md5_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{md5_line}{' ' * md5_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    if result_data.get('sha256'):
        sha_line = f" {Colors.OKCYAN}SHA256:{Colors.ENDC} {result_data['sha256']}"
        sha_clean = ansi_escape.sub('', sha_line)
        sha_padding = max(0, content_width - len(sha_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{sha_line}{' ' * sha_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    if result_data.get('entropy') is not None:
        entropy_val = result_data['entropy']
        entropy_note = " (high — possibly encrypted/obfuscated)" if entropy_val > 7.5 else ""
        entropy_line = f" {Colors.OKCYAN}Entropy:{Colors.ENDC} {entropy_val:.2f}{entropy_note}"
        entropy_clean = ansi_escape.sub('', entropy_line)
        entropy_padding = max(0, content_width - len(entropy_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{entropy_line}{' ' * entropy_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def path_completer(text, state):
    """Tab completer for file paths"""
    # Expand ~ to home directory
    if text.startswith('~'):
        text = os.path.expanduser(text)
    
    # Determine separator (Unix uses /, Windows can use both)
    sep = '/' if '/' in text else os.sep
    
    # Get directory and base name
    if sep in text:
        # Path with directory
        parts = text.rsplit(sep, 1)
        if len(parts) == 2:
            directory = parts[0] if parts[0] else '.'
            base = parts[1]
        else:
            directory = '.'
            base = text
    else:
        directory = '.'
        base = text
    
    # Handle absolute paths
    if directory.startswith('/') or (len(directory) > 1 and directory[1] == ':'):
        # Absolute path
        abs_dir = directory
    else:
        # Relative path - resolve from current directory
        abs_dir = os.path.abspath(directory)
    
    try:
        if not os.path.exists(abs_dir) or not os.path.isdir(abs_dir):
            return None
        
        # List files in directory
        files = os.listdir(abs_dir)
        matches = [f for f in files if f.startswith(base)]
        
        # Sort: directories first, then files
        matches.sort(key=lambda x: (not os.path.isdir(os.path.join(abs_dir, x)), x.lower()))
        
        if state < len(matches):
            match = matches[state]
            match_path = os.path.join(abs_dir, match)
            
            # Build return path maintaining original format
            if directory == '.':
                result = match
            else:
                # Preserve original directory format
                result = directory + sep + match
            
            # Add separator if it's a directory
            if os.path.isdir(match_path):
                result += sep
            
            return result
    except (OSError, PermissionError):
        pass
    
    return None


def setup_tab_completion():
    """Setup tab completion for file paths"""
    if READLINE_AVAILABLE:
        readline.set_completer(path_completer)
        readline.parse_and_bind("tab: complete")
        # Set delimiters to allow path completion
        readline.set_completer_delims(readline.get_completer_delims().replace('/', '').replace('\\', ''))


def print_tool_header(tool_name, mode):
    """Print a nice header for a tool in CLI or GUI mode"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    title = f"{tool_name} - {mode}"
    title_with_colors = f" {Colors.BRIGHT_CYAN}{Colors.BOLD}{title}{Colors.ENDC}"
    title_clean = ansi_escape.sub('', title_with_colors)
    title_padding = max(0, content_width - len(title_clean))
    
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{title_with_colors}{' ' * title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def run_file_type_identifier():
    """Run File Type Identifier tool"""
    choice = ask_cli_or_gui("File Type Identifier")
    
    fti_dir = Path(__file__).parent / "FTI"
    
    if choice == "1":
        # CLI versie
        print_tool_header("File Type Identifier", "CLI")
        
        # Setup tab completion for file paths
        setup_tab_completion()
        
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        
        file_path = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Voer bestandspad in ('q' om terug te gaan):{Colors.ENDC} ").strip()
        
        # Check if user wants to go back to main menu - only 'q' works
        if file_path.lower() == 'q':
            return True  # Return True to skip "press Enter" prompt in main()
        
        # Require a file path - empty input shows warning and returns
        if not file_path:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen bestandspad opgegeven. Gebruik 'q' om terug te gaan.{Colors.ENDC}")
            return True  # Return True to skip "press Enter" prompt in main()
        
        if file_path:
            fti_src_path = fti_dir / "src"
            if fti_src_path.exists():
                # Import and use the identify function directly
                sys.path.insert(0, str(fti_src_path))
                try:
                    from identifier import identify
                    result = identify(Path(file_path))
                    print_fti_result(result)
                except Exception as e:
                    print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij analyseren: {str(e)}{Colors.ENDC}\n")
            else:
                print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}FTI tool niet gevonden!{Colors.ENDC}")
        # If we get here and file_path is empty, user already returned (handled above)
    elif choice == "2":
        # GUI versie
        print_tool_header("File Type Identifier", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        
        fti_gui_path = fti_dir / "src" / "gui_web.py"
        if fti_gui_path.exists():
            # Create a nice box for the server info
            border_line = "═" * 73
            content_width = 73
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Account for the space after ║
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly
            total_length = 1 + len(start_clean) + start_padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            os.chdir(fti_gui_path.parent)
            try:
                # Import and run the GUI main function directly to catch KeyboardInterrupt
                sys.path.insert(0, str(fti_gui_path.parent))
                from gui_web import main as gui_main
                gui_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C in GUI, return to main menu
                raise ReturnToMenuException()
        else:
            # Center the error message
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}FTI GUI tool niet gevonden!{Colors.ENDC}"
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze.{Colors.ENDC}"
        print(center_text(error_msg))


def run_phishing_email_simulator():
    """Run Phishing Email Simulator tool"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.BOLD}Phishing Email Simulator{' ' * 42}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}")
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}\n")
    
    pes_path = Path(__file__).parent / "PES" / "app.py"
    if pes_path.exists():
        os.chdir(pes_path.parent)
        subprocess.run([sys.executable, "app.py"])
    else:
        print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}PES tool niet gevonden!{Colors.ENDC}")


def run_network_device_scanner():
    """Run Network Device Scanner tool"""
    choice = ask_cli_or_gui("Network Device Scanner")
    
    ndt_dir = Path(__file__).parent / "NDT"
    
    if choice == "1":
        # CLI versie
        print_tool_header("Network Device Scanner", "CLI")
        
        ndt_cli_path = ndt_dir / "cli.py"
        if ndt_cli_path.exists():
            original_dir = os.getcwd()
            try:
                # Change to NDT directory and run CLI
                os.chdir(ndt_cli_path.parent)
                sys.path.insert(0, str(ndt_cli_path.parent))
                
                from cli import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}NDT CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("Network Device Scanner", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        
        ndt_path = ndt_dir / "app.py"
        if ndt_path.exists():
            # Create a nice box for the server info
            border_line = "═" * 73
            content_width = 73
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Calculate padding: content_width includes the space after ║, so subtract 1 for that space
            # Total width should be: space(1) + message + padding = content_width
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly - recalculate if needed
            total_length = 1 + len(start_clean) + start_padding  # space + message + padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            os.chdir(ndt_path.parent)
            try:
                # Set environment variable to suppress Flask output
                os.environ['JACOPS_RUNNING'] = '1'
                
                # Import and run the Flask app directly to catch KeyboardInterrupt
                sys.path.insert(0, str(ndt_path.parent))
                from app import app
                
                # Suppress Flask/Werkzeug logging and output
                import logging
                import warnings
                from contextlib import redirect_stderr, redirect_stdout
                from io import StringIO
                import sys as sys_module
                
                # Suppress all Flask/Werkzeug output BEFORE importing Flask
                logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
                logging.getLogger('flask').setLevel(logging.CRITICAL)
                warnings.filterwarnings("ignore")
                
                # Disable Flask's default startup messages
                os.environ['WERKZEUG_RUN_MAIN'] = 'true'
                
                # Run Flask app with KeyboardInterrupt handling
                port = 5001
                try:
                    # Print server info in a nice box before starting Flask
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                    
                    server_msg = f"{Colors.OKGREEN}{Colors.BOLD}Server draait op{Colors.ENDC} {Colors.BRIGHT_CYAN}{Colors.BOLD}http://localhost:{port}{Colors.ENDC}"
                    server_clean = ansi_escape.sub('', server_msg)
                    # Calculate padding: content_width includes the space after ║, so subtract 1 for that space
                    # Total width should be: space(1) + message + padding = content_width
                    server_padding = max(0, content_width - len(server_clean) - 1)
                    # Ensure total length matches exactly - recalculate if needed
                    total_length = 1 + len(server_clean) + server_padding  # space + message + padding
                    if total_length != content_width:
                        server_padding = max(0, content_width - len(server_clean) - 1)
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                    
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                    
                    # Suppress Flask output completely by redirecting stdout/stderr
                    # Save original streams
                    original_stdout = sys_module.stdout
                    original_stderr = sys_module.stderr
                    
                    # Redirect to devnull
                    devnull = StringIO()
                    sys_module.stdout = devnull
                    sys_module.stderr = devnull
                    
                    # Also suppress werkzeug logging completely
                    werkzeug_logger = logging.getLogger('werkzeug')
                    werkzeug_logger.setLevel(logging.CRITICAL)
                    werkzeug_logger.disabled = True
                    
                    try:
                        # Use werkzeug's make_server for better control and no startup messages
                        from werkzeug.serving import make_server
                        # Create server silently
                        server = make_server('0.0.0.0', port, app, threaded=True, processes=1)
                        server.serve_forever()
                    finally:
                        # Restore original streams
                        sys_module.stdout = original_stdout
                        sys_module.stderr = original_stderr
                        werkzeug_logger.disabled = False
                except KeyboardInterrupt:
                    # User pressed Ctrl+C, return to main menu
                    raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                # Clean up environment variable
                if 'JACOPS_RUNNING' in os.environ:
                    del os.environ['JACOPS_RUNNING']
        else:
            # Center the error message
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}NDT tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze.{Colors.ENDC}"
        print(center_text(error_msg))


def run_threat_intelligence_dashboard():
    """Run Live Threat Intelligence Dashboard"""
    choice = ask_cli_or_gui("Live Threat Intelligence Dashboard")
    
    ltid_dir = Path(__file__).parent / "LTID"
    
    if choice == "1":
        # CLI versie
        print_tool_header("Live Threat Intelligence Dashboard", "CLI")
        
        ltid_cli_path = ltid_dir / "cli.py"
        if ltid_cli_path.exists():
            original_dir = os.getcwd()
            try:
                # Change to LTID directory and run CLI
                os.chdir(ltid_cli_path.parent)
                sys.path.insert(0, str(ltid_cli_path.parent))
                
                # Add virtual environment to path if it exists
                venv_site_packages = ltid_cli_path.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
                if not venv_site_packages.exists():
                    import glob
                    venv_lib = ltid_cli_path.parent / ".venv" / "lib"
                    if venv_lib.exists():
                        python_dirs = glob.glob(str(venv_lib / "python*"))
                        if python_dirs:
                            venv_site_packages = Path(python_dirs[0]) / "site-packages"
                
                if venv_site_packages.exists():
                    sys.path.insert(0, str(venv_site_packages))
                
                from cli import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}LTID CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("Live Threat Intelligence Dashboard", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        ltid_path = ltid_dir / "dashboard.py"
        if ltid_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web dashboard..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web dashboard...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Account for the space after ║
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly
            total_length = 1 + len(start_clean) + start_padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            os.chdir(ltid_path.parent)
            try:
                # Set environment variable to suppress output
                os.environ['JACOPS_RUNNING'] = '1'
                
                # Suppress logging and warnings before importing
                import logging
                import warnings
                from contextlib import redirect_stderr, redirect_stdout
                from io import StringIO
                import sys as sys_module
                
                # Suppress all logging output
                logging.basicConfig(level=logging.CRITICAL)
                logging.getLogger('uvicorn').setLevel(logging.CRITICAL)
                logging.getLogger('uvicorn.access').setLevel(logging.CRITICAL)
                logging.getLogger('fastapi').setLevel(logging.CRITICAL)
                logging.getLogger('collectors').setLevel(logging.CRITICAL)
                warnings.filterwarnings("ignore")
                
                # Check if virtual environment exists and add it to path
                venv_site_packages = ltid_path.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
                if not venv_site_packages.exists():
                    # Try alternative Python version paths
                    import glob
                    venv_lib = ltid_path.parent / ".venv" / "lib"
                    if venv_lib.exists():
                        python_dirs = glob.glob(str(venv_lib / "python*"))
                        if python_dirs:
                            venv_site_packages = Path(python_dirs[0]) / "site-packages"
                
                if venv_site_packages.exists():
                    sys.path.insert(0, str(venv_site_packages))
                
                # Import and run the dashboard
                sys.path.insert(0, str(ltid_path.parent))
                from dashboard import run as dashboard_run
                
                # Get port from config
                try:
                    from config import Config
                    port = Config.PORT
                except:
                    port = 8001  # Changed from 8000 to avoid conflict with FTI
                
                # Print server info in a nice box before starting
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                
                server_msg = f"{Colors.OKGREEN}{Colors.BOLD}Server draait op{Colors.ENDC} {Colors.BRIGHT_CYAN}{Colors.BOLD}http://localhost:{port}{Colors.ENDC}"
                server_clean = ansi_escape.sub('', server_msg)
                # Account for the space after ║
                server_padding = max(0, content_width - len(server_clean) - 1)
                # Ensure total length matches exactly
                total_length = 1 + len(server_clean) + server_padding
                if total_length != content_width:
                    server_padding = max(0, content_width - len(server_clean) - 1)
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                
                # Suppress stdout and stderr
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                devnull = StringIO()
                sys_module.stdout = devnull
                sys_module.stderr = devnull
                
                try:
                    # Run dashboard
                    dashboard_run()
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}LTID tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze!{Colors.ENDC}"
        print(center_text(error_msg))


def run_password_policy_analyzer():
    """Run Password Policy Analyzer tool"""
    choice = ask_cli_or_gui("Password Policy Analyzer")
    
    if choice == "1":
        # CLI versie
        print_tool_header("Password Policy Analyzer", "CLI")
        
        ppa_cli_path = Path(__file__).parent / "PPA" / "cli.py"
        if ppa_cli_path.exists():
            original_dir = os.getcwd()
            try:
                # Change to PPA directory and run CLI
                os.chdir(ppa_cli_path.parent)
                sys.path.insert(0, str(ppa_cli_path.parent))
                
                from cli import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}PPA CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("Password Policy Analyzer", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        ppa_app_path = Path(__file__).parent / "PPA" / "app.py"
        if ppa_app_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Account for the space after ║
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly
            total_length = 1 + len(start_clean) + start_padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            original_dir = os.getcwd()
            try:
                os.chdir(ppa_app_path.parent)
                sys.path.insert(0, str(ppa_app_path.parent))
                
                # Check if virtual environment exists and add it to path
                venv_site_packages = ppa_app_path.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
                if not venv_site_packages.exists():
                    # Try alternative Python version paths
                    import glob
                    venv_lib = ppa_app_path.parent / ".venv" / "lib"
                    if venv_lib.exists():
                        python_dirs = glob.glob(str(venv_lib / "python*"))
                        if python_dirs:
                            venv_site_packages = Path(python_dirs[0]) / "site-packages"
                
                if venv_site_packages.exists():
                    sys.path.insert(0, str(venv_site_packages))
                
                # Check for required dependencies before starting
                missing_deps = []
                try:
                    import flask
                except ImportError:
                    missing_deps.append("flask")
                
                try:
                    import flask_cors
                except ImportError:
                    missing_deps.append("flask_cors")
                
                if missing_deps:
                    deps_str = ", ".join(missing_deps)
                    error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependencies: {deps_str}{Colors.ENDC}"
                    error_clean = ansi_escape.sub('', error_msg)
                    error_padding = (box_width - len(error_clean)) // 2
                    print(f"{' ' * (box_padding + error_padding)}{error_msg}")
                    print()
                    python_exe = sys.executable
                    install_msg = f"{Colors.WARNING}Installeer dependencies met:{Colors.ENDC} {Colors.OKCYAN}cd PPA && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt{Colors.ENDC}"
                    print(center_text(install_msg))
                    print()
                    alt_msg = f"{Colors.DIM}Of: cd PPA && pip3 install -r requirements.txt --break-system-packages{Colors.ENDC}"
                    print(center_text(alt_msg))
                    print()
                    return
                
                # Set environment variable to suppress output
                os.environ['JACOPS_RUNNING'] = '1'
                
                # Suppress logging and warnings before importing
                import logging
                import warnings
                from contextlib import redirect_stderr, redirect_stdout
                from io import StringIO
                import sys as sys_module
                
                # Suppress all logging output
                logging.basicConfig(level=logging.CRITICAL)
                logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
                logging.getLogger('flask').setLevel(logging.CRITICAL)
                warnings.filterwarnings("ignore")
                
                # Import Flask app (sys.path already set above)
                from app import app
                
                # Get port (default 5500)
                port = 5500
                
                # Print server info in a nice box before starting
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                
                server_msg = f"{Colors.OKGREEN}{Colors.BOLD}Server draait op{Colors.ENDC} {Colors.BRIGHT_CYAN}{Colors.BOLD}http://localhost:{port}{Colors.ENDC}"
                server_clean = ansi_escape.sub('', server_msg)
                # Account for the space after ║
                server_padding = max(0, content_width - len(server_clean) - 1)
                # Ensure total length matches exactly
                total_length = 1 + len(server_clean) + server_padding
                if total_length != content_width:
                    server_padding = max(0, content_width - len(server_clean) - 1)
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                
                # Suppress stdout and stderr
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                devnull = StringIO()
                sys_module.stdout = devnull
                sys_module.stderr = devnull
                
                # Suppress werkzeug logger
                werkzeug_logger = logging.getLogger('werkzeug')
                werkzeug_logger.setLevel(logging.CRITICAL)
                werkzeug_logger.disabled = True
                
                try:
                    # Use werkzeug's make_server for better control and no startup messages
                    from werkzeug.serving import make_server
                    # Create server silently
                    server = make_server('0.0.0.0', port, app, threaded=True, processes=1)
                    server.serve_forever()
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    werkzeug_logger.disabled = False
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except ImportError as e:
                missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependency: {missing_module}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
                print()
                install_msg = f"{Colors.WARNING}Installeer dependencies met:{Colors.ENDC} {Colors.OKCYAN}cd PPA && pip install -r requirements.txt{Colors.ENDC}"
                print(center_text(install_msg))
                print()
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)[:60]}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}PPA web tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze.{Colors.ENDC}"
        print(center_text(error_msg))


def run_caesar_cipher_analyzer():
    """Run Caesar Cipher Frequency Analyzer tool"""
    choice = ask_cli_or_gui("Caesar Cipher Frequency Analyzer")
    
    if choice == "1":
        # CLI versie
        print_tool_header("Caesar Cipher Frequency Analyzer", "CLI")
        
        ccfa_cli_path = Path(__file__).parent / "CCFA" / "cli.py"
        if ccfa_cli_path.exists():
            original_dir = os.getcwd()
            try:
                # Change to CCFA directory and run CLI
                os.chdir(ccfa_cli_path.parent)
                sys.path.insert(0, str(ccfa_cli_path.parent))
                
                from cli import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}CCFA CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("Caesar Cipher Frequency Analyzer", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        ccfa_web_gui_path = Path(__file__).parent / "CCFA" / "caesar_web_gui.py"
        if ccfa_web_gui_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Account for the space after ║
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly
            total_length = 1 + len(start_clean) + start_padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            original_dir = os.getcwd()
            try:
                os.chdir(ccfa_web_gui_path.parent)
                sys.path.insert(0, str(ccfa_web_gui_path.parent))
                
                # Suppress output from the web server
                import io
                import sys as sys_module
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                sys_module.stdout = io.StringIO()
                sys_module.stderr = io.StringIO()
                
                # Set environment variable to suppress internal logging
                os.environ['JACOPS_RUNNING'] = '1'
                
                try:
                    from caesar_web_gui import main as web_gui_main
                    
                    # Start server in a separate thread
                    import threading
                    server_thread = threading.Thread(target=web_gui_main, daemon=True)
                    server_thread.start()
                    
                    # Wait a moment for server to start
                    import time
                    time.sleep(1)
                    
                    # Restore stdout/stderr for our messages
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    
                    # Print server running message
                    port = 8002
                    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                    server_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓{Colors.ENDC} {Colors.OKGREEN}Server draait op http://localhost:{port}{Colors.ENDC}"
                    server_clean = ansi_escape.sub('', server_msg)
                    server_padding = max(0, content_width - len(server_clean) - 1)
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                    
                    # Wait for user interrupt
                    try:
                        while server_thread.is_alive():
                            time.sleep(0.5)
                    except KeyboardInterrupt:
                        pass
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}CCFA GUI tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze.{Colors.ENDC}"
        print(center_text(error_msg))


def run_dos_detector():
    """Run DoS Attack Detector tool"""
    choice = ask_cli_or_gui("DoS Attack Detector")
    
    if choice == "1":
        # CLI versie
        print_tool_header("DoS Attack Detector", "CLI")
        
        dsad_cli_path = Path(__file__).parent / "DSAD" / "cli.py"
        if dsad_cli_path.exists():
            original_dir = os.getcwd()
            try:
                os.chdir(dsad_cli_path.parent)
                sys.path.insert(0, str(dsad_cli_path.parent))
                
                from cli import main as cli_main, ReturnToMenuException as DSADReturnToMenuException
                cli_main()
            except DSADReturnToMenuException:
                # Return to main menu from DSAD CLI - suppress traceback
                # The custom excepthook in cli.py should have suppressed the traceback
                pass  # Just return to main menu silently
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                # Only show error if it's not a ReturnToMenuException
                if 'ReturnToMenuException' not in str(type(e)):
                    print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}DSAD CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("DoS Attack Detector", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        dsad_app_path = Path(__file__).parent / "DSAD" / "app.py"
        if dsad_app_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            original_dir = os.getcwd()
            try:
                os.chdir(dsad_app_path.parent)
                sys.path.insert(0, str(dsad_app_path.parent))
                
                # Check for virtual environment
                venv_path = dsad_app_path.parent / ".venv"
                if venv_path.exists():
                    import platform
                    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                    if platform.system() == "Windows":
                        site_packages = venv_path / "Lib" / "site-packages"
                    else:
                        site_packages = venv_path / "lib" / f"python{python_version}" / "site-packages"
                    if site_packages.exists():
                        sys.path.insert(0, str(site_packages))
                
                # Check dependencies
                missing_deps = []
                try:
                    import flask
                except ImportError:
                    missing_deps.append("flask")
                try:
                    import flask_cors
                    from flask_cors import CORS
                except ImportError:
                    missing_deps.append("flask-cors")
                
                if missing_deps:
                    deps_str = ", ".join(missing_deps)
                    error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependencies: {deps_str}{Colors.ENDC}"
                    error_clean = ansi_escape.sub('', error_msg)
                    error_padding = (box_width - len(error_clean)) // 2
                    print(f"{' ' * (box_padding + error_padding)}{error_msg}")
                    print()
                    install_cmd = "cd DSAD && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
                    if os.name == 'nt':
                        install_cmd = "cd DSAD && python3 -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt"
                    print(center_text(f"{Colors.WARNING}Installeer dependencies met:{Colors.ENDC} {Colors.OKCYAN}{install_cmd}{Colors.ENDC}"))
                    print()
                    input(center_text(f"{Colors.DIM}Druk Enter om terug te gaan naar het hoofdmenu...{Colors.ENDC}"))
                    return
                
                # Suppress output from the web server
                import io
                import sys as sys_module
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                sys_module.stdout = io.StringIO()
                sys_module.stderr = io.StringIO()
                
                # Set environment variable to suppress internal logging
                os.environ['JACOPS_RUNNING'] = '1'
                
                try:
                    from app import app
                    from config import SERVER_PORT, SERVER_HOST
                    
                    # Suppress Flask logging
                    import logging
                    log = logging.getLogger('werkzeug')
                    log.setLevel(logging.ERROR)
                    
                    # Start server in a separate thread using werkzeug
                    from werkzeug.serving import make_server
                    import threading
                    
                    server = make_server(SERVER_HOST, SERVER_PORT, app, threaded=True)
                    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                    server_thread.start()
                    
                    # Wait a moment for server to start
                    import time
                    time.sleep(1)
                    
                    # Restore stdout/stderr for our messages
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    
                    # Print server running message
                    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                    server_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓{Colors.ENDC} {Colors.OKGREEN}Server draait op http://{SERVER_HOST}:{SERVER_PORT}{Colors.ENDC}"
                    server_clean = ansi_escape.sub('', server_msg)
                    server_padding = max(0, content_width - len(server_clean) - 1)
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                    
                    # Wait for user interrupt
                    try:
                        while server_thread.is_alive():
                            time.sleep(0.5)
                    except KeyboardInterrupt:
                        pass
                    finally:
                        server.shutdown()
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}DSAD GUI tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze.{Colors.ENDC}"
        print(center_text(error_msg))


def run_secure_file_sharing():
    """Run Secure File Sharing System tool"""
    choice = ask_cli_or_gui("Secure File Sharing System")
    
    if choice == "1":
        # CLI versie
        print_tool_header("Secure File Sharing System", "CLI")
        
        sfs_cli_path = Path(__file__).parent / "SFS" / "cli.py"
        if sfs_cli_path.exists():
            original_dir = os.getcwd()
            try:
                # Change to SFS directory and run CLI
                os.chdir(sfs_cli_path.parent)
                sys.path.insert(0, str(sfs_cli_path.parent))
                
                from cli import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}SFS CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("Secure File Sharing System", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        sfs_app_path = Path(__file__).parent / "SFS" / "app.py"
        if sfs_app_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Account for the space after ║
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly
            total_length = 1 + len(start_clean) + start_padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            original_dir = os.getcwd()
            try:
                os.chdir(sfs_app_path.parent)
                sys.path.insert(0, str(sfs_app_path.parent))
                
                # Check if virtual environment exists and add it to path
                venv_site_packages = sfs_app_path.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
                if not venv_site_packages.exists():
                    # Try alternative Python version paths
                    import glob
                    venv_lib = sfs_app_path.parent / ".venv" / "lib"
                    if venv_lib.exists():
                        python_dirs = glob.glob(str(venv_lib / "python*"))
                        if python_dirs:
                            venv_site_packages = Path(python_dirs[0]) / "site-packages"
                
                if venv_site_packages.exists():
                    sys.path.insert(0, str(venv_site_packages))
                
                # Check dependencies
                try:
                    import flask
                    import flask_cors
                except ImportError as e:
                    error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependency: {e.name if hasattr(e, 'name') else str(e)}{Colors.ENDC}"
                    error_clean = ansi_escape.sub('', error_msg)
                    error_padding = (box_width - len(error_clean)) // 2
                    print(f"{' ' * (box_padding + error_padding)}{error_msg}")
                    print(f"\n{' ' * box_padding}{Colors.DIM}Installeer dependencies met: cd SFS && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt{Colors.ENDC}\n")
                    return
                
                # Suppress output from Flask
                import io
                import sys as sys_module
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                sys_module.stdout = io.StringIO()
                sys_module.stderr = io.StringIO()
                
                # Set environment variable to suppress internal logging
                os.environ['JACOPS_RUNNING'] = '1'
                
                # Suppress Flask logging
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
                flask_log = logging.getLogger('flask')
                flask_log.setLevel(logging.ERROR)
                
                try:
                    from app import app as flask_app
                    from werkzeug.serving import make_server
                    from config import SERVER_PORT
                    
                    # Start server in a separate thread
                    import threading
                    server = make_server('127.0.0.1', SERVER_PORT, flask_app, threaded=True)
                    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                    server_thread.start()
                    
                    # Wait a moment for server to start
                    import time
                    time.sleep(1)
                    
                    # Restore stdout/stderr for our messages
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    
                    # Print server running message
                    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                    server_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓{Colors.ENDC} {Colors.OKGREEN}Server draait op http://localhost:{SERVER_PORT}{Colors.ENDC}"
                    server_clean = ansi_escape.sub('', server_msg)
                    server_padding = max(0, content_width - len(server_clean) - 1)
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                    
                    # Wait for user interrupt
                    try:
                        while server_thread.is_alive():
                            time.sleep(0.5)
                    except KeyboardInterrupt:
                        pass
                    finally:
                        server.shutdown()
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}SFS GUI tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze!{Colors.ENDC}"
        print(center_text(error_msg))


def run_intrusion_detection():
    """Run Intrusion Detection Monitor tool"""
    choice = ask_cli_or_gui("Intrusion Detection Monitor")

    if choice == "1":
        print_tool_header("Intrusion Detection Monitor", "CLI")
        idm_cli_path = Path(__file__).parent / "IDM" / "cli.py"
        if idm_cli_path.exists():
            original_dir = os.getcwd()
            try:
                os.chdir(idm_cli_path.parent)
                sys.path.insert(0, str(idm_cli_path.parent))
                from cli import main as cli_main, ReturnToMenuException as IDMReturnToMenuException
                cli_main()
            except IDMReturnToMenuException:
                pass
            except KeyboardInterrupt:
                raise ReturnToMenuException()
            except Exception as e:
                if "ReturnToMenuException" not in str(type(e)):
                    print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except Exception:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}IDM CLI niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        print_tool_header("Intrusion Detection Monitor", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        idm_app_path = Path(__file__).parent / "IDM" / "app.py"
        if idm_app_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            original_dir = os.getcwd()
            try:
                os.chdir(idm_app_path.parent)
                sys.path.insert(0, str(idm_app_path.parent))
                
                # Check for virtual environment
                venv_path = idm_app_path.parent / ".venv"
                if venv_path.exists():
                    import platform
                    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                    if platform.system() == "Windows":
                        site_packages = venv_path / "Lib" / "site-packages"
                    else:
                        site_packages = venv_path / "lib" / f"python{python_version}" / "site-packages"
                    if site_packages.exists():
                        sys.path.insert(0, str(site_packages))
                
                # Check dependencies
                missing_deps = []
                try:
                    import flask
                except ImportError:
                    missing_deps.append("flask")
                try:
                    import flask_cors
                    from flask_cors import CORS
                except ImportError:
                    missing_deps.append("flask-cors")
                
                if missing_deps:
                    deps_str = ", ".join(missing_deps)
                    error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependencies: {deps_str}{Colors.ENDC}"
                    error_clean = ansi_escape.sub('', error_msg)
                    error_padding = (box_width - len(error_clean)) // 2
                    print(f"{' ' * (box_padding + error_padding)}{error_msg}")
                    print()
                    install_cmd = "cd IDM && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
                    if os.name == 'nt':
                        install_cmd = "cd IDM && python3 -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt"
                    print(center_text(f"{Colors.WARNING}Installeer dependencies met:{Colors.ENDC} {Colors.OKCYAN}{install_cmd}{Colors.ENDC}"))
                    print()
                    input(center_text(f"{Colors.DIM}Druk Enter om terug te gaan naar het hoofdmenu...{Colors.ENDC}"))
                    return
                
                # Suppress output from the web server
                import io
                import sys as sys_module
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                sys_module.stdout = io.StringIO()
                sys_module.stderr = io.StringIO()
                
                # Set environment variable to suppress internal logging
                os.environ['JACOPS_RUNNING'] = '1'
                
                try:
                    from app import app
                    from config import SERVER_PORT, SERVER_HOST
                    
                    # Suppress Flask logging
                    import logging
                    log = logging.getLogger('werkzeug')
                    log.setLevel(logging.ERROR)
                    
                    # Start server in a separate thread using werkzeug
                    from werkzeug.serving import make_server
                    import threading
                    
                    server = make_server(SERVER_HOST, SERVER_PORT, app, threaded=True)
                    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                    server_thread.start()
                    
                    # Wait a moment for server to start
                    import time
                    time.sleep(1)
                    
                    # Restore stdout/stderr for our messages
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    
                    # Print server running message
                    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                    server_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓{Colors.ENDC} {Colors.OKGREEN}Server draait op http://{SERVER_HOST}:{SERVER_PORT}{Colors.ENDC}"
                    server_clean = ansi_escape.sub('', server_msg)
                    server_padding = max(0, content_width - len(server_clean) - 1)
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                    
                    # Wait for user interrupt
                    try:
                        while server_thread.is_alive():
                            time.sleep(0.5)
                    except KeyboardInterrupt:
                        pass
                    finally:
                        server.shutdown()
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}IDM GUI tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")


def run_web_vulnerability_scanner():
    """Run Web Vulnerability Scanner tool"""
    choice = ask_cli_or_gui("Web Vulnerability Scanner")
    
    if choice == "1":
        # CLI versie
        print_tool_header("Web Vulnerability Scanner", "CLI")
        
        wvs_cli_path = Path(__file__).parent / "WVS" / "cli.py"
        if wvs_cli_path.exists():
            original_dir = os.getcwd()
            try:
                # Change to WVS directory and run CLI
                os.chdir(wvs_cli_path.parent)
                sys.path.insert(0, str(wvs_cli_path.parent))
                
                # Check if virtual environment exists and add it to path
                venv_site_packages = wvs_cli_path.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
                if not venv_site_packages.exists():
                    # Try alternative Python version paths
                    import glob
                    venv_lib = wvs_cli_path.parent / ".venv" / "lib"
                    if venv_lib.exists():
                        python_dirs = glob.glob(str(venv_lib / "python*"))
                        if python_dirs:
                            venv_site_packages = Path(python_dirs[0]) / "site-packages"
                
                if venv_site_packages.exists():
                    sys.path.insert(0, str(venv_site_packages))
                
                # Check dependencies
                try:
                    import requests
                    import bs4
                except ImportError as e:
                    error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependency: {e.name if hasattr(e, 'name') else str(e)}{Colors.ENDC}"
                    print(f"\n{error_msg}")
                    print(f"{Colors.DIM}Installeer dependencies met: cd WVS && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt{Colors.ENDC}\n")
                    return
                
                from cli import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except Exception as e:
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uitvoeren: {str(e)}{Colors.ENDC}\n")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}WVS CLI tool niet gevonden!{Colors.ENDC}")
    elif choice == "2":
        # GUI versie
        print_tool_header("Web Vulnerability Scanner", "GUI")
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        box_width = 75
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73
        content_width = 73
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        wvs_app_path = Path(__file__).parent / "WVS" / "app.py"
        if wvs_app_path.exists():
            # Print nice box with server info
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            
            # "Starten van web interface..." line
            start_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}→{Colors.ENDC} {Colors.OKGREEN}Starten van web interface...{Colors.ENDC}"
            start_clean = ansi_escape.sub('', start_msg)
            # Account for the space after ║
            start_padding = max(0, content_width - len(start_clean) - 1)
            # Ensure total length matches exactly
            total_length = 1 + len(start_clean) + start_padding
            if total_length != content_width:
                start_padding = max(0, content_width - len(start_clean) - 1)
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {start_msg}{' ' * start_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            
            original_dir = os.getcwd()
            try:
                os.chdir(wvs_app_path.parent)
                sys.path.insert(0, str(wvs_app_path.parent))
                
                # Check if virtual environment exists and add it to path
                venv_site_packages = wvs_app_path.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
                if not venv_site_packages.exists():
                    # Try alternative Python version paths
                    import glob
                    venv_lib = wvs_app_path.parent / ".venv" / "lib"
                    if venv_lib.exists():
                        python_dirs = glob.glob(str(venv_lib / "python*"))
                        if python_dirs:
                            venv_site_packages = Path(python_dirs[0]) / "site-packages"
                
                if venv_site_packages.exists():
                    sys.path.insert(0, str(venv_site_packages))
                
                # Check dependencies
                try:
                    import flask
                    import flask_cors
                    import requests
                    import bs4
                except ImportError as e:
                    error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Ontbrekende dependency: {e.name if hasattr(e, 'name') else str(e)}{Colors.ENDC}"
                    error_clean = ansi_escape.sub('', error_msg)
                    error_padding = (box_width - len(error_clean)) // 2
                    print(f"{' ' * (box_padding + error_padding)}{error_msg}")
                    print(f"\n{' ' * box_padding}{Colors.DIM}Installeer dependencies met: cd WVS && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt{Colors.ENDC}\n")
                    return
                
                # Suppress output from Flask
                import io
                import sys as sys_module
                original_stdout = sys_module.stdout
                original_stderr = sys_module.stderr
                sys_module.stdout = io.StringIO()
                sys_module.stderr = io.StringIO()
                
                # Set environment variable to suppress internal logging
                os.environ['JACOPS_RUNNING'] = '1'
                
                # Suppress Flask logging
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
                flask_log = logging.getLogger('flask')
                flask_log.setLevel(logging.ERROR)
                
                try:
                    from app import app as flask_app
                    from werkzeug.serving import make_server
                    from config import SERVER_PORT
                    
                    # Start server in a separate thread
                    import threading
                    server = make_server('127.0.0.1', SERVER_PORT, flask_app, threaded=True)
                    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
                    server_thread.start()
                    
                    # Wait a moment for server to start
                    import time
                    time.sleep(1)
                    
                    # Restore stdout/stderr for our messages
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    
                    # Print server running message
                    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                    server_msg = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓{Colors.ENDC} {Colors.OKGREEN}Server draait op http://localhost:{SERVER_PORT}{Colors.ENDC}"
                    server_clean = ansi_escape.sub('', server_msg)
                    server_padding = max(0, content_width - len(server_clean) - 1)
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                    
                    # Wait for user interrupt
                    try:
                        while server_thread.is_alive():
                            time.sleep(0.5)
                    except KeyboardInterrupt:
                        pass
                    finally:
                        server.shutdown()
                finally:
                    # Restore original streams
                    sys_module.stdout = original_stdout
                    sys_module.stderr = original_stderr
                    if 'JACOPS_RUNNING' in os.environ:
                        del os.environ['JACOPS_RUNNING']
            except KeyboardInterrupt:
                # User pressed Ctrl+C, return to main menu
                raise ReturnToMenuException()
            except ReturnToMenuException:
                raise
            except Exception as e:
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij starten: {str(e)}{Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                error_padding = (box_width - len(error_clean)) // 2
                print(f"{' ' * (box_padding + error_padding)}{error_msg}")
            finally:
                try:
                    os.chdir(original_dir)
                except:
                    pass
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}WVS GUI tool niet gevonden!{Colors.ENDC}"
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_clean = ansi_escape.sub('', error_msg)
            error_padding = (box_width - len(error_clean)) // 2
            print(f"{' ' * (box_padding + error_padding)}{error_msg}")
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze!{Colors.ENDC}"
        print(center_text(error_msg))


def main():
    """Main function"""
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = get_user_choice()
        
        if choice == "0":
            try:
                term_width = shutil.get_terminal_size().columns
            except:
                term_width = 80
            
            # Thank you message box - use EXACT same dimensions as menu box
            box_width = 75  # Same as menu box
            box_padding = (term_width - box_width) // 2
            border_line = "═" * 73  # Same as menu box
            content_width = 73  # Same as menu box
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            message = "Bedankt voor het gebruiken van JacOps Security Suite!"
            message_with_colors = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}{message}{Colors.ENDC}"
            message_clean = ansi_escape.sub('', message_with_colors)
            message_length = len(message_clean)
            
            # Calculate padding to center message and fill exact width
            # Format: " " (1 space) + message_padding + message + right_padding = content_width
            # So: message_padding + message_length + right_padding = content_width - 1
            available_width = content_width - 1  # Subtract 1 for leading space
            message_padding = (available_width - message_length) // 2
            right_padding = available_width - message_length - message_padding
            
            # Ensure padding is correct and matches menu box formatting
            if message_padding < 0:
                message_padding = 0
            if right_padding < 0:
                right_padding = 0
            
            # Print with exact same formatting as menu box
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {' ' * message_padding}{message_with_colors}{' ' * right_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            sys.exit(0)
        elif choice == "1":
            # File Type Identifier returns True if user wants to skip "press Enter" prompt
            try:
                result = run_file_type_identifier()
                # If result is True (user pressed 'q'), skip the "press Enter" prompt
                if result == True:
                    continue  # Skip "press Enter" prompt and go directly back to menu
                # If we reach here, a file was processed, so show "press Enter" prompt
                print()
                enter_prompt = f"{Colors.DIM}Druk Enter om terug te gaan naar het hoofdmenu...{Colors.ENDC}"
                input(center_text(enter_prompt))
            except ReturnToMenuException:
                # User pressed Ctrl+C in GUI, return to main menu
                continue
        elif choice == "2":
            run_phishing_email_simulator()
        elif choice == "3":
            try:
                run_network_device_scanner()
            except ReturnToMenuException:
                # User pressed Ctrl+C in GUI, return to main menu
                continue
        elif choice == "4":
            run_threat_intelligence_dashboard()
        elif choice == "5":
            run_password_policy_analyzer()
        elif choice == "6":
            run_caesar_cipher_analyzer()
        elif choice == "7":
            run_dos_detector()
        elif choice == "8":
            run_secure_file_sharing()
        elif choice == "9":
            run_intrusion_detection()
        elif choice == "10":
            run_web_vulnerability_scanner()
        else:
            error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}⚠  Ongeldige keuze! Probeer opnieuw.{Colors.ENDC}"
            print(f"\n{center_text(error_msg)}")
        
        # Show "press Enter" prompt for all other tools (not choice "0" or "1")
        # For choice "1", we handle it above - if user pressed 'q', we use continue to skip
        if choice != "0" and choice != "1":
            print()
            enter_prompt = f"{Colors.DIM}Druk Enter om terug te gaan naar het hoofdmenu...{Colors.ENDC}"
            input(center_text(enter_prompt))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # User wants to exit the entire tool
        print("\n")
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        # Thank you message box - use EXACT same dimensions as menu box
        box_width = 75  # Same as menu box
        box_padding = (term_width - box_width) // 2
        border_line = "═" * 73  # Same as menu box
        content_width = 73  # Same as menu box
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        message = "Bedankt voor het gebruiken van JacOps Security Suite!"
        message_with_colors = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}{message}{Colors.ENDC}"
        message_clean = ansi_escape.sub('', message_with_colors)
        message_length = len(message_clean)
        
        # Calculate padding to center message and fill exact width
        # Format: " " (1 space) + message_padding + message + right_padding = content_width
        # So: message_padding + message_length + right_padding = content_width - 1
        available_width = content_width - 1  # Subtract 1 for leading space
        message_padding = (available_width - message_length) // 2
        right_padding = available_width - message_length - message_padding
        
        # Ensure padding is correct and matches menu box formatting
        if message_padding < 0:
            message_padding = 0
        if right_padding < 0:
            right_padding = 0
        
        # Print with exact same formatting as menu box
        print(f"\n\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {' ' * message_padding}{message_with_colors}{' ' * right_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
        sys.exit(0)
