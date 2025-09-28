"""
Global Issue Logger - Always creates issues in jensbay_utilities repo

This module provides a global issue logging system that:
1. Always creates issues in the jensbay_utilities repository
2. Works from anywhere on your system (any directory/repo)
3. Automatically includes context about where you're working
4. Provides universal access to THIS repo's issue management
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime


def detect_current_repo() -> Dict[str, Optional[str]]:
    """
    Automatically detect the current Git repository information.

    ~~~
    • Finds Git repository root directory
    • Extracts repository owner and name from remote URL
    • Handles both GitHub and other Git providers
    • Falls back to directory-based detection
    ~~~

    Returns type: repo_info (Dict[str, Optional[str]]) - repository metadata
    """
    try:
        # Get git root directory
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        git_root = result.stdout.strip()

        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_root
        )
        remote_url = result.stdout.strip()

        # Parse GitHub URL
        if "github.com" in remote_url:
            # Handle both SSH and HTTPS URLs
            if remote_url.startswith("git@github.com:"):
                # SSH: git@github.com:owner/repo.git
                repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
            elif "github.com/" in remote_url:
                # HTTPS: https://github.com/owner/repo.git
                repo_path = remote_url.split("github.com/")[1].replace(".git", "")
            else:
                repo_path = None

            if repo_path and "/" in repo_path:
                owner, repo_name = repo_path.split("/", 1)
                return {
                    "git_root": git_root,
                    "remote_url": remote_url,
                    "owner": owner,
                    "repo_name": repo_name,
                    "current_dir": os.getcwd(),
                    "relative_path": os.path.relpath(os.getcwd(), git_root)
                }

        # Fallback: use directory name and default owner
        repo_name = Path(git_root).name
        return {
            "git_root": git_root,
            "remote_url": remote_url,
            "owner": "Norris36",  # Default owner
            "repo_name": repo_name,
            "current_dir": os.getcwd(),
            "relative_path": os.path.relpath(os.getcwd(), git_root)
        }

    except subprocess.CalledProcessError:
        # Not in a git repository
        current_dir = os.getcwd()
        return {
            "git_root": None,
            "remote_url": None,
            "owner": "Norris36",
            "repo_name": Path(current_dir).name,
            "current_dir": current_dir,
            "relative_path": "."
        }
    except Exception as e:
        # Other errors
        current_dir = os.getcwd()
        return {
            "git_root": None,
            "remote_url": None,
            "owner": "Norris36",
            "repo_name": "unknown",
            "current_dir": current_dir,
            "relative_path": ".",
            "error": str(e)
        }


def global_issue(
    title: str,
    description: str = "",
    labels: Optional[List[str]] = None,
    priority: str = "medium",
    include_context: bool = True
) -> Dict[str, Any]:
    """
    Create an issue in jensbay_utilities repo from anywhere on your system.

    ~~~
    • Always creates issues in jensbay_utilities repository
    • Includes context about your current working location
    • Works from any directory (doesn't need to be in the repo)
    • Routes to GitHub or local storage automatically
    ~~~

    Args:
        title (str): Issue title
        description (str): Issue description
        labels (List[str], optional): Issue labels
        priority (str): Priority level (low, medium, high, critical)
        include_context (bool): Include automatic context information

    Returns type: issue_result (Dict[str, Any]) - issue creation result with metadata
    """
    current_location = detect_current_repo()

    # Build enhanced description with context about WHERE you're working
    if include_context:
        working_repo = current_location.get('repo_name', 'unknown')
        working_dir = current_location.get('current_dir', 'unknown')
        relative_path = current_location.get('relative_path', '.')

        context_info = f"""

## Working Context
**Working in Repository:** {working_repo}
**Current Directory:** `{working_dir}`
**Relative Path:** `{relative_path}`
**Timestamp:** {datetime.now().isoformat()}

*This issue was created from outside the jensbay_utilities repo while working on other code.*
"""
        enhanced_description = description + context_info
    else:
        enhanced_description = description

    # Add context-based labels
    repo_labels = labels or []
    repo_labels.append("global-issue")

    # Add label for where you're working
    working_repo = current_location.get('repo_name', 'unknown')
    if working_repo != 'jensbay_utilities':
        repo_labels.append(f"from-repo:{working_repo}")

    # Add directory context if available
    if current_location.get('relative_path') and current_location['relative_path'] != '.':
        dir_label = current_location['relative_path'].split('/')[0]
        repo_labels.append(f"working-in:{dir_label}")

    # ALWAYS target jensbay_utilities repo
    target_owner = "Norris36"
    target_repo = "jensbay_utilities"

    # Try to create issue in jensbay_utilities
    try:
        from .issue_logger import create_github_issue
        from .issue_config import get_github_token

        token = get_github_token()
        if token:
            print(f"🌐 Creating global issue in {target_owner}/{target_repo}")
            print(f"📍 Working from: {current_location.get('current_dir', 'unknown')}")

            result = create_github_issue(
                title=f"[Global] {title}",
                body=enhanced_description,
                labels=repo_labels,
                github_token=token,
                repo_owner=target_owner,
                repo_name=target_repo
            )

            if result.get('success'):
                print(f"✅ Global issue created: {result['issue_url']}")
                result['working_context'] = current_location
                return result

    except Exception as e:
        print(f"⚠️  GitHub creation failed: {e}")

    # Fallback to local storage (will sync to jensbay_utilities later)
    try:
        from .local_issue_store import store_issue_locally

        print(f"📱 Storing issue locally (will sync to {target_repo} later)")

        # Add working context to additional data
        additional_context = {
            "working_context": current_location,
            "global_issue": True,
            "target_repo": f"{target_owner}/{target_repo}"
        }

        result = store_issue_locally(
            title=f"[Global] {title}",
            body=enhanced_description,
            labels=repo_labels,
            priority=priority,
            additional_data=additional_context
        )

        if result.get('success'):
            print(f"✅ Global issue stored locally: {result['file_path']}")
            result['working_context'] = current_location

        return result

    except Exception as e:
        print(f"❌ All methods failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "working_context": current_location,
            "method": "failed"
        }


def quick_global_issue(title: str, description: str = "") -> None:
    """
    Quick global issue creation with minimal setup.

    ~~~
    • Simplified interface for rapid issue creation
    • Automatically detects repository context
    • Prints results for immediate feedback
    • Perfect for quick debugging and issue tracking
    ~~~

    Args:
        title (str): Issue title
        description (str): Issue description

    Returns type: None (NoneType) - prints results to console
    """
    print(f"🐛 Creating global issue: {title}")
    result = global_issue(title, description)

    if result.get('success'):
        repo_name = result.get('repo_info', {}).get('repo_name', 'unknown')
        print(f"✅ Issue created in {repo_name}")
    else:
        print(f"❌ Issue creation failed: {result.get('error', 'Unknown error')}")


def list_repo_issues(repo_owner: Optional[str] = None, repo_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List issues from the current or specified repository.

    ~~~
    • Fetches issues from GitHub API if available
    • Falls back to local issues if GitHub unavailable
    • Automatically detects current repo if not specified
    • Returns unified issue format
    ~~~

    Args:
        repo_owner (str, optional): Repository owner, auto-detected if None
        repo_name (str, optional): Repository name, auto-detected if None

    Returns type: issues (List[Dict[str, Any]]) - list of issue metadata
    """
    # Auto-detect repository if not specified
    if not repo_owner or not repo_name:
        repo_info = detect_current_repo()
        repo_owner = repo_owner or repo_info.get('owner', 'Norris36')
        repo_name = repo_name or repo_info.get('repo_name', 'unknown')

    print(f"📋 Fetching issues from {repo_owner}/{repo_name}")

    # Try GitHub API first
    try:
        from .issue_config import get_github_token
        import requests

        token = get_github_token()
        if token:
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                issues = response.json()
                print(f"✅ Found {len(issues)} GitHub issues")
                return issues

    except Exception as e:
        print(f"⚠️  GitHub API failed: {e}")

    # Fallback to local issues
    try:
        from .local_issue_store import list_local_issues

        local_issues = list_local_issues()
        # Filter by repo if possible
        repo_issues = [
            issue for issue in local_issues
            if issue.get('additional_data', {}).get('repo_info', {}).get('repo_name') == repo_name
        ]

        print(f"📱 Found {len(repo_issues)} local issues for {repo_name}")
        return repo_issues

    except Exception as e:
        print(f"❌ Local issue fetch failed: {e}")
        return []


def global_issue_context() -> Dict[str, Any]:
    """
    Get comprehensive context about the current location for issue creation.

    ~~~
    • Provides detailed environment information
    • Includes git repository context
    • Shows current working directory details
    • Useful for debugging and issue context
    ~~~

    Returns type: context (Dict[str, Any]) - comprehensive context information
    """
    repo_info = detect_current_repo()

    try:
        # Get additional git information
        git_info = {}
        if repo_info.get('git_root'):
            try:
                # Current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=repo_info['git_root']
                )
                git_info['current_branch'] = result.stdout.strip()

                # Recent commits
                result = subprocess.run(
                    ["git", "log", "--oneline", "-5"],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=repo_info['git_root']
                )
                git_info['recent_commits'] = result.stdout.strip().split('\n')

                # Status
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=repo_info['git_root']
                )
                git_info['has_changes'] = bool(result.stdout.strip())

            except subprocess.CalledProcessError:
                pass

        # Get Python and system info
        import platform
        import sys

        system_info = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "working_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat()
        }

        return {
            "repo_info": repo_info,
            "git_info": git_info,
            "system_info": system_info
        }

    except Exception as e:
        return {
            "repo_info": repo_info,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Convenience aliases for global usage
issue = global_issue  # Short alias
quick_issue_global = quick_global_issue  # Alternative name