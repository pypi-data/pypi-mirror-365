"""Core API Key Manager"""

from typing import Dict, List, Tuple
from .storage import KeyStorage

class APIKeyManager:
    """Main class for managing API keys."""
    
    def __init__(self):
        """Initialize the API Key Manager."""
        self.storage = KeyStorage()
    
    def store_key(self, api_key: str, provider: str) -> Tuple[bool, str]:
        """Store an API key for a specified provider.
        
        Args:
            api_key (str): The API key to store
            provider (str): The provider name
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Normalize provider name
        provider = provider.lower().strip()
        
        # Store the key
        success = self.storage.store_key(provider, api_key)
        
        if success:
            return True, f"API key successfully stored for {provider.title()}"
        else:
            return False, "API key already exists or failed to store"
    
    def fetch_keys(self, provider: str) -> Tuple[bool, List[str], str]:
        """Fetch all API keys for a provider.
        
        Args:
            provider (str): The provider name (case-insensitive)
            
        Returns:
            Tuple[bool, List[str], str]: (Success status, Keys list, Message)
        """
        # Normalize provider name
        provider = provider.lower().strip()
        
        # Get keys
        keys = self.storage.get_keys(provider)
        
        if not keys:
            available_providers = self.storage.list_providers()
            if available_providers:
                providers_list = ", ".join([p.title() for p in available_providers])
                message = f"No keys found for '{provider}'. Available providers: {providers_list}"
            else:
                message = "No API keys stored yet. Use 'storekey' to add some keys first."
            return False, [], message
        
        return True, keys, f"Found {len(keys)} key(s) for {provider.title()}"
    
    def delete_key(self, provider: str, key_index: int) -> Tuple[bool, str]:
        """Delete a specific API key by index.
        
        Args:
            provider (str): The provider name
            key_index (int): The index of the key to delete (1-based)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Normalize provider name
        provider = provider.lower().strip()
        
        # Validate key index
        if key_index < 1:
            return False, "Key index must be 1 or greater"
        
        # Check if provider exists and has keys
        keys = self.storage.get_keys(provider)
        if not keys:
            return False, f"No keys found for '{provider}'"
        
        if key_index > len(keys):
            return False, f"Key index {key_index} not found. {provider.title()} has only {len(keys)} key(s)"
        
        # Delete the key
        success = self.storage.delete_key(provider, key_index)
        
        if success:
            return True, f"Key #{key_index} successfully deleted for {provider.title()}"
        else:
            return False, "Failed to delete key"
    
    def fetch_all_keys(self) -> Tuple[bool, Dict[str, List[str]], str]:
        """Fetch all API keys for all providers.
        
        Returns:
            Tuple[bool, Dict[str, List[str]], str]: (Success status, All keys dict, Message)
        """
        all_keys = self.storage.get_all_keys()
        
        if not all_keys:
            return False, {}, "No API keys stored yet. Use 'storekey' to add some keys first."
        
        total_keys = sum(len(keys) for keys in all_keys.values())
        return True, all_keys, f"Found {total_keys} key(s) across {len(all_keys)} provider(s)"
    
    def list_all_providers(self) -> List[str]:
        """Get list of all providers with stored keys.
        
        Returns:
            List[str]: List of provider names
        """
        providers = self.storage.list_providers()
        return [p.title() for p in providers]