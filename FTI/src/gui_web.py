#!/usr/bin/env python3
"""
Web-based GUI for File Type Identifier.
"""

import cgi
import html
import http.server
import io
import os
import re
import shutil
import socketserver
import tempfile
import time
from pathlib import Path

import sys
from pathlib import Path

# ANSI color codes voor terminal output (same as main.py)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_RED = '\033[91m'

# Try to import config from parent directory
try:
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from config import VIRUSTOTAL_API_KEY
except ImportError:
    VIRUSTOTAL_API_KEY = None

# Use absolute imports when run as script, relative when imported as package
try:
    from .identifier import identify
except ImportError:
    from identifier import identify

# HTML template met alle styling en JavaScript
PAGE_HTML = """<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>File Type Identifier</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
      color: #e4e4e7;
      padding: 1.25rem;
      min-height: 100vh;
      position: relative;
      overflow-x: hidden;
    }}
    body::before {{
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: 
        radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
      pointer-events: none;
      z-index: 0;
    }}
    .container {{
      max-width: 900px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }}
    .page-title {{
      font-size: 2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 1.25rem;
      letter-spacing: -0.02em;
    }}
    .card {{
      background: rgba(39, 39, 42, 0.8);
      backdrop-filter: blur(20px);
      border-radius: 16px;
      padding: 1.75rem;
      box-shadow: 
        0 20px 25px -5px rgba(0, 0, 0, 0.4),
        0 10px 10px -5px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .card:hover {{
      transform: translateY(-2px);
      box-shadow: 
        0 25px 30px -5px rgba(0, 0, 0, 0.5),
        0 15px 15px -5px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }}
    .dropzone {{
      border: 2px dashed rgba(63, 63, 70, 0.6);
      border-radius: 12px;
      padding: 2.25rem 1.5rem;
      text-align: center;
      background: linear-gradient(135deg, rgba(24, 24, 27, 0.6) 0%, rgba(31, 31, 35, 0.6) 100%);
      backdrop-filter: blur(10px);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }}
    .dropzone::before {{
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
      transition: left 0.5s;
    }}
    .dropzone:hover {{
      border-color: rgba(96, 165, 250, 0.5);
      background: linear-gradient(135deg, rgba(30, 58, 95, 0.4) 0%, rgba(37, 37, 42, 0.4) 100%);
      transform: scale(1.01);
    }}
    .dropzone:hover::before {{
      left: 100%;
    }}
    .dropzone.dragover {{
      border-color: #60a5fa;
      background: linear-gradient(135deg, rgba(30, 58, 95, 0.6) 0%, rgba(59, 130, 246, 0.2) 100%);
      box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
    }}
    .dropzone.error-flash {{
      animation: flashRedBorder 2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    @keyframes flashRedBorder {{
      0%, 100% {{
        border-color: rgba(63, 63, 70, 0.6);
        background: linear-gradient(135deg, rgba(24, 24, 27, 0.6) 0%, rgba(31, 31, 35, 0.6) 100%);
        box-shadow: none;
      }}
      25%, 75% {{
        border-color: #ef4444;
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.8) 0%, rgba(153, 27, 27, 0.8) 100%);
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);
      }}
    }}
    .dropzone.has-file {{
      border-color: #22c55e;
      background: linear-gradient(135deg, rgba(20, 83, 45, 0.6) 0%, rgba(22, 163, 74, 0.3) 100%);
      box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
    }}
    .file-input {{
      display: none;
    }}
    .dropzone-inner {{
      pointer-events: none;
    }}
    .btn-upload {{
      pointer-events: auto;
    }}
    .icon {{
      font-size: 3rem;
      margin-bottom: 1rem;
      filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
      animation: float 3s ease-in-out infinite;
    }}
    @keyframes float {{
      0%, 100% {{ transform: translateY(0px); }}
      50% {{ transform: translateY(-8px); }}
    }}
    .hint {{
      font-size: 1rem;
      color: #d4d4d8;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }}
    .filename {{
      font-weight: 600;
      color: #22c55e;
      margin-top: 0.5rem;
      font-size: 0.95rem;
      text-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
    }}
    .btn {{
      display: inline-block;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
    }}
    .btn::before {{
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.2);
      transform: translate(-50%, -50%);
      transition: width 0.6s, height 0.6s;
    }}
    .btn:hover::before {{
      width: 300px;
      height: 300px;
    }}
    .btn:active {{ transform: scale(0.96); }}
    .btn-upload {{
      background: linear-gradient(135deg, #3f3f46 0%, #52525b 100%);
      color: #fff;
      margin-top: 0.5rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }}
    .btn-upload:hover {{
      background: linear-gradient(135deg, #52525b 0%, #71717a 100%);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
      transform: translateY(-2px);
    }}
    .btn-analyze {{
      background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
      color: #fff;
      width: 100%;
      margin-top: 1rem;
      padding: 0.875rem 1.5rem;
      font-size: 1rem;
      box-shadow: 0 8px 16px rgba(37, 99, 235, 0.4);
    }}
    .btn-analyze:hover {{
      background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
      box-shadow: 0 12px 24px rgba(37, 99, 235, 0.5);
      transform: translateY(-3px);
    }}
    .no-file-msg {{
      color: #f87171;
      margin-top: 1rem;
      text-align: center;
      padding: 0.75rem;
      background: rgba(239, 68, 68, 0.1);
      border-radius: 8px;
      border: 1px solid rgba(239, 68, 68, 0.3);
      font-weight: 500;
      font-size: 0.9rem;
      animation: shake 0.5s ease-in-out;
    }}
    @keyframes shake {{
      0%, 100% {{ transform: translateX(0); }}
      25% {{ transform: translateX(-5px); }}
      75% {{ transform: translateX(5px); }}
    }}
    .info-box {{
      background: linear-gradient(135deg, rgba(31, 31, 35, 0.8) 0%, rgba(39, 39, 42, 0.8) 100%);
      backdrop-filter: blur(10px);
      border-left: 4px solid #60a5fa;
      padding: 1rem 1.25rem;
      margin-top: 1.25rem;
      border-radius: 10px;
      font-size: 0.875rem;
      line-height: 1.6;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }}
    .info-box code {{
      background: rgba(39, 39, 42, 0.8);
      padding: 0.35rem 0.65rem;
      border-radius: 8px;
      font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
      font-size: 0.85rem;
      color: #60a5fa;
      display: inline-block;
      margin-top: 0.5rem;
      border: 1px solid rgba(96, 165, 250, 0.2);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }}
    .btn-lang {{
      font-family: inherit;
      font-size: 0.875rem;
      font-weight: 700;
      padding: 0.5rem 1rem;
      border: 2px solid rgba(63, 63, 70, 0.6);
      border-radius: 10px;
      background: rgba(39, 39, 42, 0.8);
      backdrop-filter: blur(10px);
      color: #fff;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      min-width: 60px;
      text-align: center;
    }}
    .btn-lang:hover {{
      background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
      border-color: #60a5fa;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }}
    .copy-btn {{
      margin-left: 0.5rem;
      padding: 0.35rem;
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(96, 165, 250, 0.3);
      border-radius: 5px;
      color: #60a5fa;
      cursor: pointer;
      transition: all 0.2s;
      vertical-align: middle;
      white-space: nowrap;
      line-height: 1;
      width: 24px;
      height: 24px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      visibility: hidden;
      flex-shrink: 0;
    }}
    .copy-btn svg {{
      width: 14px;
      height: 14px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .copy-btn:hover {{
      background: rgba(59, 130, 246, 0.25);
      border-color: #60a5fa;
      transform: scale(1.1);
    }}
    .copy-btn:active {{
      transform: scale(0.95);
    }}
    .copy-btn.copied {{
      background: rgba(34, 197, 94, 0.2);
      border-color: #22c55e;
      color: #22c55e;
      opacity: 1;
      visibility: visible;
    }}
    .hash-container {{
      position: relative;
      display: inline-flex;
      align-items: center;
      flex-wrap: nowrap;
      max-width: 100%;
    }}
    .hash-container:hover .copy-btn {{
      opacity: 1;
      visibility: visible;
    }}
    .hash-container span {{
      flex-shrink: 1;
      min-width: 0;
      overflow-wrap: break-word;
      word-break: break-all;
    }}
    .result-wrap {{
      margin-top: 1.5rem;
      animation: fadeInUp 0.5s ease-out;
    }}
    @keyframes fadeInUp {{
      from {{
        opacity: 0;
        transform: translateY(20px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
    .result-title {{
      font-size: 1.5rem;
      font-weight: 800;
      background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 1rem;
      letter-spacing: -0.01em;
    }}
    .result {{
      background: linear-gradient(135deg, rgba(31, 31, 35, 0.9) 0%, rgba(39, 39, 42, 0.9) 100%);
      backdrop-filter: blur(20px);
      border-radius: 12px;
      padding: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 
        0 10px 15px -3px rgba(0, 0, 0, 0.3),
        0 4px 6px -2px rgba(0, 0, 0, 0.2);
    }}
    .result-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
    }}
    .result-table td {{
      padding: 0.75rem;
      border-bottom: 1px solid rgba(63, 63, 70, 0.5);
      transition: background 0.2s;
      vertical-align: top;
    }}
    .result-table tr:hover td {{
      background: rgba(59, 130, 246, 0.05);
    }}
    .result-table td:last-child {{
      min-height: 1.5rem;
    }}
    .result-table tr:last-child td {{
      border-bottom: none;
    }}
    .result-table td:first-child {{
      font-weight: 600;
      color: #d4d4d8;
      width: 180px;
      font-size: 0.875rem;
    }}
    .result-table td:last-child {{
      color: #f4f4f5;
      word-break: break-all;
      font-size: 0.875rem;
    }}
    .result-hex {{
      font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
      font-size: 0.9rem;
      color: #60a5fa;
      display: inline-block;
    }}
    .result-hash {{
      font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
      font-size: 0.85rem;
      color: #a78bfa;
      display: inline-block;
    }}
    .result-entropy-high {{
      color: #fbbf24;
      font-weight: 700;
      text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);
    }}
    .result-warning {{
      margin-top: 1rem;
      padding: 1rem;
      background: linear-gradient(135deg, rgba(127, 29, 29, 0.8) 0%, rgba(153, 27, 27, 0.8) 100%);
      border-left: 4px solid #ef4444;
      border-radius: 10px;
      color: #fca5a5;
      font-weight: 600;
      font-size: 0.85rem;
      box-shadow: 0 4px 6px rgba(239, 68, 68, 0.2);
      animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.9; }}
    }}
    .result.error {{
      color: #f87171;
      background: rgba(239, 68, 68, 0.1);
      padding: 1rem;
      border-radius: 8px;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}
    .vt-detected {{
      color: #f87171;
      font-weight: 700;
      text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
    }}
    .vt-clean {{
      color: #34d399;
      font-weight: 600;
      text-shadow: 0 0 10px rgba(52, 211, 153, 0.3);
    }}
    .result-table .vt-detected,
    .result-table .vt-clean {{
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 8px;
      background: rgba(0, 0, 0, 0.2);
    }}
    .export-buttons {{
      margin-top: 1rem;
      display: flex;
      gap: 0.5rem;
    }}
    .btn-export {{
      background: linear-gradient(135deg, #3f3f46 0%, #52525b 100%);
      color: #fff;
      padding: 0.625rem 1.25rem;
      font-size: 0.85rem;
      font-weight: 600;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .btn-export:hover {{
      background: linear-gradient(135deg, #52525b 0%, #71717a 100%);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
      transform: translateY(-2px);
    }}
  </style>
</head>
<body>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.75rem;">
      <h1 class="page-title" style="margin: 0;" data-nl="File Type Identifier" data-en="File Type Identifier">File Type Identifier</h1>
      <button id="langToggle" class="btn-lang" onclick="toggleLanguage()" data-nl="NL" data-en="EN">NL</button>
    </div>
    <div class="card">
      <form method="post" action="/" enctype="multipart/form-data" id="form">
        <div class="dropzone" id="dropzone">
          <input type="file" name="file" id="file" class="file-input" accept="*" aria-label="Bestand kiezen" data-max-size="26214400">
          <div class="dropzone-inner">
            <div class="icon">📁</div>
            <div class="hint" id="hint" data-nl="Sleep een bestand hierheen of klik om te kiezen" data-en="Drag a file here or click to choose">Sleep een bestand hierheen of klik om te kiezen<br><small style="color:#71717a;" id="maxSizeHint" data-nl="Maximaal 25MB" data-en="Maximum 25MB">Maximaal 25MB</small></div>
            <div class="filename" id="filename" style="display:none;"></div>
            <span class="btn btn-upload" id="btnUpload" data-nl="Kies bestand" data-en="Choose file">Kies bestand</span>
          </div>
        </div>
        <button type="submit" class="btn btn-analyze" id="btnAnalyze" data-nl="Analyseren" data-en="Analyze">Analyseren</button>
      </form>
      <p class="no-file-msg" id="noFileMsg" style="display:none;" data-nl="Selecteer eerst een bestand." data-en="Please select a file first.">Selecteer eerst een bestand.</p>
      <div class="info-box">
        <strong id="uploadLimitLabel" data-nl="📋 Upload limiet:" data-en="📋 Upload limit:">📋 Upload limiet:</strong> <span id="uploadLimitText" data-nl="Maximaal 25MB per bestand." data-en="Maximum 25MB per file.">Maximaal 25MB per bestand.</span><br>
        <span id="cliLabel" data-nl="Voor grotere bestanden gebruik de CLI:" data-en="For larger files use the CLI:">Voor grotere bestanden gebruik de CLI:</span> <code>python3 main.py &lt;bestand&gt;</code>
      </div>
      {result_block}
      {export_block}
    </div>
  </div>
  <script>
    var currentLang = localStorage.getItem('fti_lang') || 'nl';
    function toggleLanguage() {{
      currentLang = currentLang === 'nl' ? 'en' : 'nl';
      setLanguage(currentLang);
    }}
    function setLanguage(lang) {{
      currentLang = lang;
      localStorage.setItem('fti_lang', lang);
      var langBtn = document.getElementById('langToggle');
      if (langBtn) {{
        langBtn.textContent = lang === 'nl' ? 'NL' : 'EN';
      }}
      // Update alle elementen met data-nl en data-en attributen
      document.querySelectorAll('[data-nl][data-en]').forEach(function(el) {{
        var text = el.getAttribute('data-' + lang);
        if (!text) return;
        if (el.id === 'hint') {{
          // Speciale behandeling voor hint met <small> tag
          var smallEl = el.querySelector('small');
          var smallText = smallEl ? smallEl.getAttribute('data-' + lang) : '';
          el.innerHTML = text + (smallText ? '<br><small style="color:#71717a;">' + smallText + '</small>' : '');
        }} else if (el.tagName === 'TD') {{
          // Table cells: update alleen de eerste child (label span)
          var span = el.querySelector('span[data-nl][data-en]');
          if (span) span.textContent = span.getAttribute('data-' + lang);
        }} else if (el.tagName === 'SPAN' || el.tagName === 'A') {{
          // Span of link: update text content
          if (el.innerHTML && el.innerHTML.includes('<span')) {{
            // Als er nested spans zijn, update die
            var innerSpans = el.querySelectorAll('span[data-nl][data-en]');
            if (innerSpans.length > 0) {{
              innerSpans.forEach(function(span) {{
                var spanText = span.getAttribute('data-' + lang);
                if (spanText) span.textContent = spanText;
              }});
            }} else {{
              el.textContent = text;
            }}
          }} else {{
            el.textContent = text;
          }}
        }} else if (el.innerHTML && el.innerHTML.includes('<')) {{
          // Element met HTML: update alleen de text content binnen spans
          var innerSpans = el.querySelectorAll('span[data-nl][data-en], a[data-nl][data-en]');
          if (innerSpans.length > 0) {{
            innerSpans.forEach(function(span) {{
              var spanText = span.getAttribute('data-' + lang);
              if (spanText) span.textContent = spanText;
            }});
          }} else {{
            el.textContent = text;
          }}
        }} else {{
          el.textContent = text;
        }}
      }});
      // Update maxSizeHint apart
      var maxSizeHint = document.getElementById('maxSizeHint');
      if (maxSizeHint) {{
        maxSizeHint.textContent = maxSizeHint.getAttribute('data-' + lang);
      }}
      // Update copy buttons (icon blijft hetzelfde, alleen title)
      document.querySelectorAll('.copy-btn').forEach(function(btn) {{
        if (!btn.classList.contains('copied')) {{
          btn.title = lang === 'nl' ? 'Kopieer' : 'Copy';
        }}
      }});
    }}
    setLanguage(currentLang);
    var form = document.getElementById('form');
    var dropzone = document.getElementById('dropzone');
    var fileInput = document.getElementById('file');
    var hint = document.getElementById('hint');
    var filenameEl = document.getElementById('filename');
    var noFileMsg = document.getElementById('noFileMsg');
    var maxSize = parseInt(fileInput.getAttribute('data-max-size')) || 26214400; // 25MB default
    function flashDropzoneError() {{
      dropzone.classList.add('error-flash');
      setTimeout(function() {{
        dropzone.classList.remove('error-flash');
      }}, 2000);
    }}
    function updateUI() {{
      var file = fileInput.files[0];
      if (file) {{
        filenameEl.textContent = file.name;
        filenameEl.style.display = 'block';
        hint.style.display = 'none';
        dropzone.classList.add('has-file');
        noFileMsg.style.display = 'none';
      }} else {{
        filenameEl.style.display = 'none';
        hint.style.display = 'block';
        dropzone.classList.remove('has-file');
      }}
    }}
    fileInput.addEventListener('change', function(e) {{
      var file = fileInput.files[0];
      if (!file) {{
        updateUI();
        return;
      }}
      // Check bestandsgrootte
      if (file.size > maxSize) {{
        var sizeMB = (file.size / (1024 * 1024)).toFixed(1);
        var maxMB = (maxSize / (1024 * 1024)).toFixed(0);
        // Flikker het hele dropzone blok rood
        flashDropzoneError();
        var msg = currentLang === 'nl' 
          ? 'Bestand te groot (' + sizeMB + ' MB > ' + maxMB + ' MB).\\n\\nGebruik de CLI voor grote bestanden:\\npython3 main.py <bestand>'
          : 'File too large (' + sizeMB + ' MB > ' + maxMB + ' MB).\\n\\nUse the CLI for large files:\\npython3 main.py <file>';
        alert(msg);
        fileInput.value = '';
        filenameEl.style.display = 'none';
        hint.style.display = 'block';
        dropzone.classList.remove('has-file');
        noFileMsg.style.display = 'none';
        return;
      }}
      updateUI();
    }});
    dropzone.addEventListener('dragover', function(e) {{
      e.preventDefault();
      dropzone.classList.add('dragover');
    }});
    dropzone.addEventListener('dragleave', function(e) {{
      e.preventDefault();
      dropzone.classList.remove('dragover');
    }});
    dropzone.addEventListener('drop', function(e) {{
      e.preventDefault();
      dropzone.classList.remove('dragover');
      var files = e.dataTransfer.files;
      if (files.length) {{
        // Check grootte voordat we het bestand accepteren
        if (files[0].size > maxSize) {{
          var sizeMB = (files[0].size / (1024 * 1024)).toFixed(1);
          var maxMB = (maxSize / (1024 * 1024)).toFixed(0);
          // Flikker het hele dropzone blok rood
          flashDropzoneError();
          var msg = currentLang === 'nl'
            ? 'Bestand te groot (' + sizeMB + ' MB > ' + maxMB + ' MB).\\n\\nGebruik de CLI voor grote bestanden:\\npython3 main.py <bestand>'
            : 'File too large (' + sizeMB + ' MB > ' + maxMB + ' MB).\\n\\nUse the CLI for large files:\\npython3 main.py <file>';
          alert(msg);
          return;
        }}
        fileInput.files = files;
        updateUI();
      }}
    }});
    document.getElementById('btnUpload').addEventListener('click', function(e) {{ 
      e.preventDefault(); 
      e.stopPropagation();
      fileInput.click(); 
    }});
    dropzone.addEventListener('click', function(e) {{
      // Als je niet op de button klikt, klik dan op het file input
      if (e.target.id !== 'btnUpload' && !e.target.closest('#btnUpload')) {{
        fileInput.click();
      }}
    }});
    form.addEventListener('submit', function(e) {{
      if (!fileInput.files.length) {{
        e.preventDefault();
        noFileMsg.style.display = 'block';
        return false;
      }}
      // Double-check grootte bij submit (extra veiligheid)
      var file = fileInput.files[0];
      if (file && file.size > maxSize) {{
        e.preventDefault();
        var sizeMB = (file.size / (1024 * 1024)).toFixed(1);
        var maxMB = (maxSize / (1024 * 1024)).toFixed(0);
        // Flikker het hele dropzone blok rood
        flashDropzoneError();
        var msg = currentLang === 'nl'
          ? 'Bestand te groot (' + sizeMB + ' MB > ' + maxMB + ' MB). Upload geblokkeerd.\\n\\nGebruik de CLI:\\npython3 main.py <bestand>'
          : 'File too large (' + sizeMB + ' MB > ' + maxMB + ' MB). Upload blocked.\\n\\nUse the CLI:\\npython3 main.py <file>';
        alert(msg);
        return false;
      }}
    }});
    // Update taal na nieuwe resultaten (wanneer pagina wordt geladen met resultaten)
    setTimeout(function() {{
      setLanguage(currentLang);
    }}, 100);
    function downloadJSON(jsonB64, filename) {{
      var json = atob(jsonB64);
      var blob = new Blob([json], {{type: 'application/json'}});
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = (filename || 'result').replace(/\\.[^.]+$/, '') + '.json';
      a.click();
      URL.revokeObjectURL(url);
    }}
    function downloadCSV(jsonB64) {{
      var json = JSON.parse(atob(jsonB64));
      var csv = 'filepath,file_size,detected_type,file_extension,md5,sha256,entropy,mismatch,file_cmd_output\\n';
      csv += '"' + (json.filepath || '').replace(/"/g, '""') + '",';
      csv += (json.file_size || '') + ',';
      csv += '"' + (json.detected_type || '').replace(/"/g, '""') + '",';
      csv += '"' + (json.file_extension || '').replace(/"/g, '""') + '",';
      csv += '"' + (json.md5 || '').replace(/"/g, '""') + '",';
      csv += '"' + (json.sha256 || '').replace(/"/g, '""') + '",';
      csv += (json.entropy || '') + ',';
      csv += (json.mismatch ? 'true' : 'false') + ',';
      csv += '"' + (json.file_cmd_output || '').replace(/"/g, '""') + '"\\n';
      var blob = new Blob([csv], {{type: 'text/csv'}});
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = (json.filepath || 'result').split('/').pop().replace(/\\.[^.]+$/, '') + '.csv';
      a.click();
      URL.revokeObjectURL(url);
    }}
    function copyToClipboard(text, btn) {{
      navigator.clipboard.writeText(text).then(function() {{
        var originalIcon = btn.getAttribute('data-icon');
        var checkIcon = btn.getAttribute('data-check');
        var originalTitle = btn.getAttribute('title');
        btn.innerHTML = checkIcon;
        btn.title = currentLang === 'nl' ? 'Gekopieerd!' : 'Copied!';
        btn.classList.add('copied');
        setTimeout(function() {{
          btn.innerHTML = originalIcon;
          btn.title = originalTitle;
          btn.classList.remove('copied');
        }}, 1500);
      }}).catch(function(err) {{
        alert(currentLang === 'nl' ? 'Fout bij kopiëren' : 'Error copying');
      }});
    }}
  </script>
</body>
</html>
"""


def parse_multipart(handler: http.server.BaseHTTPRequestHandler):
    """Parse multipart/form-data; retourneer (bestandsinhoud als bytes, bestandsnaam)."""
    ctype = handler.headers.get("Content-Type", "")
    if not ctype.startswith("multipart/form-data"):
        return None, None
    try:
        content_length = int(handler.headers.get("Content-Length", 0))
    except ValueError:
        return None, None
    if content_length <= 0:
        return None, None
    
    # Veiligheid: limiet op upload grootte (max 25MB)
    max_upload = 25 * 1024 * 1024
    if content_length > max_upload:
        raise ValueError(f"Bestand te groot ({content_length / (1024*1024):.1f} MB > 25MB). Gebruik de CLI: python3 main.py <bestand>")
    
    try:
        # Lees body in chunks met timeout check
        body_parts = []
        remaining = content_length
        chunk_size = 2 * 1024 * 1024  # 2MB chunks
        max_read_time = 30  # Max 30 seconden lezen
        start_time = time.time()
        bytes_read = 0
        
        while remaining > 0:
            # Timeout check
            if time.time() - start_time > max_read_time:
                raise ValueError("Timeout bij lezen bestand (te groot of te traag)")
            
            chunk = handler.rfile.read(min(chunk_size, remaining))
            if not chunk:
                break
            body_parts.append(chunk)
            remaining -= len(chunk)
            bytes_read += len(chunk)
            
            # Veiligheid: stop als we te veel hebben gelezen
            if bytes_read > max_upload:
                raise ValueError(f"Bestand te groot (>{max_upload / (1024*1024):.0f}MB)")
        
        body = b"".join(body_parts)
    except ValueError:
        raise  # Her-raise ValueError
    except (OSError, ConnectionError, MemoryError):
        return None, None
    except Exception:
        return None, None
    
    if len(body) != content_length:
        return None, None
    
    env = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": ctype,
        "CONTENT_LENGTH": str(content_length),
    }
    try:
        fs = cgi.FieldStorage(
            fp=io.BytesIO(body),
            environ=env,
            keep_blank_values=True,
        )
        if "file" not in fs:
            return None, None
        field = fs["file"]
        if isinstance(field, list):
            field = field[0] if field else None
        if field is None:
            return None, None
        filename = getattr(field, "filename", None) or "upload"
        # Lees inhoud direct nu (field.file kan daarna gesloten worden door cgi)
        if getattr(field, "file", None):
            f = field.file
            try:
                content = f.read()
            except (OSError, ValueError):
                return None, None
        elif isinstance(field, bytes):
            content = field
        elif isinstance(field, str):
            content = field.encode("utf-8")
        else:
            val = getattr(field, "value", None)
            if isinstance(val, bytes):
                content = val
            else:
                return None, None
        return content, filename
    except Exception:
        return None, None
    return None, None


def render_result(data: dict) -> tuple:
    """Render analysis result as HTML. Returns (result_html, export_html)."""
    if "error" in data:
        return (
            '<div class="result-wrap">'
            '<div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
            f'<div class="result error">{html.escape(data["error"])} — {html.escape(data.get("filepath", ""))}</div>'
            '</div>',
            ""
        )
    
    # Labels met vertalingen
    labels = {
        "Bestand": {"nl": "Bestand", "en": "File"},
        "Grootte": {"nl": "Grootte", "en": "Size"},
        "Raw hex": {"nl": "Raw hex", "en": "Raw hex"},
        "Gedetecteerd type": {"nl": "Gedetecteerd type", "en": "Detected type"},
        "Bestandsextensie": {"nl": "Bestandsextensie", "en": "File extension"},
        "file-commando": {"nl": "file-commando", "en": "file command"},
        "MD5": {"nl": "MD5", "en": "MD5"},
        "SHA256": {"nl": "SHA256", "en": "SHA256"},
        "Entropy": {"nl": "Entropy", "en": "Entropy"},
        "VirusTotal": {"nl": "VirusTotal", "en": "VirusTotal"},
    }
    
    rows = [
        ("Bestand", data["filepath"], labels["Bestand"]),
        ("Grootte", data.get("file_size_formatted", "—"), labels["Grootte"]),
        ("Raw hex", data["raw_hex"], labels["Raw hex"]),
        ("Gedetecteerd type", data["detected_type"], labels["Gedetecteerd type"]),
        ("Bestandsextensie", data["file_extension"], labels["Bestandsextensie"]),
    ]
    if data.get("file_cmd_output"):
        rows.append(("file-commando", data["file_cmd_output"], labels["file-commando"]))
    if data.get("md5"):
        rows.append(("MD5", data["md5"], labels["MD5"]))
    if data.get("sha256"):
        rows.append(("SHA256", data["sha256"], labels["SHA256"]))
    if data.get("entropy") is not None:
        entropy_val = data["entropy"]
        entropy_note_nl = " (hoog — mogelijk encrypted/obfuscated)" if entropy_val > 7.5 else ""
        entropy_note_en = " (high — possibly encrypted/obfuscated)" if entropy_val > 7.5 else ""
        rows.append(("Entropy", f"{entropy_val:.2f}", labels["Entropy"], entropy_note_nl, entropy_note_en))
    
    # VirusTotal resultaten
    vt_result = data.get("virustotal")
    if vt_result:
        if vt_result.get("error"):
            error_nl = f"Fout: {html.escape(vt_result['error'])}"
            error_en = f"Error: {html.escape(vt_result['error'])}"
            rows.append(("VirusTotal", f'<span style="color: #f59e0b;" data-nl="{error_nl}" data-en="{error_en}">{error_nl}</span>', labels["VirusTotal"]))
        elif vt_result.get("status") == "not_found":
            rows.append(("VirusTotal", '<span style="color: #71717a;" data-nl="Niet gevonden in database" data-en="Not found in database">Niet gevonden in database</span>', labels["VirusTotal"]))
        else:
            detected = vt_result.get("detected", 0)
            total = vt_result.get("total", 0)
            vt_class = "vt-detected" if detected > 0 else "vt-clean"
            if detected > 0:
                vt_text_nl = f"⚠️ {detected}/{total} engines detecteren malware"
                vt_text_en = f"⚠️ {detected}/{total} engines detected malware"
            else:
                vt_text_nl = f"✓ 0/{total} — Geen malware gedetecteerd"
                vt_text_en = f"✓ 0/{total} — No malware detected"
            rows.append(("VirusTotal", f'<span class="{vt_class}" data-nl="{vt_text_nl}" data-en="{vt_text_en}">{vt_text_nl}</span>', labels["VirusTotal"]))
            if vt_result.get("permalink"):
                rows.append(("", f'<a href="{html.escape(vt_result["permalink"])}" target="_blank" style="color: #3b82f6; text-decoration: none;" data-nl="🔗 Bekijk op VirusTotal" data-en="🔗 View on VirusTotal">🔗 Bekijk op VirusTotal</a>', None))
    elif VIRUSTOTAL_API_KEY:
        rows.append(("VirusTotal", '<span style="color: #71717a;" data-nl="Geen resultaat beschikbaar" data-en="No result available">Geen resultaat beschikbaar</span>', labels["VirusTotal"]))
    
    table_rows = []
    for row in rows:
        if len(row) == 2:
            label, value = row
            label_translations = None
            note_nl = note_en = None
        elif len(row) == 3:
            label, value, label_translations = row
            note_nl = note_en = None
        else:
            label, value, label_translations, note_nl, note_en = row[:5]
        
        cell_class = ""
        copy_button = ""
        # SVG icons voor copy en check (niet escapen, want we willen HTML)
        copy_icon_svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" fill="none"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" fill="none"/></svg>'
        check_icon_svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12" fill="none" stroke-width="2.5"/></svg>'
        if label == "Raw hex":
            cell_class = " result-hex"
            # Voeg copy button toe
            raw_value = str(value)
            raw_value_escaped = html.escape(raw_value)
            raw_value_js = raw_value.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
            # Escape quotes voor data attributes maar niet voor innerHTML
            copy_icon_attr = copy_icon_svg.replace('"', '&quot;')
            check_icon_attr = check_icon_svg.replace('"', '&quot;')
            copy_button = f'<span class="hash-container"><span class="{cell_class}">{raw_value_escaped}</span><button class="copy-btn" onclick="copyToClipboard(\'{raw_value_js}\', this)" title="Kopieer" data-icon="{copy_icon_attr}" data-check="{check_icon_attr}">{copy_icon_svg}</button></span>'
            value_display = copy_button
        elif label in ("MD5", "SHA256"):
            cell_class = " result-hash"
            # Voeg copy button toe
            hash_value = str(value)
            hash_value_escaped = html.escape(hash_value)
            hash_value_js = hash_value.replace("'", "\\'").replace('"', '\\"')
            # Escape quotes voor data attributes maar niet voor innerHTML
            copy_icon_attr = copy_icon_svg.replace('"', '&quot;')
            check_icon_attr = check_icon_svg.replace('"', '&quot;')
            copy_button = f'<span class="hash-container"><span class="{cell_class}">{hash_value_escaped}</span><button class="copy-btn" onclick="copyToClipboard(\'{hash_value_js}\', this)" title="Kopieer" data-icon="{copy_icon_attr}" data-check="{check_icon_attr}">{copy_icon_svg}</button></span>'
            value_display = copy_button
        elif label == "Entropy":
            cell_class = " result-entropy-high" if note_nl and "hoog" in note_nl else ""
            if note_nl and note_en:
                value = f"{value}<span data-nl=\"{note_nl}\" data-en=\"{note_en}\">{note_nl}</span>"
            # HTML content niet escapen
            is_html = isinstance(value, str) and (value.startswith('<') or 'href=' in value)
            value_display = value if is_html else html.escape(str(value))
        else:
            # HTML content (zoals VirusTotal links, copy buttons) niet escapen
            is_html = isinstance(value, str) and (value.startswith('<') or 'href=' in value or 'copy-btn' in value or 'hash-container' in value)
            value_display = value if is_html else html.escape(str(value))
        
        # Label met vertalingen
        if label_translations:
            label_html = f'<span data-nl="{label_translations["nl"]}" data-en="{label_translations["en"]}">{html.escape(label_translations["nl"])}</span>'
        else:
            label_html = html.escape(label)
        
        table_rows.append(
            f"<tr><td>{label_html}</td><td class=\"{cell_class}\">{value_display}</td></tr>"
        )
    table_body = "".join(table_rows)
    warning_block = ""
    if data.get("mismatch") and data.get("message"):
        warning_nl = "Let op: Controleer of het magic number overeenkomt met de extensie — mogelijke spoofing."
        warning_en = "Note: Check if magic number matches the extension — possible spoofing."
        warning_block = f'<div class="result-warning" data-nl="{warning_nl}" data-en="{warning_en}">{html.escape(data["message"])}</div>'
    
    # Export knoppen
    export_block = ""
    if not data.get("error"):
        import base64
        import json as json_lib
        json_data = json_lib.dumps(data, ensure_ascii=False)
        json_b64 = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
        export_block = (
            '<div class="export-buttons">'
            f'<button class="btn btn-export" onclick="downloadJSON(\'{json_b64}\', \'{html.escape(data.get("filepath", "result").split("/")[-1])}\')" data-nl="Export JSON" data-en="Export JSON">Export JSON</button>'
            f'<button class="btn btn-export" onclick="downloadCSV(\'{json_b64}\')" data-nl="Export CSV" data-en="Export CSV">Export CSV</button>'
            '</div>'
        )
    
    result_html = (
        '<div class="result-wrap">'
        '<div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
        f'<div class="result"><table class="result-table"><tbody>{table_body}</tbody></table>{warning_block}</div>'
        '</div>'
    )
    return result_html, export_block


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html_out = PAGE_HTML.format(result_block="", export_block="")
            self.wfile.write(html_out.encode("utf-8"))
        else:
            super().do_GET()
    
    def do_POST(self) -> None:
        """Handle POST requests with error recovery."""
        result_block = ""
        export_block = ""
        
        # Zorg dat we ALTIJD een response sturen, zelfs bij crashes
        try:
            # Check content-length VOORDAT we beginnen met lezen
            try:
                content_length = int(self.headers.get("Content-Length", 0))
            except (ValueError, TypeError):
                content_length = 0
            
            max_upload = 25 * 1024 * 1024  # 25MB
            if content_length > max_upload:
                result_block = (
                    '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                    f'<div class="result error">Bestand te groot ({content_length / (1024*1024):.1f} MB > 25MB). '
                    'Gebruik de CLI voor grote bestanden:<br><code style="background:#27272a;padding:0.25rem 0.5rem;border-radius:4px;">python3 main.py &lt;bestand&gt;</code></div></div>'
                )
                self._send_response(result_block, "")
                return
            
            # Parse multipart (kan crashen bij grote bestanden)
            try:
                file_content, orig_name = parse_multipart(self)
            except ValueError as e:
                # Bestand te groot tijdens parsing
                result_block = (
                    '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                    f'<div class="result error">{html.escape(str(e))}</div></div>'
                )
                self._send_response(result_block, "")
                return
            except Exception as e:
                result_block = (
                    '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                    f'<div class="result error">Fout bij lezen bestand: {html.escape(str(e))}</div></div>'
                )
                self._send_response(result_block, "")
                return
            
            if file_content and orig_name:
                # Schrijf naar temp file voor analyse
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(orig_name).suffix)
                tmp_path = tmp_file.name
                try:
                    tmp_file.write(file_content)
                    tmp_file.close()
                    
                    # Analyseer bestand
                    result = identify(tmp_path, use_file_cmd=True, virustotal_api_key=VIRUSTOTAL_API_KEY)
                    result_block, export_block = render_result(result)
                finally:
                    # Ruim temp file op
                    if os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass
            else:
                result_block = '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div><div class="result error" data-nl="Geen bestand ontvangen. Kies een bestand en klik op Analyseren." data-en="No file received. Please select a file and click Analyze.">Geen bestand ontvangen. Kies een bestand en klik op Analyseren.</div></div>'
        except ValueError as e:
            # Bestand te groot of andere validatie fout
            error_msg = str(e)
            if "te groot" in error_msg.lower() or "too large" in error_msg.lower():
                result_block = (
                    '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                    f'<div class="result error">{html.escape(error_msg)}</div></div>'
                )
            else:
                result_block = (
                    '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                    f'<div class="result error">Fout: {html.escape(error_msg)}</div></div>'
                )
            export_block = ""
        except MemoryError:
            result_block = (
                '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                '<div class="result error" data-nl="Onvoldoende geheugen. Het bestand is te groot om te verwerken. Probeer een kleiner bestand (&lt;25MB) of gebruik de CLI." data-en="Insufficient memory. The file is too large to process. Try a smaller file (&lt;25MB) or use the CLI.">Onvoldoende geheugen. Het bestand is te groot om te verwerken. Probeer een kleiner bestand (&lt;25MB) of gebruik de CLI.</div></div>'
            )
            export_block = ""
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            result_block = (
                '<div class="result-wrap"><div class="result-title" data-nl="Resultaat" data-en="Result">Resultaat</div>'
                f'<div class="result error">Server fout: {html.escape(error_msg)}</div></div>'
            )
            export_block = ""
        
        # Stuur altijd een response
        self._send_response(result_block, export_block)
    
    def _send_response(self, result_block: str, export_block: str) -> None:
        """Helper om altijd een response te sturen, zelfs bij errors."""
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html_out = PAGE_HTML.format(result_block=result_block, export_block=export_block)
            self.wfile.write(html_out.encode("utf-8"))
            self.wfile.flush()
        except Exception:
            # Als zelfs dit faalt, probeer een minimale error response
            try:
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
            except Exception:
                pass  # Geen response mogelijk, server crasht


class ReuseTCPServer(socketserver.TCPServer):
    """TCPServer met SO_REUSEADDR om port conflicts te voorkomen."""
    allow_reuse_address = True




def main():
    """Start de web server."""
    port = 8000
    max_port = 8010
    
    # Get terminal width for centering messages
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80
    
    box_width = 75  # Same as main.py
    box_padding = (term_width - box_width) // 2
    border_line = "═" * 73
    content_width = 73
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    while port <= max_port:
        try:
            with ReuseTCPServer(("", port), Handler) as httpd:
                # Print server info in a nice box
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                
                # Server URL line
                server_msg = f"{Colors.OKGREEN}{Colors.BOLD}Server draait op{Colors.ENDC} {Colors.BRIGHT_CYAN}{Colors.BOLD}http://localhost:{port}{Colors.ENDC}"
                server_clean = ansi_escape.sub('', server_msg)
                # Account for the space after ║
                server_padding = max(0, content_width - len(server_clean) - 1)
                # Ensure total length matches exactly
                total_length = 1 + len(server_clean) + server_padding
                if total_length != content_width:
                    server_padding = max(0, content_width - len(server_clean) - 1)
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {server_msg}{' ' * server_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                
                # Start the server (blocking)
                httpd.serve_forever()
        except OSError:
            port += 1
            if port > max_port:
                # Print error in a box
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{border_line}╗{Colors.ENDC}")
                error_msg = f"{Colors.BRIGHT_RED}{Colors.BOLD}✗{Colors.ENDC} {Colors.FAIL}Geen beschikbare poort gevonden (8000-8010){Colors.ENDC}"
                error_clean = ansi_escape.sub('', error_msg)
                # Account for the space after ║
                error_padding = max(0, content_width - len(error_clean) - 1)
                # Ensure total length matches exactly
                total_length = 1 + len(error_clean) + error_padding
                if total_length != content_width:
                    error_padding = max(0, content_width - len(error_clean) - 1)
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC} {error_msg}{' ' * error_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.ENDC}")
                print(f"{' ' * box_padding}{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{border_line}╝{Colors.ENDC}\n")
                return
        except KeyboardInterrupt:
            # Ctrl+C pressed - let it propagate to stop entire application
            raise


if __name__ == "__main__":
    main()
