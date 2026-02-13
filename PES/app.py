from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from models import db, Campaign, Recipient, Click
from email_service import EmailService
from oauth_service import OAuthService
from config import Config
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = Config.SECRET_KEY

db.init_app(app)

# Initialize services
email_service = EmailService()
oauth_service = OAuthService() if Config.USE_OAUTH2 else None

@app.route('/')
def index():
    """Hoofdpagina met overzicht van campaigns"""
    campaigns = Campaign.query.all()
    return render_template('index.html', campaigns=campaigns)

@app.route('/campaign/new', methods=['GET', 'POST'])
def new_campaign():
    """Nieuwe campaign aanmaken"""
    if request.method == 'POST':
        data = request.form
        
        campaign = Campaign(
            name=data['name'],
            subject=data['subject'],
            sender_email=data['sender_email'],
            sender_name=data['sender_name'],
            template_type=data['template_type'],
            target_url=data.get('target_url', ''),
            created_at=datetime.now()
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # Recipients toevoegen
        recipients = [email.strip() for email in data['recipients'].split('\n') if email.strip()]
        for email in recipients:
            recipient = Recipient(
                campaign_id=campaign.id,
                email=email,
                name=email.split('@')[0]
            )
            db.session.add(recipient)
        
        db.session.commit()
        
        return redirect(url_for('campaign_detail', campaign_id=campaign.id))
    
    return render_template('new_campaign.html')

@app.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    """Campaign details en resultaten"""
    campaign = Campaign.query.get_or_404(campaign_id)
    recipients = Recipient.query.filter_by(campaign_id=campaign_id).all()
    clicks = Click.query.join(Recipient).filter(Recipient.campaign_id == campaign_id).all()
    
    stats = {
        'total_recipients': len(recipients),
        'total_clicks': len(clicks),
        'unique_clicks': len(set(c.email for c in clicks)),
        'click_rate': (len(set(c.email for c in clicks)) / len(recipients) * 100) if recipients else 0
    }
    
    email_config = Config.get_email_config()
    
    return render_template('campaign_detail.html', campaign=campaign, recipients=recipients, clicks=clicks, stats=stats, config=email_config)

@app.route('/campaign/<int:campaign_id>/send', methods=['POST'])
def send_campaign(campaign_id):
    """Emails versturen voor een campaign"""
    campaign = Campaign.query.get_or_404(campaign_id)
    recipients = Recipient.query.filter_by(campaign_id=campaign_id).all()
    
    if not Config.is_email_configured():
        return jsonify({
            'success': False,
            'error': 'Email configuratie niet compleet. Ga naar Instellingen om email te configureren.',
            'sent': 0,
            'total': len(recipients)
        }), 400
    
    sent_count = 0
    errors = []
    
    for recipient in recipients:
        try:
            email_service.send_email(campaign, recipient)
            sent_count += 1
        except Exception as e:
            error_msg = f"{recipient.email}: {str(e)}"
            errors.append(error_msg)
            print(f"Error sending to {recipient.email}: {e}")
    
    response = {
        'success': True,
        'sent': sent_count,
        'total': len(recipients),
        'errors': errors[:5]  # Max 5 errors
    }
    
    if errors:
        response['warning'] = f"{len(errors)} email(s) konden niet worden verzonden"
    
    return jsonify(response)

@app.route('/track/<int:recipient_id>/<token>')
def track_click(recipient_id, token):
    """Track wanneer iemand op een link klikt"""
    recipient = Recipient.query.get_or_404(recipient_id)
    
    # Verifieer token
    if recipient.token != token:
        return "Invalid link", 404
    
    # Check of deze click al bestaat
    existing_click = Click.query.filter_by(
        recipient_id=recipient_id,
        clicked_at=datetime.now().date()
    ).first()
    
    if not existing_click:
        click = Click(
            recipient_id=recipient_id,
            clicked_at=datetime.now(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(click)
        db.session.commit()
    
    # Redirect naar target URL of landing page
    campaign = recipient.campaign
    if campaign.target_url:
        return redirect(campaign.target_url)
    else:
        return render_template('landing_page.html', campaign=campaign)

@app.route('/api/stats/<int:campaign_id>')
def api_stats(campaign_id):
    """API endpoint voor real-time statistieken"""
    campaign = Campaign.query.get_or_404(campaign_id)
    recipients = Recipient.query.filter_by(campaign_id=campaign_id).all()
    clicks = Click.query.join(Recipient).filter(Recipient.campaign_id == campaign_id).all()
    
    return jsonify({
        'total_recipients': len(recipients),
        'total_clicks': len(clicks),
        'unique_clicks': len(set(c.email for c in clicks)),
        'click_rate': round((len(set(c.email for c in clicks)) / len(recipients) * 100) if recipients else 0, 2)
    })

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Email configuratie pagina"""
    if request.method == 'POST':
        data = request.form
        
        # Update configuratie (in productie zou je dit in een database opslaan)
        # Voor nu gebruiken we environment variables
        config_updates = {
            'SMTP_SERVER': data.get('smtp_server', ''),
            'SMTP_PORT': data.get('smtp_port', '587'),
            'SMTP_USERNAME': data.get('smtp_username', ''),
            'SMTP_PASSWORD': data.get('smtp_password', ''),
            'SMTP_USE_TLS': 'true' if data.get('smtp_use_tls') == 'on' else 'false',
            'SMTP_USE_SSL': 'true' if data.get('smtp_use_ssl') == 'on' else 'false',
            'BASE_URL': data.get('base_url', 'http://localhost:5000')
        }
        
        # Note: In productie zou je deze waarden opslaan in een database of config file
        # Voor nu moeten gebruikers de .env file aanpassen
        flash('Configuratie opgeslagen! Let op: je moet de applicatie herstarten of de .env file aanpassen voor permanente wijzigingen.', 'info')
        return redirect(url_for('settings'))
    
    email_config = Config.get_email_config()
    return render_template('settings.html', config=email_config)

@app.route('/auth/login')
def auth_login():
    """Start OAuth2 login flow"""
    if not Config.USE_OAUTH2:
        return jsonify({'error': 'OAuth2 niet ingeschakeld'}), 400
    
    auth_url = oauth_service.get_auth_url(state='test')
    return redirect(auth_url)

@app.route('/auth/callback')
def auth_callback():
    """OAuth2 callback handler"""
    if not Config.USE_OAUTH2:
        return jsonify({'error': 'OAuth2 niet ingeschakeld'}), 400
    
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"OAuth error: {error}", 400
    
    if not code:
        return "Geen authorization code ontvangen", 400
    
    try:
        access_token = oauth_service.acquire_token_by_authorization_code(code)
        # Sla token op in session (in productie: database)
        session['access_token'] = access_token
        session['oauth_authenticated'] = True
        
        flash('OAuth2 authenticatie succesvol! Je kunt nu emails versturen.', 'success')
        return redirect(url_for('settings'))
    except Exception as e:
        flash(f'OAuth2 authenticatie mislukt: {str(e)}', 'error')
        return redirect(url_for('settings'))

@app.route('/settings/test-email', methods=['POST'])
def test_email():
    """Test email verzenden"""
    data = request.json
    test_email_address = data.get('email', '')
    
    if not test_email_address:
        return jsonify({'success': False, 'error': 'Geen email adres opgegeven'}), 400
    
    if not Config.is_email_configured():
        return jsonify({'success': False, 'error': 'Email configuratie niet compleet'}), 400
    
    try:
        # Maak een test campaign en recipient
        from models import Campaign, Recipient
        test_campaign = Campaign(
            name='Test Email',
            subject='Test Email - Phishing Simulator',
            sender_email=Config.SMTP_USERNAME if not Config.USE_OAUTH2 else session.get('user_email', ''),
            sender_name='Phishing Simulator',
            template_type='generic',
            target_url='',
            created_at=datetime.now()
        )
        
        test_recipient = Recipient(
            campaign_id=0,  # Temporary
            email=test_email_address,
            name='Test Gebruiker',
            token='test-token'
        )
        
        # Verstuur test email
        email_service.send_email(test_campaign, test_recipient)
        
        return jsonify({
            'success': True,
            'message': f'Test email verzonden naar {test_email_address}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fout bij verzenden: {str(e)}'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
