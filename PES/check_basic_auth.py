#!/usr/bin/env python3
"""
Script om te controleren of basic authentication werkt
en alternatieve methoden te proberen
"""

import smtplib
import ssl
from config import Config

print("=" * 70)
print("Outlook SMTP Test - Meerdere Configuraties")
print("=" * 70)
print()

configs_to_try = [
    {
        'name': 'smtp-mail.outlook.com (TLS)',
        'server': 'smtp-mail.outlook.com',
        'port': 587,
        'tls': True,
        'ssl': False
    },
    {
        'name': 'smtp-mail.outlook.com (SSL)',
        'server': 'smtp-mail.outlook.com',
        'port': 465,
        'tls': False,
        'ssl': True
    },
    {
        'name': 'smtp.office365.com (TLS)',
        'server': 'smtp.office365.com',
        'port': 587,
        'tls': True,
        'ssl': False
    },
    {
        'name': 'smtp.office365.com (SSL)',
        'server': 'smtp.office365.com',
        'port': 465,
        'tls': False,
        'ssl': True
    },
]

username = Config.SMTP_USERNAME
password = Config.SMTP_PASSWORD

print(f"Testing with:")
print(f"  Username: {username}")
print(f"  Password: {'*' * len(password)}")
print()

for config in configs_to_try:
    print(f"Testing: {config['name']}")
    print(f"  Server: {config['server']}:{config['port']}")
    
    try:
        if config['ssl']:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(config['server'], config['port'], context=context)
        else:
            server = smtplib.SMTP(config['server'], config['port'])
            if config['tls']:
                server.starttls()
        
        server.login(username, password)
        server.quit()
        
        print(f"  ✅ SUCCESS! Deze configuratie werkt!")
        print()
        print("=" * 70)
        print("Gebruik deze instellingen in je .env bestand:")
        print("=" * 70)
        print(f"SMTP_SERVER={config['server']}")
        print(f"SMTP_PORT={config['port']}")
        print(f"SMTP_USERNAME={username}")
        print(f"SMTP_PASSWORD={password}")
        print(f"SMTP_USE_TLS={'true' if config['tls'] else 'false'}")
        print(f"SMTP_USE_SSL={'true' if config['ssl'] else 'false'}")
        print("=" * 70)
        exit(0)
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"  ❌ Authenticatie fout: {str(e)[:100]}")
    except Exception as e:
        print(f"  ❌ Fout: {str(e)[:100]}")
    
    print()

print("=" * 70)
print("❌ Geen van de configuraties werkt")
print("=" * 70)
print()
print("Het probleem is dat Microsoft basic authentication heeft uitgeschakeld")
print("voor je account.")
print()
print("Oplossingen:")
print("1. Controleer of je basic authentication kunt inschakelen in je account")
print("2. Maak een nieuw App Password aan")
print("3. Contacteer Microsoft support als basic authentication nodig is")
print("=" * 70)
