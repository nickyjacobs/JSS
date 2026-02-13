"""OAuth2 service voor Microsoft Graph API"""

from msal import ConfidentialClientApplication
from config import Config
import requests
import json

class OAuthService:
    def __init__(self):
        self.app = ConfidentialClientApplication(
            client_id=Config.AZURE_CLIENT_ID,
            client_credential=Config.AZURE_CLIENT_SECRET,
            authority=Config.AZURE_AUTHORITY
        )
        self.token_cache = {}  # In productie: gebruik database of session storage
    
    def get_auth_url(self, state=None):
        """Genereer authorization URL voor OAuth2 flow"""
        auth_url = self.app.get_authorization_request_url(
            scopes=Config.AZURE_SCOPE,
            redirect_uri=Config.AZURE_REDIRECT_URI,
            state=state
        )
        return auth_url
    
    def acquire_token_by_authorization_code(self, code):
        """Verkrijg access token via authorization code"""
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=Config.AZURE_SCOPE,
            redirect_uri=Config.AZURE_REDIRECT_URI
        )
        
        if "access_token" in result:
            return result["access_token"]
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise Exception(f"Token acquisition failed: {error}")
    
    def get_token_for_user(self, user_email):
        """Haal token op voor gebruiker (uit cache of refresh)"""
        if user_email in self.token_cache:
            token_data = self.token_cache[user_email]
            # Check if token is still valid (simplified - in production check expiry)
            return token_data.get('access_token')
        return None
    
    def store_token(self, user_email, access_token):
        """Sla token op voor gebruiker"""
        self.token_cache[user_email] = {
            'access_token': access_token,
            'user_email': user_email
        }
    
    def send_email_via_graph(self, access_token, from_email, to_email, subject, html_body):
        """Verstuur email via Microsoft Graph API"""
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=message)
        
        if response.status_code == 202:
            return True
        elif response.status_code == 401:
            error_msg = "OAuth2 token verlopen of ongeldig. Log opnieuw in via /auth/login"
            raise Exception(error_msg)
        else:
            error_msg = f"Graph API error: {response.status_code} - {response.text}"
            raise Exception(error_msg)
