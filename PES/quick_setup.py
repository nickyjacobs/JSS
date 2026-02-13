#!/usr/bin/env python3
"""
Quick Setup Helper - Helpt je snel de juiste email provider configuratie te kiezen
"""

import os

PROVIDERS = {
    '1': {
        'name': 'Gmail',
        'server': 'smtp.gmail.com',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'Je moet een App Password gebruiken (niet je normale wachtwoord)'
    },
    '2': {
        'name': 'Outlook / Hotmail / Live.com',
        'server': 'smtp-mail.outlook.com',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'Gebruik je normale wachtwoord'
    },
    '3': {
        'name': 'Yahoo Mail',
        'server': 'smtp.mail.yahoo.com',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'App Password vereist'
    },
    '4': {
        'name': 'iCloud Mail',
        'server': 'smtp.mail.me.com',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'App-specifiek wachtwoord vereist'
    },
    '5': {
        'name': 'Microsoft 365 / Office 365',
        'server': 'smtp.office365.com',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'Gebruik je bedrijfs email en wachtwoord'
    },
    '6': {
        'name': 'Zoho Mail',
        'server': 'smtp.zoho.com',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'Gebruik je Zoho email en wachtwoord'
    },
    '7': {
        'name': 'Custom SMTP Server',
        'server': '',
        'port': '587',
        'tls': True,
        'ssl': False,
        'notes': 'Je moet de server details zelf invullen'
    }
}

def print_header():
    print("\n" + "="*60)
    print("  Phishing Email Simulator - Quick Setup Helper")
    print("="*60 + "\n")

def show_providers():
    print("Kies je email provider:\n")
    for key, provider in PROVIDERS.items():
        print(f"  {key}. {provider['name']}")
        if provider['notes']:
            print(f"     └─ {provider['notes']}")
    print()

def get_provider_choice():
    while True:
        choice = input("Voer het nummer in (1-7): ").strip()
        if choice in PROVIDERS:
            return choice
        print("❌ Ongeldige keuze. Probeer opnieuw.")

def get_custom_server():
    print("\n📧 Custom SMTP Server Configuratie:")
    server = input("SMTP Server adres (bijv. mail.jouwbedrijf.com): ").strip()
    port = input("SMTP Poort (meestal 587 of 465) [587]: ").strip() or '587'
    
    encryption = input("Encryptie type (1=TLS, 2=SSL) [1]: ").strip() or '1'
    use_tls = encryption == '1'
    use_ssl = encryption == '2'
    
    return {
        'server': server,
        'port': port,
        'tls': use_tls,
        'ssl': use_ssl,
        'notes': 'Custom configuratie'
    }

def generate_env_content(provider, email, password, base_url='http://localhost:5000'):
    """Genereer .env bestand inhoud"""
    content = f"""# Database Configuratie
DATABASE_URL=sqlite:///phishing_simulator.db
SECRET_KEY={os.urandom(24).hex()}

# SMTP Email Configuratie - {provider['name']}
SMTP_SERVER={provider['server']}
SMTP_PORT={provider['port']}
SMTP_USERNAME={email}
SMTP_PASSWORD={password}
SMTP_USE_TLS={'true' if provider['tls'] else 'false'}
SMTP_USE_SSL={'true' if provider['ssl'] else 'false'}

# Base URL voor tracking links
BASE_URL={base_url}

# Flask Configuratie
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
"""
    return content

def main():
    print_header()
    
    print("Deze helper maakt het makkelijker om je .env bestand te configureren.\n")
    
    # Check of .env al bestaat
    env_path = '.env'
    if os.path.exists(env_path):
        overwrite = input("⚠️  .env bestand bestaat al. Overschrijven? (j/n) [n]: ").strip().lower()
        if overwrite != 'j':
            print("❌ Geannuleerd. Je .env bestand blijft ongewijzigd.")
            return
    
    # Kies provider
    show_providers()
    choice = get_provider_choice()
    
    if choice == '7':
        provider = get_custom_server()
    else:
        provider = PROVIDERS[choice]
    
    print(f"\n✓ Gekozen: {provider['name']}\n")
    
    # Vraag email gegevens
    email = input(f"📧 Email adres: ").strip()
    if not email:
        print("❌ Email adres is verplicht!")
        return
    
    password = input(f"🔒 Wachtwoord (of App Password): ").strip()
    if not password:
        print("❌ Wachtwoord is verplicht!")
        return
    
    # Base URL (optioneel)
    base_url = input(f"🌐 Base URL [http://localhost:5000]: ").strip() or 'http://localhost:5000'
    
    # Genereer .env content
    env_content = generate_env_content(provider, email, password, base_url)
    
    # Schrijf naar .env
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"\n✅ .env bestand succesvol aangemaakt!")
        print(f"\n📋 Configuratie:")
        print(f"   Provider: {provider['name']}")
        print(f"   Server: {provider['server']}")
        print(f"   Poort: {provider['port']}")
        print(f"   Email: {email}")
        print(f"   Base URL: {base_url}")
        print(f"\n💡 Volgende stappen:")
        print(f"   1. Start de applicatie: python3 app.py")
        print(f"   2. Ga naar: http://localhost:5000")
        print(f"   3. Klik op 'Instellingen' en test je email configuratie")
        print(f"\n⚠️  Let op: {provider['notes']}")
    except Exception as e:
        print(f"\n❌ Fout bij schrijven van .env bestand: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Geannuleerd door gebruiker.")
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
