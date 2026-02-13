#!/usr/bin/env python3
"""
DoS Attack Detector Web GUI
Web-based graphical user interface for the DoS attack detector.
Works on all platforms including macOS where tkinter may have issues.
Uses simple HTTP polling instead of websockets for compatibility.
"""

from flask import Flask, render_template_string, jsonify, request
import threading
import queue
from datetime import datetime
from dos_detector import DoSDetector
import os
import sys
import webbrowser
import time

app = Flask(__name__)

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DoS Attack Detector</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .control-panel {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .control-row {
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        label {
            font-weight: 600;
            color: #495057;
            font-size: 0.9em;
        }
        
        select, input {
            padding: 10px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .status {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .status.stopped {
            background: #dc3545;
            color: white;
        }
        
        .status.monitoring {
            background: #28a745;
            color: white;
        }
        
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-start {
            background: #28a745;
            color: white;
        }
        
        .btn-start:hover {
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
        }
        
        .btn-stop {
            background: #dc3545;
            color: white;
        }
        
        .btn-stop:hover {
            background: #c82333;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
        }
        
        .config-panel {
            padding: 30px;
            background: white;
            border-bottom: 2px solid #e9ecef;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .config-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .stats-panel {
            padding: 30px;
            background: white;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .stat-title {
            font-weight: 600;
            color: #495057;
            font-size: 1.1em;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #212529;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s, background 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        .progress-fill.warning {
            background: linear-gradient(90deg, #ffc107, #fd7e14);
        }
        
        .progress-fill.danger {
            background: linear-gradient(90deg, #dc3545, #c82333);
        }
        
        .alerts-panel {
            padding: 30px;
            background: #f8f9fa;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .alert-item {
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 5px solid #dc3545;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .alert-type {
            font-weight: 700;
            color: #dc3545;
            font-size: 1.2em;
        }
        
        .alert-time {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .alert-details {
            color: #495057;
            line-height: 1.6;
        }
        
        .alert-details strong {
            color: #212529;
        }
        
        .empty-alerts {
            text-align: center;
            color: #6c757d;
            padding: 40px;
            font-style: italic;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ DoS Attack Detector</h1>
            <p>Real-time Network Traffic Monitoring</p>
        </div>
        
        <div class="control-panel">
            <div class="control-row">
                <div class="control-group">
                    <label for="interface">Network Interface:</label>
                    <select id="interface">
                        <option value="All">All Interfaces</option>
                    </select>
                </div>
                <div class="control-group">
                    <span class="status stopped" id="status">Status: Stopped</span>
                </div>
                <button class="btn-start" id="startStopBtn" onclick="toggleMonitoring()">Start Monitoring</button>
            </div>
        </div>
        
        <div class="config-panel">
            <h2 style="margin-bottom: 20px; color: #495057;">Configuration</h2>
            <div class="config-grid">
                <div class="config-item">
                    <label>SYN Flood Threshold:</label>
                    <input type="number" id="synThreshold" value="100" min="1">
                </div>
                <div class="config-item">
                    <label>UDP Flood Threshold:</label>
                    <input type="number" id="udpThreshold" value="200" min="1">
                </div>
                <div class="config-item">
                    <label>ICMP Flood Threshold:</label>
                    <input type="number" id="icmpThreshold" value="150" min="1">
                </div>
                <div class="config-item">
                    <label>HTTP Flood Threshold:</label>
                    <input type="number" id="httpThreshold" value="300" min="1">
                </div>
                <div class="config-item">
                    <label>Time Window (seconds):</label>
                    <input type="number" id="timeWindow" value="10" min="1">
                </div>
            </div>
            <button onclick="applySettings()" style="background: #667eea; color: white; margin-top: 10px;">Apply Settings</button>
        </div>
        
        <div class="stats-panel">
            <h2 style="margin-bottom: 20px; color: #495057;">Real-time Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">SYN Flood</span>
                        <span class="stat-value" id="synValue">0/100</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="synProgress" style="width: 0%">0%</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">UDP Flood</span>
                        <span class="stat-value" id="udpValue">0/200</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="udpProgress" style="width: 0%">0%</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">ICMP Flood</span>
                        <span class="stat-value" id="icmpValue">0/150</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="icmpProgress" style="width: 0%">0%</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">HTTP Flood</span>
                        <span class="stat-value" id="httpValue">0/300</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="httpProgress" style="width: 0%">0%</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alerts-panel">
            <h2 style="margin-bottom: 20px; color: #495057;">Attack Alerts</h2>
            <div id="alertsContainer">
                <div class="empty-alerts">No alerts yet. Start monitoring to detect attacks.</div>
            </div>
        </div>
    </div>
    
    <script>
        let isMonitoring = false;
        
        function updateStatistics(stats) {
            const types = ['syn', 'udp', 'icmp', 'http'];
            types.forEach(type => {
                const data = stats[type];
                const current = data.current;
                const threshold = data.threshold;
                const percentage = Math.min(100, (current / threshold) * 100);
                
                // Update value
                document.getElementById(type + 'Value').textContent = `${current}/${threshold}`;
                
                // Update progress bar
                const progressBar = document.getElementById(type + 'Progress');
                progressBar.style.width = percentage + '%';
                progressBar.textContent = Math.round(percentage) + '%';
                
                // Update color
                progressBar.className = 'progress-fill';
                if (percentage >= 100) {
                    progressBar.classList.add('danger');
                } else if (percentage >= 75) {
                    progressBar.classList.add('warning');
                }
            });
        }
        
        function displayAlert(alert) {
            const container = document.getElementById('alertsContainer');
            if (container.querySelector('.empty-alerts')) {
                container.innerHTML = '';
            }
            
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item pulse';
            alertDiv.innerHTML = `
                <div class="alert-header">
                    <span class="alert-type">${alert.attack_type.toUpperCase()} ATTACK</span>
                    <span class="alert-time">${alert.timestamp}</span>
                </div>
                <div class="alert-details">
                    <strong>Source IP:</strong> ${alert.src_ip}<br>
                    <strong>Packet Count:</strong> ${alert.count} (Threshold: ${alert.threshold})<br>
                    <strong>Attack Rate:</strong> ${alert.rate.toFixed(2)} packets/second
                </div>
            `;
            
            container.insertBefore(alertDiv, container.firstChild);
            
            // Remove pulse after animation
            setTimeout(() => {
                alertDiv.classList.remove('pulse');
            }, 2000);
        }
        
        function updateStatus(status) {
            const statusEl = document.getElementById('status');
            const btn = document.getElementById('startStopBtn');
            
            if (status === 'monitoring') {
                statusEl.textContent = 'Status: Monitoring';
                statusEl.className = 'status monitoring';
                btn.textContent = 'Stop Monitoring';
                btn.className = 'btn-stop';
                isMonitoring = true;
            } else {
                statusEl.textContent = 'Status: Stopped';
                statusEl.className = 'status stopped';
                btn.textContent = 'Start Monitoring';
                btn.className = 'btn-start';
                isMonitoring = false;
            }
        }
        
        function toggleMonitoring() {
            fetch('/api/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    interface: document.getElementById('interface').value,
                    syn_threshold: parseInt(document.getElementById('synThreshold').value),
                    udp_threshold: parseInt(document.getElementById('udpThreshold').value),
                    icmp_threshold: parseInt(document.getElementById('icmpThreshold').value),
                    http_threshold: parseInt(document.getElementById('httpThreshold').value),
                    time_window: parseInt(document.getElementById('timeWindow').value)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    updateStatus(data.status);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }
        
        function applySettings() {
            alert('Settings will be applied when you start monitoring.');
        }
        
        // Poll for updates
        function pollUpdates() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.stats) {
                        updateStatistics(data.stats);
                    }
                    if (data.status) {
                        updateStatus(data.status);
                    }
                })
                .catch(error => console.error('Error:', error));
            
            fetch('/api/alerts')
                .then(response => response.json())
                .then(data => {
                    if (data.alerts && data.alerts.length > 0) {
                        data.alerts.forEach(alert => {
                            displayAlert(alert);
                        });
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        // Poll every 500ms
        setInterval(pollUpdates, 500);
        
        // Initial poll
        pollUpdates();
    </script>
</body>
</html>
"""


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


@app.route('/')
def index():
    """Serve the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    """Handle start/stop monitoring request."""
    global detector, detector_thread, is_monitoring, current_stats
    
    data = request.json
    
    if not is_monitoring:
        # Start monitoring
        try:
            interface = data.get('interface')
            if interface == 'All':
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


def main():
    """Main entry point."""
    port = 5002  # Changed from 5000 to avoid conflict with PES
    
    print("="*70)
    print("DoS Attack Detector - Web GUI")
    print("="*70)
    print(f"Starting web server on http://localhost:{port}")
    print("The browser should open automatically.")
    print("If not, navigate to http://localhost:{port} in your browser.")
    print("="*70)
    print("\nPress Ctrl+C to stop the server.\n")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask server
    app.run(host='127.0.0.1', port=port, debug=False, threaded=True)


if __name__ == '__main__':
    main()
