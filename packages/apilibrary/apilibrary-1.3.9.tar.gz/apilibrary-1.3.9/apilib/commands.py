"""Command Line Interface for API Library"""

import sys
import os
import re
import click
from .core import APIKeyManager

def store_key_command():
    """Entry point for storekey command."""
    # Check for --env flag
    env_flag = "--env" in sys.argv
    
    if env_flag:
        # Handle storekey --env functionality
        # Check for .env file in current working directory
        env_file_path = os.path.join(os.getcwd(), ".env")
        
        if not os.path.exists(env_file_path):
            click.echo("❌ No .env file found in current directory")
            click.echo("Create a .env file with API keys in format: variable_name = your_key")
            sys.exit(1)
        
        try:
            with open(env_file_path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            click.echo(f"❌ Failed to read .env file: {e}")
            sys.exit(1)
        
        # Pattern to match any variable with equals sign
        api_key_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$')
        
        manager = APIKeyManager()
        stored_count = 0
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = api_key_pattern.match(line)
            if match:
                provider = match.group(1)
                api_key = match.group(2).strip()
                
                if not api_key:
                    errors.append(f"Line {line_num}: Empty API key for {provider}")
                    continue
                
                # Store the key
                success, message = manager.store_key(api_key, provider)
                
                if success:
                    stored_count += 1
                    click.echo(f"✅ Stored API key for {provider}")
                else:
                    errors.append(f"Line {line_num}: Failed to store {provider} key - {message}")
        
        # Summary
        if stored_count > 0:
            click.echo(f"\n🎉 Successfully stored {stored_count} API key(s) from .env file")
        
        if errors:
            click.echo(f"\n⚠️  Encountered {len(errors)} error(s):")
            for error in errors:
                click.echo(f"   {error}")
        
        if stored_count == 0 and not errors:
            click.echo("❌ No valid API keys found in .env file")
            click.echo("Expected format: variable_name = your_key")
            click.echo("Example: OPENAI_API_KEY = sk-1234567890abcdef")
            click.echo("Example: nomic_key = djahsjkdadsb")
    else:
        # Normal storekey behavior
        if len(sys.argv) < 3:
            click.echo("Usage: storekey <provider_name> <api_key>")
            click.echo("Usage: storekey --env")
            click.echo("Example: storekey openai sk-1234567890abcdef")
            click.echo("Example: storekey --env (reads from .env file)")
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
        click.echo("Usage: fetchkey <provider_name> [key_index] [--env]")
        click.echo("Example: fetchkey openai")
        click.echo("Example: fetchkey openai 1")
        click.echo("Example: fetchkey openai 1 --env")
        
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
    
    # Check for --env flag
    env_flag = "--env" in sys.argv
    
    # Parse key_index (default to 1 if not provided or if --env is used)
    key_index = 1
    if len(sys.argv) >= 3 and sys.argv[2] != "--env":
        try:
            key_index = int(sys.argv[2])
        except ValueError:
            click.echo("Error: Key index must be a number")
            click.echo("Example: fetchkey openai 1")
            sys.exit(1)
    
    manager = APIKeyManager()
    success, keys, message = manager.fetch_keys(provider)
    
    if not success:
        click.echo(f"❌ {message}")
        sys.exit(1)
    
    # Handle --env flag
    if env_flag:
        if key_index < 1 or key_index > len(keys):
            click.echo(f"❌ Invalid key index. Available keys: 1-{len(keys)}")
            sys.exit(1)
        
        selected_key = keys[key_index - 1]
        
        # Check current working directory for .env file
        env_file_path = os.path.join(os.getcwd(), ".env")
        env_var_name = f"{provider.upper()}_API_KEY"
        env_line = f"{env_var_name} = {selected_key}\n"
        
        try:
            if os.path.exists(env_file_path):
                # Read existing .env file
                with open(env_file_path, 'r') as f:
                    lines = f.readlines()
                
                # Check if the variable already exists and update it
                updated = False
                for i, line in enumerate(lines):
                    if line.strip().startswith(f"{env_var_name} ="):
                        lines[i] = env_line
                        updated = True
                        break
                
                # If variable doesn't exist, append it
                if not updated:
                    lines.append(env_line)
                
                # Write back to file
                with open(env_file_path, 'w') as f:
                    f.writelines(lines)
                
                click.echo(f"✅ Updated {env_var_name} in existing .env file")
            else:
                # Create new .env file
                with open(env_file_path, 'w') as f:
                    f.write(env_line)
                
                click.echo(f"✅ Created .env file with {env_var_name}")
        
        except Exception as e:
            click.echo(f"❌ Failed to write to .env file: {e}")
            sys.exit(1)
    else:
        # Normal fetchkey behavior (show all keys)
        click.echo(f"\n🔑 {message}:")
        click.echo("-" * 50)
        for i, key in enumerate(keys, 1):
            # Return the exact unencrypted API key
            click.echo(f"{i}. {key}")
        click.echo("-" * 50)

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
        click.echo("Error: Bigman use the numbers not the letters")
        click.echo("Example: deletekey openai 1")
        sys.exit(1)
    
    if not provider or provider.strip() == "":
        click.echo("Error: companyname cant be empty. Do this again i'll delete your OS")
        sys.exit(1)
    
    manager = APIKeyManager()
    success, message = manager.delete_key(provider, key_index)
    
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def mask_api_key(api_key):
    """Mask API key showing only prefix and suffix."""
    if len(api_key) <= 8:
        # For very short keys, show first 2 and last 2 characters
        return f"{api_key[:2]}{'*' * (len(api_key) - 4)}{api_key[-2:]}"
    else:
        # For longer keys, show first 4 and last 4 characters
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

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
                masked_key = mask_api_key(key)
                click.echo(f"  {i}. {masked_key}")
        
        click.echo("=" * 60)
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def delete_all_keys_command():
    """Entry point for deleteallkeys command."""
    from .auth import PasswordManager
    
    # Check if password is set up
    password_manager = PasswordManager()
    
    if password_manager.is_first_time_user():
        click.echo("❌ No password set up. Run 'hiiapi' to set up your password first.")
        sys.exit(1)
    
    # Authenticate user
    click.echo("🔐 Authentication required to delete all API keys.")
    
    if not password_manager.authenticate():
        click.echo("❌ Authentication failed. Cannot delete all keys.")
        sys.exit(1)
    
    # Show warning and confirmation
    click.echo("\n⚠️  WARNING: This will delete ALL stored API keys!")
    click.echo("This action cannot be undone.")
    
    # Double confirmation
    confirm1 = click.prompt("\nAre you sure you want to delete all API keys? (yes/no)", type=str)
    
    if confirm1.lower() not in ['yes', 'y']:
        click.echo("❌ Operation cancelled.")
        return
    
    confirm2 = click.prompt("\nType 'DELETE ALL' to confirm", type=str)
    
    if confirm2 != 'DELETE ALL':
        click.echo("❌ Confirmation failed. Operation cancelled.")
        return
    
    # Proceed with deletion
    manager = APIKeyManager()
    success, message = manager.delete_all_keys()
    
    if success:
        click.echo(f"\n✅ {message}")
        click.echo("🗑️  All API keys have been permanently deleted.")
    else:
        click.echo(f"\n❌ {message}")
        sys.exit(1)

def hiiapi_command():
    """Entry point for hiiapi command - shows all commands and sets up password."""
    from .auth import PasswordManager
    
    # Display welcome message
    click.echo("\n🚀 Welcome to API Library!")
    click.echo("=" * 50)
    
    # Display all available commands with descriptions
    commands = [
        ("storekey", "Store API keys securely"),
        ("fetchkey", "Retrieve stored API keys"),
        ("deletekey", "Delete specific API keys"),
        ("fetchallkeys", "Display all stored API keys"),
        ("deleteallkeys", "Delete all stored API keys"),
        ("checkauth", "Check password authentication status"),
        ("hiiapi", "Show commands and setup password")
    ]
    
    click.echo("\n📋 Available Commands:")
    click.echo("-" * 30)
    for cmd, desc in commands:
        click.echo(f"  {cmd:<15} - {desc}")
    click.echo("-" * 30)
    
    # Check if password is already set up
    password_manager = PasswordManager()
    
    if not password_manager.is_first_time_user():
        click.echo("\n✅ Password is already set up!")
        click.echo("You can start using the API library commands.")
        return
    
    # Prompt user to setup password
    click.echo("\n🔐 Password Setup Required")
    click.echo("To use the API library, you need to set up a master password.")
    
    setup_choice = click.prompt("\nWould you like to set up your password now? (y/n)", type=str, default="y")
    
    if setup_choice.lower() in ['y', 'yes']:
        success, message = password_manager.setup_password()
        
        if success:
            click.echo(f"\n✅ {message}")
            click.echo("\n🎉 Setup complete! You can now use all API library commands.")
        else:
            click.echo(f"\n❌ {message}")
            sys.exit(1)
    else:
        click.echo("\n⚠️  Password setup skipped.")
        click.echo("Run 'hiiapi' again when you're ready to set up your password.")





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