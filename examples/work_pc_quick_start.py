#!/usr/bin/env python3
"""
WORK PC QUICK START GUIDE

Copy this entire file to your work PC for immediate issue logging capability.
This includes everything you need in one simple file.
"""

def setup_once():
    """
    Run this function ONCE on your work PC to set up the GitHub token.
    Replace 'YOUR_TOKEN_HERE' with your actual GitHub token.
    """
    print("🔧 SETTING UP GITHUB TOKEN...")

    # Replace this with your actual token
    github_token = "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"

    try:
        from conegliano_utilities.issue_config import setup_token_config
        success = setup_token_config(github_token)

        if success:
            print("✅ Token setup complete!")
            print("💡 You can now use work_pc_issue() to create issues")
            return True
        else:
            print("❌ Token setup failed")
            return False

    except ImportError:
        print("❌ Package not installed. Run: pip install git+https://github.com/Norris36/jensbay_utilities.git")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False


def work_pc_issue(title, description="", labels=None, priority="medium"):
    """
    🎯 MAIN FUNCTION: Use this to create issues from your work PC

    This function automatically:
    • Tries GitHub first (if accessible)
    • Falls back to local storage (if GitHub blocked)
    • Handles all errors gracefully
    • Works in any environment

    Examples:
        work_pc_issue("Bug found", "Description here")
        work_pc_issue("Feature request", "Details...", ["enhancement"])
        work_pc_issue("Critical error", "Stack trace...", priority="high")

    Args:
        title (str): Short issue title
        description (str): Detailed description
        labels (list): Tags like ["bug", "urgent"]
        priority (str): "low", "medium", "high", or "critical"

    Returns:
        dict: Result with success status and details
    """
    print(f"🐛 Creating issue: {title}")

    # Method 1: Try GitHub first
    try:
        from conegliano_utilities.issue_logger import create_github_issue
        from conegliano_utilities.issue_config import get_github_token

        token = get_github_token()
        if token:
            print("🌐 Trying GitHub...")
            result = create_github_issue(
                title=title,
                body=description,
                labels=labels or [],
                github_token=token
            )

            if result.get('success'):
                print(f"✅ GitHub issue created: {result['issue_url']}")
                return result
            else:
                print(f"⚠️  GitHub failed: {result.get('message', 'Unknown error')}")
        else:
            print("🔑 No GitHub token found")

    except Exception as e:
        print(f"⚠️  GitHub blocked or unavailable: {e}")

    # Method 2: Fallback to local storage
    try:
        from conegliano_utilities.local_issue_store import store_issue_locally
        print("📱 Storing locally...")

        result = store_issue_locally(
            title=title,
            body=description,
            labels=labels or [],
            priority=priority
        )

        if result.get('success'):
            print(f"✅ Local issue stored: {result['file_path']}")
            print("💡 Will sync to GitHub when access returns")
            return result
        else:
            print(f"❌ Local storage failed: {result.get('error')}")

    except Exception as e:
        print(f"❌ Local storage error: {e}")

    # Method 3: Emergency fallback
    print("🚨 All methods failed - creating manual template")
    return create_manual_template(title, description, labels, priority)


def create_manual_template(title, description, labels, priority):
    """
    Emergency fallback: Creates a text template you can copy-paste
    """
    template = f"""
MANUAL ISSUE TEMPLATE
====================
Title: {title}
Priority: {priority}
Labels: {', '.join(labels or [])}
Created: {_get_timestamp()}

Description:
{description}

System Info:
- Python: {_get_python_version()}
- OS: {_get_os_info()}
- Working Dir: {_get_current_dir()}

To create GitHub issue manually:
1. Go to: https://github.com/Norris36/jensbay_utilities/issues/new
2. Copy-paste this template
3. Submit the issue

====================
"""

    print("📋 MANUAL TEMPLATE CREATED:")
    print(template)

    # Try to save to file
    try:
        import os
        filename = f"manual_issue_{_get_timestamp().replace(':', '-').replace(' ', '_')}.txt"
        filepath = os.path.join(os.getcwd(), filename)

        with open(filepath, 'w') as f:
            f.write(template)

        print(f"💾 Template saved to: {filepath}")
        return {"success": True, "method": "manual", "file_path": filepath}

    except Exception as e:
        print(f"⚠️  Could not save template: {e}")
        return {"success": False, "method": "manual", "template": template}


def sync_when_github_available():
    """
    Run this when you regain GitHub access to sync all local issues
    """
    print("🔄 SYNCING LOCAL ISSUES TO GITHUB...")

    try:
        from conegliano_utilities.local_issue_store import sync_local_issues_to_github
        from conegliano_utilities.issue_config import get_github_token

        token = get_github_token()
        if not token:
            print("❌ No GitHub token found. Run setup_once() first.")
            return

        result = sync_local_issues_to_github(token)

        print(f"📊 SYNC RESULTS:")
        print(f"  Total issues: {result['total_issues']}")
        print(f"  Synced: {result['synced']}")
        print(f"  Failed: {result['failed']}")

        if result['errors']:
            print("❌ Errors:")
            for error in result['errors'][:3]:  # Show first 3
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ Sync failed: {e}")


def check_status():
    """
    Check the current status of your issue logging setup
    """
    print("🔍 CHECKING ISSUE LOGGER STATUS...")
    print("=" * 40)

    # Check package installation
    try:
        import conegliano_utilities
        print(f"✅ Package installed: v{conegliano_utilities.__version__}")
    except ImportError:
        print("❌ Package not installed")
        print("   Run: pip install git+https://github.com/Norris36/jensbay_utilities.git")
        return

    # Check token
    try:
        from conegliano_utilities.issue_config import get_github_token
        token = get_github_token()

        if token:
            print(f"✅ GitHub token found: {token[:10]}...")
        else:
            print("❌ No GitHub token found")
            print("   Run: setup_once()")
    except Exception as e:
        print(f"⚠️  Token check failed: {e}")

    # Check local issues
    try:
        from conegliano_utilities.local_issue_store import list_local_issues
        local_issues = list_local_issues()
        print(f"📋 Local issues stored: {len(local_issues)}")

        if local_issues:
            open_issues = [i for i in local_issues if i.get('status') == 'open']
            print(f"   Open issues: {len(open_issues)}")
    except Exception as e:
        print(f"⚠️  Local storage check failed: {e}")

    print("=" * 40)
    print("💡 READY TO USE: work_pc_issue('Bug title', 'Description')")


# Helper functions
def _get_timestamp():
    """Get current timestamp"""
    try:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown"

def _get_python_version():
    """Get Python version"""
    try:
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    except:
        return "Unknown"

def _get_os_info():
    """Get OS information"""
    try:
        import platform
        return f"{platform.system()} {platform.release()}"
    except:
        return "Unknown"

def _get_current_dir():
    """Get current directory"""
    try:
        import os
        return os.getcwd()
    except:
        return "Unknown"


# Example usage and tests
def run_examples():
    """
    Run example usage to test the system
    """
    print("🧪 RUNNING EXAMPLES...")
    print("=" * 40)

    # Example 1: Simple issue
    print("1️⃣ Simple issue:")
    work_pc_issue("Test issue", "This is a test from work PC")

    print("\n2️⃣ Detailed issue:")
    work_pc_issue(
        title="Complex bug report",
        description="Detailed description with multiple lines\nand specific error details",
        labels=["bug", "urgent", "work-pc"],
        priority="high"
    )

    print("\n3️⃣ Feature request:")
    work_pc_issue(
        title="Feature: Add dark mode",
        description="Users have requested a dark mode option",
        labels=["enhancement", "ui"],
        priority="low"
    )

    print("=" * 40)
    print("✅ Examples complete!")


if __name__ == "__main__":
    print("🚀 WORK PC ISSUE LOGGER")
    print("=" * 50)
    print("QUICK START GUIDE:")
    print("1. setup_once()           # Run once to setup token")
    print("2. work_pc_issue('Bug')   # Create issues anytime")
    print("3. check_status()         # Check if everything works")
    print("4. sync_when_github_available()  # Sync later")
    print("=" * 50)

    # Automatically check status
    check_status()

    print("\n💡 Copy this file to your work PC and run:")
    print("   python work_pc_quick_start.py")