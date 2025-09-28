"""
Local Issue Storage - Store issues locally when GitHub access is restricted
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid


def get_local_issues_dir() -> Path:
    """
    Get or create local directory for storing issues.

    ~~~
    • Creates issues directory in user home or project root
    • Ensures directory exists with proper permissions
    • Returns Path object for issues storage
    • Falls back to temp directory if needed
    ~~~

    Returns type: issues_dir (Path) - directory path for storing local issues
    """
    # Try user home first
    home_dir = Path.home() / '.local_issues'

    # Try project directory as fallback
    project_dir = Path.cwd() / 'local_issues'

    # Try temp directory as last resort
    temp_dir = Path('/tmp') / 'local_issues' if os.name != 'nt' else Path(os.environ.get('TEMP', '.')) / 'local_issues'

    for directory in [home_dir, project_dir, temp_dir]:
        try:
            directory.mkdir(exist_ok=True, mode=0o755)
            # Test write access
            test_file = directory / '.test'
            test_file.write_text('test')
            test_file.unlink()
            return directory
        except Exception:
            continue

    # If all else fails, use current directory
    fallback_dir = Path('.') / 'local_issues'
    fallback_dir.mkdir(exist_ok=True)
    return fallback_dir


def store_issue_locally(
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
    priority: str = "medium",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store issue data locally when GitHub access is not available.

    ~~~
    • Creates JSON file with issue details and metadata
    • Generates unique ID and timestamp for tracking
    • Stores in local issues directory with organized structure
    • Returns issue metadata for reference and follow-up
    ~~~

    Args:
        title (str): Issue title
        body (str): Issue description and details
        labels (List[str], optional): Issue labels
        priority (str): Issue priority (low, medium, high, critical)
        additional_data (Dict[str, Any], optional): Extra debugging data

    Returns type: issue_info (Dict[str, Any]) - local issue metadata and file path
    """
    try:
        issues_dir = get_local_issues_dir()

        # Generate unique ID and timestamp
        issue_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y%m%d_%H%M%S")

        # Create issue data
        issue_data = {
            "id": issue_id,
            "title": title,
            "body": body,
            "labels": labels or [],
            "priority": priority,
            "status": "open",
            "created_at": timestamp.isoformat(),
            "additional_data": additional_data or {},
            "source": "local_issue_store"
        }

        # Create filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
        filename = f"{date_str}_{issue_id}_{safe_title.replace(' ', '_')}.json"

        # Save to file
        file_path = issues_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(issue_data, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "issue_id": issue_id,
            "file_path": str(file_path),
            "created_at": timestamp.isoformat(),
            "title": title,
            "storage_type": "local"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "storage_type": "local"
        }


def list_local_issues(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all locally stored issues with optional status filtering.

    ~~~
    • Scans local issues directory for JSON files
    • Loads and parses issue metadata
    • Filters by status if specified (open, closed, in_progress)
    • Returns sorted list of issues by creation date
    ~~~

    Args:
        status (str, optional): Filter by issue status

    Returns type: issues_list (List[Dict[str, Any]]) - list of issue metadata
    """
    try:
        issues_dir = get_local_issues_dir()
        issues = []

        for file_path in issues_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    issue_data = json.load(f)

                # Add file path for reference
                issue_data['file_path'] = str(file_path)

                # Filter by status if specified
                if status is None or issue_data.get('status') == status:
                    issues.append(issue_data)

            except Exception:
                continue  # Skip corrupted files

        # Sort by creation date (newest first)
        issues.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return issues

    except Exception:
        return []


def sync_local_issues_to_github(github_token: str, repo_owner: str = "Norris36", repo_name: str = "jensbay_utilities") -> Dict[str, Any]:
    """
    Sync locally stored issues to GitHub when access becomes available.

    ~~~
    • Reads all local issues from storage directory
    • Creates GitHub issues for each local issue
    • Updates local files with GitHub issue numbers
    • Moves synced issues to archive folder
    ~~~

    Args:
        github_token (str): GitHub personal access token
        repo_owner (str): GitHub repository owner
        repo_name (str): GitHub repository name

    Returns type: sync_result (Dict[str, Any]) - summary of sync operation results
    """
    from .issue_logger import create_github_issue

    try:
        local_issues = list_local_issues(status="open")
        results = {
            "total_issues": len(local_issues),
            "synced": 0,
            "failed": 0,
            "errors": []
        }

        for issue in local_issues:
            try:
                # Create GitHub issue
                github_result = create_github_issue(
                    title=f"[Local] {issue['title']}",
                    body=f"{issue['body']}\n\n---\n*Originally created locally at {issue['created_at']}*",
                    labels=issue.get('labels', []) + ['synced-from-local'],
                    github_token=github_token,
                    repo_owner=repo_owner,
                    repo_name=repo_name
                )

                if github_result.get("success"):
                    # Update local issue with GitHub info
                    issue['github_issue_number'] = github_result['issue_number']
                    issue['github_url'] = github_result['issue_url']
                    issue['status'] = 'synced'
                    issue['synced_at'] = datetime.now().isoformat()

                    # Save updated issue
                    with open(issue['file_path'], 'w', encoding='utf-8') as f:
                        json.dump(issue, f, indent=2, ensure_ascii=False)

                    results["synced"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Issue '{issue['title']}': {github_result.get('message', 'Unknown error')}")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Issue '{issue['title']}': {str(e)}")

        return results

    except Exception as e:
        return {
            "total_issues": 0,
            "synced": 0,
            "failed": 0,
            "errors": [f"Sync operation failed: {str(e)}"]
        }


def create_local_debug_issue(
    title: str,
    description: str = "",
    exception: Optional[Exception] = None,
    additional_context: Optional[Dict[str, Any]] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a comprehensive local issue with debug information.

    ~~~
    • Combines issue description with system information
    • Formats exception details and stack traces
    • Stores comprehensive debugging data locally
    • Returns issue metadata for immediate reference
    ~~~

    Args:
        title (str): Issue title
        description (str): Issue description
        exception (Exception, optional): Exception to include
        additional_context (Dict[str, Any], optional): Extra debug data
        priority (str): Issue priority level

    Returns type: issue_result (Dict[str, Any]) - local issue creation result
    """
    from .issue_logger import format_system_info, format_stack_trace

    # Build comprehensive issue body
    body_parts = []

    if description:
        body_parts.append(f"## Description\n\n{description}\n")

    if exception:
        body_parts.append(format_stack_trace(exception))

    if additional_context:
        body_parts.append("## Additional Context\n")
        for key, value in additional_context.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            body_parts.append(f"**{key}:**\n```\n{value}\n```\n")

    # Add system information
    body_parts.append(format_system_info())
    body_parts.append("---\n*This issue was created locally by the issue_logger module.*")

    body = "\n".join(body_parts)

    return store_issue_locally(
        title=title,
        body=body,
        labels=["bug", "local-debug", "needs-investigation"],
        priority=priority,
        additional_data=additional_context
    )