#!/usr/bin/env python3
"""
Caesar Cipher Frequency Analyzer - CLI entry point.
"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from caesar_decoder import CaesarDecoder

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


def print_results(result: Dict):
    """Print de resultaten in een mooie box"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Header
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Decryptie Resultaten{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Encrypted text
    encrypted_line = f" {Colors.BOLD}Encrypted:{Colors.ENDC} {result['encrypted'][:60]}"
    if len(result['encrypted']) > 60:
        encrypted_line = f" {Colors.BOLD}Encrypted:{Colors.ENDC} {result['encrypted'][:57]}..."
    encrypted_clean = ansi_escape.sub('', encrypted_line)
    encrypted_padding = max(0, content_width - len(encrypted_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{encrypted_line}{' ' * encrypted_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Shift
    shift_line = f" {Colors.BOLD}Gevonden shift:{Colors.ENDC} {Colors.BRIGHT_GREEN}{result['shift']}{Colors.ENDC}"
    shift_clean = ansi_escape.sub('', shift_line)
    shift_padding = max(0, content_width - len(shift_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{shift_line}{' ' * shift_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Confidence score
    score_line = f" {Colors.BOLD}Confidence score:{Colors.ENDC} {Colors.OKCYAN}{result['confidence_score']:.2f}{Colors.ENDC} {Colors.DIM}(lager = beter){Colors.ENDC}"
    score_clean = ansi_escape.sub('', score_line)
    if len(score_clean) > content_width:
        score_line = f" {Colors.BOLD}Confidence score:{Colors.ENDC} {Colors.OKCYAN}{result['confidence_score']:.2f}{Colors.ENDC}"
        score_clean = ansi_escape.sub('', score_line)
    score_padding = max(0, content_width - len(score_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{score_line}{' ' * score_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Decrypted text
    decrypted_text = result['decrypted']
    decrypted_header = f" {Colors.BOLD}Decrypted tekst:{Colors.ENDC}"
    decrypted_header_clean = ansi_escape.sub('', decrypted_header)
    decrypted_header_padding = max(0, content_width - len(decrypted_header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{decrypted_header}{' ' * decrypted_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Wrap decrypted text if needed
    words = decrypted_text.split()
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_clean = ansi_escape.sub('', f" {test_line}")
        if len(test_clean) > content_width:
            if current_line:
                current_clean = ansi_escape.sub('', f" {current_line}")
                current_padding = max(0, content_width - len(current_clean))
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.OKGREEN}{current_line}{Colors.ENDC}{' ' * current_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            current_line = word
        else:
            current_line = test_line.strip()
    
    if current_line:
        current_clean = ansi_escape.sub('', f" {current_line}")
        current_padding = max(0, content_width - len(current_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.OKGREEN}{current_line}{Colors.ENDC}{' ' * current_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # All attempts if available
    if result.get('all_attempts'):
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
        attempts_header = f" {Colors.BOLD}Top 5 meest waarschijnlijke decrypties:{Colors.ENDC}"
        attempts_header_clean = ansi_escape.sub('', attempts_header)
        attempts_header_padding = max(0, content_width - len(attempts_header_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{attempts_header}{' ' * attempts_header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
        
        for i, attempt in enumerate(result['all_attempts'][:5], 1):
            attempt_line = f" {Colors.DIM}{i}.{Colors.ENDC} Shift {Colors.BOLD}{attempt['shift']:2d}{Colors.ENDC} (score: {Colors.OKCYAN}{attempt['score']:.2f}{Colors.ENDC}): {attempt['text'][:40]}"
            if len(attempt['text']) > 40:
                attempt_line = f" {Colors.DIM}{i}.{Colors.ENDC} Shift {Colors.BOLD}{attempt['shift']:2d}{Colors.ENDC} (score: {Colors.OKCYAN}{attempt['score']:.2f}{Colors.ENDC}): {attempt['text'][:37]}..."
            attempt_clean = ansi_escape.sub('', attempt_line)
            if len(attempt_clean) > content_width:
                attempt_line = f" {Colors.DIM}{i}.{Colors.ENDC} Shift {Colors.BOLD}{attempt['shift']:2d}{Colors.ENDC}: {attempt['text'][:50]}"
                if len(attempt['text']) > 50:
                    attempt_line = f" {Colors.DIM}{i}.{Colors.ENDC} Shift {Colors.BOLD}{attempt['shift']:2d}{Colors.ENDC}: {attempt['text'][:47]}..."
                attempt_clean = ansi_escape.sub('', attempt_line)
            attempt_padding = max(0, content_width - len(attempt_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{attempt_line}{' ' * attempt_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def print_frequencies(frequencies: Dict[str, float]):
    """Print letter frequencies in a formatted box"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Header
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Letter Frequenties{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Frequencies (top 10)
    for letter, freq in list(frequencies.items())[:10]:
        freq_line = f" {Colors.BOLD}{letter}:{Colors.ENDC} {Colors.OKCYAN}{freq:.2f}%{Colors.ENDC}"
        freq_clean = ansi_escape.sub('', freq_line)
        freq_padding = max(0, content_width - len(freq_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{freq_line}{' ' * freq_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def main():
    """Main CLI function"""
    decoder = CaesarDecoder()
    
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
            menu_title = f" {Colors.BOLD}Caesar Cipher Frequency Analyzer{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub('', menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Decrypt een bericht (automatisch shift detectie)"
            option1_clean = ansi_escape.sub('', option1)
            option1_padding = max(0, content_width - len(option1_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option2 = f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  Encrypt een bericht"
            option2_clean = ansi_escape.sub('', option2)
            option2_padding = max(0, content_width - len(option2_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option3 = f" {Colors.OKCYAN}{Colors.BOLD}[3]{Colors.ENDC}  Analyseer letter frequenties"
            option3_clean = ansi_escape.sub('', option3)
            option3_padding = max(0, content_width - len(option3_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option3}{' ' * option3_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option4 = f" {Colors.OKCYAN}{Colors.BOLD}[4]{Colors.ENDC}  Test met voorbeeld"
            option4_clean = ansi_escape.sub('', option4)
            option4_padding = max(0, content_width - len(option4_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option4}{' ' * option4_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option5 = f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten"
            option5_clean = ansi_escape.sub('', option5)
            option5_padding = max(0, content_width - len(option5_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option5}{' ' * option5_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
            
            # Get user choice
            print()
            choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} ").strip().lower()
            
            if choice == "1":
                encrypted_input = input(f"{center_text('Voer encrypted tekst in: ')}").strip()
                if encrypted_input:
                    show_all_input = input(f"{center_text('Toon alle pogingen? (j/n): ')}").strip().lower()
                    show_all = show_all_input == 'j'
                    print_progress("Analyseren en decrypten...")
                    result = decoder.crack(encrypted_input, show_all=show_all)
                    print_results(result)
                else:
                    error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen tekst opgegeven!{Colors.ENDC}"
                    print(center_text(error_msg))
            
            elif choice == "2":
                text_input = input(f"{center_text('Voer tekst in om te encrypten: ')}").strip()
                if text_input:
                    try:
                        shift_input = input(f"{center_text('Voer shift waarde in (0-25): ')}").strip()
                        shift = int(shift_input)
                        if 0 <= shift <= 25:
                            encrypted = decoder.encrypt(text_input, shift)
                            print_boxed_message(f"Encrypted tekst: {encrypted}", Colors.OKGREEN)
                        else:
                            error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Shift moet tussen 0 en 25 zijn!{Colors.ENDC}"
                            print(center_text(error_msg))
                    except ValueError:
                        error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige shift waarde!{Colors.ENDC}"
                        print(center_text(error_msg))
                else:
                    error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen tekst opgegeven!{Colors.ENDC}"
                    print(center_text(error_msg))
            
            elif choice == "3":
                text_input = input(f"{center_text('Voer tekst in om te analyseren: ')}").strip()
                if text_input:
                    print_progress("Analyseren van letter frequenties...")
                    frequencies = decoder.analyze_frequencies(text_input)
                    if frequencies:
                        print_frequencies(frequencies)
                    else:
                        print_boxed_message("Geen letters gevonden in de tekst!", Colors.WARNING)
                else:
                    error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen tekst opgegeven!{Colors.ENDC}"
                    print(center_text(error_msg))
            
            elif choice == "4":
                # Test voorbeeld
                test_message = "HELLO WORLD THIS IS A TEST MESSAGE"
                test_shift = 3
                encrypted_test = decoder.encrypt(test_message, test_shift)
                
                print_boxed_message("Test Voorbeeld", Colors.OKCYAN)
                print(center_text(f"Origineel bericht: {test_message}"))
                print(center_text(f"Shift gebruikt: {test_shift}"))
                print(center_text(f"Encrypted: {encrypted_test}"))
                print()
                print_progress("Proberen te kraken...")
                
                result = decoder.crack(encrypted_test, show_all=True)
                print_results(result)
                
                if result['shift'] == test_shift:
                    print_boxed_message("✓ SUCCES! Shift correct gedetecteerd!", Colors.OKGREEN)
                else:
                    error_msg = f"✗ Shift niet correct (verwacht: {test_shift}, gevonden: {result['shift']})"
                    print_boxed_message(error_msg, Colors.WARNING)
            
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
