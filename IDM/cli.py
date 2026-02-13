#!/usr/bin/env python3
"""
Intrusion Detection Monitor - CLI entry point.
Monitor auth.log for failed logins (brute force) and show alerts.
"""

import os
import re
import shutil
import sys
import signal
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from detector import IntrusionDetector

try:
    from config import AUTH_LOG, FAILED_LOGIN_THRESHOLD, TIME_WINDOW_SECONDS
except ImportError:
    AUTH_LOG = "/var/log/auth.log"
    FAILED_LOGIN_THRESHOLD = 5
    TIME_WINDOW_SECONDS = 300


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BRIGHT_CYAN = "\033[1;96m"
    BRIGHT_RED = "\033[1;91m"


def center_text(text, width=None):
    if width is None:
        try:
            width = shutil.get_terminal_size().columns
        except Exception:
            width = 80
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    text_without_codes = ansi_escape.sub("", text)
    padding = (width - len(text_without_codes)) // 2
    return " " * padding + text


def _wrap_line(line, max_len):
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
        last_space = chunk.rfind(" ")
        if last_space > 0:
            out.append(line[:last_space])
            line = line[last_space:]
        else:
            out.append(line[:max_len])
            line = line[max_len:]
    return out


def print_boxed_message(message, color=Colors.OKGREEN):
    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 80
    box_width = min(75, max(40, term_width - 4))
    box_padding = max(0, (term_width - box_width) // 2)
    border_line = "═" * (box_width - 2)
    content_width = box_width - 2
    max_text_len = content_width - 2
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    wrapped = []
    for line in str(message).split("\n"):
        wrapped.extend(_wrap_line(line, max_text_len))
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    for line in wrapped:
        if not line.strip():
            continue
        msg_with_colors = f"{color}{Colors.BOLD}{line}{Colors.ENDC}"
        msg_clean = ansi_escape.sub("", msg_with_colors)
        msg_padding = max(0, content_width - len(msg_clean) - 1)
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {msg_with_colors}{' ' * msg_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")


def _get_box_dims():
    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 80
    box_width = min(75, max(40, term_width - 4))
    box_padding = max(0, (term_width - box_width) // 2)
    content_width = box_width - 2
    border_line = "═" * (box_width - 2)
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return box_padding, border_line, content_width, ansi_escape


detector_instance = None
_ctrl_c_requested = False
# Overrides from "Configuratie" (option 2); None = use config.py defaults
_current_log_path = None
_current_threshold = None
_current_window = None


class ReturnToMenuException(Exception):
    pass


_original_excepthook = sys.excepthook


def _custom_excepthook(exc_type, exc_value, exc_traceback):
    if exc_type == ReturnToMenuException:
        return
    if exc_type == KeyboardInterrupt and _ctrl_c_requested:
        return
    _original_excepthook(exc_type, exc_value, exc_traceback)


sys.excepthook = _custom_excepthook


def signal_handler(sig, frame):
    global detector_instance, _ctrl_c_requested
    _ctrl_c_requested = True
    if detector_instance:
        detector_instance.stop()


def _alert_callback(event_type, ip, count, threshold, rate, ts):
    box_padding, border_line, content_width, ansi_escape = _get_box_dims()
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    h = f" {Colors.BOLD}INTRUSIE GEDETECTEERD{Colors.ENDC}"
    pad = max(0, content_width - len(ansi_escape.sub("", h)))
    print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{h}{' ' * pad}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    for label, val in [
        ("Type", event_type),
        ("IP", ip),
        ("Aantal", f"{count} (drempel: {threshold})"),
        ("Rate", f"{rate:.2f}/min"),
        ("Tijd", ts),
    ]:
        line = f" {Colors.BOLD}{label}:{Colors.ENDC} {val}"
        pad = max(0, content_width - len(ansi_escape.sub("", line)))
        print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}{line}{' ' * pad}{Colors.BRIGHT_RED}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_RED}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    sys.stdout.flush()
    sys.stderr.flush()


def start_monitoring(log_path=None, failed_threshold=None, time_window=None):
    global detector_instance
    signal.signal(signal.SIGINT, signal_handler)

    log_path = Path(log_path if log_path is not None else _current_log_path or AUTH_LOG)
    failed_threshold = failed_threshold if failed_threshold is not None else (_current_threshold if _current_threshold is not None else FAILED_LOGIN_THRESHOLD)
    time_window = time_window if time_window is not None else (_current_window if _current_window is not None else TIME_WINDOW_SECONDS)

    if not log_path.exists():
        print_boxed_message(
            f"Logbestand niet gevonden: {log_path}\nOp dit systeem wordt mogelijk een ander pad gebruikt (bv. /var/log/secure).",
            Colors.WARNING,
        )
        return
    try:
        with open(log_path, "r"):
            pass
    except PermissionError:
        print_boxed_message(
            f"Geen leesrechten voor {log_path}. Voer uit met sudo om auth.log te monitoren.",
            Colors.FAIL,
        )
        return

    detector_instance = IntrusionDetector(
        log_path=log_path,
        failed_threshold=failed_threshold,
        time_window=time_window,
        alert_callback=_alert_callback,
    )

    box_padding, border_line, content_width, ansi_escape = _get_box_dims()
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    h = f" {Colors.BOLD}IDM Configuratie{Colors.ENDC}"
    pad = max(0, content_width - len(ansi_escape.sub("", h)))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{h}{' ' * pad}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    for line in [
        f" {Colors.BOLD}Log:{Colors.ENDC} {log_path}",
        f" {Colors.BOLD}Drempel:{Colors.ENDC} {failed_threshold} mislukte pogingen",
        f" {Colors.BOLD}Tijdvenster:{Colors.ENDC} {time_window} seconden",
    ]:
        p = max(0, content_width - len(ansi_escape.sub("", line)))
        print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{line}{' ' * p}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")

    print_boxed_message("Monitoring gestart. Druk Ctrl+C om te stoppen.", Colors.OKGREEN)
    detector_instance.start()

    try:
        while detector_instance.running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if detector_instance:
            detector_instance.stop()


def configure_idm():
    """Set global config overrides (log path, threshold, time window)."""
    global _current_log_path, _current_threshold, _current_window
    box_padding, border_line, content_width, ansi_escape = _get_box_dims()
    cur_path = _current_log_path or AUTH_LOG
    cur_thresh = _current_threshold if _current_threshold is not None else FAILED_LOGIN_THRESHOLD
    cur_win = _current_window if _current_window is not None else TIME_WINDOW_SECONDS
    print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
    h = f" {Colors.BOLD}IDM Configuratie{Colors.ENDC}"
    pad = max(0, content_width - len(ansi_escape.sub("", h)))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{h}{' ' * pad}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
    info = f" Huidig: {cur_path}, drempel {cur_thresh}, venster {cur_win}s"
    p = max(0, content_width - len(info))
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{info}{' ' * p}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
    print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
    path_str = input(center_text(f"Logpad (Enter = ongewijzigd): ")).strip()
    thresh_str = input(center_text(f"Drempel mislukte logins (Enter = {cur_thresh}): ")).strip()
    window_str = input(center_text(f"Tijdvenster seconden (Enter = {cur_win}): ")).strip()
    if path_str:
        _current_log_path = path_str
    if thresh_str.isdigit():
        _current_threshold = int(thresh_str)
    if window_str.isdigit():
        _current_window = int(window_str)
    print_boxed_message("Configuratie opgeslagen. Kies [1] om monitoring te starten.", Colors.OKGREEN)


def main():
    try:
        while True:
            box_padding, border_line, content_width, ansi_escape = _get_box_dims()
            print(f"\n{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
            menu_title = f" {Colors.BOLD}Intrusion Detection Monitor{Colors.ENDC}"
            menu_title_clean = ansi_escape.sub("", menu_title)
            menu_title_padding = max(0, content_width - len(menu_title_clean))
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{menu_title}{' ' * menu_title_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╠{border_line}╣{Colors.ENDC}")
            opts = [
                f" {Colors.OKCYAN}{Colors.BOLD}[1]{Colors.ENDC}  Start monitoring (auth.log)",
                f" {Colors.OKCYAN}{Colors.BOLD}[2]{Colors.ENDC}  Configuratie",
                f" {Colors.OKCYAN}{Colors.BOLD}[q]{Colors.ENDC}  Afsluiten",
            ]
            for line in opts:
                line_clean = ansi_escape.sub("", line)
                p = max(0, content_width - len(line_clean))
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}{line}{' ' * p}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
            print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
            choice = input(center_text(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}➜{Colors.ENDC} {Colors.BOLD}Keuze:{Colors.ENDC} ")).strip().lower()

            if choice == "1":
                try:
                    start_monitoring()
                except ReturnToMenuException:
                    raise
                except KeyboardInterrupt:
                    raise ReturnToMenuException()
            elif choice == "2":
                try:
                    configure_idm()
                except ReturnToMenuException:
                    raise
                except KeyboardInterrupt:
                    raise ReturnToMenuException()
            elif choice == "q":
                print_boxed_message("Afsluiten...", Colors.OKGREEN)
                break
            else:
                print_boxed_message("Ongeldige keuze. Kies 1, 2 of q.", Colors.WARNING)
    except KeyboardInterrupt:
        raise ReturnToMenuException()
    except ReturnToMenuException:
        raise


if __name__ == "__main__":
    main()
