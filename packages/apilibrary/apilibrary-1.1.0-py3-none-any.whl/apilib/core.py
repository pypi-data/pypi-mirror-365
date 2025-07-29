"""Core API Key Manager"""

from typing import List, Tuple
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
    
    def list_all_providers(self) -> List[str]:
        """Get list of all providers with stored keys.
        
        Returns:
            List[str]: List of provider names
        """
        providers = self.storage.list_providers()
        return [p.title() for p in providers]