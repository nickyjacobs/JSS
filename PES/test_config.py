#!/usr/bin/env python3
"""Test script om te controleren of de configuratie correct wordt geladen"""

from config import Config

print("=" * 60)
print("Configuratie Test")
print("=" * 60)
print()

print("SMTP Server:", Config.SMTP_SERVER)
print("SMTP Port:", Config.SMTP_PORT)
print("SMTP Username:", Config.SMTP_USERNAME)
print("SMTP Password:", "***" if Config.SMTP_PASSWORD else "(leeg)")
print("SMTP Password Length:", len(Config.SMTP_PASSWORD) if Config.SMTP_PASSWORD else 0)
print("SMTP Use TLS:", Config.SMTP_USE_TLS)
print("SMTP Use SSL:", Config.SMTP_USE_SSL)
print("Base URL:", Config.BASE_URL)
print()

if Config.is_email_configured():
    print("✅ Email configuratie is compleet")
else:
    print("❌ Email configuratie is niet compleet")

print()
print("=" * 60)
