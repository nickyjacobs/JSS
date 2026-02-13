#!/usr/bin/env python3
"""
Secure File Sharing System - CLI entry point.
"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from file_manager import FileManager
from config import MAX_FILE_SIZE, DEFAULT_EXPIRY_HOURS, DOWNLOAD_DIR

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


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_datetime(dt_str: str) -> str:
    """Format ISO datetime string to readable format"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str


def upload_file(file_manager: FileManager):
    """Upload a file"""
    file_path_input = input(f"{center_text('Voer pad naar bestand in: ')}").strip()
    
    if not file_path_input:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen pad opgegeven!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    file_path = Path(file_path_input)
    if not file_path.exists():
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Bestand niet gevonden!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    if file_path.is_dir():
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Dit is een directory, geen bestand!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Bestand te groot! Maximum: {format_file_size(MAX_FILE_SIZE)}{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    # Read file
    print_progress("Bestand lezen...")
    file_data = file_path.read_bytes()
    
    # Ask for password (optional)
    password_input = input(f"{center_text('Wachtwoord (optioneel, Enter voor geen): ')}").strip()
    password = password_input if password_input else None
    
    # Ask for expiry hours
    expiry_input = input(f"{center_text(f'Verlooptijd in uren (standaard {DEFAULT_EXPIRY_HOURS}): ')}").strip()
    try:
        expiry_hours = int(expiry_input) if expiry_input else DEFAULT_EXPIRY_HOURS
        expiry_hours = max(1, min(expiry_hours, 168))  # Max 7 days
    except ValueError:
        expiry_hours = DEFAULT_EXPIRY_HOURS
    
    # Save file
    print_progress("Bestand versleutelen en opslaan...")
    try:
        result = file_manager.save_file(
            file_data,
            file_path.name,
            password=password,
            expiry_hours=expiry_hours
        )
        
        # Display result
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
        header = f" {Colors.BOLD}Bestand geüpload!{Colors.ENDC}"
        header_clean = ansi_escape.sub('', header)
        header_padding = max(0, content_width - len(header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        
        token_line = f" {Colors.BOLD}Token:{Colors.ENDC} {Colors.BRIGHT_GREEN}{result['token']}{Colors.ENDC}"
        token_clean = ansi_escape.sub('', token_line)
        token_padding = max(0, content_width - len(token_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{token_line}{' ' * token_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        filename_line = f" {Colors.BOLD}Bestandsnaam:{Colors.ENDC} {result['filename']}"
        filename_clean = ansi_escape.sub('', filename_line)
        filename_padding = max(0, content_width - len(filename_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{filename_line}{' ' * filename_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        expiry_line = f" {Colors.BOLD}Verloopt op:{Colors.ENDC} {format_datetime(result['expiry_time'])}"
        expiry_clean = ansi_escape.sub('', expiry_line)
        expiry_padding = max(0, content_width - len(expiry_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{expiry_line}{' ' * expiry_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
        
    except Exception as e:
        error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij uploaden: {str(e)}{Colors.ENDC}"
        print(center_text(error_msg))


def download_file(file_manager: FileManager):
    """Download a file"""
    # Show downloads directory info
    downloads_info = f"Downloads worden opgeslagen in: {DOWNLOAD_DIR}"
    print(center_text(f"{Colors.DIM}{downloads_info}{Colors.ENDC}"))
    print()
    
    token_input = input(f"{center_text('Voer token in: ')}").strip()
    
    if not token_input:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen token opgegeven!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    # Get file info
    file_info = file_manager.get_file_info(token_input)
    if not file_info:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Token niet gevonden of verlopen!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    # Check password if required
    password = None
    if file_info.get("password_protected"):
        password_input = input(f"{center_text('Voer wachtwoord in: ')}").strip()
        password = password_input
    
    # Download file
    print_progress("Bestand downloaden en ontsleutelen...")
    file_data = file_manager.download_file(token_input, password)
    
    if not file_data:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Download mislukt! Controleer wachtwoord.{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    # Save file to downloads directory
    default_filename = file_info["filename"]
    default_path = DOWNLOAD_DIR / default_filename
    
    # Handle filename conflicts by adding number suffix
    counter = 1
    while default_path.exists():
        name_part = default_path.stem
        ext_part = default_path.suffix
        default_path = DOWNLOAD_DIR / f"{name_part}_{counter}{ext_part}"
        counter += 1
    
    save_prompt = f"Opslaan als (standaard: {default_path.name} in downloads/): "
    output_path_input = input(f"{center_text(save_prompt)}").strip()
    
    if output_path_input:
        # User specified a path - if relative, use downloads dir, if absolute use as-is
        user_path = Path(output_path_input)
        if user_path.is_absolute():
            output_path = user_path
        else:
            # Relative path - save in downloads directory
            output_path = DOWNLOAD_DIR / user_path
    else:
        # Use default filename in downloads directory
        output_path = default_path
    
    try:
        output_path.write_bytes(file_data)
        # Show relative path if in downloads directory
        if DOWNLOAD_DIR in output_path.parents or output_path.parent == DOWNLOAD_DIR:
            relative_path = output_path.relative_to(DOWNLOAD_DIR)
            print_boxed_message(f"Bestand opgeslagen in downloads/: {relative_path}\nVolledig pad: {output_path}", Colors.OKGREEN)
        else:
            print_boxed_message(f"Bestand opgeslagen: {output_path}", Colors.OKGREEN)
    except Exception as e:
        error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Fout bij opslaan: {str(e)}{Colors.ENDC}"
        print(center_text(error_msg))


def list_files(file_manager: FileManager):
    """List all active files"""
    print_progress("Actieve bestanden ophalen...")
    files = file_manager.list_files()
    
    if not files:
        print_boxed_message("Geen actieve bestanden gevonden.", Colors.WARNING)
        return
    
    # Display files
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
    header = f" {Colors.BOLD}Actieve Bestanden ({len(files)}){Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    for i, file_info in enumerate(files, 1):
        filename = file_info["filename"]
        if len(filename) > 30:
            filename = filename[:27] + "..."
        
        file_line = f" {Colors.DIM}{i}.{Colors.ENDC} {Colors.BOLD}{filename}{Colors.ENDC} ({format_file_size(file_info['file_size'])})"
        if file_info.get("password_protected"):
            file_line += f" {Colors.WARNING}[Wachtwoord]{Colors.ENDC}"
        
        file_clean = ansi_escape.sub('', file_line)
        if len(file_clean) > content_width:
            file_line = f" {Colors.DIM}{i}.{Colors.ENDC} {filename[:20]}..."
            file_clean = ansi_escape.sub('', file_line)
        
        file_padding = max(0, content_width - len(file_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{file_line}{' ' * file_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        token_line = f"    Token: {Colors.OKCYAN}{file_info['token']}{Colors.ENDC}"
        token_clean = ansi_escape.sub('', token_line)
        token_padding = max(0, content_width - len(token_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{token_line}{' ' * token_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        expiry_line = f"    Verloopt: {format_datetime(file_info['expiry_time'])}"
        expiry_clean = ansi_escape.sub('', expiry_line)
        expiry_padding = max(0, content_width - len(expiry_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{expiry_line}{' ' * expiry_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        if i < len(files):
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def delete_file(file_manager: FileManager):
    """Delete a file"""
    token_input = input(f"{center_text('Voer token in om te verwijderen: ')}").strip()
    
    if not token_input:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen token opgegeven!{Colors.ENDC}"
        print(center_text(error_msg))
        return
    
    confirm = input(f"{center_text('Weet je zeker dat je dit bestand wilt verwijderen? (j/n): ')}").strip().lower()
    if confirm != 'j':
        print(center_text("Geannuleerd."))
        return
    
    if file_manager.delete_file(token_input):
        print_boxed_message("Bestand verwijderd!", Colors.OKGREEN)
    else:
        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Bestand niet gevonden!{Colors.ENDC}"
        print(center_text(error_msg))


def cleanup_expired(file_manager: FileManager):
    """Clean up expired files"""
    print_progress("Verlopen bestanden opruimen...")
    deleted_count = file_manager.cleanup_expired()
    print_boxed_message(f"{deleted_count} verlopen bestand(en) verwijderd.", Colors.OKGREEN)


def main():
    """Main CLI function"""
    file_manager = FileManager()
    
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
            menu_title = f" {Colors.BOLD}Secure File Sharing System{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub('', menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Upload bestand"
            option1_clean = ansi_escape.sub('', option1)
            option1_padding = max(0, content_width - len(option1_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option2 = f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  Download bestand"
            option2_clean = ansi_escape.sub('', option2)
            option2_padding = max(0, content_width - len(option2_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option3 = f" {Colors.OKCYAN}{Colors.BOLD}[3]{Colors.ENDC}  Lijst actieve bestanden"
            option3_clean = ansi_escape.sub('', option3)
            option3_padding = max(0, content_width - len(option3_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option3}{' ' * option3_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option4 = f" {Colors.OKCYAN}{Colors.BOLD}[4]{Colors.ENDC}  Verwijder bestand"
            option4_clean = ansi_escape.sub('', option4)
            option4_padding = max(0, content_width - len(option4_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option4}{' ' * option4_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option5 = f" {Colors.OKCYAN}{Colors.BOLD}[5]{Colors.ENDC}  Ruim verlopen bestanden op"
            option5_clean = ansi_escape.sub('', option5)
            option5_padding = max(0, content_width - len(option5_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option5}{' ' * option5_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option6 = f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten"
            option6_clean = ansi_escape.sub('', option6)
            option6_padding = max(0, content_width - len(option6_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option6}{' ' * option6_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
            
            # Get user choice
            print()
            choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} ").strip().lower()
            
            if choice == "1":
                upload_file(file_manager)
            elif choice == "2":
                download_file(file_manager)
            elif choice == "3":
                list_files(file_manager)
            elif choice == "4":
                delete_file(file_manager)
            elif choice == "5":
                cleanup_expired(file_manager)
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
