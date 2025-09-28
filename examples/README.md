# Issue Logger Examples

This directory contains complete examples for using the issue logging system in different environments, especially restricted work environments where GitHub access may be limited.

## 📁 Files Overview

### `work_pc_quick_start.py`
**🎯 MAIN FILE FOR WORK PC**
- Complete standalone solution
- Copy this entire file to your work PC
- Includes setup, issue creation, and sync functions
- Works with or without GitHub access

### `issue_logger_examples.py`
**📚 COMPREHENSIVE EXAMPLES**
- Detailed examples for all use cases
- Shows when to use each method
- Exception handling examples
- Environment detection

## 🚀 Quick Start for Work PC

### 1. Install Package
```bash
pip install git+https://github.com/Norris36/jensbay_utilities.git
```

### 2. Copy and Run Setup
```python
# Copy work_pc_quick_start.py to your work PC
python work_pc_quick_start.py

# Then run setup once:
setup_once()  # This saves your GitHub token
```

### 3. Create Issues
```python
# Simple usage
work_pc_issue("Bug found", "Description here")

# Detailed usage
work_pc_issue(
    title="Critical database error",
    description="Stack trace and details...",
    labels=["bug", "critical", "database"],
    priority="high"
)
```

## 🔄 Different Scenarios

### Scenario 1: Home/Personal Computer
- ✅ GitHub access available
- ✅ Token saved in config file
- ✅ Issues go directly to GitHub

```python
from conegliano_utilities.issue_config import setup_token_config
setup_token_config('your_github_token')

# Issues will be created on GitHub
work_pc_issue("Bug title", "Description")
```

### Scenario 2: Work Computer (GitHub Blocked)
- ❌ GitHub access blocked by firewall
- ✅ Local storage works
- ✅ Can sync later when access returns

```python
# Issues are stored locally
work_pc_issue("Work PC bug", "Description")  # → Saved locally

# Later, when you have GitHub access:
sync_when_github_available()  # → Syncs all local issues to GitHub
```

### Scenario 3: Completely Restricted Environment
- ❌ GitHub blocked
- ❌ Local storage restricted
- ✅ Manual templates generated

```python
# Creates manual template for copy-paste
work_pc_issue("Emergency bug", "Critical issue")
# → Generates text template you can manually copy to GitHub
```

## 🛠️ Functions Reference

### Setup Functions
```python
setup_once()                    # One-time GitHub token setup
check_status()                  # Check current configuration
```

### Issue Creation
```python
work_pc_issue(title, description, labels, priority)  # Main function
create_manual_template(...)     # Emergency fallback
```

### Management
```python
sync_when_github_available()    # Sync local issues to GitHub
run_examples()                  # Test all functionality
```

## 🎯 Use Cases

### Bug Reports
```python
work_pc_issue(
    "Login fails with special characters",
    "Stack trace:\n...\nSteps to reproduce:\n1. Enter email with + symbol\n2. Click login\n3. Error occurs",
    ["bug", "login", "urgent"],
    "high"
)
```

### Feature Requests
```python
work_pc_issue(
    "Feature: Export data to CSV",
    "Users need ability to export dashboard data to CSV format",
    ["enhancement", "export"],
    "medium"
)
```

### Exception Handling
```python
try:
    # Some code that might fail
    process_data()
except Exception as e:
    work_pc_issue(
        f"Error in process_data: {type(e).__name__}",
        f"Exception: {str(e)}\nFunction: process_data\nTimestamp: {datetime.now()}",
        ["error", "auto-generated"],
        "high"
    )
```

## 🔧 Troubleshooting

### Import Errors
```python
# If imports fail, try direct approach:
def simple_issue_logger(title, description):
    try:
        from conegliano_utilities.issue_logger import create_github_issue
        from conegliano_utilities.issue_config import get_github_token
        token = get_github_token()
        if token:
            return create_github_issue(title, description, github_token=token)
    except:
        # Manual fallback
        print(f"MANUAL ISSUE:\nTitle: {title}\nDescription: {description}")
```

### No GitHub Access
```python
# Force local storage only
from conegliano_utilities.local_issue_store import store_issue_locally
store_issue_locally("Title", "Description", ["local"], "medium")
```

### Package Not Available
```python
# Emergency standalone function
def emergency_issue_log(title, description):
    import os
    from datetime import datetime

    filename = f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w') as f:
        f.write(f"Title: {title}\nDescription: {description}\nTime: {datetime.now()}")
    print(f"Issue logged to: {filename}")
```

## 💡 Best Practices

1. **Always try the main function first**: `work_pc_issue()`
2. **Set up token once**: Use `setup_once()` when you first start
3. **Check status regularly**: Use `check_status()` to verify setup
4. **Sync when possible**: Run `sync_when_github_available()` when you regain access
5. **Include context**: Add labels and priority for better organization
6. **Handle exceptions**: Use issue logging in your error handling code

## 🔄 Workflow Example

```python
# Week 1: At home (GitHub access)
setup_once()  # Setup token
work_pc_issue("Bug 1", "Description")  # → Goes to GitHub

# Week 2: At work (GitHub blocked)
work_pc_issue("Bug 2", "Description")  # → Stored locally
work_pc_issue("Bug 3", "Description")  # → Stored locally

# Week 3: Back home (GitHub access)
sync_when_github_available()  # → Syncs Bug 2 & 3 to GitHub
work_pc_issue("Bug 4", "Description")  # → Goes directly to GitHub
```

This system ensures you never lose track of issues, regardless of your environment restrictions!