"""Command Line Interface for API Library"""

import sys
import click
from .core import APIKeyManager

def store_key_command():
    """Entry point for storekey command."""
    if len(sys.argv) < 3:
        click.echo("Usage: storekey <provider_name> <api_key>")
        click.echo("Example: storekey openai \"sk-1234567890abcdef\"")
        sys.exit(1)
    
    provider = sys.argv[1]
    api_key = sys.argv[2]
    
    if not provider or provider.strip() == "":
        click.echo("Error: Provider name cannot be empty")
        sys.exit(1)
        
    if not api_key or api_key.strip() == "":
        click.echo("Error: API key cannot be empty")
        sys.exit(1)
    
    manager = APIKeyManager()
    success, message = manager.store_key(api_key, provider)
    
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def fetch_key_command():
    """Entry point for fetchkey command."""
    if len(sys.argv) < 2:
        click.echo("Usage: fetchkey <provider_name>")
        click.echo("Example: fetchkey openai")
        
        # Show available providers if any exist
        manager = APIKeyManager()
        providers = manager.list_all_providers()
        if providers:
            click.echo(f"\nAvailable providers: {', '.join(providers)}")
        else:
            click.echo("\nNo API keys stored yet. Use 'storekey' to add some keys first.")
        sys.exit(1)
    
    provider = sys.argv[1]
    
    if not provider or provider.strip() == "":
        click.echo("Error: Provider name cannot be empty")
        sys.exit(1)
    
    manager = APIKeyManager()
    success, keys, message = manager.fetch_keys(provider)
    
    if success:
        click.echo(f"\n🔑 {message}:")
        click.echo("-" * 50)
        for i, key in enumerate(keys, 1):
            # Return the exact unencrypted API key
            click.echo(f"{i}. {key}")
        click.echo("-" * 50)
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def delete_key_command():
    """Entry point for deletekey command."""
    if len(sys.argv) < 3:
        click.echo("Usage: deletekey <provider_name> <key_index>")
        click.echo("Example: deletekey openai 1")
        click.echo("\nNote: key_index is the number shown when using 'fetchkey <provider>'")
        sys.exit(1)
    
    provider = sys.argv[1]
    
    try:
        key_index = int(sys.argv[2])
    except ValueError:
        click.echo("Error: Key index must be a number")
        click.echo("Example: deletekey openai 1")
        sys.exit(1)
    
    if not provider or provider.strip() == "":
        click.echo("Error: Provider name cannot be empty")
        sys.exit(1)
    
    manager = APIKeyManager()
    success, message = manager.delete_key(provider, key_index)
    
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def fetch_all_keys_command():
    """Entry point for fetchallkeys command."""
    manager = APIKeyManager()
    success, all_keys, message = manager.fetch_all_keys()
    
    if success:
        click.echo(f"\n🔑 {message}:")
        click.echo("=" * 60)
        
        for provider, keys in all_keys.items():
            click.echo(f"\n📁 {provider.title()}:")
            click.echo("-" * 40)
            for i, key in enumerate(keys, 1):
                click.echo(f"  {i}. {key}")
        
        click.echo("=" * 60)
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

if __name__ == "__main__":
    # This allows testing the commands directly
    if len(sys.argv) > 1 and sys.argv[1] == "store":
        store_key_command()
    elif len(sys.argv) > 1 and sys.argv[1] == "fetch":
        fetch_key_command()
    elif len(sys.argv) > 1 and sys.argv[1] == "delete":
        delete_key_command()
    elif len(sys.argv) > 1 and sys.argv[1] == "fetchall":
        fetch_all_keys_command()
    else:
        click.echo("Available commands: store, fetch, delete, fetchall")