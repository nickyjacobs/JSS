"""
DoS Attack Detector - Flask Web Application
"""
import os
import threading
import queue
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dos_detector import DoSDetector
from config import SERVER_PORT, SERVER_HOST

app = Flask(__name__, template_folder='templates')
CORS(app)

# Suppress Flask logging when running from jacops.py
if os.getenv('JACOPS_RUNNING') == '1':
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Suppress Flask startup messages
    import sys
    from io import StringIO
    sys.stdout = StringIO()
    sys.stderr = StringIO()

# Global detector instance
detector = None
detector_thread = None
is_monitoring = False

# Queues for thread-safe communication
stats_queue = queue.Queue()
alert_queue = queue.Queue()

# Current statistics and alerts
current_stats = {
    'syn': {'current': 0, 'threshold': 100},
    'udp': {'current': 0, 'threshold': 200},
    'icmp': {'current': 0, 'threshold': 150},
    'http': {'current': 0, 'threshold': 300}
}

# Attack history
attack_history = []


def stats_callback(stats_dict):
    """Callback for statistics updates."""
    global current_stats
    current_stats = stats_dict
    stats_queue.put(stats_dict)


def alert_callback(attack_type, src_ip, count, threshold, rate, timestamp):
    """Callback for alerts."""
    alert_data = {
        'attack_type': attack_type,
        'src_ip': src_ip,
        'count': count,
        'threshold': threshold,
        'rate': rate,
        'timestamp': timestamp
    }
    alert_queue.put(alert_data)
    attack_history.append(alert_data)
    # Keep only last 100 alerts
    if len(attack_history) > 100:
        attack_history.pop(0)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    """Handle start/stop monitoring request."""
    global detector, detector_thread, is_monitoring, current_stats
    
    data = request.get_json()
    
    if not is_monitoring:
        # Start monitoring
        try:
            interface = data.get('interface')
            if interface == 'All' or not interface:
                interface = None
            
            detector = DoSDetector(
                syn_threshold=data.get('syn_threshold', 100),
                udp_threshold=data.get('udp_threshold', 200),
                icmp_threshold=data.get('icmp_threshold', 150),
                http_threshold=data.get('http_threshold', 300),
                time_window=data.get('time_window', 10),
                interface=interface,
                stats_callback=stats_callback,
                alert_callback=alert_callback
            )
            
            # Update thresholds in current_stats
            current_stats['syn']['threshold'] = data.get('syn_threshold', 100)
            current_stats['udp']['threshold'] = data.get('udp_threshold', 200)
            current_stats['icmp']['threshold'] = data.get('icmp_threshold', 150)
            current_stats['http']['threshold'] = data.get('http_threshold', 300)
            
            detector_thread = threading.Thread(target=detector.start_monitoring, args=(True,), daemon=True)
            detector_thread.start()
            
            is_monitoring = True
            return jsonify({'status': 'monitoring'})
            
        except Exception as e:
            return jsonify({'error': str(e), 'status': 'stopped'}), 500
    else:
        # Stop monitoring
        if detector:
            detector.stop()
            detector = None
        
        is_monitoring = False
        return jsonify({'status': 'stopped'})


@app.route('/api/stats')
def api_stats():
    """Get current statistics."""
    return jsonify({
        'stats': current_stats,
        'status': 'monitoring' if is_monitoring else 'stopped'
    })


@app.route('/api/alerts')
def api_alerts():
    """Get new alerts."""
    alerts = []
    try:
        while True:
            alert_data = alert_queue.get_nowait()
            alerts.append(alert_data)
    except queue.Empty:
        pass
    
    return jsonify({'alerts': alerts})


@app.route('/api/run-test', methods=['POST'])
def api_run_test():
    """Run DoS test: inject packets into a temporary detector and show alerts."""
    try:
        from scapy.all import IP, TCP, UDP, ICMP
    except ImportError:
        return jsonify({'error': 'Scapy niet geïnstalleerd', 'ok': False}), 500
    data = request.get_json() or {}
    test_type = data.get('test_type', 'all')
    if test_type not in ('syn', 'udp', 'icmp', 'all'):
        test_type = 'all'
    # Leeg de alert-queue zodat alleen alerts van deze testrun getoond worden
    try:
        while True:
            alert_queue.get_nowait()
    except queue.Empty:
        pass
    counts = {'syn': 60, 'udp': 90, 'icmp': 70}
    src = '127.0.0.1'
    test_detector = DoSDetector(
        syn_threshold=50,
        udp_threshold=80,
        icmp_threshold=60,
        http_threshold=300,
        time_window=10,
        interface=None,
        stats_callback=lambda s: None,
        alert_callback=alert_callback,
    )
    test_detector.running = True
    if test_type == 'syn':
        for i in range(counts['syn']):
            pkt = IP(src=src, dst=src) / TCP(flags='S', sport=40000 + i, dport=80)
            test_detector.process_packet(pkt)
    elif test_type == 'udp':
        for i in range(counts['udp']):
            pkt = IP(src=src, dst=src) / UDP(sport=50000 + i, dport=53)
            test_detector.process_packet(pkt)
    elif test_type == 'icmp':
        for i in range(counts['icmp']):
            pkt = IP(src=src, dst=src) / ICMP(id=i % 65535, seq=i)
            test_detector.process_packet(pkt)
    elif test_type == 'all':
        for i in range(counts['syn']):
            pkt = IP(src=src, dst=src) / TCP(flags='S', sport=40000 + i, dport=80)
            test_detector.process_packet(pkt)
        for i in range(counts['udp']):
            pkt = IP(src=src, dst=src) / UDP(sport=50000 + i, dport=53)
            test_detector.process_packet(pkt)
        for i in range(counts['icmp']):
            pkt = IP(src=src, dst=src) / ICMP(id=i % 65535, seq=i)
            test_detector.process_packet(pkt)
    return jsonify({'ok': True, 'test_type': test_type, 'message': 'Test voltooid. Bekijk de alerts hierboven.'})


@app.route('/api/interfaces')
def api_interfaces():
    """Get available network interfaces."""
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        return jsonify({'interfaces': interfaces})
    except ImportError:
        # Fallback
        try:
            import subprocess
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if ': ' in line and 'lo:' not in line:
                    parts = line.split(': ')
                    if len(parts) > 1:
                        interfaces.append(parts[1].split('@')[0].strip())
            return jsonify({'interfaces': interfaces if interfaces else ['eth0', 'wlan0']})
        except:
            return jsonify({'interfaces': ['eth0', 'wlan0']})


if __name__ == '__main__':
    # Suppress output if running from jacops.py
    if os.getenv('JACOPS_RUNNING') != '1':
        print(f"Starting DoS Attack Detector on http://{SERVER_HOST}:{SERVER_PORT}")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)
