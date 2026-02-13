#!/usr/bin/env python3
"""
Web-based GUI voor Caesar Cipher Decoder met Frequency Analysis
Werkt in de browser - geen tkinter nodig!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from caesar_decoder import CaesarDecoder


class CaesarWebHandler(BaseHTTPRequestHandler):
    """HTTP handler voor de web GUI"""
    
    decoder = CaesarDecoder()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(self.get_css().encode())
        elif self.path == '/script.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(self.get_javascript().encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests voor API calls"""
        if self.path == '/api/decrypt':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            show_all = data.get('show_all', False)
            
            result = self.decoder.crack(text, show_all=show_all)
            
            # Convert to JSON-serializable format
            response = {
                'success': True,
                'shift': result['shift'],
                'decrypted': result['decrypted'],
                'confidence_score': result['confidence_score'],
                'encrypted': result['encrypted'],
                'all_attempts': [
                    {
                        'shift': a['shift'],
                        'text': a['text'],
                        'score': a['score']
                    }
                    for a in result.get('all_attempts', [])[:10]
                ]
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/encrypt':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            shift = int(data.get('shift', 3))
            
            encrypted = self.decoder.encrypt(text, shift)
            
            response = {
                'success': True,
                'encrypted': encrypted,
                'shift': shift
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging when running from jacops.py"""
        import os
        if os.getenv('JACOPS_RUNNING') != '1':
            super().log_message(format, *args)
        """Suppress default logging"""
        pass
    
    def get_html(self):
        """Return HTML content"""
        return """<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Caesar Cipher Decoder - Frequency Analysis</title>
    <link rel="stylesheet" href="/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="background-animation"></div>
    <div class="container">
        <header class="header">
            <div class="header-logo">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
            </div>
            <h1>Caesar Cipher Decoder</h1>
            <p class="subtitle">Automatische decryptie met Frequency Analysis</p>
        </header>
        
        <div class="card mode-card">
            <div class="mode-selector">
                <label class="radio-label">
                    <input type="radio" name="mode" value="decrypt" checked>
                    <div class="radio-custom"></div>
                    <span class="mode-text">
                        <svg class="mode-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path>
                            <line x1="7" y1="12" x2="21" y2="12"></line>
                            <polyline points="17 8 21 12 17 16"></polyline>
                        </svg>
                        <span>
                            <strong>Decrypt</strong>
                            <small>Automatisch kraken</small>
                        </span>
                    </span>
                </label>
                <label class="radio-label">
                    <input type="radio" name="mode" value="encrypt">
                    <div class="radio-custom"></div>
                    <span class="mode-text">
                        <svg class="mode-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                        </svg>
                        <span>
                            <strong>Encrypt</strong>
                            <small>Met shift waarde</small>
                        </span>
                    </span>
                </label>
            </div>
        </div>
        
        <div id="shift-container" class="card shift-card hidden">
            <div class="shift-input-wrapper">
                <label class="shift-label">
                    <svg class="shift-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="2" x2="12" y2="22"></line>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                    </svg>
                    Shift waarde
                </label>
                <div class="shift-controls">
                    <button class="shift-btn" id="shift-decrease">−</button>
                    <input type="number" id="shift-input" min="0" max="25" value="3" readonly>
                    <button class="shift-btn" id="shift-increase">+</button>
                </div>
            </div>
        </div>
        
        <div class="card input-card">
            <label for="input-text" class="input-label">
                <svg class="label-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                Tekst invoer
            </label>
            <textarea id="input-text" placeholder="Plak of typ hier je encrypted tekst..."></textarea>
            <div class="char-count">
                <span id="char-count">0</span> karakters
            </div>
        </div>
        
        <div class="button-group">
            <button id="process-btn" class="btn btn-primary">
                <svg class="btn-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="5 12 3 12 12 3 21 12 19 12"></polyline>
                    <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"></path>
                </svg>
                <span class="btn-text">Verwerk</span>
            </button>
            <button id="clear-btn" class="btn btn-secondary">
                <svg class="btn-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                <span class="btn-text">Wissen</span>
            </button>
        </div>
        
        <div class="card output-card">
            <div id="info-label" class="info-label">
                <svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                Voer tekst in en klik op 'Verwerk'
            </div>
            <div id="output-text" class="output-text"></div>
        </div>
        
        <div id="results-container" class="card results-card hidden">
            <h3 class="results-title">
                <svg class="title-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
                Top 5 Meest Waarschijnlijke Decrypties
            </h3>
            <div id="attempts-list" class="attempts-list"></div>
        </div>
    </div>
    
    <script src="/script.js"></script>
</body>
</html>"""
    
    def get_css(self):
        """Return CSS content"""
        return """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary: #3b82f6;
    --primary-dark: #2563eb;
    --primary-light: #60a5fa;
    --secondary: #1e40af;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --dark: #0f172a;
    --dark-light: #1e293b;
    --dark-lighter: #334155;
    --gray: #64748b;
    --gray-light: #94a3b8;
    --gray-lighter: #cbd5e1;
    --bg-dark: #0a0e27;
    --bg-card: #1a1f3a;
    --border: #2d3748;
    --border-light: #3d4758;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f172a 100%);
    background-attachment: fixed;
    min-height: 100vh;
    padding: 20px;
    position: relative;
    overflow-x: hidden;
    color: var(--text-primary);
}

.background-animation {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(30, 64, 175, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(37, 99, 235, 0.08) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.4),
        0 2px 8px rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.5),
        0 4px 12px rgba(0, 0, 0, 0.4);
    border-color: var(--border-light);
}

.header {
    text-align: center;
    margin-bottom: 30px;
    padding: 40px 20px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(30, 64, 175, 0.15) 100%);
    border-radius: 16px;
    border: 1px solid var(--border);
}

.header-logo {
    margin-bottom: 20px;
    display: inline-block;
    color: var(--primary);
    opacity: 0.9;
}

.header-logo svg {
    filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.3));
}

.header h1 {
    color: var(--text-primary);
    font-size: 2.6em;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: -0.02em;
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1.05em;
    font-weight: 400;
}

.mode-selector {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.radio-label {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 20px;
    border: 2px solid var(--border);
    border-radius: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: var(--dark-light);
    position: relative;
    overflow: hidden;
}

.radio-label::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(30, 64, 175, 0.2) 100%);
    opacity: 0;
    transition: opacity 0.3s;
}

.radio-label:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2);
    background: var(--dark-lighter);
}

.radio-label input[type="radio"] {
    position: absolute;
    opacity: 0;
    pointer-events: none;
}

.radio-custom {
    width: 24px;
    height: 24px;
    border: 2px solid var(--gray);
    border-radius: 50%;
    margin-right: 15px;
    position: relative;
    flex-shrink: 0;
    transition: all 0.3s;
    background: var(--dark);
}

.radio-label input[type="radio"]:checked ~ .radio-custom {
    border-color: var(--primary);
    background: var(--primary);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.radio-label input[type="radio"]:checked ~ .radio-custom::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 10px;
    height: 10px;
    background: white;
    border-radius: 50%;
}

.radio-label input[type="radio"]:checked ~ .mode-text {
    color: var(--primary-light);
}

.mode-text {
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 1;
    position: relative;
}

.mode-icon {
    color: var(--text-secondary);
    flex-shrink: 0;
}

.radio-label input[type="radio"]:checked ~ .mode-text .mode-icon {
    color: var(--primary-light);
}

.mode-text strong {
    display: block;
    font-size: 1.1em;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 2px;
}

.mode-text small {
    display: block;
    font-size: 0.85em;
    color: var(--text-secondary);
    font-weight: 400;
}

.radio-label input[type="radio"]:checked ~ .mode-text strong {
    color: var(--text-primary);
}

.shift-card {
    text-align: center;
}

.shift-input-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
}

.shift-label {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1.1em;
}

.shift-icon {
    color: var(--primary-light);
}

.shift-controls {
    display: flex;
    align-items: center;
    gap: 0;
    background: var(--dark);
    border-radius: 10px;
    overflow: hidden;
    border: 2px solid var(--border);
}

.shift-btn {
    width: 45px;
    height: 45px;
    border: none;
    background: var(--dark-light);
    color: var(--primary-light);
    font-size: 1.5em;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.shift-btn:hover {
    background: var(--primary);
    color: white;
}

.shift-btn:active {
    transform: scale(0.95);
}

#shift-input {
    width: 80px;
    height: 45px;
    border: none;
    text-align: center;
    font-size: 1.2em;
    font-weight: 700;
    color: var(--text-primary);
    background: var(--dark);
    -moz-appearance: textfield;
}

#shift-input::-webkit-outer-spin-button,
#shift-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

.input-label {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1.1em;
}

.label-icon {
    color: var(--primary-light);
}

#input-text {
    width: 100%;
    min-height: 180px;
    padding: 20px;
    border: 2px solid var(--border);
    border-radius: 12px;
    font-family: 'Courier New', 'Monaco', monospace;
    font-size: 15px;
    resize: vertical;
    background: var(--dark);
    color: var(--text-primary);
    transition: all 0.3s;
    line-height: 1.6;
}

#input-text:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
    transform: translateY(-1px);
    background: var(--dark-light);
}

#input-text::placeholder {
    color: var(--gray);
}

.char-count {
    margin-top: 8px;
    text-align: right;
    font-size: 0.85em;
    color: var(--text-secondary);
    font-weight: 500;
}

.button-group {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    justify-content: center;
    flex-wrap: wrap;
}

.btn {
    padding: 16px 35px;
    font-size: 1.1em;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    overflow: hidden;
    min-width: 150px;
    justify-content: center;
}

.btn::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.btn:active::before {
    width: 300px;
    height: 300px;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
}

.btn-primary:active {
    transform: translateY(-1px);
}

.btn-secondary {
    background: var(--dark-light);
    color: var(--text-secondary);
    border: 2px solid var(--border);
}

.btn-secondary:hover {
    background: var(--dark-lighter);
    border-color: var(--border-light);
    color: var(--text-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
}

.btn-icon {
    font-size: 1.2em;
}

.info-label {
    padding: 16px 20px;
    margin-bottom: 15px;
    border-radius: 12px;
    color: var(--text-secondary);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--dark);
    border: 2px solid var(--border);
    transition: all 0.3s;
}

.info-icon {
    color: var(--text-secondary);
    flex-shrink: 0;
}

.info-label.success {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border-color: rgba(16, 185, 129, 0.3);
}

.info-label.success .info-icon {
    color: #34d399;
}

.info-label.error {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border-color: rgba(239, 68, 68, 0.3);
}

.info-label.error .info-icon {
    color: #f87171;
}

.output-text {
    background: var(--dark);
    padding: 25px;
    border-radius: 12px;
    min-height: 120px;
    font-family: 'Courier New', 'Monaco', monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
    border: 2px solid var(--border);
    line-height: 1.8;
    color: var(--text-primary);
    font-size: 14px;
    transition: all 0.3s;
}

.output-text:empty::before {
    content: 'Resultaat verschijnt hier...';
    color: var(--gray);
    font-style: italic;
}

.results-title {
    color: var(--text-primary);
    margin-bottom: 20px;
    font-size: 1.4em;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
}

.title-icon {
    color: var(--primary-light);
}

.attempts-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.attempt-item {
    background: var(--dark-light);
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid var(--primary);
    transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.4s ease-out;
    animation-fill-mode: both;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.attempt-item:nth-child(1) { animation-delay: 0.1s; }
.attempt-item:nth-child(2) { animation-delay: 0.2s; }
.attempt-item:nth-child(3) { animation-delay: 0.3s; }
.attempt-item:nth-child(4) { animation-delay: 0.4s; }
.attempt-item:nth-child(5) { animation-delay: 0.5s; }

.attempt-item:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    border-left-color: var(--primary-light);
}

.attempt-item.best {
    border-left-color: var(--success);
    background: rgba(16, 185, 129, 0.1);
    border-width: 4px;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
}

.attempt-header {
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 10px;
    font-size: 1.05em;
    display: flex;
    align-items: center;
    gap: 8px;
}

.attempt-item.best .attempt-header::before {
    content: '✓';
    color: var(--success);
    font-weight: bold;
    font-size: 1.1em;
}

.attempt-text {
    font-family: 'Courier New', 'Monaco', monospace;
    color: var(--text-secondary);
    margin-top: 8px;
    line-height: 1.6;
    padding: 12px;
    background: var(--dark);
    border-radius: 8px;
    border: 1px solid var(--border);
}

.hidden {
    display: none !important;
}

@media (max-width: 768px) {
    .mode-selector {
        grid-template-columns: 1fr;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .button-group {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
    }
    
    .shift-input-wrapper {
        flex-direction: column;
        gap: 15px;
    }
}"""
    
    def get_javascript(self):
        """Return JavaScript content"""
        return """document.addEventListener('DOMContentLoaded', function() {
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    const shiftContainer = document.getElementById('shift-container');
    const shiftInput = document.getElementById('shift-input');
    const shiftDecrease = document.getElementById('shift-decrease');
    const shiftIncrease = document.getElementById('shift-increase');
    const processBtn = document.getElementById('process-btn');
    const clearBtn = document.getElementById('clear-btn');
    const inputText = document.getElementById('input-text');
    const outputText = document.getElementById('output-text');
    const infoLabel = document.getElementById('info-label');
    const charCount = document.getElementById('char-count');
    const resultsContainer = document.getElementById('results-container');
    const attemptsList = document.getElementById('attempts-list');
    
    // Character counter
    inputText.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
    
    // Shift controls
    shiftDecrease.addEventListener('click', function() {
        let value = parseInt(shiftInput.value);
        if (value > 0) {
            shiftInput.value = value - 1;
        }
    });
    
    shiftIncrease.addEventListener('click', function() {
        let value = parseInt(shiftInput.value);
        if (value < 25) {
            shiftInput.value = value + 1;
        }
    });
    
    // Helper function to create SVG icon
    function createSVGIcon(path, viewBox = '0 0 24 24') {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '18');
        svg.setAttribute('height', '18');
        svg.setAttribute('viewBox', viewBox);
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathEl.setAttribute('d', path);
        svg.appendChild(pathEl);
        return svg;
    }
    
    // Mode change handler
    modeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'encrypt') {
                shiftContainer.classList.remove('hidden');
                processBtn.querySelector('.btn-text').textContent = 'Encrypt';
            } else {
                shiftContainer.classList.add('hidden');
                processBtn.querySelector('.btn-text').textContent = 'Decrypt';
            }
        });
    });
    
    // Process button
    processBtn.addEventListener('click', async function() {
        const text = inputText.value.trim();
        if (!text) {
            infoLabel.innerHTML = '<svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>Voer eerst tekst in!';
            infoLabel.className = 'info-label error';
            return;
        }
        
        const mode = document.querySelector('input[name="mode"]:checked').value;
        processBtn.disabled = true;
        processBtn.querySelector('.btn-text').textContent = 'Verwerken...';
        
        // Clear previous results
        outputText.textContent = '';
        resultsContainer.classList.add('hidden');
        infoLabel.innerHTML = '<svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>Analyseren...';
        infoLabel.className = 'info-label';
        
        try {
            if (mode === 'encrypt') {
                const shift = parseInt(shiftInput.value);
                const response = await fetch('/api/encrypt', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, shift: shift})
                });
                const data = await response.json();
                if (data.success) {
                    outputText.textContent = data.encrypted;
                    infoLabel.innerHTML = '<svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>Geëncrypteerd met shift ' + data.shift;
                    infoLabel.className = 'info-label success';
                }
            } else {
                const response = await fetch('/api/decrypt', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, show_all: true})
                });
                const data = await response.json();
                if (data.success) {
                    let output = `Gevonden shift: ${data.shift}\\n`;
                    output += `Confidence score: ${data.confidence_score.toFixed(2)} (lager = beter)\\n\\n`;
                    output += '='.repeat(60) + '\\n';
                    output += 'DECRYPTED TEKST:\\n';
                    output += '='.repeat(60) + '\\n\\n';
                    output += data.decrypted;
                    
                    outputText.textContent = output;
                    infoLabel.innerHTML = '<svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>Automatisch gedecrypteerd! Shift: ' + data.shift;
                    infoLabel.className = 'info-label success';
                    
                    // Show attempts
                    if (data.all_attempts && data.all_attempts.length > 0) {
                        attemptsList.innerHTML = '';
                        data.all_attempts.forEach((attempt, index) => {
                            const item = document.createElement('div');
                            item.className = 'attempt-item' + (index === 0 ? ' best' : '');
                            item.style.animationDelay = (index * 0.1) + 's';
                            item.innerHTML = `
                                <div class="attempt-header">
                                    ${index + 1}. Shift ${attempt.shift} (score: ${attempt.score.toFixed(2)})
                                </div>
                                <div class="attempt-text">${attempt.text}</div>
                            `;
                            attemptsList.appendChild(item);
                        });
                        resultsContainer.classList.remove('hidden');
                    }
                }
            }
        } catch (error) {
            infoLabel.innerHTML = '<svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>Fout: ' + error.message;
            infoLabel.className = 'info-label error';
        } finally {
            processBtn.disabled = false;
            const mode = document.querySelector('input[name="mode"]:checked').value;
            if (mode === 'encrypt') {
                processBtn.querySelector('.btn-text').textContent = 'Encrypt';
            } else {
                processBtn.querySelector('.btn-text').textContent = 'Decrypt';
            }
        }
    });
    
    // Clear button
    clearBtn.addEventListener('click', function() {
        inputText.value = '';
        outputText.textContent = '';
        charCount.textContent = '0';
        infoLabel.innerHTML = '<svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>Voer tekst in en klik op \\'Verwerk\\'';
        infoLabel.className = 'info-label';
        resultsContainer.classList.add('hidden');
    });
});"""


def main():
    """Start de web server"""
    import os
    
    port = 8002  # Changed from 8000 to avoid conflict with FTI and LTID
    server_address = ('', port)
    httpd = HTTPServer(server_address, CaesarWebHandler)
    
    # Suppress output if running from jacops.py
    if os.getenv('JACOPS_RUNNING') != '1':
        print("="*70)
        print("🌐 Caesar Cipher Decoder - Web GUI")
        print("="*70)
        print(f"\n✅ Server gestart op http://localhost:{port}")
        print("\n📝 Open je browser en ga naar:")
        print(f"   http://localhost:{port}")
        print("\n⚠️  Druk op Ctrl+C om te stoppen\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        if os.getenv('JACOPS_RUNNING') != '1':
            print("\n\n👋 Server gestopt. Tot ziens!")
        httpd.shutdown()


if __name__ == "__main__":
    main()
