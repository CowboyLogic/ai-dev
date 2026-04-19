#!/usr/bin/env python3
"""
Git Commit Message Generator

This script analyzes git changes and suggests commit messages
following conventional commit standards.
"""

import subprocess
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

def run_git_command(command: List[str]) -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(['git'] + command,
                              capture_output=True,
                              text=True,
                              check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        return ""

def get_staged_changes() -> str:
    """Get the diff of staged changes."""
    return run_git_command(['diff', '--cached'])

def get_unstaged_changes() -> str:
    """Get the diff of unstaged changes."""
    return run_git_command(['diff'])

def analyze_changes(diff: str) -> dict:
    """Analyze the diff to determine change characteristics."""
    analysis = {
        'has_new_files': False,
        'has_deleted_files': False,
        'has_modified_files': False,
        'has_renamed_files': False,
        'modified_extensions': set(),
        'affected_paths': set(),
        'lines_added': 0,
        'lines_deleted': 0,
        'test_files': 0,
        'config_files': 0,
        'doc_files': 0
    }

    lines = diff.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # File header
        if line.startswith('diff --git'):
            match = re.search(r'diff --git a/(.+) b/(.+)', line)
            if match:
                old_path = match.group(1)
                new_path = match.group(2)
                analysis['affected_paths'].add(new_path)

                # Check file extension
                ext = Path(new_path).suffix.lower()
                if ext:
                    analysis['modified_extensions'].add(ext)

                # Categorize files
                if any(test in new_path.lower() for test in ['test', 'spec', '__tests__']):
                    analysis['test_files'] += 1
                elif any(config in new_path.lower() for config in ['config', 'package.json', 'requirements.txt', '.env']):
                    analysis['config_files'] += 1
                elif any(doc in new_path.lower() for doc in ['readme', 'docs', '.md', '.txt']):
                    analysis['doc_files'] += 1

        # File status
        elif line.startswith('new file mode'):
            analysis['has_new_files'] = True
        elif line.startswith('deleted file mode'):
            analysis['has_deleted_files'] = True
        elif line.startswith('rename'):
            analysis['has_renamed_files'] = True

        # Count lines
        elif line.startswith('+') and not line.startswith('+++'):
            analysis['lines_added'] += 1
        elif line.startswith('-') and not line.startswith('---'):
            analysis['lines_deleted'] += 1

        i += 1

    return analysis

def determine_commit_type(analysis: dict) -> str:
    """Determine the conventional commit type based on analysis."""
    if analysis['test_files'] > 0 and analysis['test_files'] == len(analysis['affected_paths']):
        return 'test'
    elif analysis['doc_files'] > 0 and analysis['doc_files'] == len(analysis['affected_paths']):
        return 'docs'
    elif analysis['config_files'] > 0 and any(ext in ['.json', '.yml', '.yaml', '.toml', '.ini'] for ext in analysis['modified_extensions']):
        return 'chore'
    elif analysis['has_new_files'] and not analysis['has_modified_files'] and not analysis['has_deleted_files']:
        return 'feat'
    elif analysis['has_deleted_files'] and not analysis['has_new_files'] and not analysis['has_modified_files']:
        return 'chore'
    elif analysis['lines_added'] > analysis['lines_deleted'] * 2:
        return 'feat'
    elif analysis['lines_deleted'] > analysis['lines_added'] * 2:
        return 'refactor'
    else:
        return 'fix'

def determine_scope(analysis: dict) -> str:
    """Determine the scope based on affected paths."""
    if not analysis['affected_paths']:
        return ''

    # Common scopes based on directory structure
    scopes = []
    for path in analysis['affected_paths']:
        parts = Path(path).parts
        if len(parts) > 1:
            # Use first directory as scope
            scope = parts[0].lower()
            if scope not in ['src', 'lib', 'app', 'test', 'tests', 'docs']:
                scopes.append(scope)

    # Return most common scope or first one
    if scopes:
        return scopes[0] if len(scopes) == 1 else max(set(scopes), key=scopes.count)

    return ''

def generate_subject(type_hint: str, scope: str, analysis: dict) -> str:
    """Generate a commit subject line."""
    type_str = type_hint

    if scope:
        type_str += f"({scope})"

    # Generate description based on analysis
    if type_hint == 'feat':
        if analysis['has_new_files']:
            desc = "add new functionality"
        else:
            desc = "implement new feature"
    elif type_hint == 'fix':
        desc = "fix issue"
    elif type_hint == 'docs':
        desc = "update documentation"
    elif type_hint == 'test':
        desc = "add tests"
    elif type_hint == 'refactor':
        desc = "refactor code"
    elif type_hint == 'style':
        desc = "update code style"
    elif type_hint == 'chore':
        desc = "update configuration"
    else:
        desc = "update code"

    return f"{type_str}: {desc}"

def generate_commit_message() -> None:
    """Main function to generate commit message."""
    # Check if there are staged changes
    staged_diff = get_staged_changes()
    if not staged_diff:
        print("No staged changes found. Stage your changes first with 'git add'.")
        return

    # Analyze changes
    analysis = analyze_changes(staged_diff)

    # Determine commit characteristics
    commit_type = determine_commit_type(analysis)
    scope = determine_scope(analysis)

    # Generate subject
    subject = generate_subject(commit_type, scope, analysis)

    print("Suggested commit message:")
    print("=" * 50)
    print(subject)
    print()
    print("Analysis:")
    print(f"- Type: {commit_type}")
    print(f"- Scope: {scope or 'general'}")
    print(f"- Files changed: {len(analysis['affected_paths'])}")
    print(f"- Lines added: {analysis['lines_added']}")
    print(f"- Lines deleted: {analysis['lines_deleted']}")
    print(f"- New files: {analysis['has_new_files']}")
    print(f"- Test files: {analysis['test_files']}")
    print(f"- Config files: {analysis['config_files']}")
    print(f"- Doc files: {analysis['doc_files']}")
    print()
    print("To use this message:")
    print(f'git commit -m "{subject}"')

def main():
    """Entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Git Commit Message Generator")
        print()
        print("Analyzes staged git changes and suggests a commit message")
        print("following conventional commit standards.")
        print()
        print("Usage:")
        print("  python commit-generator.py    # Generate commit message")
        print("  python commit-generator.py --help  # Show this help")
        return

    generate_commit_message()

if __name__ == '__main__':
    main()