"""
Issue Logger - Create GitHub issues remotely for debugging and tracking
"""

import json
import platform
import sys
import traceback
from datetime import datetime
from typing import Dict, Optional, Any, List
import requests
import os
import subprocess


def create_github_issue(
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
    github_token: Optional[str] = None,
    repo_owner: str = "Norris36",
    repo_name: str = "jensbay_utilities",
) -> Dict[str, Any]:
    """
    Create a GitHub issue using the API for remote debugging and issue tracking.

    ~~~
    • Validates GitHub token and repository access
    • Formats issue body with debugging information
    • Creates issue via GitHub API with proper headers
    • Returns issue URL and metadata for reference
    ~~~

    Args:
        title (str): Issue title - should be descriptive and concise
        body (str): Issue description with details, stack traces, etc.
        labels (List[str], optional): Labels to apply to the issue
        github_token (str, optional): GitHub personal access token
        repo_owner (str): GitHub repository owner (default: "Norris36")
        repo_name (str): GitHub repository name (default: "jensbay_utilities")

    Returns type: issue_data (Dict[str, Any]) - GitHub API response with
        issue URL and metadata
    """
    # Get GitHub token from environment or parameter
    if not github_token:
        github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        raise ValueError(
            "GitHub token is required. Set GITHUB_TOKEN environment "
            "variable or pass as parameter."
        )

    # Default labels for debugging issues
    if labels is None:
        labels = ["bug", "remote-debug"]

    # Prepare issue data
    issue_data = {"title": title, "body": body, "labels": labels}

    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

    # Create the issue
    response = requests.post(url, json=issue_data, headers=headers)

    if response.status_code == 201:
        issue_info = response.json()
        return {
            "success": True,
            "issue_number": issue_info["number"],
            "issue_url": issue_info["html_url"],
            "api_url": issue_info["url"],
            "created_at": issue_info["created_at"],
            "title": issue_info["title"],
        }
    else:
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text,
            "message": f"Failed to create issue: {response.status_code}",
        }


def format_system_info() -> str:
    """
    Collect comprehensive system information for debugging purposes.

    ~~~
    • Gathers Python version and implementation details
    • Collects operating system and platform information
    • Gets current working directory and environment variables
    • Formats information in markdown for GitHub issue display
    ~~~

    Returns type: system_info (str) - formatted system information in markdown
    """
    try:
        # Get git info if available
        try:
            git_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=os.getcwd(), text=True
            ).strip()
            git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=os.getcwd(), text=True
            ).strip()[:8]
        except (subprocess.CalledProcessError, FileNotFoundError):
            git_branch = "N/A"
            git_commit = "N/A"

        system_info = f"""## System Information

**Python Information:**
- Python Version: {sys.version}
- Python Executable: {sys.executable}
- Platform: {platform.platform()}
- Architecture: {platform.architecture()[0]}

**Environment:**
- OS: {platform.system()} {platform.release()}
- Working Directory: {os.getcwd()}
- Git Branch: {git_branch}
- Git Commit: {git_commit}

**Timestamp:** {datetime.now().isoformat()}
"""
        return system_info

    except Exception as e:
        return f"## System Information\n\nError collecting system info: {str(e)}\n"


def format_stack_trace(exception: Optional[Exception] = None) -> str:
    """
    Format current or provided exception with full stack trace for debugging.

    ~~~
    • Captures current exception if none provided
    • Formats full stack trace with file paths and line numbers
    • Includes exception type and message details
    • Returns markdown-formatted traceback for GitHub issues
    ~~~

    Args:
        exception (Exception, optional): Exception to format, uses current if None

    Returns type: formatted_trace (str) - markdown formatted stack trace
    """
    if exception:
        # Format provided exception
        trace_lines = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        trace_text = "".join(trace_lines)
    else:
        # Get current exception if available
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            trace_text = traceback.format_exc()
        else:
            trace_text = (
                "No active exception found. Call this function within an except block."
            )

    return f"""## Stack Trace

```python
{trace_text}
```
"""


def create_debug_issue(
    title: str,
    description: str = "",
    exception: Optional[Exception] = None,
    additional_context: Optional[Dict[str, Any]] = None,
    labels: Optional[List[str]] = None,
    include_system_info: bool = True,
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a comprehensive GitHub issue for debugging with system info and stack traces.

    ~~~
    • Combines user description with system information
    • Formats stack traces and additional context
    • Creates GitHub issue with proper labels and formatting
    • Returns issue URL and metadata for follow-up
    ~~~

    Args:
        title (str): Issue title describing the problem
        description (str): Detailed description of the issue
        exception (Exception, optional): Exception to include in the issue
        additional_context (Dict[str, Any], optional): Extra debugging information
        labels (List[str], optional): GitHub labels for the issue
        include_system_info (bool): Include system information in the issue
        github_token (str, optional): GitHub personal access token

    Returns type: issue_result (Dict[str, Any]) - issue creation result
        with URL and metadata
    """
    # Build issue body
    body_parts = []

    # Add description
    if description:
        body_parts.append(f"## Description\n\n{description}\n")

    # Add stack trace if exception provided
    if exception:
        body_parts.append(format_stack_trace(exception))

    # Add additional context
    if additional_context:
        body_parts.append("## Additional Context\n")
        for key, value in additional_context.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            body_parts.append(f"**{key}:** \n```\n{value}\n```\n")

    # Add system information
    if include_system_info:
        body_parts.append(format_system_info())

    # Add footer
    body_parts.append(
        "---\n*This issue was created automatically by the issue_logger module.*"
    )

    body = "\n".join(body_parts)

    # Default labels for debug issues
    if labels is None:
        labels = ["bug", "auto-generated", "needs-investigation"]

    return create_github_issue(
        title=title, body=body, labels=labels, github_token=github_token
    )


def log_error_and_create_issue(
    error_title: str,
    error_description: str = "",
    auto_submit: bool = False,
    github_token: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Capture current exception and create GitHub issue for remote debugging.

    ~~~
    • Captures current exception context automatically
    • Prompts user for submission unless auto_submit is True
    • Creates comprehensive GitHub issue with all debugging info
    • Returns issue metadata for reference and follow-up
    ~~~

    Args:
        error_title (str): Title for the GitHub issue
        error_description (str): Additional description of the error context
        auto_submit (bool): If True, creates issue without prompting
        github_token (str, optional): GitHub personal access token

    Returns type: issue_info (Optional[Dict[str, Any]]) - issue creation
        result or None if cancelled
    """
    # Get current exception
    exc_info = sys.exc_info()
    current_exception = exc_info[1] if exc_info[0] is not None else None

    if not auto_submit:
        print(f"\n🐛 Error captured: {error_title}")
        print(f"Description: {error_description}")
        if current_exception:
            print(f"Exception: {type(current_exception).__name__}: {current_exception}")

        response = (
            input("\nCreate GitHub issue for this error? (y/N): ").strip().lower()
        )
        if response not in ["y", "yes"]:
            print("Issue creation cancelled.")
            return None

    try:
        result = create_debug_issue(
            title=error_title,
            description=error_description,
            exception=current_exception,
            github_token=github_token,
        )

        if result.get("success"):
            print("✅ Issue created successfully!")
            print(f"🔗 Issue URL: {result['issue_url']}")
            print(f"📝 Issue Number: #{result['issue_number']}")
        else:
            print(f"❌ Failed to create issue: {result.get('message', 'Unknown error')}")

        return result

    except Exception as e:
        print(f"❌ Error creating GitHub issue: {str(e)}")
        return None


def quick_issue(
    title: str, description: str = "", labels: Optional[List[str]] = None
) -> None:
    """
    Quick helper to create a simple GitHub issue with minimal setup.

    ~~~
    • Creates GitHub issue with title and description
    • Uses default labels if none provided
    • Prints issue URL for immediate access
    • Handles errors gracefully with user feedback
    ~~~

    Args:
        title (str): Issue title
        description (str): Issue description
        labels (List[str], optional): Issue labels

    Returns type: None (NoneType) - prints results and issue URL
    """
    try:
        result = create_github_issue(title=title, body=description, labels=labels)

        if result.get("success"):
            print(f"✅ Issue created: {result['issue_url']}")
        else:
            print(f"❌ Failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
