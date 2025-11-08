#!/usr/bin/env python3
"""
Helper script to create AIRIA_API_KEY.txt file.

This script prompts you for your Airia API key and creates the file
in the correct location.
"""

from pathlib import Path
import sys

def main():
    print("=" * 50)
    print("🛡️  Aegis - Airia API Key Setup")
    print("=" * 50)
    print()
    print("This script will help you add your Airia API key.")
    print("Airia is optional - Aegis works fine without it.")
    print("If you don't have an Airia API key, just press Enter to skip.")
    print()
    
    # Get API key from user
    api_key = input("Enter your Airia API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("\n✅ Skipped. Aegis will work without Airia.")
        print("   You can run this script again later if you get an API key.")
        return
    
    # Determine file path (project root)
    script_dir = Path(__file__).parent
    key_file = script_dir / "AIRIA_API_KEY.txt"
    
    try:
        # Write the key to file
        key_file.write_text(api_key)
        print(f"\n✅ Success! API key saved to: {key_file}")
        print("\n📝 Next steps:")
        print("   1. Install Airia: pip install airia")
        print("   2. Restart your API server")
        print("   3. Airia AI analysis will now be enabled!")
        print()
    except Exception as e:
        print(f"\n❌ Error saving API key: {e}")
        print(f"   Try creating the file manually: {key_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()

