from flask import Flask, render_template, redirect, url_for, request, jsonify, Response, session
import csv
import json
import logging
import os
import re
import subprocess
import threading
import time
from ipaddress import ip_network, IPv4Network
from datetime import datetime

# Setup logging naar bestand in plaats van stdout
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"ndt_{datetime.now().strftime('%Y%m%d')}.log")

# Configureer logger voor NDT
ndt_logger = logging.getLogger('NDT')
ndt_logger.setLevel(logging.INFO)
ndt_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
ndt_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
ndt_logger.addHandler(ndt_handler)
ndt_logger.propagate = False  # Voorkom dat het naar root logger gaat

def ndt_log(message):
    """Log naar bestand in plaats van stdout"""
    ndt_logger.info(message)

from scanner.network_scan import scan_network
from scanner.storage import (
    save_scan_with_history,
    get_latest_scan,
    mark_as_known,
    mark_as_unknown,
    get_note,
    set_note,
    get_scan_history,
)
from scanner.osint_lookup import enrich_device_with_osint
from scanner.port_scan import scan_common_ports, get_service_name
from translations import TRANSLATIONS

app = Flask(__name__)

# Taal en theme (session-based)
# Gebruik een vaste secret key voor sessies (in productie zou dit uit een config file komen)
app.secret_key = os.environ.get('SECRET_KEY', 'ndt-secret-key-change-in-production-' + os.urandom(16).hex())

# Global scan status tracking
scan_status = {
    'in_progress': False,
    'progress': 0,
    'message': ''
}
scan_lock = threading.Lock()


def get_translations(lang: str = "nl") -> dict:
    """Haal vertalingen op voor gegeven taal."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["nl"])


def detect_local_subnet() -> str:
    """
    Probeer het huidige subnet automatisch te detecteren (Linux-focused):
    - Negeert localhost/loopback interfaces (lo, lo0, etc.)
    - Negeert loopback IP-adressen (127.x.x.x)
    - Gebruikt alleen actieve netwerkinterfaces met echte IP-adressen
    - Geeft een lege string terug als detectie mislukt.
    """
    import platform
    system = platform.system()
    
    # Interfaces die we moeten negeren (localhost/loopback)
    ignored_interfaces = {'lo', 'lo0', 'lo1', 'lo2', 'lo3'}
    
    # Linux: gebruik 'ip' command (moderne methode)
    if system == "Linux":
        try:
            # Haal alle interfaces op met 'ip addr'
            ip_output = subprocess.check_output(
                ["ip", "-4", "addr", "show"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            
            current_interface = None
            for line in ip_output.split('\n'):
                # Interface regel: "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>"
                if_match = re.match(r'^\d+:\s+(\w+):', line)
                if if_match:
                    current_interface = if_match.group(1)
                    continue
                
                # IP regel: "    inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0"
                if current_interface and 'inet ' in line:
                    # Skip loopback interfaces
                    if current_interface in ignored_interfaces:
                        continue
                    
                    inet_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
                    if inet_match:
                        ip = inet_match.group(1)
                        cidr = inet_match.group(2)
                        
                        # Skip loopback IP-adressen (127.x.x.x)
                        if ip.startswith('127.'):
                            continue
                        
                        # Skip link-local adressen (169.254.x.x)
                        if ip.startswith('169.254.'):
                            continue
                        
                        # Controleer of interface UP is (heeft "state UP" of "UP" in flags)
                        # We hebben al de interface, check of deze actief is
                        try:
                            net: IPv4Network = ip_network(f"{ip}/{cidr}", strict=False)
                            return str(net)
                        except ValueError:
                            continue
        except Exception as e:
            ndt_log(f"Fout bij ip command: {e}")
            pass
        
        # Fallback: gebruik 'ifconfig' op Linux
        try:
            ifconfig_output = subprocess.check_output(
                ["ifconfig"], 
                text=True, 
                stderr=subprocess.DEVNULL
            )
            
            current_interface = None
            for line in ifconfig_output.split('\n'):
                # Interface regel: "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>"
                if_match = re.match(r'^(\w+):', line)
                if if_match:
                    current_interface = if_match.group(1)
                    # Skip loopback interfaces
                    if current_interface in ignored_interfaces:
                        current_interface = None
                    continue
                
                # IP regel: "        inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255"
                if current_interface and 'inet ' in line and 'inet6' not in line:
                    inet_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+).*netmask (\d+\.\d+\.\d+\.\d+)', line)
                    if inet_match:
                        ip = inet_match.group(1)
                        netmask = inet_match.group(2)
                        
                        # Skip loopback IP-adressen (127.x.x.x)
                        if ip.startswith('127.'):
                            continue
                        
                        # Skip link-local adressen (169.254.x.x)
                        if ip.startswith('169.254.'):
                            continue
                        
                        # Converteer netmask naar CIDR
                        netmask_parts = netmask.split('.')
                        netmask_int = (int(netmask_parts[0]) << 24) + (int(netmask_parts[1]) << 16) + (int(netmask_parts[2]) << 8) + int(netmask_parts[3])
                        cidr = bin(netmask_int).count('1')
                        try:
                            net: IPv4Network = ip_network(f"{ip}/{cidr}", strict=False)
                            return str(net)
                        except ValueError:
                            continue
        except Exception as e:
            ndt_log(f"Fout bij ifconfig: {e}")
            pass
    
    # macOS: gebruik ipconfig commando's (voor toekomstige ondersteuning)
    elif system == "Darwin":
        # Lijst van interfaces om te proberen (meest voorkomende eerst)
        interfaces = ["en0", "en1", "eth0", "eth1", "wlan0", "wlan1"]
        
        for iface in interfaces:
            if iface in ignored_interfaces:
                continue
                
            try:
                # Probeer IP-adres op te halen
                ip_result = subprocess.check_output(
                    ["ipconfig", "getifaddr", iface], 
                    text=True, 
                    stderr=subprocess.DEVNULL
                ).strip()
                
                if not ip_result or ip_result.startswith('127.'):
                    continue
                
                # Probeer subnetmasker op te halen
                mask_result = subprocess.check_output(
                    ["ipconfig", "getoption", iface, "subnet_mask"],
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
                
                if not mask_result:
                    continue
                
                # Controleer of het een geldig IPv4 adres is (geen IPv6)
                if ":" in ip_result:  # IPv6 adres, skip
                    continue
                
                # Maak subnet object
                net: IPv4Network = ip_network(f"{ip_result}/{mask_result}", strict=False)
                return str(net)
                
            except (subprocess.CalledProcessError, ValueError, Exception):
                # Probeer volgende interface
                continue
    
    # Als alles faalt, geef lege string terug
    ndt_log("Waarschuwing: Kon geen actief subnet detecteren. Controleer je netwerkverbinding.")
    return ""


@app.route("/")
def index():
    timestamp, devices, _ = get_latest_scan()
    lang = session.get("lang", "nl")
    theme = session.get("theme", "dark")
    t = get_translations(lang)
    
    # Laad notities en voeg toe aan devices
    for d in devices:
        mac = d.get("mac", "")
        if mac:
            d["note"] = get_note(mac) or ""
    
    return render_template(
        "dashboard.html",
        timestamp=timestamp,
        devices=devices,
        current_subnet=detect_local_subnet(),
        lang=lang,
        theme=theme,
        t=t,
        history=get_scan_history()[-10:],  # Laatste 10 scans
    )


def run_scan_async(cidr, enable_osint, enable_portscan):
    """Run scan in background thread"""
    global scan_status
    try:
        with scan_lock:
            scan_status['in_progress'] = True
            scan_status['message'] = 'Netwerk scannen...'
        
        ndt_log(f"Scan gestart voor subnet: {cidr}")
        devices = scan_network(cidr)
        ndt_log(f"Scan voltooid. {len(devices)} apparaten gevonden.")
        
        # Port scanning (optioneel)
        if enable_portscan:
            with scan_lock:
                scan_status['message'] = 'Ports scannen...'
            ndt_log("Port scanning gestart...")
            for i, device in enumerate(devices):
                ip = device.get("ip")
                if ip:
                    try:
                        open_ports = scan_common_ports(ip, timeout=0.5)
                        device["open_ports"] = open_ports
                        device["services"] = [get_service_name(p) for p in open_ports]
                    except Exception as e:
                        ndt_log(f"Port scan error voor {ip}: {e}")
            ndt_log("Port scanning voltooid.")
        
        # OSINT enrichment (optioneel, kan lang duren)
        if enable_osint:
            with scan_lock:
                scan_status['message'] = 'OSINT data ophalen...'
            ndt_log("OSINT enrichment gestart...")
            for device in devices:
                try:
                    enrich_device_with_osint(device)
                    # Rate limiting: kleine delay tussen requests
                    time.sleep(0.2)
                except Exception as e:
                    ndt_log(f"OSINT error voor {device.get('ip')}: {e}")
            ndt_log("OSINT enrichment voltooid.")
    except Exception as e:
        import traceback
        ndt_log(f"Fout bij scan: {e}")
        ndt_log(f"Traceback: {traceback.format_exc()}")
        devices = []

    try:
        new_devices, removed_devices = save_scan_with_history(devices, selected_network=None)
        if new_devices:
            ndt_log(f"{len(new_devices)} nieuwe apparaten gevonden")
        if removed_devices:
            ndt_log(f"{len(removed_devices)} apparaten verdwenen")
    except Exception as e:
        ndt_log(f"Fout bij opslaan scan: {e}")
    finally:
        # Always reset scan status, even if there was an error
        with scan_lock:
            scan_status['in_progress'] = False
            scan_status['message'] = ''
            ndt_log(f"Scan status gereset. in_progress={scan_status['in_progress']}")


@app.route("/scan", methods=["POST"])
def trigger_scan():
    cidr = detect_local_subnet()
    
    # Controleer of subnet detectie is gelukt
    if not cidr:
        return redirect(url_for("index"))
    
    # Check if scan is already in progress
    with scan_lock:
        if scan_status['in_progress']:
            return redirect(url_for("index"))
    
    enable_osint = request.form.get("enable_osint", "false") == "true"
    enable_portscan = request.form.get("enable_portscan", "false") == "true"

    # Start scan in background thread
    thread = threading.Thread(
        target=run_scan_async,
        args=(cidr, enable_osint, enable_portscan),
        daemon=True
    )
    thread.start()
    
    # Return immediately - scan runs in background
    return redirect(url_for("index"))


@app.route("/api/scan-status", methods=["GET"])
def scan_status_api():
    """API endpoint to check scan status"""
    with scan_lock:
        status = {
            'in_progress': scan_status['in_progress'],
            'message': scan_status['message']
        }
        # Log alleen naar bestand, niet naar stdout
        ndt_log(f"Status API called: {status}")
        return jsonify(status)


@app.route("/api/mark-known", methods=["POST"])
def api_mark_known():
    """Markeer een MAC-adres als bekend."""
    data = request.get_json()
    mac = data.get("mac", "").strip()
    if mac:
        mark_as_known(mac)
        # Update ook de huidige scan
        _, devices, _ = get_latest_scan()
        for d in devices:
            if d.get("mac", "").lower() == mac.lower():
                d["known"] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Geen MAC-adres opgegeven"}), 400


@app.route("/api/mark-unknown", methods=["POST"])
def api_mark_unknown():
    """Markeer een MAC-adres als onbekend."""
    data = request.get_json()
    mac = data.get("mac", "").strip()
    if mac:
        mark_as_unknown(mac)
        # Update ook de huidige scan
        _, devices, _ = get_latest_scan()
        for d in devices:
            if d.get("mac", "").lower() == mac.lower():
                d["known"] = False
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Geen MAC-adres opgegeven"}), 400


@app.route("/export/json")
def export_json():
    """Exporteer huidige scan als JSON."""
    _, devices, _ = get_latest_scan()
    return Response(
        json.dumps(devices, indent=2, default=str),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=devices.json"},
    )


@app.route("/export/csv")
def export_csv():
    """Exporteer huidige scan als CSV."""
    _, devices, _ = get_latest_scan()
    
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["IP", "MAC", "Hostname", "Vendor", "Known", "Note", "Open Ports"])
    for d in devices:
        ports = d.get("open_ports", [])
        writer.writerow([
            d.get("ip", ""),
            d.get("mac", ""),
            d.get("hostname", ""),
            d.get("vendor", ""),
            "Ja" if d.get("known") else "Nee",
            d.get("note", ""),
            ", ".join(map(str, ports)) if ports else "",
        ])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=devices.csv"},
    )


@app.route("/api/note", methods=["POST"])
def api_set_note():
    """Zet notitie voor een device."""
    data = request.get_json()
    mac = data.get("mac", "").strip()
    note = data.get("note", "").strip()
    if mac:
        set_note(mac, note)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Geen MAC-adres opgegeven"}), 400


@app.route("/api/portscan", methods=["POST"])
def api_portscan():
    """Voer port scan uit op een specifiek IP."""
    data = request.get_json()
    ip = data.get("ip", "").strip()
    if ip:
        try:
            open_ports = scan_common_ports(ip, timeout=1.0)
            services = [{"port": p, "service": get_service_name(p)} for p in open_ports]
            return jsonify({"success": True, "ports": open_ports, "services": services})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    return jsonify({"success": False, "error": "Geen IP-adres opgegeven"}), 400


@app.route("/api/set-lang", methods=["POST"])
def api_set_lang():
    """Zet taal voorkeur."""
    data = request.get_json()
    lang = data.get("lang", "nl")
    if lang in ["nl", "en"]:
        session["lang"] = lang
        return jsonify({"success": True})
    return jsonify({"success": False}), 400


@app.route("/api/set-theme", methods=["POST"])
def api_set_theme():
    """Zet theme voorkeur."""
    data = request.get_json()
    theme = data.get("theme", "dark")
    if theme in ["dark", "light"]:
        session["theme"] = theme
        return jsonify({"success": True})
    return jsonify({"success": False}), 400


if __name__ == "__main__":
    # host="0.0.0.0" zodat je eventueel vanaf een andere machine kunt verbinden
    # debug=False en use_reloader=False om dubbele processen en poort-verwarring te voorkomen
    import logging
    import warnings
    
    # Suppress Flask/Werkzeug output when run directly
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    warnings.filterwarnings("ignore")
    
    port = 5001
    # Don't print startup message when run from JacOps (it will be handled there)
    # Only print if run directly
    if os.environ.get('JACOPS_RUNNING') != '1':
        print(f"Starting NDT on http://localhost:{port}")
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)

