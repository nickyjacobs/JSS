"""
Intrusion Detection Monitor - Flask Web Application
"""
import os
import threading
import queue
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from detector import IntrusionDetector
from config import SERVER_PORT, SERVER_HOST, AUTH_LOG, FAILED_LOGIN_THRESHOLD, TIME_WINDOW_SECONDS

app = Flask(__name__, template_folder='templates')
CORS(app)

# Suppress Flask logging when running from jacops.py
if os.getenv('JACOPS_RUNNING') == '1':
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    import sys
    from io import StringIO
    sys.stdout = StringIO()
    sys.stderr = StringIO()

# Global detector instance
detector = None
detector_thread = None
is_monitoring = False

# Queue for alerts
alert_queue = queue.Queue()

# Attack history
attack_history = []

# Current configuration
current_config = {
    'log_path': AUTH_LOG,
    'failed_threshold': FAILED_LOGIN_THRESHOLD,
    'time_window': TIME_WINDOW_SECONDS
}


def alert_callback(event_type, ip, count, threshold, rate, timestamp):
    """Callback for alerts."""
    alert_data = {
        'event_type': event_type,
        'ip': ip,
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
    global detector, detector_thread, is_monitoring, current_config
    
    data = request.get_json() or {}
    
    if not is_monitoring:
        # Start monitoring
        try:
            log_path = data.get('log_path', current_config['log_path'])
            failed_threshold = int(data.get('failed_threshold', current_config['failed_threshold']))
            time_window = int(data.get('time_window', current_config['time_window']))
            
            current_config['log_path'] = log_path
            current_config['failed_threshold'] = failed_threshold
            current_config['time_window'] = time_window
            
            detector = IntrusionDetector(
                log_path=log_path,
                failed_threshold=failed_threshold,
                time_window=time_window,
                alert_callback=alert_callback
            )
            
            detector_thread = threading.Thread(target=detector.start, daemon=True)
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


@app.route('/api/status')
def api_status():
    """Get current status and configuration."""
    return jsonify({
        'status': 'monitoring' if is_monitoring else 'stopped',
        'config': current_config
    })


@app.route('/api/update-config', methods=['POST'])
def api_update_config():
    """Update configuration without starting monitoring."""
    global current_config
    from pathlib import Path
    
    if is_monitoring:
        return jsonify({'error': 'Cannot update config while monitoring is active. Stop monitoring first.'}), 400
    
    data = request.get_json() or {}
    
    try:
        # Validate log path if provided
        if 'log_path' in data:
            log_path = data['log_path'].strip()
            if not log_path:
                return jsonify({'error': 'Log file path cannot be empty.'}), 400
            
            log_file = Path(log_path)
            if not log_file.exists():
                return jsonify({'error': f'Log file does not exist: {log_path}'}), 400
            
            # Check if file is readable
            try:
                with open(log_file, 'r'):
                    pass
            except PermissionError:
                return jsonify({'error': f'Permission denied: Cannot read {log_path}. Run with sudo or check file permissions.'}), 400
            except Exception as e:
                return jsonify({'error': f'Cannot access log file: {str(e)}'}), 400
            
            current_config['log_path'] = log_path
        
        # Validate threshold
        if 'failed_threshold' in data:
            threshold = int(data['failed_threshold'])
            if threshold < 1:
                return jsonify({'error': 'Failed login threshold must be at least 1.'}), 400
            current_config['failed_threshold'] = threshold
        
        # Validate time window
        if 'time_window' in data:
            time_window = int(data['time_window'])
            if time_window < 1:
                return jsonify({'error': 'Time window must be at least 1 second.'}), 400
            current_config['time_window'] = time_window
        
        return jsonify({'status': 'updated', 'config': current_config, 'message': 'Configuration updated successfully!'})
    except ValueError as e:
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@app.route('/api/history')
def api_history():
    """Get attack history."""
    return jsonify({'history': attack_history[-50:]})


if __name__ == '__main__':
    if os.getenv('JACOPS_RUNNING') != '1':
        print(f"Starting Intrusion Detection Monitor on http://{SERVER_HOST}:{SERVER_PORT}")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)
