"""Storage Module for API Keys"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from .crypto import KeyEncryption

class KeyStorage:
    """Handle storage and retrieval of encrypted API keys."""
    
    def __init__(self):
        """Initialize storage with default location."""
        self.storage_dir = Path.home() / '.apilib'
        self.storage_file = self.storage_dir / 'keys.json'
        self.encryption = KeyEncryption()
        
        # Ensure storage directory exists
        self.storage_dir.mkdir(exist_ok=True)
    
    def _load_data(self) -> Dict:
        """Load data from storage file.
        
        Returns:
            Dict: The stored data or empty dict if file doesn't exist
        """
        if not self.storage_file.exists():
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_data(self, data: Dict) -> None:
        """Save data to storage file.
        
        Args:
            data (Dict): The data to save
        """
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def store_key(self, provider: str, api_key: str) -> bool:
        """Store an encrypted API key.
        
        Args:
            provider (str): The API provider name
            api_key (str): The API key to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = self._load_data()
            
            # Initialize provider list if it doesn't exist
            if provider not in data:
                data[provider] = []
            
            # Encrypt the API key
            encrypted_key = self.encryption.encrypt(api_key)
            
            # Check if key already exists (compare decrypted values)
            for existing_encrypted_key in data[provider]:
                try:
                    existing_key = self.encryption.decrypt(existing_encrypted_key)
                    if existing_key == api_key:
                        return False  # Key already exists
                except:
                    continue  # Skip corrupted entries
            
            # Add the new encrypted key
            data[provider].append(encrypted_key)
            
            # Save the updated data
            self._save_data(data)
            return True
            
        except Exception as e:
            print(f"Error storing key: {e}")
            return False
    
    def get_keys(self, provider: str) -> List[str]:
        """Retrieve all API keys for a provider.
        
        Args:
            provider (str): The API provider name
            
        Returns:
            List[str]: List of decrypted API keys
        """
        try:
            data = self._load_data()
            
            if provider not in data:
                return []
            
            decrypted_keys = []
            for encrypted_key in data[provider]:
                try:
                    decrypted_key = self.encryption.decrypt(encrypted_key)
                    decrypted_keys.append(decrypted_key)
                except:
                    continue  # Skip corrupted entries
            
            return decrypted_keys
            
        except Exception as e:
            print(f"Error retrieving keys: {e}")
            return []
    
    def list_providers(self) -> List[str]:
        """Get list of all providers with stored keys.
        
        Returns:
            List[str]: List of provider names
        """
        try:
            data = self._load_data()
            return [provider for provider, keys in data.items() if keys]
        except:
            return []
    
    def delete_key(self, provider: str, key_index: int) -> bool:
        """Delete a specific API key by index.
        
        Args:
            provider (str): The API provider name
            key_index (int): The index of the key to delete (1-based)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = self._load_data()
            
            if provider not in data or not data[provider]:
                return False
            
            # Convert to 0-based index
            index = key_index - 1
            
            if index < 0 or index >= len(data[provider]):
                return False
            
            # Remove the key at the specified index
            data[provider].pop(index)
            
            # Remove provider if no keys left
            if not data[provider]:
                del data[provider]
            
            self._save_data(data)
            return True
            
        except Exception as e:
            print(f"Error deleting key: {e}")
            return False
    
    def get_all_keys(self) -> Dict[str, List[str]]:
        """Retrieve all API keys for all providers.
        
        Returns:
            Dict[str, List[str]]: Dictionary with provider names as keys and lists of decrypted API keys as values
        """
        try:
            data = self._load_data()
            all_keys = {}
            
            for provider, encrypted_keys in data.items():
                decrypted_keys = []
                for encrypted_key in encrypted_keys:
                    try:
                        decrypted_key = self.encryption.decrypt(encrypted_key)
                        decrypted_keys.append(decrypted_key)
                    except:
                        continue  # Skip corrupted entries
                
                if decrypted_keys:  # Only include providers with valid keys
                    all_keys[provider] = decrypted_keys
            
            return all_keys
            
        except Exception as e:
            print(f"Error retrieving all keys: {e}")
            return {}
    
    def delete_provider_keys(self, provider: str) -> bool:
        """Delete all keys for a provider.
        
        Args:
            provider (str): The API provider name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = self._load_data()
            
            if provider in data:
                del data[provider]
                self._save_data(data)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting provider keys: {e}")
            return False