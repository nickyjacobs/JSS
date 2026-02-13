"""
Web Vulnerability Scanner - Flask Web Application
"""
import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from scanner import VulnerabilityScanner
from config import SERVER_PORT, SERVER_HOST

app = Flask(__name__, template_folder='templates')
CORS(app)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def scan_website():
    """Run vulnerability scan"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        url = data.get('url', '').strip()
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Get scan types
        scan_types = data.get('scan_types', ['all'])
        if not isinstance(scan_types, list):
            scan_types = ['all']
        
        # Run scan
        scanner = VulnerabilityScanner(url)
        vulnerabilities = scanner.scan(scan_types)
        
        return jsonify({
            'success': True,
            'data': {
                'url': url,
                'vulnerabilities': vulnerabilities,
                'count': len(vulnerabilities)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Suppress output if running from jacops.py
    if os.getenv('JACOPS_RUNNING') != '1':
        print(f"Starting Web Vulnerability Scanner on http://{SERVER_HOST}:{SERVER_PORT}")
    
    app.run(host='127.0.0.1', port=SERVER_PORT, debug=False)
