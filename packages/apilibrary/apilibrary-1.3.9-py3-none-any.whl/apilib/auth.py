"""Authentication Module for Password Management"""

import os
import json
import hashlib
import getpass
from pathlib import Path
from typing import Optional, Tuple

class PasswordManager:
    """Handle user password authentication and management."""
    
    def __init__(self):
        """Initialize password manager."""
        self.config_dir = Path.home() / '.apilib'
        self.config_file = self.config_dir / 'config.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> dict:
        """Load configuration from file.
        
        Returns:
            dict: Configuration data
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_config(self, config: dict) -> None:
        """Save configuration to file.
        
        Args:
            config (dict): Configuration data to save
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Salted and hashed password
        """
        # Use a deterministic salt based on username for consistency
        import getpass
        salt = f"apilib_{getpass.getuser()}_salt_2024"
        salted_password = salt + password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest()
    
    def is_first_time_user(self) -> bool:
        """Check if this is the first time the user is using the library.
        
        Returns:
            bool: True if first time user, False otherwise
        """
        config = self._load_config()
        return 'password_hash' not in config
    
    def setup_password(self) -> Tuple[bool, str]:
        """Setup password for first-time users.
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if not self.is_first_time_user():
            return False, "Password already exists. Use authenticate() instead."
        
        print("\n🔐 Welcome to API Library! This is your first time using the library.")
        print("For security, you need to create a master password.")
        print("This password will be required every time you fetch API keys.\n")
        
        while True:
            password = getpass.getpass("Create a master password: ")
            
            if len(password) < 6:
                print("❌ Password must be at least 6 characters long. Please try again.\n")
                continue
            
            confirm_password = getpass.getpass("Confirm your password: ")
            
            if password != confirm_password:
                print("❌ Passwords don't match. Please try again.\n")
                continue
            
            # Save hashed password
            config = self._load_config()
            config['password_hash'] = self._hash_password(password)
            config['setup_complete'] = True
            
            try:
                self._save_config(config)
                print("\n✅ Master password created successfully!")
                print("Remember this password - you'll need it to fetch your API keys.\n")
                return True, "Password setup completed successfully"
            except Exception as e:
                return False, f"Failed to save password: {e}"
    
    def authenticate(self, password: Optional[str] = None) -> Tuple[bool, str]:
        """Authenticate user with password.
        
        Args:
            password (str, optional): Password to authenticate. If None, prompts user.
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if self.is_first_time_user():
            return self.setup_password()
        
        config = self._load_config()
        stored_hash = config.get('password_hash')
        
        if not stored_hash:
            return False, "No password found. Please run setup first."
        
        if password is None:
            password = getpass.getpass("Enter your master password: ")
        
        if self._hash_password(password) == stored_hash:
            return True, "Authentication successful"
        else:
            return False, "Incorrect password"
    
    def get_password_for_encryption(self) -> Optional[str]:
        """Get the user's password for encryption purposes.
        
        Returns:
            Optional[str]: The password if authenticated, None otherwise
        """
        if self.is_first_time_user():
            success, _ = self.setup_password()
            if not success:
                return None
        
        password = getpass.getpass("Enter your master password: ")
        success, _ = self.authenticate(password)
        
        if success:
            return password
        else:
            print("❌ Authentication failed.")
            return None