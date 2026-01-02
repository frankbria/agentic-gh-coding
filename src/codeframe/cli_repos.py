"""Repos object - Repository health and status management."""

import subprocess
import sys


def setup_repos_parser(subparsers):
    """Setup the 'repos' object parser with its commands."""
    repos_parser = subparsers.add_parser(
        "repos",
        help="Repository health and status",
        description="Manage and monitor repository health",
    )

    repos_subparsers = repos_parser.add_subparsers(
        title="commands",
        description="Available commands for repos",
        dest="command",
        required=True,
        help="Command to run",
    )

    # cf repos health
    health_parser = repos_subparsers.add_parser(
        "health",
        help="System health check",
        description="Check health of cron, services, and system components",
    )
    health_parser.set_defaults(func=cmd_repos_health)

    # cf repos status
    status_parser = repos_subparsers.add_parser(
        "status",
        help="Repository status",
        description="Show status across all repositories (not implemented yet)",
    )
    status_parser.set_defaults(func=cmd_repos_status)


def cmd_repos_health(args):
    """Check system health."""
    print("System Health Check")
    print("=" * 50)
    print()

    # Check cron service
    print("Cron Service:")
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "cron"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip() == "active":
            print("  ✓ Cron is running")
        else:
            print("  ✗ Cron is not running")
    except Exception as e:
        print(f"  ✗ Could not check cron status: {e}")

    print()

    # Check database
    print("Database:")
    try:
        from .database import Database

        db = Database("traycer_queue.db")
        ready = db.get_issues_ready_for_processing()
        print(f"  ✓ Database accessible ({len(ready)} issues ready)")
    except Exception as e:
        print(f"  ✗ Database error: {e}")

    print()

    # Check slot availability
    print("Slot Availability:")
    try:
        from .database import Database
        from .slot_calculator import SlotCalculator

        db = Database("traycer_queue.db")
        calculator = SlotCalculator(db)
        slot_status = calculator.calculate_available_slots()
        print(f"  ✓ {slot_status.available_slots}/{slot_status.total_slots} slots available")
        if slot_status.consumed_slots > 0:
            print(f"    ({slot_status.consumed_slots} slots consumed in last 30 min)")
    except Exception as e:
        print(f"  ✗ Could not calculate slots: {e}")

    print()

    # Check GitHub CLI
    print("GitHub CLI:")
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            print("  ✓ GitHub CLI authenticated")
        else:
            print("  ✗ GitHub CLI not authenticated")
    except FileNotFoundError:
        print("  ✗ GitHub CLI (gh) not installed")
    except Exception as e:
        print(f"  ✗ Could not check gh status: {e}")

    print()
    print("=" * 50)
    return 0


def cmd_repos_status(args):
    """Show repository status."""
    print("Repository Status (coming soon)")
    print()
    print("This command will show:")
    print("  - All repos with open issues")
    print("  - Issues in various states (planning, building, reviewing)")
    print("  - PRs awaiting review or merge")
    print("  - Deployment status")
    return 0
