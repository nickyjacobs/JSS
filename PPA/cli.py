#!/usr/bin/env python3
"""
Password Policy Analyzer - CLI entry point.
"""

import os
import re
import shutil
import sys
import json
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from policy_analyzer import PolicyAnalyzer, PolicyRequirement, calculate_security_score
except ImportError:
    print("Error: Could not import policy_analyzer. Make sure you're in the correct directory.")
    sys.exit(1)

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
    LOW = '\033[90m'
    MEDIUM = '\033[94m'
    HIGH = '\033[93m'
    CRITICAL = '\033[91m'


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
        'critical': Colors.CRITICAL,
        'high': Colors.HIGH,
        'medium': Colors.MEDIUM,
        'low': Colors.LOW
    }
    return severity_colors.get(severity.lower(), Colors.ENDC)


def load_policy_from_file(file_path: Path) -> Dict:
    """Load policy from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Support both direct policy object and nested policy object
            if 'policy' in data:
                return data['policy']
            return data
    except FileNotFoundError:
        print_boxed_message(f"Fout: Bestand '{file_path}' niet gevonden!", Colors.FAIL)
        return None
    except json.JSONDecodeError as e:
        print_boxed_message(f"Fout: Ongeldige JSON in bestand '{file_path}': {e}", Colors.FAIL)
        return None


def get_policy_input() -> Optional[PolicyRequirement]:
    """Get policy input from user"""
    print_progress("Voer password policy parameters in:")
    print()
    
    try:
        min_length = int(input(f"{center_text('Minimale lengte (standaard: 8): ')}").strip() or "8")
        max_length_input = input(f"{center_text('Maximale lengte (optioneel, Enter voor geen limiet): ')}").strip()
        max_length = int(max_length_input) if max_length_input else None
        
        print()
        print_progress("Complexity vereisten (j/n):")
        require_uppercase = input(f"{center_text('Hoofdletters vereisen? (j/n, standaard: j): ')}").strip().lower() != 'n'
        require_lowercase = input(f"{center_text('Kleine letters vereisen? (j/n, standaard: j): ')}").strip().lower() != 'n'
        require_numbers = input(f"{center_text('Cijfers vereisen? (j/n, standaard: j): ')}").strip().lower() != 'n'
        require_special_chars = input(f"{center_text('Speciale tekens vereisen? (j/n, standaard: j): ')}").strip().lower() != 'n'
        
        print()
        print_progress("Password aging (Enter voor standaard):")
        max_age_input = input(f"{center_text('Maximale leeftijd (dagen, Enter voor geen limiet): ')}").strip()
        max_age_days = int(max_age_input) if max_age_input else None
        min_age_input = input(f"{center_text('Minimale leeftijd (dagen, standaard: 0): ')}").strip()
        min_age_days = int(min_age_input) if min_age_input else 0
        
        print()
        print_progress("Andere instellingen:")
        password_history_input = input(f"{center_text('Password history count (standaard: 0): ')}").strip()
        password_history = int(password_history_input) if password_history_input else 0
        
        lockout_attempts_input = input(f"{center_text('Lockout attempts (Enter voor geen lockout): ')}").strip()
        lockout_attempts = int(lockout_attempts_input) if lockout_attempts_input else None
        
        lockout_duration_input = input(f"{center_text('Lockout duration (minuten, Enter voor geen lockout): ')}").strip()
        lockout_duration_minutes = int(lockout_duration_input) if lockout_duration_input else None
        
        print()
        print_progress("Security features (j/n):")
        prevent_common = input(f"{center_text('Voorkom veelvoorkomende wachtwoorden? (j/n): ')}").strip().lower() == 'j'
        prevent_user_info = input(f"{center_text('Voorkom gebruikersinformatie? (j/n): ')}").strip().lower() == 'j'
        prevent_repeating = input(f"{center_text('Voorkom herhalende karakters? (j/n): ')}").strip().lower() == 'j'
        prevent_sequential = input(f"{center_text('Voorkom sequentiële karakters? (j/n): ')}").strip().lower() == 'j'
        
        return PolicyRequirement(
            min_length=min_length,
            max_length=max_length,
            require_uppercase=require_uppercase,
            require_lowercase=require_lowercase,
            require_numbers=require_numbers,
            require_special_chars=require_special_chars,
            max_age_days=max_age_days,
            min_age_days=min_age_days,
            password_history=password_history,
            lockout_attempts=lockout_attempts,
            lockout_duration_minutes=lockout_duration_minutes,
            prevent_common_passwords=prevent_common,
            prevent_user_info=prevent_user_info,
            prevent_repeating_chars=prevent_repeating,
            prevent_sequential_chars=prevent_sequential
        )
    except ValueError:
        print_boxed_message("Fout: Ongeldige invoer! Gebruik alleen cijfers voor numerieke waarden.", Colors.FAIL)
        return None
    except KeyboardInterrupt:
        print()
        return None


def print_results(score_data: Dict, findings: list):
    """Print analysis results in a formatted box"""
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    score = score_data['score']
    grade = score_data['grade']
    message = score_data['message']
    
    # Determine color based on grade
    if grade in ['A+', 'A']:
        grade_color = Colors.OKGREEN
    elif grade == 'B':
        grade_color = Colors.OKCYAN
    elif grade == 'C':
        grade_color = Colors.WARNING
    elif grade == 'D':
        grade_color = Colors.HIGH
    else:
        grade_color = Colors.CRITICAL
    
    # Header
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    header = f" {Colors.BOLD}Security Score{Colors.ENDC}"
    header_clean = ansi_escape.sub('', header)
    header_padding = max(0, content_width - len(header_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{header}{' ' * header_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Score
    score_line = f" {Colors.BOLD}Score:{Colors.ENDC} {grade_color}{score}{Colors.ENDC}/100"
    score_clean = ansi_escape.sub('', score_line)
    score_padding = max(0, content_width - len(score_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{score_line}{' ' * score_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Grade
    grade_line = f" {Colors.BOLD}Grade:{Colors.ENDC} {grade_color}{grade}{Colors.ENDC}"
    grade_clean = ansi_escape.sub('', grade_line)
    grade_padding = max(0, content_width - len(grade_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{grade_line}{' ' * grade_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    # Message
    message_line = f" {Colors.BOLD}Status:{Colors.ENDC} {message}"
    message_clean = ansi_escape.sub('', message_line)
    if len(message_clean) > content_width:
        # Wrap message
        words = message.split()
        current_line = f" {Colors.BOLD}Status:{Colors.ENDC} "
        for word in words:
            test_line = current_line + word + " "
            test_clean = ansi_escape.sub('', test_line)
            if len(test_clean) > content_width:
                current_clean = ansi_escape.sub('', current_line)
                current_padding = max(0, content_width - len(current_clean))
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{current_line}{' ' * current_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                current_line = "              " + word + " "  # Indent continuation
            else:
                current_line = test_line
        if current_line.strip():
            current_clean = ansi_escape.sub('', current_line)
            current_padding = max(0, content_width - len(current_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{current_line}{' ' * current_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    else:
        message_padding = max(0, content_width - len(message_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{message_line}{' ' * message_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    
    # Findings summary
    summary_line = f" {Colors.BOLD}Findings Summary:{Colors.ENDC}"
    summary_clean = ansi_escape.sub('', summary_line)
    summary_padding = max(0, content_width - len(summary_clean))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{summary_line}{' ' * summary_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    critical_count = score_data.get('critical_count', 0)
    high_count = score_data.get('high_count', 0)
    medium_count = score_data.get('medium_count', 0)
    low_count = score_data.get('low_count', 0)
    total = score_data.get('total_findings', 0)
    
    findings_lines = [
        f"   • Critical: {Colors.CRITICAL}{critical_count}{Colors.ENDC}",
        f"   • High:     {Colors.HIGH}{high_count}{Colors.ENDC}",
        f"   • Medium:   {Colors.MEDIUM}{medium_count}{Colors.ENDC}",
        f"   • Low:      {Colors.LOW}{low_count}{Colors.ENDC}",
        f"   • Total:    {total}"
    ]
    
    for line in findings_lines:
        line_clean = ansi_escape.sub('', line)
        line_padding = max(0, content_width - len(line_clean))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{line}{' ' * line_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    
    # Print findings details if any
    if findings:
        print_progress("Findings & Recommendations:")
        print()
        
        # Group by severity
        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for finding in findings:
            severity = finding['severity'].lower()
            if severity in by_severity:
                by_severity[severity].append(finding)
        
        index = 1
        for severity in ['critical', 'high', 'medium', 'low']:
            if by_severity[severity]:
                severity_color = get_severity_color(severity)
                print_boxed_message(f"{severity.upper()} SEVERITY ({len(by_severity[severity])} findings)", severity_color)
                
                for finding in by_severity[severity]:
                    title = f"{index}. {finding['title']}"
                    print(center_text(title, term_width))
                    print(center_text(f"[{severity.upper()}]", term_width))
                    print(center_text(finding['description'], term_width))
                    if finding.get('breach_statistics'):
                        stats = f"Statistics: {finding['breach_statistics']}"
                        print(center_text(stats, term_width))
                    rec = f"Recommendation: {finding['recommendation']}"
                    print(center_text(rec, term_width))
                    std = f"{Colors.BOLD}{Colors.OKCYAN}Standard:{Colors.ENDC} {Colors.OKCYAN}{finding['standard']}{Colors.ENDC}"
                    print(center_text(std, term_width))
                    print()
                    index += 1
    else:
        print_boxed_message("✓ Geen issues gevonden! Je password policy voldoet aan alle industry standards.", Colors.OKGREEN)


def export_results(score_data: Dict, findings: list, policy: PolicyRequirement, output_file: Path):
    """Export results to JSON file"""
    report = {
        'score': score_data,
        'findings': findings,
        'policy': {
            'min_length': policy.min_length,
            'max_length': policy.max_length,
            'require_uppercase': policy.require_uppercase,
            'require_lowercase': policy.require_lowercase,
            'require_numbers': policy.require_numbers,
            'require_special_chars': policy.require_special_chars,
            'max_age_days': policy.max_age_days,
            'min_age_days': policy.min_age_days,
            'password_history': policy.password_history,
            'lockout_attempts': policy.lockout_attempts,
            'lockout_duration_minutes': policy.lockout_duration_minutes,
            'prevent_common_passwords': policy.prevent_common_passwords,
            'prevent_user_info': policy.prevent_user_info,
            'prevent_repeating_chars': policy.prevent_repeating_chars,
            'prevent_sequential_chars': policy.prevent_sequential_chars
        }
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_boxed_message(f"✓ Rapport geëxporteerd naar: {output_file}", Colors.OKGREEN)
    except Exception as e:
        print_boxed_message(f"Fout bij exporteren: {e}", Colors.FAIL)


def analyze_policy(policy: PolicyRequirement, lang: str = 'nl') -> tuple:
    """Analyze a policy and return results"""
    analyzer = PolicyAnalyzer(lang=lang)
    findings = analyzer.analyze(policy)
    
    # Calculate score
    score_data = calculate_security_score(findings, lang=lang)
    
    # Convert findings to dict
    findings_dict = []
    for finding in findings:
        findings_dict.append({
            'severity': finding.severity.value,
            'title': finding.title,
            'description': finding.description,
            'recommendation': finding.recommendation,
            'standard': finding.standard,
            'breach_statistics': finding.breach_statistics,
            'impact_score': finding.impact_score
        })
    
    return score_data, findings_dict, policy


def main():
    """Main CLI function"""
    # Check if command-line arguments are provided (for scripting)
    if len(sys.argv) > 1:
        # Use argparse for command-line mode
        import argparse
        parser = argparse.ArgumentParser(
            description='Password Policy Analyzer - CLI Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Analyze from JSON file
  python cli.py --file example_policy.json

  # Analyze with command-line arguments
  python cli.py --min-length 8 --prevent-common-passwords

  # Export to JSON
  python cli.py --file example_policy.json --export report.json

  # Use English language
  python cli.py --file example_policy.json --lang en
            """
        )
        
        # Input options
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument('--file', '-f', type=Path, help='Path to JSON policy file')
        input_group.add_argument('--min-length', type=int, help='Minimum password length')
        
        # Policy parameters
        parser.add_argument('--max-length', type=int, help='Maximum password length')
        parser.add_argument('--require-uppercase', action='store_true', help='Require uppercase letters')
        parser.add_argument('--require-lowercase', action='store_true', help='Require lowercase letters')
        parser.add_argument('--require-numbers', action='store_true', help='Require numbers')
        parser.add_argument('--require-special-chars', action='store_true', help='Require special characters')
        parser.add_argument('--max-age-days', type=int, help='Maximum password age in days')
        parser.add_argument('--min-age-days', type=int, help='Minimum password age in days')
        parser.add_argument('--password-history', type=int, help='Password history count')
        parser.add_argument('--lockout-attempts', type=int, help='Account lockout attempts')
        parser.add_argument('--lockout-duration-minutes', type=int, help='Lockout duration in minutes')
        parser.add_argument('--prevent-common-passwords', action='store_true', help='Prevent common passwords')
        parser.add_argument('--prevent-user-info', action='store_true', help='Prevent user information in passwords')
        parser.add_argument('--prevent-repeating-chars', action='store_true', help='Prevent repeating characters')
        parser.add_argument('--prevent-sequential-chars', action='store_true', help='Prevent sequential characters')
        
        # Output options
        parser.add_argument('--lang', choices=['nl', 'en'], default='nl', help='Language (default: nl)')
        parser.add_argument('--export', '-e', type=Path, help='Export results to JSON file')
        parser.add_argument('--json', action='store_true', help='Output results as JSON only')
        parser.add_argument('--quiet', '-q', action='store_true', help='Suppress colored output')
        
        args = parser.parse_args()
        
        # Load policy
        if args.file:
            policy_dict = load_policy_from_file(args.file)
            if policy_dict is None:
                sys.exit(1)
            policy = PolicyRequirement(**policy_dict)
        else:
            if not args.min_length:
                parser.error("--min-length is required when not using --file")
            policy = PolicyRequirement(
                min_length=args.min_length,
                max_length=args.max_length,
                require_uppercase=args.require_uppercase,
                require_lowercase=args.require_lowercase,
                require_numbers=args.require_numbers,
                require_special_chars=args.require_special_chars,
                max_age_days=args.max_age_days,
                min_age_days=args.min_age_days or 0,
                password_history=args.password_history or 0,
                lockout_attempts=args.lockout_attempts,
                lockout_duration_minutes=args.lockout_duration_minutes,
                prevent_common_passwords=args.prevent_common_passwords,
                prevent_user_info=args.prevent_user_info,
                prevent_repeating_chars=args.prevent_repeating_chars,
                prevent_sequential_chars=args.prevent_sequential_chars
            )
        
        # Analyze
        score_data, findings_dict, policy = analyze_policy(policy, args.lang)
        
        # Output results
        if args.json:
            result = {
                'success': True,
                'score': score_data,
                'findings': findings_dict,
                'policy': {
                    'min_length': policy.min_length,
                    'max_length': policy.max_length,
                    'require_uppercase': policy.require_uppercase,
                    'require_lowercase': policy.require_lowercase,
                    'require_numbers': policy.require_numbers,
                    'require_special_chars': policy.require_special_chars,
                    'max_age_days': policy.max_age_days,
                    'min_age_days': policy.min_age_days,
                    'password_history': policy.password_history,
                    'lockout_attempts': policy.lockout_attempts,
                    'lockout_duration_minutes': policy.lockout_duration_minutes,
                    'prevent_common_passwords': policy.prevent_common_passwords,
                    'prevent_user_info': policy.prevent_user_info,
                    'prevent_repeating_chars': policy.prevent_repeating_chars,
                    'prevent_sequential_chars': policy.prevent_sequential_chars
                }
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print_results(score_data, findings_dict)
            if args.export:
                export_results(score_data, findings_dict, policy, args.export)
        
        # Exit with error code if there are critical findings
        sys.exit(1 if score_data.get('critical_count', 0) > 0 else 0)
    
    # Interactive menu mode
    current_results = None
    current_policy = None
    
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
            menu_title = f" {Colors.BOLD}Password Policy Analyzer{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub('', menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            
            option1 = f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Analyseer vanuit JSON bestand"
            option1_clean = ansi_escape.sub('', option1)
            option1_padding = max(0, content_width - len(option1_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option1}{' ' * option1_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option2 = f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  Analyseer met handmatige input"
            option2_clean = ansi_escape.sub('', option2)
            option2_padding = max(0, content_width - len(option2_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option2}{' ' * option2_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            if current_results:
                option3 = f" {Colors.OKCYAN}{Colors.BOLD}[3]{Colors.ENDC}  Export resultaten"
                option3_clean = ansi_escape.sub('', option3)
                option3_padding = max(0, content_width - len(option3_clean))
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option3}{' ' * option3_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            option4 = f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten"
            option4_clean = ansi_escape.sub('', option4)
            option4_padding = max(0, content_width - len(option4_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{option4}{' ' * option4_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}")
            
            # Get user choice
            print()
            choice = input(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} ").strip().lower()
            
            if choice == "1":
                file_path_input = input(f"{center_text('Pad naar JSON bestand: ')}").strip()
                if file_path_input:
                    file_path = Path(file_path_input)
                    policy_dict = load_policy_from_file(file_path)
                    if policy_dict:
                        policy = PolicyRequirement(**policy_dict)
                        print_progress("Analyseren van policy...")
                        score_data, findings_dict, policy = analyze_policy(policy)
                        current_results = (score_data, findings_dict)
                        current_policy = policy
                        print_results(score_data, findings_dict)
                else:
                    error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen pad opgegeven!{Colors.ENDC}"
                    print(center_text(error_msg))
            
            elif choice == "2":
                policy = get_policy_input()
                if policy:
                    print_progress("Analyseren van policy...")
                    score_data, findings_dict, policy = analyze_policy(policy)
                    current_results = (score_data, findings_dict)
                    current_policy = policy
                    print_results(score_data, findings_dict)
            
            elif choice == "3" and current_results:
                export_path_input = input(f"{center_text('Export pad (bijv. report.json): ')}").strip()
                if export_path_input:
                    export_path = Path(export_path_input)
                    score_data, findings_dict = current_results
                    export_results(score_data, findings_dict, current_policy, export_path)
                else:
                    error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Geen pad opgegeven!{Colors.ENDC}"
                    print(center_text(error_msg))
            
            elif choice == "q":
                print_boxed_message("Afsluiten...", Colors.OKGREEN)
                break
            
            else:
                error_msg = f"{Colors.WARNING}{Colors.BOLD}⚠{Colors.ENDC} {Colors.WARNING}Ongeldige keuze!{Colors.ENDC}"
                print(center_text(error_msg))
    
    except KeyboardInterrupt:
        print()
        print_boxed_message("Afsluiten...", Colors.OKGREEN)


if __name__ == '__main__':
    main()
