# Automated Versioning Setup Template

This template shows which files you need to copy to other repos to replicate the automated versioning and release system.

## Files to Copy

### 1. GitHub Actions Workflow
Copy this file to enable automatic releases:

**File:** `.github/workflows/release.yml`

```yaml
name: Create Release

on:
  push:
    branches: [ main ]
    paths: [ 'setup.py' ]  # Only trigger when setup.py changes

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Fetch all history for changelog
    
    - name: Extract version from setup.py
      id: get_version
      run: |
        VERSION=$(python -c "import re; content=open('setup.py').read(); print(re.search(r'version=\"([^\"]+)\"', content).group(1))")
        echo "version=$VERSION" >> $GITHUB_OUTPUT
        echo "tag=v$VERSION" >> $GITHUB_OUTPUT
    
    - name: Check if tag exists
      id: check_tag
      run: |
        if git rev-parse "v${{ steps.get_version.outputs.version }}" >/dev/null 2>&1; then
          echo "exists=true" >> $GITHUB_OUTPUT
        else
          echo "exists=false" >> $GITHUB_OUTPUT
        fi
    
    - name: Generate changelog
      id: changelog
      if: steps.check_tag.outputs.exists == 'false'
      run: |
        # Get commits since last tag, or all commits if no tags exist
        LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
        if [ -n "$LAST_TAG" ]; then
          COMMITS=$(git log $LAST_TAG..HEAD --oneline --no-merges)
        else
          COMMITS=$(git log --oneline --no-merges)
        fi
        
        # Format commits for release notes
        echo "## Changes" > changelog.md
        echo "" >> changelog.md
        if [ -n "$COMMITS" ]; then
          echo "$COMMITS" | sed 's/^/• /' >> changelog.md
        else
          echo "• No new changes" >> changelog.md
        fi
        
        echo "changelog<<EOF" >> $GITHUB_OUTPUT
        cat changelog.md >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT
    
    - name: Create Release
      if: steps.check_tag.outputs.exists == 'false'
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ steps.get_version.outputs.tag }}
        release_name: Release ${{ steps.get_version.outputs.tag }}
        body: ${{ steps.changelog.outputs.changelog }}
        draft: false
        prerelease: false
```

### 2. Manual Release Script (Optional)
Copy this file for manual release creation:

**File:** `scripts/create_release.py`

```python
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
    """Extract version from setup.py file."""
    setup_path = Path(__file__).parent.parent / "setup.py"
    
    with open(setup_path, 'r') as f:
        content = f.read()
    
    import re
    version_match = re.search(r'version="([^"]+)"', content)
    if version_match:
        return version_match.group(1)
    else:
        raise ValueError("Could not find version in setup.py")

def create_github_release(version, github_token, repo_owner="YOUR_USERNAME", repo_name="YOUR_REPO_NAME"):
    """Create a GitHub release using the API."""
    # Implementation details...
    # (Copy the full function from the original file)

# Usage: python scripts/create_release.py
```

### 3. Package Init with Version Checking
Add to your package's `__init__.py`:

```python
import warnings
import requests
import json
from packaging import version

__version__ = "1.0.0"  # Update this with each release

def check_for_updates():
    """Check if a newer version is available on GitHub."""
    try:
        # Update with your repo details
        url = "https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO_NAME/releases/latest"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            latest_info = response.json()
            latest_version = latest_info['tag_name'].lstrip('v')
            current_version = __version__
            
            if version.parse(latest_version) > version.parse(current_version):
                warnings.warn(
                    f"\n🔔 UPDATE AVAILABLE 🔔\n"
                    f"Current version: {current_version}\n"
                    f"Latest version: {latest_version}\n"
                    f"Run: pip install --upgrade git+https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git\n",
                    UserWarning,
                    stacklevel=2
                )
    except Exception:
        pass

# Check for updates on import (optional)
try:
    check_for_updates()
except Exception:
    pass
```

### 4. Requirements Update
Add to your `requirements.txt`:

```
packaging>=21.0
requests>=2.25.0
```

## Setup Instructions

### Step 1: Copy Files
1. Copy `.github/workflows/release.yml` to your new repo
2. Optionally copy `scripts/create_release.py`
3. Update your package `__init__.py` with version checking code

### Step 2: Update Repository Details
Replace these placeholders in the copied files:
- `YOUR_USERNAME` → Your GitHub username
- `YOUR_REPO_NAME` → Your repository name
- Update repository URLs accordingly

### Step 3: Setup Dependencies
Add `packaging` and `requests` to your requirements.txt

### Step 4: Version Management
1. Keep version in sync between `setup.py` and `__init__.py`
2. Bump version in `setup.py` for each release
3. Commit and push → Automatic release creation!

## Workflow

1. **Make changes** to your code
2. **Update version** in `setup.py` (e.g., 1.0.1 → 1.0.2)  
3. **Update version** in `__init__.py` to match
4. **Commit and push** → GitHub Actions automatically creates release
5. **Users get notifications** when importing outdated versions

## Benefits

✅ **Automatic release creation** on version bumps  
✅ **User notifications** for available updates  
✅ **One-liner updates** with clear instructions  
✅ **Professional release management** with changelogs  
✅ **Zero maintenance** after initial setup  

## Manual Commands for Users

### Install
```bash
pip install git+https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Update
```bash
pip install --upgrade git+https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```