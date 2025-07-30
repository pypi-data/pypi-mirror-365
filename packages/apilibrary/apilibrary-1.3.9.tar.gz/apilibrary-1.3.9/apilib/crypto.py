"""Encryption Module for API Keys"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class KeyEncryption:
    """Handle encryption and decryption of API keys."""
    
    def __init__(self, password: str = None):
        """Initialize encryption with a password.
        
        Args:
            password (str, optional): User password for encryption. If None, uses system-based key for backward compatibility.
        """
        if password is None:
            # Fallback to system-based key for backward compatibility
            import getpass
            import platform
            password = f"{getpass.getuser()}_{platform.node()}_apilib"
        
        self.password = password.encode()
        self._fernet = None
    
    def _get_fernet(self) -> Fernet:
        """Get or create Fernet instance."""
        if self._fernet is None:
            # Use a deterministic salt based on password for consistency
            # This ensures the same password always generates the same key
            import hashlib
            salt = hashlib.sha256(self.password + b'apilib_2024').digest()[:16]
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.password))
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string.
        
        Args:
            data (str): The string to encrypt
            
        Returns:
            str: Base64 encoded encrypted data
        """
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string.
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data
            
        Returns:
            str: The decrypted string
        """
        fernet = self._get_fernet()
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()