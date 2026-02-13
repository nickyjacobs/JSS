"""
Password Policy Analyzer - Flask Web Application

Flask web applicatie die de Password Policy Analyzer exposeert via een REST API
en web interface.

Routes:
    /: Main page met web interface
    /api/analyze: POST endpoint voor policy analyse
    /api/standards: GET endpoint voor industry standards informatie
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from policy_analyzer import PolicyAnalyzer, PolicyRequirement, calculate_security_score
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_policy():
    """Analyze a password policy"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate and sanitize input
        try:
            min_length = max(1, min(256, int(data.get('min_length', 8))))
            max_length = None
            if data.get('max_length'):
                max_length = max(1, min(1024, int(data.get('max_length'))))
                if max_length < min_length:
                    return jsonify({
                        'success': False,
                        'error': 'Maximum length must be greater than or equal to minimum length'
                    }), 400
            
            min_age_days = max(0, int(data.get('min_age_days', 0)))
            password_history = max(0, min(100, int(data.get('password_history', 0))))
            
            lockout_attempts = None
            if data.get('lockout_attempts'):
                lockout_attempts = max(1, min(1000, int(data.get('lockout_attempts'))))
            
            lockout_duration_minutes = None
            if data.get('lockout_duration_minutes'):
                lockout_duration_minutes = max(1, min(1440, int(data.get('lockout_duration_minutes'))))
            
            max_age_days = None
            if data.get('max_age_days'):
                max_age_days = max(1, min(3650, int(data.get('max_age_days'))))
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'error': f'Invalid input data: {str(e)}'
            }), 400
        
        # Create policy requirement from JSON
        policy = PolicyRequirement(
            min_length=min_length,
            max_length=max_length,
            require_uppercase=bool(data.get('require_uppercase', True)),
            require_lowercase=bool(data.get('require_lowercase', True)),
            require_numbers=bool(data.get('require_numbers', True)),
            require_special_chars=bool(data.get('require_special_chars', True)),
            max_age_days=max_age_days,
            min_age_days=min_age_days,
            password_history=password_history,
            lockout_attempts=lockout_attempts,
            lockout_duration_minutes=lockout_duration_minutes,
            prevent_common_passwords=bool(data.get('prevent_common_passwords', False)),
            prevent_user_info=bool(data.get('prevent_user_info', False)),
            prevent_repeating_chars=bool(data.get('prevent_repeating_chars', False)),
            prevent_sequential_chars=bool(data.get('prevent_sequential_chars', False))
        )
        
        # Get language from request (default to 'nl', validate)
        lang = data.get('lang', 'nl')
        if lang not in ['nl', 'en']:
            lang = 'nl'
        
        # Analyze policy
        analyzer = PolicyAnalyzer(lang=lang)
        findings = analyzer.analyze(policy)
        
        # Calculate security score
        score_data = calculate_security_score(findings, lang=lang)
        
        # Convert findings to dict for JSON response
        findings_dict = []
        for finding in findings:
            findings_dict.append({
                'severity': finding.severity.value,
                'title': finding.title,
                'description': finding.description,
                'recommendation': finding.recommendation,
                'standard': finding.standard,
                'breach_statistics': finding.breach_statistics,
                'impact_score': finding.impact_score
            })
        
        return jsonify({
            'success': True,
            'score': score_data,
            'findings': findings_dict,
            'policy': {
                'min_length': policy.min_length,
                'max_length': policy.max_length,
                'require_uppercase': policy.require_uppercase,
                'require_lowercase': policy.require_lowercase,
                'require_numbers': policy.require_numbers,
                'require_special_chars': policy.require_special_chars,
                'max_age_days': policy.max_age_days,
                'min_age_days': policy.min_age_days,
                'password_history': policy.password_history,
                'lockout_attempts': policy.lockout_attempts,
                'lockout_duration_minutes': policy.lockout_duration_minutes,
                'prevent_common_passwords': policy.prevent_common_passwords,
                'prevent_user_info': policy.prevent_user_info,
                'prevent_repeating_chars': policy.prevent_repeating_chars,
                'prevent_sequential_chars': policy.prevent_sequential_chars
            }
        })
    
    except Exception as e:
        # Log error in production (you might want to add proper logging)
        import traceback
        error_msg = str(e)
        if app.debug:
            error_msg += f"\n{traceback.format_exc()}"
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400

@app.route('/api/standards', methods=['GET'])
def get_standards():
    """Get information about industry standards"""
    lang = request.args.get('lang', 'nl')
    if lang not in ['nl', 'en']:
        lang = 'nl'
    
    if lang == 'nl':
        return jsonify({
            'standards': [
                {
                    'name': 'NIST 800-63B',
                    'description': 'Digital Identity Guidelines - Authentication and Lifecycle Management',
                    'key_points': [
                        'Minimaal 8 karakters (aanbevolen: 12+)',
                        'Geen geforceerde wachtwoordverlopen',
                        'Controle op gecompromitteerde wachtwoorden',
                        'Geen complexity vereisten (lengte boven complexity)',
                        'Maximaal 64+ karakters toestaan voor passphrases'
                    ]
                },
                {
                    'name': 'OWASP',
                    'description': 'OWASP Authentication Cheat Sheet',
                    'key_points': [
                        'Account lockout mechanisme',
                        'Voorkom gebruikersinformatie in wachtwoorden',
                        'Controle op veelvoorkomende wachtwoorden',
                        'Voorkom herhalende en sequentiële karakters'
                    ]
                }
            ]
        })
    else:
        return jsonify({
            'standards': [
                {
                    'name': 'NIST 800-63B',
                    'description': 'Digital Identity Guidelines - Authentication and Lifecycle Management',
                    'key_points': [
                        'Minimum 8 characters (recommended: 12+)',
                        'No forced password expiration',
                        'Check against compromised passwords',
                        'No complexity requirements (length over complexity)',
                        'Allow up to 64+ characters for passphrases'
                    ]
                },
                {
                    'name': 'OWASP',
                    'description': 'OWASP Authentication Cheat Sheet',
                    'key_points': [
                        'Account lockout mechanism',
                        'Prevent user information in passwords',
                        'Check against common passwords',
                        'Prevent repeating and sequential characters'
                    ]
                }
            ]
        })

if __name__ == '__main__':
    import os
    # Only enable debug mode in development
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5500)
