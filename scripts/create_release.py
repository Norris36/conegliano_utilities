#!/usr/bin/env python3
"""
Script to create GitHub releases automatically.

1. Gets current version from setup.py
2. Creates release using GitHub API
3. Tags the current commit
4. Generates release notes from commit messages

Returns type: release_info (dict) - GitHub release information or error details
"""

import requests
import json
import subprocess
import sys
import os
from pathlib import Path

def get_current_version():
    """
    Extract version from setup.py file.
    
    1. Reads setup.py content
    2. Parses version string using regex
    3. Returns clean version number
    
    Returns type: version (str) - current version number from setup.py
    """
    setup_path = Path(__file__).parent.parent / "setup.py"
    
    with open(setup_path, 'r') as f:
        content = f.read()
    
    import re
    version_match = re.search(r'version="([^"]+)"', content)
    if version_match:
        return version_match.group(1)
    else:
        raise ValueError("Could not find version in setup.py")

def get_commit_messages_since_last_tag():
    """
    Get commit messages since last release tag.
    
    1. Gets latest tag from git
    2. Gets commit messages since that tag
    3. Formats messages for release notes
    
    Returns type: messages (str) - formatted commit messages for release notes
    """
    try:
        # Get latest tag
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True, check=True)
        last_tag = result.stdout.strip()
        
        # Get commits since last tag
        result = subprocess.run(['git', 'log', f'{last_tag}..HEAD', '--oneline'], 
                              capture_output=True, text=True, check=True)
        commits = result.stdout.strip()
        
    except subprocess.CalledProcessError:
        # No previous tags, get all commits
        result = subprocess.run(['git', 'log', '--oneline'], 
                              capture_output=True, text=True, check=True)
        commits = result.stdout.strip()
    
    if not commits:
        return "No new changes since last release."
    
    # Format commits for release notes
    formatted_commits = []
    for line in commits.split('\n'):
        if line.strip():
            formatted_commits.append(f"• {line}")
    
    return "\n".join(formatted_commits)

def create_github_release(version, github_token, repo_owner="Norris36", repo_name="conegliano_utilities"):
    """
    Create a GitHub release using the API.
    
    1. Prepares release data with version and notes
    2. Makes POST request to GitHub releases API
    3. Creates git tag if release is successful
    4. Returns release information or error details
    
    Args:
        version (str): Version number for the release
        github_token (str): GitHub personal access token
        repo_owner (str): GitHub repository owner
        repo_name (str): GitHub repository name
    
    Returns type: release_data (dict) - GitHub API response with release info
    """
    # Get release notes
    release_notes = get_commit_messages_since_last_tag()
    
    # Prepare release data
    release_data = {
        "tag_name": f"v{version}",
        "target_commitish": "main",
        "name": f"Release v{version}",
        "body": f"## Changes\n\n{release_notes}",
        "draft": False,
        "prerelease": False
    }
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Create the release
    response = requests.post(url, json=release_data, headers=headers)
    
    if response.status_code == 201:
        print(f"✅ Successfully created release v{version}")
        return response.json()
    else:
        print(f"❌ Failed to create release: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    """
    Main function to create GitHub release.
    
    1. Gets current version from setup.py
    2. Reads GitHub token from environment or prompts user
    3. Creates GitHub release with current version
    4. Prints success or error message
    
    Returns type: None (NoneType) - prints results and exits
    """
    try:
        # Get current version
        version = get_current_version()
        print(f"Current version: {version}")
        
        # Get GitHub token
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            github_token = input("Enter your GitHub personal access token: ").strip()
        
        if not github_token:
            print("❌ GitHub token is required")
            sys.exit(1)
        
        # Create release
        release_info = create_github_release(version, github_token)
        
        if release_info:
            print(f"🎉 Release created: {release_info['html_url']}")
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()