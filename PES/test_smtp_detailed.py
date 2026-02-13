#!/usr/bin/env python3
"""Gedetailleerde SMTP test met meer informatie"""

import smtplib
import ssl
from config import Config

print("=" * 60)
print("Gedetailleerde SMTP Test")
print("=" * 60)
print()

print("📋 Configuratie:")
print(f"   Server: {Config.SMTP_SERVER}")
print(f"   Port: {Config.SMTP_PORT}")
print(f"   Username: {Config.SMTP_USERNAME}")
print(f"   Password: {Config.SMTP_PASSWORD[:4]}...{Config.SMTP_PASSWORD[-4:] if len(Config.SMTP_PASSWORD) > 8 else '***'}")
print(f"   Password Length: {len(Config.SMTP_PASSWORD)}")
print(f"   TLS: {Config.SMTP_USE_TLS}")
print(f"   SSL: {Config.SMTP_USE_SSL}")
print()

print("🔌 Verbinden met SMTP server...")
print()

try:
    if Config.SMTP_USE_SSL:
        print("   Gebruik SSL verbinding...")
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT, context=context)
        print("   ✅ SSL verbinding succesvol")
    else:
        print("   Gebruik TLS verbinding...")
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        print("   ✅ Verbinding met server succesvol")
        
        if Config.SMTP_USE_TLS:
            print("   Start TLS...")
            server.starttls()
            print("   ✅ TLS gestart")
    
    print()
    print("🔐 Authenticeren...")
    print(f"   Username: {Config.SMTP_USERNAME}")
    print(f"   Password: {'*' * len(Config.SMTP_PASSWORD)}")
    
    server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
    print("   ✅ Authenticatie succesvol!")
    
    server.quit()
    print()
    print("=" * 60)
    print("✅ ALLES WERKT! Je SMTP configuratie is correct.")
    print("=" * 60)
    
except smtplib.SMTPAuthenticationError as e:
    print()
    print("=" * 60)
    print("❌ AUTHENTICATIE FOUT")
    print("=" * 60)
    print()
    print(f"Fout details: {str(e)}")
    print()
    print("💡 Mogelijke oorzaken:")
    print("   1. Het App Password is niet correct gekopieerd")
    print("   2. Het App Password heeft spaties - verwijder deze")
    print("   3. Je moet een nieuw App Password genereren")
    print("   4. Je account heeft mogelijk extra beveiliging")
    print()
    print("🔧 Probeer dit:")
    print("   1. Ga naar: https://account.microsoft.com/security")
    print("   2. Maak een NIEUW App Password aan")
    print("   3. Kopieer het EXACT (zonder spaties)")
    print("   4. Update je .env bestand")
    
except smtplib.SMTPServerDisconnected as e:
    print()
    print("=" * 60)
    print("❌ SERVER VERBINDING VERBROKEN")
    print("=" * 60)
    print()
    print(f"Fout details: {str(e)}")
    print()
    print("💡 Probeer alternatieve instellingen:")
    print("   - Poort 465 met SSL")
    print("   - smtp.office365.com in plaats van smtp-mail.outlook.com")
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ONVERWACHTE FOUT")
    print("=" * 60)
    print()
    print(f"Fout type: {type(e).__name__}")
    print(f"Fout details: {str(e)}")
