#!/usr/bin/env python3
"""
Issue Logger Examples - Complete guide for different environments and use cases

This file demonstrates when and how to use each issue logging method.
Perfect for restricted work environments where GitHub access may be limited.
"""

import os
from datetime import datetime


def example_1_first_time_setup():
    """
    EXAMPLE 1: First-time setup on any machine

    Use this when setting up issue logging for the first time.
    """
    print("=" * 60)
    print("EXAMPLE 1: FIRST-TIME SETUP")
    print("=" * 60)

    # Method A: Config file (recommended for personal machines)
    from conegliano_utilities.issue_config import setup_token_config

    # Replace with your actual GitHub token
    github_token = "ghp_YOUR_ACTUAL_TOKEN_HERE"

    success = setup_token_config(github_token)
    if success:
        print("✅ Token saved securely to ~/.github_config/token")
    else:
        print("❌ Setup failed")

    # Method B: Environment variable (temporary)
    # os.environ['GITHUB_TOKEN'] = github_token

    # Method C: Hardcoded (for restricted environments)
    from conegliano_utilities.issue_config import set_hardcoded_token
    encoded_token = set_hardcoded_token(github_token)
    print(f"📝 For hardcoding, use: _FALLBACK_TOKEN = \"{encoded_token}\"")


def example_2_work_pc_wrapper():
    """
    EXAMPLE 2: Simple wrapper for work PCs (RECOMMENDED)

    Use this when you need reliable issue creation that handles
    both GitHub access and restrictions automatically.
    """
    print("=" * 60)
    print("EXAMPLE 2: WORK PC WRAPPER (RECOMMENDED)")
    print("=" * 60)

    def work_pc_issue(title, description="", labels=None, priority="medium"):
        """
        Reliable issue creation for work environments

        ~~~
        • Tries GitHub first if token available
        • Automatically falls back to local storage
        • Handles network restrictions gracefully
        • Returns consistent result format
        ~~~

        Args:
            title (str): Issue title
            description (str): Issue description
            labels (list): Issue labels
            priority (str): Priority level (low, medium, high, critical)

        Returns type: result (dict) - creation result with success status
        """
        try:
            from conegliano_utilities.issue_logger import create_github_issue
            from conegliano_utilities.issue_config import get_github_token

            token = get_github_token()
            if token:
                print("🌐 Trying GitHub...")
                result = create_github_issue(title, description, labels or [], github_token=token)
                if result.get('success'):
                    print(f"✅ GitHub issue created: {result['issue_url']}")
                    return result
                else:
                    print(f"⚠️  GitHub failed: {result.get('message')}")
        except Exception as e:
            print(f"⚠️  GitHub error: {e}")

        # Fallback to local storage
        try:
            from conegliano_utilities.local_issue_store import store_issue_locally
            print("📱 Using local storage...")
            result = store_issue_locally(title, description, labels or [], priority)
            if result.get('success'):
                print(f"✅ Local issue stored: {result['file_path']}")
            return result
        except Exception as e:
            print(f"❌ Both methods failed: {e}")
            return {"success": False, "error": str(e)}

    # Test the wrapper
    print("🧪 Testing work PC wrapper...")
    result = work_pc_issue(
        "Example bug report",
        "This is a test issue to demonstrate the wrapper function",
        ["bug", "test", "work-pc"],
        "medium"
    )
    print(f"Result: {result.get('success', False)}")

    return work_pc_issue


def example_3_exception_handling():
    """
    EXAMPLE 3: Exception handling and automatic issue creation

    Use this to automatically create issues when errors occur.
    """
    print("=" * 60)
    print("EXAMPLE 3: EXCEPTION HANDLING")
    print("=" * 60)

    def debug_function_with_auto_issues():
        """Example function that creates issues when errors occur"""
        try:
            # Simulate some work that might fail
            result = 10 / 0  # This will cause an error

        except ZeroDivisionError as e:
            print(f"🐛 Error caught: {e}")

            # Method A: Manual issue creation with exception details
            try:
                from conegliano_utilities.local_issue_store import create_local_debug_issue

                issue_result = create_local_debug_issue(
                    title="Division by zero error in debug_function",
                    description="Function failed when processing user input",
                    exception=e,
                    additional_context={
                        "function": "debug_function_with_auto_issues",
                        "user_input": "example_data",
                        "timestamp": datetime.now().isoformat()
                    },
                    priority="high"
                )

                if issue_result.get('success'):
                    print(f"✅ Debug issue created: {issue_result['file_path']}")

            except Exception as creation_error:
                print(f"❌ Failed to create issue: {creation_error}")

        except Exception as e:
            # Catch-all for other errors
            print(f"🚨 Unexpected error: {e}")

            # Simple error logging
            try:
                from conegliano_utilities.local_issue_store import store_issue_locally

                store_issue_locally(
                    title=f"Unexpected error in {debug_function_with_auto_issues.__name__}",
                    body=f"Error: {str(e)}\nType: {type(e).__name__}",
                    labels=["error", "unexpected", "auto-generated"],
                    priority="high"
                )
                print("✅ Error logged locally")

            except Exception:
                print("❌ Could not log error")

    # Test exception handling
    print("🧪 Testing exception handling...")
    debug_function_with_auto_issues()


def example_4_different_environments():
    """
    EXAMPLE 4: Code for different environments

    Use this to understand which method works best in your environment.
    """
    print("=" * 60)
    print("EXAMPLE 4: ENVIRONMENT-SPECIFIC USAGE")
    print("=" * 60)

    def detect_environment():
        """Detect what environment we're running in"""
        try:
            from conegliano_utilities.issue_config import get_github_token
            token = get_github_token()

            if token:
                print("🏠 Environment: Home/Personal (GitHub token available)")
                return "home"
            else:
                print("🏢 Environment: Work/Restricted (No GitHub token)")
                return "work"
        except Exception:
            print("❓ Environment: Unknown (Import issues)")
            return "unknown"

    environment = detect_environment()

    if environment == "home":
        print("\n💡 RECOMMENDED FOR HOME/PERSONAL:")
        print("  - Use setup_token_config() once")
        print("  - Use work_pc_issue() for reliability")
        print("  - Issues will go directly to GitHub")

    elif environment == "work":
        print("\n💡 RECOMMENDED FOR WORK/RESTRICTED:")
        print("  - Copy work_pc_issue() function")
        print("  - Issues will be stored locally")
        print("  - Sync later with sync_local_issues_to_github()")

    else:
        print("\n💡 TROUBLESHOOTING:")
        print("  - Check package installation")
        print("  - Try direct imports")
        print("  - Use simple local storage")


def example_5_sync_and_management():
    """
    EXAMPLE 5: Managing and syncing local issues

    Use this when you have access to GitHub again and want to sync
    previously stored local issues.
    """
    print("=" * 60)
    print("EXAMPLE 5: SYNC AND MANAGEMENT")
    print("=" * 60)

    # List all local issues
    try:
        from conegliano_utilities.local_issue_store import list_local_issues

        all_issues = list_local_issues()
        open_issues = list_local_issues(status="open")

        print(f"📋 Total local issues: {len(all_issues)}")
        print(f"📋 Open local issues: {len(open_issues)}")

        if open_issues:
            print("\n🔍 Recent local issues:")
            for issue in open_issues[:3]:  # Show first 3
                print(f"  - {issue.get('title', 'No title')} ({issue.get('priority', 'medium')})")

        # Sync to GitHub (when you have access)
        print("\n🔄 To sync local issues to GitHub later:")
        print("from conegliano_utilities.local_issue_store import sync_local_issues_to_github")
        print("sync_result = sync_local_issues_to_github('your_github_token')")
        print("print(f'Synced: {sync_result[\"synced\"]} issues')")

    except Exception as e:
        print(f"❌ Management functions not available: {e}")


def example_6_email_fallback():
    """
    EXAMPLE 6: Email fallback when everything else fails

    Use this as a last resort when neither GitHub nor local storage work.
    """
    print("=" * 60)
    print("EXAMPLE 6: EMAIL FALLBACK")
    print("=" * 60)

    try:
        from conegliano_utilities.email_issue_reporter import create_mailto_link, print_email_issue

        # Generate mailto link
        mailto_url = create_mailto_link(
            title="Critical bug found",
            body="Bug details and stack trace here...",
            recipient="team@company.com"
        )

        print(f"📧 Mailto link generated (first 100 chars):")
        print(f"   {mailto_url[:100]}...")

        # Print email template
        print("\n📝 Email template:")
        print_email_issue(
            title="System error report",
            body="Error occurred in production system\nStack trace: ...",
            recipient="support@company.com"
        )

    except Exception as e:
        print(f"❌ Email functions not available: {e}")


def main():
    """
    Run all examples to demonstrate the complete issue logging system
    """
    print("🚀 ISSUE LOGGER COMPLETE EXAMPLES")
    print("=" * 80)
    print("This demonstrates all available methods for different situations.")
    print("=" * 80)

    # Skip first-time setup to avoid overwriting tokens
    print("⏭️  Skipping Example 1 (first-time setup) - run manually if needed")

    # Run practical examples
    work_pc_issue_func = example_2_work_pc_wrapper()
    example_3_exception_handling()
    example_4_different_environments()
    example_5_sync_and_management()
    example_6_email_fallback()

    print("\n" + "=" * 80)
    print("🎉 ALL EXAMPLES COMPLETE!")
    print("=" * 80)
    print("💡 QUICK REFERENCE:")
    print("  • Home/Personal: Use work_pc_issue() function")
    print("  • Work/Restricted: Copy work_pc_issue() function")
    print("  • Debugging: Use create_local_debug_issue()")
    print("  • Emergency: Use email templates")
    print("  • Later sync: Use sync_local_issues_to_github()")

    return work_pc_issue_func


if __name__ == "__main__":
    # Return the work_pc_issue function for immediate use
    work_pc_issue = main()

    print("\n🎯 READY TO USE:")
    print("work_pc_issue('Bug title', 'Description here')")