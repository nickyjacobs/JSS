#!/usr/bin/env python3
"""Direct email test script - test SMTP zonder web interface"""

from email_service import EmailService
from config import Config
from models import Campaign, Recipient
from datetime import datetime

print("=" * 60)
print("Direct Email Test")
print("=" * 60)
print()

# Check configuratie
print("📋 Configuratie:")
print(f"   Server: {Config.SMTP_SERVER}")
print(f"   Port: {Config.SMTP_PORT}")
print(f"   Username: {Config.SMTP_USERNAME}")
print(f"   Password: {'***' if Config.SMTP_PASSWORD else '(leeg)'}")
print(f"   TLS: {Config.SMTP_USE_TLS}")
print(f"   SSL: {Config.SMTP_USE_SSL}")
print()

if not Config.is_email_configured():
    print("❌ Email configuratie is niet compleet!")
    exit(1)

# Maak test campaign en recipient
test_campaign = Campaign(
    name='Test Email',
    subject='Test Email - Phishing Simulator',
    sender_email=Config.SMTP_USERNAME,
    sender_name='Phishing Simulator',
    template_type='generic',
    target_url='',
    created_at=datetime.now()
)

test_recipient = Recipient(
    campaign_id=0,
    email=Config.SMTP_USERNAME,  # Stuur naar jezelf
    name='Test Gebruiker',
    token='test-token'
)

# Test email verzenden
print("📧 Versturen test email naar:", Config.SMTP_USERNAME)
print()

email_service = EmailService()

try:
    email_service.send_email(test_campaign, test_recipient)
    print("✅ Email succesvol verzonden!")
    print("   Check je inbox (en spam folder)")
except Exception as e:
    print("❌ Fout bij verzenden:")
    print(f"   {str(e)}")
    print()
    print("💡 Mogelijke oplossingen:")
    print("   1. Controleer of je App Password correct is")
    print("   2. Controleer of je kunt inloggen op outlook.com")
    print("   3. Probeer een nieuw App Password te genereren")

print()
print("=" * 60)
