"""Issues object - Manage GitHub issues and automated planning."""

import subprocess
import sys


def setup_issues_parser(subparsers):
    """Setup the 'issues' object parser with its commands."""
    issues_parser = subparsers.add_parser(
        "issues",
        help="Manage GitHub issues and automated planning",
        description="Work with GitHub issues across your repositories",
    )

    issues_subparsers = issues_parser.add_subparsers(
        title="commands",
        description="Available commands for issues",
        dest="command",
        required=True,
        help="Command to run",
    )

    # cf issues view [--live] [--global]
    view_parser = issues_subparsers.add_parser(
        "view",
        help="Show issues dashboard",
        description="Display TUI dashboard of issues needing plans",
    )
    view_parser.add_argument(
        "--live",
        action="store_true",
        help="Live updating dashboard (auto-refresh)",
    )
    view_parser.add_argument(
        "--refresh",
        type=int,
        default=5,
        metavar="SECONDS",
        help="Refresh interval for live mode (default: 5)",
    )
    view_parser.add_argument(
        "--global",
        dest="global_scope",
        action="store_true",
        help="Show issues across all repos (not implemented yet)",
    )
    view_parser.set_defaults(func=cmd_issues_view)

    # cf issues create-plan [--global] [--repo REPO]
    create_plan_parser = issues_subparsers.add_parser(
        "create-plan",
        help="Generate plans for issues",
        description="Scan repos and queue issues for Traycer planning",
    )
    create_plan_parser.add_argument(
        "--global",
        dest="global_scope",
        action="store_true",
        help="Scan all repos",
    )
    create_plan_parser.add_argument(
        "--repo",
        metavar="REPO",
        help="Specific repo to scan (format: owner/repo)",
    )
    create_plan_parser.set_defaults(func=cmd_issues_create_plan)

    # cf issues process
    process_parser = issues_subparsers.add_parser(
        "process",
        help="Process issue planning queue",
        description="Process queued issues (respects rate limits)",
    )
    process_parser.set_defaults(func=cmd_issues_process)

    # cf issues status
    status_parser = issues_subparsers.add_parser(
        "status",
        help="Quick status summary",
        description="Show quick status of issue queue",
    )
    status_parser.set_defaults(func=cmd_issues_status)


def cmd_issues_view(args):
    """Show issues dashboard."""
    from .dashboard import main as dashboard_main

    # Build arguments for dashboard
    dashboard_args = []
    if args.live:
        dashboard_args.append("--live")
        dashboard_args.append("--refresh")
        dashboard_args.append(str(args.refresh))

    if args.global_scope:
        print("Note: --global not yet implemented, showing current repo queue")

    # Run dashboard
    sys.argv = ["dashboard"] + dashboard_args
    return dashboard_main()


def cmd_issues_create_plan(args):
    """Generate plans for issues via Traycer."""
    from .scanner import main as scanner_main

    if args.repo:
        print(f"Note: --repo filter not yet implemented, scanning all repos")

    if not args.global_scope:
        print("Scanning all user repositories for rate-limited issues...")
        print("(Use --global to explicitly scan all repos)")

    # Run scanner
    return scanner_main()


def cmd_issues_process(args):
    """Process issue planning queue."""
    from .processor import main as processor_main

    # Run processor
    return processor_main()


def cmd_issues_status(args):
    """Show quick status summary."""
    from .database import Database
    from .slot_calculator import SlotCalculator

    db = Database("traycer_queue.db")
    calculator = SlotCalculator(db)

    # Get queue stats
    ready_issues = db.get_issues_ready_for_processing()

    # Get slot availability
    slot_status = calculator.calculate_available_slots()

    # Print summary
    print(f"Issues Queue Status:")
    print(f"  Ready now: {len(ready_issues)}")
    print(f"  Available slots: {slot_status.available_slots}/{slot_status.total_slots}")
    if slot_status.consumed_slots > 0:
        print(f"  Consumed slots: {slot_status.consumed_slots}")

    return 0
