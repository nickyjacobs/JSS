"""
Secure File Sharing System - Flask Web Application
"""
import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from file_manager import FileManager
from config import MAX_FILE_SIZE, DEFAULT_EXPIRY_HOURS, SERVER_PORT, SERVER_HOST
import io

app = Flask(__name__)
CORS(app)

# Initialize file manager
file_manager = FileManager()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read file data
        file_data = file.read()
        
        if len(file_data) > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB'
            }), 400
        
        # Get optional password
        password = request.form.get('password', '').strip() or None
        
        # Get expiry hours
        try:
            expiry_hours = int(request.form.get('expiry_hours', DEFAULT_EXPIRY_HOURS))
            expiry_hours = max(1, min(expiry_hours, 168))  # Max 7 days
        except (ValueError, TypeError):
            expiry_hours = DEFAULT_EXPIRY_HOURS
        
        # Save file
        result = file_manager.save_file(
            file_data,
            file.filename,
            password=password,
            expiry_hours=expiry_hours
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/list', methods=['GET'])
def list_files():
    """List all active files"""
    try:
        files = file_manager.list_files()
        return jsonify({
            'success': True,
            'data': files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/info/<token>', methods=['GET'])
def get_file_info(token):
    """Get file information"""
    try:
        file_info = file_manager.get_file_info(token)
        if not file_info:
            return jsonify({
                'success': False,
                'error': 'File not found or expired'
            }), 404
        
        # Don't expose password hash
        file_info.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'data': file_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<token>', methods=['POST'])
def download_file(token):
    """Download a file"""
    try:
        data = request.get_json() or {}
        password = data.get('password', '').strip() or None
        
        file_data = file_manager.download_file(token, password)
        
        if not file_data:
            return jsonify({
                'success': False,
                'error': 'File not found, expired, or incorrect password'
            }), 404
        
        # Get file info for filename
        file_info = file_manager.get_file_info(token)
        filename = file_info['filename'] if file_info else 'download'
        
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/delete/<token>', methods=['DELETE'])
def delete_file(token):
    """Delete a file"""
    try:
        if file_manager.delete_file(token):
            return jsonify({
                'success': True,
                'message': 'File deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cleanup', methods=['POST'])
def cleanup_expired():
    """Clean up expired files"""
    try:
        deleted_count = file_manager.cleanup_expired()
        return jsonify({
            'success': True,
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Suppress output if running from jacops.py
    if os.getenv('JACOPS_RUNNING') != '1':
        print(f"Starting Secure File Sharing System on http://{SERVER_HOST}:{SERVER_PORT}")
    
    app.run(host='127.0.0.1', port=SERVER_PORT, debug=False)
