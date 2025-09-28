#!/usr/bin/env python3
"""
Token Setup and Testing Script for Work PC
Run this script to set up GitHub token and test issue creation
"""

from conegliano_utilities import issue_config, smart_issue, quick_issue, setup_token_config, set_hardcoded_token
import os


def main():
    print("🔧 GITHUB TOKEN SETUP FOR WORK PC")
    print("=" * 40)

    # Check current status
    current_token = issue_config.get_github_token()
    if current_token and current_token != 'YOUR_TOKEN_HERE':
        print("✅ Token already configured!")
        test_issue_creation()
        return

    print("❌ No token configured. Let's set it up!")
    print("\n📝 Choose setup method:")
    print("1. Config file (recommended - secure)")
    print("2. Hardcoded (for restricted environments)")
    print("3. Environment variable (temporary)")
    print("4. Test without token (local storage only)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        setup_config_file()
    elif choice == "2":
        setup_hardcoded()
    elif choice == "3":
        setup_environment()
    elif choice == "4":
        test_local_only()
    else:
        print("Invalid choice!")
        return

    # Test the setup
    test_issue_creation()


def setup_config_file():
    """Set up token in config file"""
    print("\n🔐 CONFIG FILE SETUP")
    token = input("Paste your GitHub token (ghp_...): ").strip()

    if not token or not token.startswith('ghp_'):
        print("❌ Invalid token format!")
        return

    success = setup_token_config(token)
    if success:
        print("✅ Token saved to ~/.github_config/token")
        print("🔒 File permissions set to 600 (owner only)")
    else:
        print("❌ Failed to save token")


def setup_hardcoded():
    """Generate encoded token for hardcoding"""
    print("\n🔒 HARDCODED SETUP")
    token = input("Paste your GitHub token (ghp_...): ").strip()

    if not token or not token.startswith('ghp_'):
        print("❌ Invalid token format!")
        return

    encoded = set_hardcoded_token(token)
    print(f"\n📋 COPY THIS ENCODED TOKEN:")
    print(f"   {encoded}")
    print("\n📝 STEPS:")
    print("1. Open: conegliano_utilities/issue_config.py")
    print("2. Find: _FALLBACK_TOKEN = base64.b64encode(b\"YOUR_TOKEN_HERE\").decode()")
    print(f"3. Replace with: _FALLBACK_TOKEN = \"{encoded}\"")
    print("4. Save the file")

    input("\nPress Enter after you've made the change...")

    # Test if it worked
    new_token = issue_config.get_github_token()
    if new_token and new_token != 'YOUR_TOKEN_HERE':
        print("✅ Hardcoded token detected!")
    else:
        print("❌ Token not detected - check your edit")


def setup_environment():
    """Set up environment variable"""
    print("\n🌍 ENVIRONMENT VARIABLE SETUP")
    token = input("Paste your GitHub token (ghp_...): ").strip()

    if not token or not token.startswith('ghp_'):
        print("❌ Invalid token format!")
        return

    os.environ['GITHUB_TOKEN'] = token
    print("✅ Environment variable set for this session")
    print("💡 To make permanent, add to your shell profile:")
    print(f"   export GITHUB_TOKEN='{token}'")


def test_local_only():
    """Test local storage without GitHub token"""
    print("\n📁 TESTING LOCAL STORAGE ONLY")
    print("This will test issue creation without GitHub access")


def test_issue_creation():
    """Test creating an issue"""
    print("\n🧪 TESTING ISSUE CREATION")
    print("-" * 30)

    test_title = "Test from setup script"
    test_desc = f"Testing issue creation at {os.getcwd()}"

    try:
        print("Creating test issue...")
        result = smart_issue(test_title, test_desc, labels=["test", "setup"])

        storage_type = result.get('storage_type', 'unknown')
        if result.get('success'):
            if storage_type == 'local':
                print(f"✅ Local issue created: {result.get('file_path')}")
                print("💡 Issue stored locally - sync to GitHub later with sync_local_issues_to_github()")
            else:
                print(f"✅ GitHub issue created: {result.get('issue_url')}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🎉 Setup complete! You can now use:")
    print("   quick_issue('Bug title', 'Description')")
    print("   smart_issue('Title', 'Desc', force_local=True)")


if __name__ == "__main__":
    main()