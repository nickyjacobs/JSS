from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets

db = SQLAlchemy()

class Campaign(db.Model):
    """Phishing campaign model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    sender_email = db.Column(db.String(200), nullable=False)
    sender_name = db.Column(db.String(200), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # 'password_reset', 'urgent', 'invoice', etc.
    target_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    recipients = db.relationship('Recipient', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Campaign {self.name}>'

class Recipient(db.Model):
    """Email recipient model"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200))
    token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    sent_at = db.Column(db.DateTime)
    
    clicks = db.relationship('Click', backref='recipient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Recipient {self.email}>'

class Click(db.Model):
    """Click tracking model"""
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), nullable=False)
    clicked_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Click {self.recipient.email} at {self.clicked_at}>'
