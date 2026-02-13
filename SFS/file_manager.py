"""
Core file management functionality for Secure File Sharing System
"""
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from cryptography.fernet import Fernet

from config import (
    UPLOAD_DIR, METADATA_DIR, ENCRYPTION_KEY_FILE,
    TOKEN_LENGTH, DEFAULT_EXPIRY_HOURS, MAX_FILE_SIZE
)


class FileManager:
    """Manages file uploads, encryption, and sharing"""
    
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.metadata_dir = METADATA_DIR
        
        # Load or generate encryption key
        if ENCRYPTION_KEY_FILE.exists():
            self.encryption_key = ENCRYPTION_KEY_FILE.read_bytes()
        else:
            self.encryption_key = Fernet.generate_key()
            ENCRYPTION_KEY_FILE.write_bytes(self.encryption_key)
        
        self.cipher = Fernet(self.encryption_key)
    
    def generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(TOKEN_LENGTH)
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def encrypt_file(self, file_path: Path) -> bytes:
        """Encrypt a file"""
        with open(file_path, "rb") as f:
            file_data = f.read()
        return self.cipher.encrypt(file_data)
    
    def decrypt_file(self, encrypted_data: bytes) -> bytes:
        """Decrypt file data"""
        return self.cipher.decrypt(encrypted_data)
    
    def save_file(self, file_data: bytes, filename: str, password: Optional[str] = None,
                  expiry_hours: int = DEFAULT_EXPIRY_HOURS) -> Dict:
        """Save an uploaded file and return sharing info"""
        
        # Generate unique token
        token = self.generate_token()
        
        # Calculate file hash
        temp_file = self.upload_dir / f"temp_{token}"
        temp_file.write_bytes(file_data)
        file_hash = self.calculate_file_hash(temp_file)
        
        # Encrypt file
        encrypted_data = self.encrypt_file(temp_file)
        
        # Save encrypted file
        encrypted_file = self.upload_dir / f"{token}.enc"
        encrypted_file.write_bytes(encrypted_data)
        
        # Remove temp file
        temp_file.unlink()
        
        # Create metadata
        expiry_time = datetime.now() + timedelta(hours=expiry_hours)
        metadata = {
            "token": token,
            "filename": filename,
            "file_hash": file_hash,
            "file_size": len(file_data),
            "upload_time": datetime.now().isoformat(),
            "expiry_time": expiry_time.isoformat(),
            "password_protected": password is not None,
            "password_hash": self._hash_password(password) if password else None,
            "download_count": 0,
            "max_downloads": None  # None = unlimited
        }
        
        # Save metadata
        metadata_file = self.metadata_dir / f"{token}.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        return {
            "token": token,
            "filename": filename,
            "expiry_time": expiry_time.isoformat(),
            "download_url": f"/download/{token}"
        }
    
    def get_file_info(self, token: str) -> Optional[Dict]:
        """Get file metadata by token"""
        metadata_file = self.metadata_dir / f"{token}.json"
        if not metadata_file.exists():
            return None
        
        metadata = json.loads(metadata_file.read_text())
        
        # Check if expired
        expiry_time = datetime.fromisoformat(metadata["expiry_time"])
        if datetime.now() > expiry_time:
            return None
        
        return metadata
    
    def verify_password(self, token: str, password: str) -> bool:
        """Verify password for a protected file"""
        metadata = self.get_file_info(token)
        if not metadata or not metadata.get("password_protected"):
            return False
        
        password_hash = metadata.get("password_hash")
        return password_hash == self._hash_password(password)
    
    def download_file(self, token: str, password: Optional[str] = None) -> Optional[bytes]:
        """Download and decrypt a file"""
        metadata = self.get_file_info(token)
        if not metadata:
            return None
        
        # Check password if required
        if metadata.get("password_protected"):
            if not password or not self.verify_password(token, password):
                return None
        
        # Read encrypted file
        encrypted_file = self.upload_dir / f"{token}.enc"
        if not encrypted_file.exists():
            return None
        
        encrypted_data = encrypted_file.read_bytes()
        
        # Decrypt file
        try:
            file_data = self.decrypt_file(encrypted_data)
        except Exception:
            return None
        
        # Update download count
        metadata["download_count"] = metadata.get("download_count", 0) + 1
        metadata_file = self.metadata_dir / f"{token}.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        return file_data
    
    def delete_file(self, token: str) -> bool:
        """Delete a file and its metadata"""
        encrypted_file = self.upload_dir / f"{token}.enc"
        metadata_file = self.metadata_dir / f"{token}.json"
        
        deleted = False
        if encrypted_file.exists():
            encrypted_file.unlink()
            deleted = True
        if metadata_file.exists():
            metadata_file.unlink()
            deleted = True
        
        return deleted
    
    def list_files(self) -> List[Dict]:
        """List all active files"""
        files = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                metadata = json.loads(metadata_file.read_text())
                expiry_time = datetime.fromisoformat(metadata["expiry_time"])
                if datetime.now() <= expiry_time:
                    files.append({
                        "token": metadata["token"],
                        "filename": metadata["filename"],
                        "file_size": metadata["file_size"],
                        "upload_time": metadata["upload_time"],
                        "expiry_time": metadata["expiry_time"],
                        "download_count": metadata.get("download_count", 0),
                        "password_protected": metadata.get("password_protected", False)
                    })
            except Exception:
                continue
        
        return sorted(files, key=lambda x: x["upload_time"], reverse=True)
    
    def cleanup_expired(self) -> int:
        """Remove expired files and return count of deleted files"""
        deleted_count = 0
        now = datetime.now()
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                metadata = json.loads(metadata_file.read_text())
                expiry_time = datetime.fromisoformat(metadata["expiry_time"])
                
                if now > expiry_time:
                    token = metadata["token"]
                    if self.delete_file(token):
                        deleted_count += 1
            except Exception:
                continue
        
        return deleted_count
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return hashlib.sha256(password.encode()).hexdigest()
