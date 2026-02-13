import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """Applicatie configuratie"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///phishing_simulator.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # Email/SMTP Configuratie (voor legacy SMTP)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
    
    # OAuth2 / Microsoft Graph API Configuratie
    USE_OAUTH2 = os.getenv('USE_OAUTH2', 'false').lower() == 'true'
    AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID', '')
    AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', '')
    AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID', 'common')  # 'common' voor personal accounts
    AZURE_AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
    AZURE_SCOPE = ["https://graph.microsoft.com/Mail.Send"]
    AZURE_REDIRECT_URI = os.getenv('AZURE_REDIRECT_URI', 'http://localhost:5003/auth/callback')
    
    # Base URL voor tracking links
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Flask config
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    @classmethod
    def is_email_configured(cls):
        """Check of email configuratie compleet is"""
        if cls.USE_OAUTH2:
            return bool(cls.AZURE_CLIENT_ID and cls.AZURE_CLIENT_SECRET)
        else:
            return bool(cls.SMTP_USERNAME and cls.SMTP_PASSWORD and cls.SMTP_SERVER)
    
    @classmethod
    def get_email_config(cls):
        """Haal email configuratie op als dictionary"""
        config = {
            'use_oauth2': cls.USE_OAUTH2,
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT,
            'smtp_username': cls.SMTP_USERNAME,
            'smtp_password': '***' if cls.SMTP_PASSWORD else '',
            'smtp_use_tls': cls.SMTP_USE_TLS,
            'smtp_use_ssl': cls.SMTP_USE_SSL,
            'base_url': cls.BASE_URL,
            'configured': cls.is_email_configured()
        }
        
        if cls.USE_OAUTH2:
            config.update({
                'azure_client_id': cls.AZURE_CLIENT_ID,
                'azure_client_secret': '***' if cls.AZURE_CLIENT_SECRET else '',
                'azure_tenant_id': cls.AZURE_TENANT_ID,
                'azure_redirect_uri': cls.AZURE_REDIRECT_URI
            })
        
        return config
