from __future__ import annotations

import logging
import os
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from ipaddress import ip_network
from typing import Dict, List, Optional

from .mac_lookup import lookup_vendor

# Setup logging naar bestand
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"ndt_{datetime.now().strftime('%Y%m%d')}.log")

ndt_logger = logging.getLogger('NDT.scanner')
ndt_logger.setLevel(logging.INFO)
ndt_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
ndt_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
ndt_logger.addHandler(ndt_handler)
ndt_logger.propagate = False

def ndt_log(message):
    """Log naar bestand in plaats van stdout"""
    ndt_logger.info(message)


def _ping(ip: str, timeout: float = 0.5) -> bool:
  """
  Stuur één ping naar een IP-adres via het systeem-commando.
  Werkt zonder root (gebruikt gewoon 'ping').
  Linux-compatible versie.
  """
  import platform
  system = platform.system()
  
  try:
      if system == "Linux":
          # Linux: ping -c 1 -W <timeout_seconds> <ip>
          # -W is timeout in seconds on Linux
          result = subprocess.run(
              ["ping", "-c", "1", "-W", str(timeout), ip],
              stdout=subprocess.DEVNULL,
              stderr=subprocess.DEVNULL,
              timeout=timeout + 0.5,  # Extra timeout voor subprocess zelf
          )
          return result.returncode == 0
      else:
          # macOS: ping -c 1 -W <timeout_milliseconds> <ip>
          result = subprocess.run(
              ["ping", "-c", "1", "-W", str(int(timeout * 1000)), ip],
              stdout=subprocess.DEVNULL,
              stderr=subprocess.DEVNULL,
              timeout=timeout + 0.5,
          )
          return result.returncode == 0
  except (subprocess.TimeoutExpired, Exception):
      return False


def _get_mac(ip: str) -> Optional[str]:
  """
  Lees het MAC-adres voor een IP uit de ARP-tabel.
  Werkt op zowel Linux als macOS.
  """
  import platform
  import re
  system = platform.system()
  
  try:
      if system == "Linux":
          # Linux: gebruik 'ip neigh' of 'arp -n'
          try:
              # Probeer eerst 'ip neigh' (moderne methode)
              out = subprocess.check_output(["ip", "neigh", "show", ip], text=True, stderr=subprocess.DEVNULL)
              # Format: "10.120.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff STALE"
              m = re.search(r"lladdr\s+(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})", out, re.IGNORECASE)
              if m:
                  return m.group(1).lower()
          except:
              pass
          
          # Fallback naar arp
          out = subprocess.check_output(["arp", "-n", ip], text=True, stderr=subprocess.DEVNULL)
          # Linux format: "? (10.120.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0"
          m = re.search(r"(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})", out, re.IGNORECASE)
          if m:
              return m.group(1).lower()
      else:
          # macOS: arp -n <ip>
          out = subprocess.check_output(["arp", "-n", ip], text=True, stderr=subprocess.DEVNULL)
          # Typische regel op macOS:
          # ? (10.120.1.1) at aa:bb:cc:dd:ee:ff on en0 ifscope [ethernet]
          m = re.search(r"(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})", out, re.IGNORECASE)
          if m:
              return m.group(1).lower()
  except Exception:
      return None
  
  return None


def resolve_hostname(ip: str) -> Optional[str]:
  try:
      name, _, _ = socket.gethostbyaddr(ip)
      return name
  except Exception:
      return None


def _get_arp_cache() -> Dict[str, str]:
    """Haal alle IP->MAC mappings uit de ARP-tabel (performance-tweak)."""
    import platform
    import re
    cache: Dict[str, str] = {}
    system = platform.system()
    
    try:
        if system == "Linux":
            # Linux: gebruik 'ip neigh' (moderne methode)
            try:
                out = subprocess.check_output(["ip", "neigh", "show"], text=True, stderr=subprocess.DEVNULL)
                # Format: "10.120.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff STALE"
                for line in out.split('\n'):
                    if 'lladdr' in line:
                        match = re.search(r"(\d+\.\d+\.\d+\.\d+).*lladdr\s+(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})", line, re.IGNORECASE)
                        if match:
                            ip = match.group(1)
                            mac = match.group(2).lower()
                            cache[ip] = mac
            except:
                pass
            
            # Fallback naar arp -a
            try:
                out = subprocess.check_output(["arp", "-a"], text=True, stderr=subprocess.DEVNULL)
                # Linux format: "? (10.120.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0"
                for match in re.finditer(r"\(([0-9.]+)\)\s+at\s+(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})", out, re.IGNORECASE):
                    ip = match.group(1)
                    mac = match.group(2).lower()
                    cache[ip] = mac
            except:
                pass
        else:
            # macOS: arp -a
            out = subprocess.check_output(["arp", "-a"], text=True, stderr=subprocess.DEVNULL)
            # Match: ? (10.120.1.1) at aa:bb:cc:dd:ee:ff
            for match in re.finditer(r"\(([0-9.]+)\)\s+at\s+(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})", out, re.IGNORECASE):
                ip = match.group(1)
                mac = match.group(2).lower()
                cache[ip] = mac
    except Exception:
        pass
    
    return cache


def scan_network(cidr: str) -> List[Dict]:
  """
  Netwerkscan zonder scapy/root:
    1) Check eerst ARP-cache voor snelle resultaten (alle IP's die verbinding maken).
    2) Ping hosts binnen het subnet die nog niet in ARP-cache staan.
    3) Gebruik de ARP-tabel om MAC-adressen op te halen.
    4) Bepaal hostname + vendor.
  
  Toont ALLE devices die verbinding maken met het subnet, ook als ze zelf
  niet in dat subnet zitten (bijv. routers, gateways, andere subnetten).
  """
  net = ip_network(cidr, strict=False)
  hosts = [str(ip) for ip in net.hosts()]
  
  # Performance-tweak: check eerst ARP-cache (bevat alle IP's die verbinding maken)
  arp_cache = _get_arp_cache()
  
  # Start met ALLE IP's uit ARP-cache (ook die buiten het subnet)
  from ipaddress import ip_address
  alive = list(arp_cache.keys())
  
  # Ping alleen hosts binnen het subnet die nog niet in ARP-cache staan
  to_ping = [ip for ip in hosts if ip not in alive]
  
  # Limiteer aantal IPs om te pingen voor grote subnetten (max 254 IPs)
  # Voor /24 subnetten is dit prima, voor grotere subnetten kunnen we dit aanpassen
  if len(to_ping) > 254:
      ndt_log(f"Waarschuwing: Groot subnet gedetecteerd ({len(to_ping)} IPs). Scan kan lang duren.")
      # Voor grote subnetten, scan alleen eerste 254 IPs of gebruik een slimmere strategie
      to_ping = to_ping[:254]
  
  if to_ping:
      ndt_log(f"Ping scan gestart voor {len(to_ping)} IPs...")
      with ThreadPoolExecutor(max_workers=128) as executor:  # Meer workers voor snellere scan
          future_to_ip = {executor.submit(_ping, ip, timeout=0.3): ip for ip in to_ping}  # Kortere timeout
          completed = 0
          for fut in as_completed(future_to_ip):
              ip = future_to_ip[fut]
              completed += 1
              try:
                  if fut.result():
                      alive.append(ip)
                      ndt_log(f"Actief apparaat gevonden: {ip} ({completed}/{len(to_ping)})")
              except Exception:
                  continue
      ndt_log(f"Ping scan voltooid. {len(alive)} actieve apparaten gevonden.")

  devices: List[Dict] = []
  for ip in sorted(alive, key=lambda s: list(map(int, s.split(".")))):
      # Gebruik cached MAC als beschikbaar, anders haal opnieuw op
      mac = arp_cache.get(ip) or _get_mac(ip)
      vendor = lookup_vendor(mac) if mac else None
      hostname = resolve_hostname(ip)
      
      # Bepaal of IP binnen het gevraagde subnet valt
      in_subnet = False
      try:
          in_subnet = ip_address(ip) in net
      except ValueError:
          pass

      devices.append(
          {
              "ip": ip,
              "mac": mac,
              "hostname": hostname,
              "vendor": vendor,
              "in_subnet": in_subnet,  # Extra veld om te zien of het binnen subnet valt
          }
      )

  return devices

