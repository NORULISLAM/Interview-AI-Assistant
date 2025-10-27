"""
Security and privacy service for data protection
"""
import os
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
from passlib.context import CryptContext

from app.core.config import settings


class SecurityService:
    """Security service for encryption, hashing, and privacy protection"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_string = settings.ENCRYPTION_KEY
        
        # Convert string key to bytes using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'resume_encryption_salt',  # In production, use random salt per user
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_string.encode()))
        return key
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return encrypted_data
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.JWTError as e:
            print(f"JWT error: {e}")
            return None
    
    def generate_file_hash(self, file_content: bytes) -> str:
        """Generate SHA256 hash for file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]
    
    def sanitize_user_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Limit length
        return text[:1000]
    
    def redact_pii(self, text: str) -> str:
        """Redact personally identifiable information"""
        import re
        
        # Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Phone numbers
        text = re.sub(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', '[PHONE]', text)
        
        # SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        # Credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
        
        return text
    
    def create_audit_log(self, user_id: int, event_type: str, event_data: Dict[str, Any], 
                        ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Create audit log entry"""
        return {
            "user_id": user_id,
            "event_type": event_type,
            "event_data": self.redact_pii(json.dumps(event_data)),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "retention_until": datetime.utcnow() + timedelta(hours=settings.AUTO_DELETE_HOURS)
        }
    
    def validate_file_upload(self, file_content: bytes, filename: str, max_size: int = None) -> Dict[str, Any]:
        """Validate file upload for security"""
        if max_size is None:
            max_size = settings.MAX_FILE_SIZE
        
        # Check file size
        if len(file_content) > max_size:
            return {"valid": False, "error": f"File size exceeds {max_size} bytes"}
        
        # Check file extension
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            return {"valid": False, "error": f"File type {file_ext} not allowed"}
        
        # Check for suspicious content (basic check)
        suspicious_patterns = [b'<script', b'javascript:', b'vbscript:', b'onload=']
        for pattern in suspicious_patterns:
            if pattern in file_content.lower():
                return {"valid": False, "error": "File contains suspicious content"}
        
        # Generate file hash
        file_hash = self.generate_file_hash(file_content)
        
        return {
            "valid": True,
            "file_hash": file_hash,
            "file_size": len(file_content),
            "sanitized_filename": self.sanitize_user_input(filename)
        }
    
    def encrypt_file_content(self, file_content: bytes) -> bytes:
        """Encrypt file content"""
        try:
            encrypted_content = self.cipher.encrypt(file_content)
            return encrypted_content
        except Exception as e:
            print(f"Error encrypting file content: {e}")
            return file_content
    
    def decrypt_file_content(self, encrypted_content: bytes) -> bytes:
        """Decrypt file content"""
        try:
            decrypted_content = self.cipher.decrypt(encrypted_content)
            return decrypted_content
        except Exception as e:
            print(f"Error decrypting file content: {e}")
            return encrypted_content
    
    def create_data_retention_policy(self, user_id: int, retention_hours: int) -> Dict[str, Any]:
        """Create data retention policy for user"""
        return {
            "user_id": user_id,
            "retention_hours": retention_hours,
            "auto_delete_enabled": True,
            "created_at": datetime.utcnow(),
            "policy_hash": self.generate_file_hash(
                f"{user_id}_{retention_hours}_{datetime.utcnow().isoformat()}".encode()
            )
        }
    
    def should_delete_data(self, created_at: datetime, retention_hours: int) -> bool:
        """Check if data should be deleted based on retention policy"""
        if retention_hours <= 0:
            return False  # Never delete
        
        expiry_time = created_at + timedelta(hours=retention_hours)
        return datetime.utcnow() > expiry_time
