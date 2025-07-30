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
        env_var_name = {provider.upper()}
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

def addgitignore_command():
    """Entry point for addgitignore command."""
    from pathlib import Path
    
    # Define common .gitignore patterns
    patterns = [
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        "MANIFEST",
        "",
        "# PyInstaller",
        "*.manifest",
        "*.spec",
        "",
        "# Installer logs",
        "pip-log.txt",
        "pip-delete-this-directory.txt",
        "",
        "# Unit test / coverage reports",
        "htmlcov/",
        ".tox/",
        ".nox/",
        ".coverage",
        ".coverage.*",
        ".cache",
        "nosetests.xml",
        "coverage.xml",
        "*.cover",
        ".hypothesis/",
        ".pytest_cache/",
        "",
        "# Translations",
        "*.mo",
        "*.pot",
        "",
        "# Django stuff:",
        "*.log",
        "local_settings.py",
        "db.sqlite3",
        "",
        "# Flask stuff:",
        "instance/",
        ".webassets-cache",
        "",
        "# Scrapy stuff:",
        ".scrapy",
        "",
        "# Sphinx documentation",
        "docs/_build/",
        "",
        "# PyBuilder",
        "target/",
        "",
        "# Jupyter Notebook",
        ".ipynb_checkpoints",
        "",
        "# pyenv",
        ".python-version",
        "",
        "# celery beat schedule file",
        "celerybeat-schedule",
        "",
        "# SageMath parsed files",
        "*.sage.py",
        "",
        "# Environments",
        ".env",
        ".venv",
        "env/",
        "venv/",
        "ENV/",
        "env.bak/",
        "venv.bak/",
        "",
        "# Spyder project settings",
        ".spyderproject",
        ".spyproject",
        "",
        "# Rope project settings",
        ".ropeproject",
        "",
        "# mkdocs documentation",
        "/site",
        "",
        "# mypy",
        ".mypy_cache/",
        ".dmypy.json",
        "dmypy.json",
        "",
        "# Pyre type checker",
        ".pyre/",
        "",
        "# IDEs",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "*~",
        "",
        "# OS generated files",
        ".DS_Store",
        ".DS_Store?",
        ".Spotlight-V100",
        ".Trashes",
        "ehthumbs.db",
        "Thumbs.db"
    ]
    
    gitignore_path = Path.cwd() / ".gitignore"
    
    try:
        existing_patterns = set()
        existing_content = ""
        
        # Check if .gitignore already exists and read existing patterns
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
                # Extract patterns to avoid duplicates (ignore comments and empty lines)
                existing_lines = existing_content.splitlines()
                existing_patterns = {line.strip() for line in existing_lines 
                                   if line.strip() and not line.strip().startswith('#')}
            click.echo("📁 Found existing .gitignore file")
        else:
            click.echo("📁 Creating new .gitignore file")
        
        # Filter out patterns that already exist (excluding comments and empty lines)
        new_patterns_to_add = []
        for pattern in patterns:
            if pattern.strip() == "" or pattern.startswith("#"):
                # Always add comments and empty lines for structure
                new_patterns_to_add.append(pattern)
            elif pattern.strip() not in existing_patterns:
                # Only add if pattern doesn't exist
                new_patterns_to_add.append(pattern)
        
        # Count actual new patterns (excluding comments and empty lines)
        actual_new_patterns = [p for p in new_patterns_to_add 
                             if p.strip() and not p.startswith('#')]
        
        if not actual_new_patterns and gitignore_path.exists():
            click.echo("✅ .gitignore already contains all standard patterns")
            return
        
        # Prepare the content to write
        content_to_write = []
        
        if gitignore_path.exists() and existing_content.strip():
            # Add existing content first
            content_to_write.append(existing_content.rstrip())
            # Add separators
            content_to_write.extend(["", "", "# Added by apilib"])
        
        # Add new patterns
        content_to_write.extend(new_patterns_to_add)
        
        # Write the updated content
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_to_write))
        
        # Count added patterns (excluding comments and empty lines)
        added_count = len(actual_new_patterns)
        
        if gitignore_path.exists() and existing_content:
            click.echo(f"✅ Added {added_count} new patterns to existing .gitignore")
        else:
            click.echo(f"✅ Created .gitignore with {added_count} patterns")
            
        click.echo(f"📍 Location: {gitignore_path}")
        
        if added_count > 0:
            click.echo("\n📋 Added patterns include:")
            click.echo("   • Python cache files (__pycache__, *.pyc)")
            click.echo("   • Build directories (build/, dist/, *.egg-info/)")
            click.echo("   • Virtual environments (.venv, venv/, env/)")
            click.echo("   • IDE files (.vscode/, .idea/)")
            click.echo("   • OS files (.DS_Store, Thumbs.db)")
            click.echo("   • Environment files (.env)")
            click.echo("   • And many more development-related patterns")
        
    except PermissionError:
        click.echo("❌ Permission denied. Please check file permissions or run as administrator.")
    except Exception as e:
        click.echo(f"❌ Error creating/updating .gitignore: {e}")

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
        ("addgitignore", "Add common .gitignore patterns"),
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