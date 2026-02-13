from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

# Veelgebruikte poorten om te scannen
COMMON_PORTS = [
    21,    # FTP
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    80,    # HTTP
    88,    # Kerberos
    110,   # POP3
    135,   # MSRPC
    139,   # NetBIOS
    143,   # IMAP
    443,   # HTTPS
    445,   # SMB
    554,   # RTSP
    993,   # IMAPS
    995,   # POP3S
    1433,  # MSSQL
    3306,  # MySQL
    3389,  # RDP
    5432,  # PostgreSQL
    5900,  # VNC
    8080,  # HTTP-alt
    8443,  # HTTPS-alt
    9100,  # Printer
]


def scan_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """Scan een enkele poort."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def scan_common_ports(ip: str, ports: List[int] = None, timeout: float = 1.0) -> List[int]:
    """
    Scan veelgebruikte poorten op een IP-adres.
    Retourneert lijst van open poorten.
    """
    if ports is None:
        ports = COMMON_PORTS
    
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_port = {executor.submit(scan_port, ip, port, timeout): port for port in ports}
        for fut in as_completed(future_to_port):
            port = future_to_port[fut]
            try:
                if fut.result():
                    open_ports.append(port)
            except Exception:
                continue
    
    return sorted(open_ports)


def get_service_name(port: int) -> str:
    """Geef service naam voor een poort."""
    service_map = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 88: "Kerberos", 110: "POP3", 135: "MSRPC",
        139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        554: "RTSP", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
        8080: "HTTP-alt", 8443: "HTTPS-alt", 9100: "Printer",
    }
    return service_map.get(port, f"Port {port}")
