from models import db, Recipient
from config import Config
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import ssl
from flask import session

# Conditionally import OAuth service
try:
    from oauth_service import OAuthService
    oauth_service = OAuthService() if Config.USE_OAUTH2 else None
except:
    oauth_service = None

class EmailService:
    def __init__(self):
        # Configuratie wordt dynamisch geladen bij elke email
        pass
    
    def _get_config(self):
        """Haal huidige configuratie op (wordt dynamisch geladen)"""
        return {
            'smtp_server': Config.SMTP_SERVER,
            'smtp_port': Config.SMTP_PORT,
            'smtp_username': Config.SMTP_USERNAME,
            'smtp_password': Config.SMTP_PASSWORD,
            'smtp_use_tls': Config.SMTP_USE_TLS,
            'smtp_use_ssl': Config.SMTP_USE_SSL,
            'base_url': Config.BASE_URL
        }
    
    def get_email_template(self, campaign, recipient):
        """Haal de juiste email template op"""
        templates = {
            'password_reset': self._password_reset_template,
            'urgent': self._urgent_template,
            'invoice': self._invoice_template,
            'security_alert': self._security_alert_template,
            'generic': self._generic_template
        }
        
        template_func = templates.get(campaign.template_type, templates['generic'])
        return template_func(campaign, recipient)
    
    def _password_reset_template(self, campaign, recipient):
        """Password reset phishing template"""
        config = self._get_config()
        tracking_url = f"{config['base_url']}/track/{recipient.id}/{recipient.token}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #ffffff; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #007bff; 
                          color: #ffffff; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Wachtwoord Reset Verzoek</h2>
                </div>
                <div class="content">
                    <p>Beste {recipient.name or 'gebruiker'},</p>
                    <p>We hebben een verzoek ontvangen om uw wachtwoord te resetten. Als u dit verzoek heeft gedaan, klik dan op de onderstaande knop:</p>
                    <p style="text-align: center;">
                        <a href="{tracking_url}" class="button">Wachtwoord Resetten</a>
                    </p>
                    <p>Als u dit verzoek niet heeft gedaan, negeer dan deze email. Uw wachtwoord blijft ongewijzigd.</p>
                    <p>Deze link is 24 uur geldig.</p>
                    <p>Met vriendelijke groet,<br>{campaign.sender_name}</p>
                </div>
                <div class="footer">
                    <p>Dit is een automatisch gegenereerde email. Reageer niet op dit bericht.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _urgent_template(self, campaign, recipient):
        """Urgent action required template"""
        config = self._get_config()
        tracking_url = f"{config['base_url']}/track/{recipient.id}/{recipient.token}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #ffffff; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #dc3545; 
                          color: #ffffff; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ Dringende Actie Vereist</h2>
                </div>
                <div class="content">
                    <p>Beste {recipient.name or 'collega'},</p>
                    <p><strong>BELANGRIJK:</strong> Er is ongebruikelijke activiteit gedetecteerd op uw account. 
                    Om de beveiliging te waarborgen, moet u onmiddellijk actie ondernemen.</p>
                    <p style="text-align: center;">
                        <a href="{tracking_url}" class="button">Account Verifiëren</a>
                    </p>
                    <p>Als u geen actie onderneemt binnen 24 uur, kan uw account worden geblokkeerd.</p>
                    <p>Met vriendelijke groet,<br>{campaign.sender_name}<br>IT Beveiliging</p>
                </div>
                <div class="footer">
                    <p>Dit is een automatisch gegenereerde email. Reageer niet op dit bericht.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _invoice_template(self, campaign, recipient):
        """Invoice/payment template"""
        config = self._get_config()
        tracking_url = f"{config['base_url']}/track/{recipient.id}/{recipient.token}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #ffffff; }}
                .invoice-box {{ border: 2px solid #28a745; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #28a745; 
                          color: #ffffff; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Nieuwe Factuur Beschikbaar</h2>
                </div>
                <div class="content">
                    <p>Beste {recipient.name or 'klant'},</p>
                    <p>Er is een nieuwe factuur voor u beschikbaar. Klik op de onderstaande link om de factuur te bekijken en te betalen.</p>
                    <div class="invoice-box">
                        <p><strong>Factuurnummer:</strong> INV-2026-{recipient.id:04d}</p>
                        <p><strong>Bedrag:</strong> € 1.234,56</p>
                        <p><strong>Vervaldatum:</strong> {datetime.now().strftime('%d-%m-%Y')}</p>
                    </div>
                    <p style="text-align: center;">
                        <a href="{tracking_url}" class="button">Factuur Bekijken</a>
                    </p>
                    <p>Met vriendelijke groet,<br>{campaign.sender_name}</p>
                </div>
                <div class="footer">
                    <p>Dit is een automatisch gegenereerde email. Reageer niet op dit bericht.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _security_alert_template(self, campaign, recipient):
        """Security alert template"""
        config = self._get_config()
        tracking_url = f"{config['base_url']}/track/{recipient.id}/{recipient.token}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ffc107; color: #333; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #ffffff; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #ffc107; 
                          color: #333; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔒 Beveiligingswaarschuwing</h2>
                </div>
                <div class="content">
                    <p>Beste {recipient.name or 'gebruiker'},</p>
                    <p>Er is een nieuwe inlogpoging gedetecteerd vanaf een onbekend apparaat:</p>
                    <ul>
                        <li><strong>Locatie:</strong> Amsterdam, Nederland</li>
                        <li><strong>Tijd:</strong> {datetime.now().strftime('%d-%m-%Y %H:%M')}</li>
                        <li><strong>Apparaat:</strong> Windows 10 / Chrome</li>
                    </ul>
                    <p>Als dit u niet was, klik dan direct op de onderstaande link om uw account te beveiligen:</p>
                    <p style="text-align: center;">
                        <a href="{tracking_url}" class="button">Account Beveiligen</a>
                    </p>
                    <p>Met vriendelijke groet,<br>{campaign.sender_name}<br>Beveiligingsteam</p>
                </div>
                <div class="footer">
                    <p>Dit is een automatisch gegenereerde email. Reageer niet op dit bericht.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generic_template(self, campaign, recipient):
        """Generic phishing template"""
        config = self._get_config()
        tracking_url = f"{config['base_url']}/track/{recipient.id}/{recipient.token}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .content {{ padding: 20px; background-color: #ffffff; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #007bff; 
                          color: #ffffff; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <p>Beste {recipient.name or 'gebruiker'},</p>
                    <p>Klik op de onderstaande link voor meer informatie:</p>
                    <p style="text-align: center;">
                        <a href="{tracking_url}" class="button">Klik Hier</a>
                    </p>
                    <p>Met vriendelijke groet,<br>{campaign.sender_name}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_email(self, campaign, recipient):
        """Verstuur een phishing email"""
        config = self._get_config()
        
        if not Config.is_email_configured():
            print(f"[DEMO MODE] Would send email to {recipient.email}")
            print(f"Subject: {campaign.subject}")
            print(f"Template: {campaign.template_type}")
            print(f"Tracking URL: {config['base_url']}/track/{recipient.id}/{recipient.token}")
            # In demo mode markeren we het als verzonden voor testing
            if hasattr(recipient, 'id') and recipient.id:
                recipient.sent_at = datetime.now()
                try:
                    db.session.commit()
                except:
                    pass
            return
        
        # HTML content
        html_content = self.get_email_template(campaign, recipient)
        
        # Gebruik OAuth2 / Microsoft Graph API als ingeschakeld
        if Config.USE_OAUTH2 and oauth_service:
            try:
                # Haal access token op uit session
                access_token = session.get('access_token')
                if not access_token:
                    raise Exception("Geen OAuth2 access token gevonden. Log eerst in via /auth/login")
                
                # Verstuur via Microsoft Graph API
                from_email = campaign.sender_email or Config.SMTP_USERNAME
                oauth_service.send_email_via_graph(
                    access_token=access_token,
                    from_email=from_email,
                    to_email=recipient.email,
                    subject=campaign.subject,
                    html_body=html_content
                )
                
                # Markeer als verzonden
                if hasattr(recipient, 'id') and recipient.id:
                    recipient.sent_at = datetime.now()
                    db.session.commit()
                
                print(f"✓ Email sent via Graph API to {recipient.email}")
                return
            except Exception as e:
                error_msg = f"Graph API fout: {str(e)}"
                print(f"✗ {error_msg}")
                raise Exception(error_msg) from e
        
        # Fallback naar SMTP
        # Maak email bericht
        msg = MIMEMultipart('alternative')
        msg['Subject'] = campaign.subject
        msg['From'] = formataddr((campaign.sender_name, campaign.sender_email))
        msg['To'] = recipient.email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Verstuur email via SMTP
        try:
            if config['smtp_use_ssl']:
                # SSL verbinding
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'], context=context) as server:
                    server.login(config['smtp_username'], config['smtp_password'])
                    server.send_message(msg)
            else:
                # TLS verbinding (meest gebruikelijk)
                with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                    if config['smtp_use_tls']:
                        server.starttls()
                    server.login(config['smtp_username'], config['smtp_password'])
                    server.send_message(msg)
            
            # Markeer als verzonden
            if hasattr(recipient, 'id') and recipient.id:
                recipient.sent_at = datetime.now()
                db.session.commit()
            
            print(f"✓ Email sent to {recipient.email}")
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Authenticatie fout: Controleer je gebruikersnaam en wachtwoord. Voor Gmail gebruik een App Password."
            print(f"✗ {error_msg}")
            raise Exception(error_msg) from e
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Email adres geweigerd: {recipient.email}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg) from e
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"Server verbinding verbroken: Controleer SMTP server en poort instellingen."
            print(f"✗ {error_msg}")
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Fout bij verzenden naar {recipient.email}: {str(e)}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg) from e
