#!/usr/bin/env python3
"""
GLOBAL UTILITIES GUIDE

This file demonstrates the new global features that work from anywhere:
1. Global issue logger (always creates issues in jensbay_utilities repo)
2. Function code extractor (copy any function code)
3. Issue solver (solve issues with code integration)

These utilities work from ANY directory on your system!
"""

def demo_global_issue_logger():
    """
    Demonstrate global issue logging from anywhere on your system
    """
    print("🌐 GLOBAL ISSUE LOGGER DEMO")
    print("=" * 50)

    # Import the global utilities
    from conegliano_utilities import global_issue, issue, quick_global_issue

    print("📍 Current working directory:", end=" ")
    import os
    print(os.getcwd())

    # Example 1: Simple global issue
    print("\n1️⃣ Creating simple global issue...")
    try:
        # This creates an issue in jensbay_utilities repo regardless of where you are
        result = global_issue(
            "Global test issue",
            "This issue was created from outside the jensbay_utilities repo",
            labels=["test", "global"]
        )
        if result.get("success"):
            print(f"✅ Issue created: {result.get('issue_url', 'Success')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 2: Using the short alias
    print("\n2️⃣ Using short alias 'issue()'...")
    try:
        # Short alias for quick usage
        issue("Quick global issue", "Testing the short alias function")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 3: Quick global issue (minimal interface)
    print("\n3️⃣ Quick global issue...")
    try:
        quick_global_issue("Minimal test", "Testing minimal interface")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n💡 All issues are created in jensbay_utilities repo with context about your current location!")


def demo_code_extractor():
    """
    Demonstrate function code extraction and clipboard copying
    """
    print("\n🔍 CODE EXTRACTOR DEMO")
    print("=" * 50)

    from conegliano_utilities import get_code, copy_func, find_func, extract_function_code

    # Example 1: Quick code extraction
    print("1️⃣ Quick function copy (copies to clipboard)...")
    try:
        get_code("global_issue")  # Copies the global_issue function to clipboard
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 2: Detailed function extraction
    print("\n2️⃣ Detailed function extraction...")
    try:
        result = extract_function_code("issue_solved")
        if result.get("success"):
            print(f"✅ Found function in: {result.get('relative_path', result.get('file_path'))}")
            print(f"📍 Lines: {result.get('start_line')}-{result.get('end_line')}")
            print(f"📝 Code length: {len(result.get('source_code', ''))} characters")
            if result.get("total_matches", 0) > 1:
                print(f"💡 Found {result['total_matches']} matches total")
        else:
            print(f"❌ Not found: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 3: Copy with metadata
    print("\n3️⃣ Copy function with metadata...")
    try:
        result = copy_func("quick_global_issue", include_metadata=True)
        if result.get("success") and result.get("copied_to_clipboard"):
            print("✅ Function copied to clipboard with metadata!")
            print("📋 Ready to paste in any editor")
        else:
            print("⚠️  Function found but clipboard copy may have failed")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_issue_solver():
    """
    Demonstrate issue solving with code integration
    """
    print("\n🔧 ISSUE SOLVER DEMO")
    print("=" * 50)

    from conegliano_utilities import list_issues, solve, quick_solve, issue_solved

    # Example 1: List open issues
    print("1️⃣ Listing open issues...")
    try:
        list_issues(limit=5)  # Show first 5 open issues
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 2: Solve issue with function code
    print("\n2️⃣ Solving issue with function code...")
    try:
        # This extracts the 'global_issue' function and creates a solution issue
        result = issue_solved(
            solution_code="",  # Will be extracted automatically
            solution_title="Solution: Global issue logging implementation",
            function_name="global_issue",  # Extract this function's code
            description="Implementation of global issue logging that works from any directory",
            original_issue_number=None  # Set to actual issue number if solving a specific issue
        )
        if result.get("success"):
            print(f"✅ Solution issue created: {result.get('issue_url')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 3: Quick solve (simplified interface)
    print("\n3️⃣ Quick solve with function...")
    try:
        # Quick way to solve an issue with existing function
        quick_solve(
            function_name="copy_function_to_clipboard",
            solution_title="Code extraction utility implementation",
            issue_number=None  # Set to actual issue number
        )
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_real_world_workflow():
    """
    Demonstrate real-world workflow combining all utilities
    """
    print("\n🚀 REAL-WORLD WORKFLOW DEMO")
    print("=" * 50)

    print("Scenario: You're working in another project and encounter a bug...")

    # Step 1: Create global issue from anywhere
    print("\n📝 Step 1: Create issue from current working directory")
    try:
        from conegliano_utilities import global_issue
        issue_result = global_issue(
            "Bug in data processing function",
            "Function fails when processing large datasets. Need to implement chunking.",
            labels=["bug", "performance", "data-processing"],
            priority="high"
        )
        print(f"Issue created: {issue_result.get('success', False)}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 2: Later, when you have a solution, extract the code
    print("\n🔍 Step 2: Extract solution function code")
    try:
        from conegliano_utilities import extract_function_code
        func_result = extract_function_code("create_dataframe_from_folder_sizes")
        if func_result.get("success"):
            print(f"✅ Found solution function: {func_result.get('relative_path')}")
        else:
            print(f"Function not found: {func_result.get('error')}")
    except Exception as e:
        print(f"Error: {e}")

    # Step 3: Create solution issue with the code
    print("\n✅ Step 3: Create solution issue")
    try:
        from conegliano_utilities import issue_solved
        solution_result = issue_solved(
            solution_code="",  # Extract automatically
            solution_title="Data processing chunking implementation",
            function_name="create_dataframe_from_folder_sizes",
            description="This function demonstrates proper chunking for large datasets",
            original_issue_number=None  # Would link to the issue from Step 1
        )
        print(f"Solution created: {solution_result.get('success', False)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n💡 Complete workflow: Issue → Code → Solution → Link!")


def show_global_context():
    """
    Show what context information is automatically included
    """
    print("\n📍 GLOBAL CONTEXT DEMO")
    print("=" * 50)

    try:
        from conegliano_utilities import global_issue_context

        context = global_issue_context()
        print("🌍 Current working context:")

        repo_info = context.get("repo_info", {})
        print(f"📁 Current directory: {repo_info.get('current_dir', 'unknown')}")
        print(f"📂 Git repository: {repo_info.get('repo_name', 'not in git repo')}")
        print(f"🌿 Git branch: {context.get('git_info', {}).get('current_branch', 'unknown')}")
        print(f"🐍 Python version: {context.get('system_info', {}).get('python_version', 'unknown')}")

        if context.get("git_info", {}).get("has_changes"):
            print("⚠️  Working directory has uncommitted changes")
        else:
            print("✅ Working directory is clean")

        print("\n💡 This context is automatically included in global issues!")

    except Exception as e:
        print(f"❌ Error getting context: {e}")


def main():
    """
    Run all demonstrations
    """
    print("🎯 GLOBAL UTILITIES DEMONSTRATION")
    print("=" * 80)
    print("These utilities work from ANY directory on your system!")
    print("They always target the jensbay_utilities repository.")
    print("=" * 80)

    # Show current context first
    show_global_context()

    # Run all demos
    demo_global_issue_logger()
    demo_code_extractor()
    demo_issue_solver()
    demo_real_world_workflow()

    print("\n" + "=" * 80)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("💡 QUICK REFERENCE FOR GLOBAL USAGE:")
    print("   • issue('Title', 'Description')           # Create global issue")
    print("   • get_code('function_name')               # Copy function to clipboard")
    print("   • list_issues()                           # Show open issues")
    print("   • solve('function_name', 'Solution')      # Solve issue with code")
    print("   • quick_solve('func', 'title', issue_num) # Quick solution")
    print("")
    print("🌐 All functions work from anywhere and target jensbay_utilities repo!")
    print("📍 Context about your current location is automatically included.")


if __name__ == "__main__":
    main()