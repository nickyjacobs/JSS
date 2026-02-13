#!/usr/bin/env python3
"""
DoS Test Simulator - Genereert gesimuleerd DoS-verkeer voor het testen van de detector.
Alleen voor lokaal testen op eigen systeem. Gebruik nooit tegen externe doelen zonder toestemming.
"""

import argparse
import time
import sys
import warnings
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))

# Onderdruk Scapy-warning: 'iface' heeft geen effect bij L3 send()
warnings.filterwarnings("ignore", message=".*iface.*no effect.*", category=SyntaxWarning)

try:
    from scapy.all import IP, TCP, UDP, ICMP, send
except ImportError:
    print("Scapy is vereist. Installeer met: pip install scapy")
    sys.exit(1)


def send_syn_flood(target: str, count: int, interval: float, interface: str = None):
    """Verstuur SYN-pakketten (onder drempel = legaal testverkeer)."""
    for i in range(count):
        pkt = IP(dst=target) / TCP(flags="S", sport=40000 + (i % 20000), dport=80)
        send(pkt, verbose=False)
        if interval > 0:
            time.sleep(interval)


def send_udp_flood(target: str, count: int, interval: float, interface: str = None):
    """Verstuur UDP-pakketten."""
    for i in range(count):
        pkt = IP(dst=target) / UDP(sport=50000 + (i % 15000), dport=53) / (b"X" * 64)
        send(pkt, verbose=False)
        if interval > 0:
            time.sleep(interval)


def send_icmp_flood(target: str, count: int, interval: float, interface: str = None):
    """Verstuur ICMP Echo Request (ping)-pakketten."""
    for i in range(count):
        pkt = IP(dst=target) / ICMP(id=i % 65535, seq=i)
        send(pkt, verbose=False)
        if interval > 0:
            time.sleep(interval)


def run_test(
    test_type: str,
    target: str = "127.0.0.1",
    count: int = 150,
    duration_sec: float = 8.0,
    interface: str = None,
):
    """
    Voer een DoS-simulatie uit.
    test_type: syn, udp, icmp, all
    """
    if count <= 0 or duration_sec <= 0:
        raise ValueError("count en duration_sec moeten positief zijn")
    interval = duration_sec / count if count else 0
    start = time.time()
    sent = 0

    if test_type == "syn":
        send_syn_flood(target, count, interval, interface)
        sent = count
    elif test_type == "udp":
        send_udp_flood(target, count, interval, interface)
        sent = count
    elif test_type == "icmp":
        send_icmp_flood(target, count, interval, interface)
        sent = count
    elif test_type == "all":
        # Voor "all" verzenden we meer pakketten per type zodat we zeker boven thresholds komen
        # SYN: 120, UDP: 100, ICMP: 80 (totaal ~300)
        syn_count = int(count * 0.4)  # 40% voor SYN
        udp_count = int(count * 0.35)  # 35% voor UDP
        icmp_count = count - syn_count - udp_count  # Rest voor ICMP
        
        send_syn_flood(target, syn_count, duration_sec / (3 * syn_count) if syn_count else 0, interface)
        sent = syn_count
        send_udp_flood(target, udp_count, duration_sec / (3 * udp_count) if udp_count else 0, interface)
        sent += udp_count
        send_icmp_flood(target, icmp_count, duration_sec / (3 * icmp_count) if icmp_count else 0, interface)
        sent += icmp_count
    else:
        raise ValueError(f"Onbekend type: {test_type}")

    elapsed = time.time() - start
    return sent, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="DoS-test simulator voor DSAD (alleen lokaal testen)."
    )
    parser.add_argument(
        "--type", "-t",
        choices=["syn", "udp", "icmp", "all"],
        default="syn",
        help="Type test (default: syn)",
    )
    parser.add_argument(
        "--target",
        default="127.0.0.1",
        help="Doel-IP (default: 127.0.0.1, alleen lokaal)",
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=150,
        help="Aantal pakketten per type (default: 150)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=8.0,
        help="Duur in seconden (default: 8)",
    )
    parser.add_argument(
        "--interface", "-i",
        default=None,
        help="Netwerkinterface (optioneel)",
    )
    args = parser.parse_args()
    run_test(
        test_type=args.type,
        target=args.target,
        count=args.count,
        duration_sec=args.duration,
        interface=args.interface,
    )
    print(f"Test voltooid: {args.type.upper()}, doel={args.target}, pakketten verzonden.")


if __name__ == "__main__":
    main()
