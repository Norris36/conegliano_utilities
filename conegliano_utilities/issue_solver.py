"""
Issue Solver - Solve GitHub issues with code integration

This module provides tools for:
1. Creating solution issues with code snippets
2. Linking solutions to existing issues
3. Managing issue workflow (open -> solved)
4. Integrating with GitHub Issues API
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from .global_issue_logger import list_repo_issues
from .code_extractor import extract_function_code


def get_open_issues(repo_owner: str = "Norris36", repo_name: str = "jensbay_utilities") -> List[Dict[str, Any]]:
    """
    Get all open issues from the jensbay_utilities repository.

    ~~~
    • Fetches open issues from GitHub API
    • Filters by state and labels if needed
    • Returns organized list with issue metadata
    • Handles API errors gracefully
    ~~~

    Args:
        repo_owner (str): Repository owner (default: Norris36)
        repo_name (str): Repository name (default: jensbay_utilities)

    Returns type: issues (List[Dict[str, Any]]) - list of open issue metadata
    """
    try:
        from .issue_config import get_github_token

        token = get_github_token()
        if not token:
            print("❌ No GitHub token found. Cannot fetch issues.")
            return []

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        params = {
            "state": "open",
            "per_page": 50  # Adjust as needed
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            issues = response.json()
            print(f"📋 Found {len(issues)} open issues")

            # Return simplified issue data
            simplified_issues = []
            for issue in issues:
                simplified_issues.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "body": issue["body"] or "",
                    "labels": [label["name"] for label in issue["labels"]],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                    "html_url": issue["html_url"],
                    "state": issue["state"]
                })

            return simplified_issues

        else:
            print(f"❌ Failed to fetch issues: {response.status_code}")
            print(f"Response: {response.text}")
            return []

    except Exception as e:
        print(f"❌ Error fetching issues: {e}")
        return []


def display_open_issues(limit: int = 10) -> None:
    """
    Display open issues in a readable format.

    ~~~
    • Fetches and formats open issues
    • Shows essential information for each issue
    • Limits display to specified number
    • Provides issue numbers for reference
    ~~~

    Args:
        limit (int): Maximum number of issues to display

    Returns type: None (NoneType) - prints formatted issue list
    """
    issues = get_open_issues()

    if not issues:
        print("📭 No open issues found")
        return

    print(f"📋 OPEN ISSUES (showing {min(limit, len(issues))} of {len(issues)}):")
    print("=" * 60)

    for i, issue in enumerate(issues[:limit]):
        print(f"#{issue['number']}: {issue['title']}")
        print(f"   Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}")
        print(f"   Created: {issue['created_at'][:10]}")
        print(f"   URL: {issue['html_url']}")
        print()

    if len(issues) > limit:
        print(f"... and {len(issues) - limit} more issues")


def issue_solved(
    solution_code: str,
    solution_title: str,
    original_issue_number: Optional[int] = None,
    function_name: Optional[str] = None,
    description: str = "",
    close_original: bool = False
) -> Dict[str, Any]:
    """
    Create a solution issue with code and optionally link to original issue.

    ~~~
    • Creates new issue with solution code and description
    • Links to original issue if provided
    • Optionally closes the original issue
    • Formats code properly for GitHub display
    ~~~

    Args:
        solution_code (str): The solution code (function, snippet, etc.)
        solution_title (str): Title for the solution issue
        original_issue_number (int, optional): Number of original issue being solved
        function_name (str, optional): Name of function if extracting from codebase
        description (str): Additional description of the solution
        close_original (bool): Whether to close the original issue

    Returns type: solution_result (Dict[str, Any]) - solution issue creation result
    """
    # If function_name provided, extract the code automatically
    if function_name and not solution_code:
        print(f"🔍 Extracting code for function: {function_name}")
        extraction_result = extract_function_code(function_name)

        if extraction_result.get("success"):
            solution_code = extraction_result["source_code"]
            if not description:
                file_location = extraction_result.get("relative_path", extraction_result.get("file_path", ""))
                description = f"Solution extracted from `{file_location}` at lines {extraction_result.get('start_line', '?')}-{extraction_result.get('end_line', '?')}"
            print(f"✅ Extracted {len(solution_code)} characters of code")
        else:
            print(f"❌ Could not extract function '{function_name}': {extraction_result.get('error', 'Unknown error')}")
            return extraction_result

    # Build solution issue body
    body_parts = []

    # Add link to original issue if provided
    if original_issue_number:
        body_parts.append(f"## Solution for Issue #{original_issue_number}\n")
        body_parts.append(f"This issue provides a solution for #{original_issue_number}.\n")

    # Add description
    if description:
        body_parts.append(f"## Description\n\n{description}\n")

    # Add solution code
    body_parts.append("## Solution Code\n")
    body_parts.append("```python")
    body_parts.append(solution_code)
    body_parts.append("```\n")

    # Add metadata
    body_parts.append("## Solution Details\n")
    body_parts.append(f"- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if function_name:
        body_parts.append(f"- **Function:** `{function_name}`")
    if original_issue_number:
        body_parts.append(f"- **Solves:** Issue #{original_issue_number}")
    body_parts.append("")

    body_parts.append("---")
    body_parts.append("*This solution was created using the issue_solver module.*")

    solution_body = "\n".join(body_parts)

    # Create the solution issue
    try:
        from .issue_logger import create_github_issue
        from .issue_config import get_github_token

        token = get_github_token()
        if not token:
            print("❌ No GitHub token found")
            return {"success": False, "error": "No GitHub token"}

        labels = ["solution", "code"]
        if original_issue_number:
            labels.append(f"solves-#{original_issue_number}")

        print(f"🌐 Creating solution issue: {solution_title}")

        result = create_github_issue(
            title=f"[SOLUTION] {solution_title}",
            body=solution_body,
            labels=labels,
            github_token=token,
            repo_owner="Norris36",
            repo_name="jensbay_utilities"
        )

        if result.get("success"):
            print(f"✅ Solution issue created: {result['issue_url']}")

            # Add comment to original issue if provided
            if original_issue_number:
                try:
                    comment_result = add_comment_to_issue(
                        issue_number=original_issue_number,
                        comment=f"💡 **Solution Available**\n\nA solution for this issue has been created: #{result['issue_number']}\n\nSee: {result['issue_url']}"
                    )

                    if comment_result.get("success"):
                        print(f"✅ Added solution link to original issue #{original_issue_number}")
                    else:
                        print(f"⚠️  Could not comment on original issue: {comment_result.get('error')}")

                except Exception as e:
                    print(f"⚠️  Could not comment on original issue: {e}")

            # Close original issue if requested
            if close_original and original_issue_number:
                try:
                    close_result = close_issue(original_issue_number)
                    if close_result.get("success"):
                        print(f"✅ Closed original issue #{original_issue_number}")
                    else:
                        print(f"⚠️  Could not close original issue: {close_result.get('error')}")
                except Exception as e:
                    print(f"⚠️  Could not close original issue: {e}")

            result.update({
                "original_issue": original_issue_number,
                "function_name": function_name,
                "solution_code": solution_code,
                "closed_original": close_original
            })

            return result

        else:
            print(f"❌ Failed to create solution issue: {result.get('message', 'Unknown error')}")
            return result

    except Exception as e:
        print(f"❌ Error creating solution issue: {e}")
        return {"success": False, "error": str(e)}


def add_comment_to_issue(issue_number: int, comment: str, repo_owner: str = "Norris36", repo_name: str = "jensbay_utilities") -> Dict[str, Any]:
    """
    Add a comment to an existing GitHub issue.

    ~~~
    • Posts comment to specified issue
    • Handles GitHub API authentication
    • Returns success status and comment metadata
    • Used for linking solutions to original issues
    ~~~

    Args:
        issue_number (int): Issue number to comment on
        comment (str): Comment text (supports markdown)
        repo_owner (str): Repository owner
        repo_name (str): Repository name

    Returns type: comment_result (Dict[str, Any]) - comment creation result
    """
    try:
        from .issue_config import get_github_token

        token = get_github_token()
        if not token:
            return {"success": False, "error": "No GitHub token"}

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

        data = {"body": comment}

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            comment_data = response.json()
            return {
                "success": True,
                "comment_id": comment_data["id"],
                "comment_url": comment_data["html_url"],
                "created_at": comment_data["created_at"]
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def close_issue(issue_number: int, repo_owner: str = "Norris36", repo_name: str = "jensbay_utilities") -> Dict[str, Any]:
    """
    Close a GitHub issue.

    ~~~
    • Updates issue state to 'closed'
    • Handles GitHub API authentication
    • Returns success status and updated issue data
    • Used when issue is resolved
    ~~~

    Args:
        issue_number (int): Issue number to close
        repo_owner (str): Repository owner
        repo_name (str): Repository name

    Returns type: close_result (Dict[str, Any]) - close operation result
    """
    try:
        from .issue_config import get_github_token

        token = get_github_token()
        if not token:
            return {"success": False, "error": "No GitHub token"}

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

        data = {"state": "closed"}

        response = requests.patch(url, json=data, headers=headers)

        if response.status_code == 200:
            issue_data = response.json()
            return {
                "success": True,
                "issue_number": issue_number,
                "state": issue_data["state"],
                "closed_at": issue_data.get("closed_at"),
                "html_url": issue_data["html_url"]
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def quick_solve(function_name: str, solution_title: str, issue_number: Optional[int] = None) -> None:
    """
    Quick function to solve an issue with existing function code.

    ~~~
    • Extracts function code automatically
    • Creates solution issue with formatted code
    • Links to original issue if provided
    • Simplified interface for rapid issue resolution
    ~~~

    Args:
        function_name (str): Name of function containing the solution
        solution_title (str): Title for the solution issue
        issue_number (int, optional): Original issue number to link

    Returns type: None (NoneType) - prints results to console
    """
    print(f"🔧 Creating solution with function '{function_name}'...")

    result = issue_solved(
        solution_code="",  # Will be extracted automatically
        solution_title=solution_title,
        original_issue_number=issue_number,
        function_name=function_name,
        description=f"Solution implemented in the `{function_name}` function."
    )

    if result.get("success"):
        print(f"✅ Solution created successfully!")
        if issue_number:
            print(f"🔗 Linked to original issue #{issue_number}")
    else:
        print(f"❌ Solution creation failed: {result.get('error', 'Unknown error')}")


# Convenience aliases
solve = issue_solved
quick_solution = quick_solve
list_issues = display_open_issues