"""
CodeFRAME CLI - The next-generation IDE for autonomous development.

Orchestrate AI-driven development across repos, issues, PRs, and deployments.
"""

import argparse
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="codeframe",
        description="CodeFRAME CLI - The next-generation IDE for autonomous development",
        epilog="For more help on a specific object, run: codeframe <OBJECT> --help",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="codeframe 0.1.0",
    )

    # Create subparsers for objects (issues, prs, repos, etc.)
    subparsers = parser.add_subparsers(
        title="objects",
        description="Objects you can work with",
        dest="object",
        required=False,
        help="Object type (issues, prs, repos, etc.)",
    )

    # Import object handlers
    from .cli_issues import setup_issues_parser
    from .cli_repos import setup_repos_parser

    # Setup each object's commands
    setup_issues_parser(subparsers)
    setup_repos_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # If no object specified, show quick status
    if not args.object:
        print("CodeFRAME CLI - The next-generation IDE for autonomous development")
        print()
        print("Usage: codeframe <OBJECT> <COMMAND> [options]")
        print("       cf <OBJECT> <COMMAND> [options]")
        print()
        print("Objects:")
        print("  issues    - Manage GitHub issues and planning")
        print("  repos     - Repository health and status")
        print("  prs       - Pull request management (coming soon)")
        print("  ideas     - Idea generation (coming soon)")
        print()
        print("Run 'codeframe <OBJECT> --help' for object-specific commands")
        print("Run 'codeframe --help' for full help")
        return 0

    # Execute the command
    if hasattr(args, "func"):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return 130
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
