# CodeFRAME CLI

**The next-generation IDE for autonomous AI development**

CodeFRAME CLI orchestrates AI-driven development across repos, issues, PRs, and deployments. Work with high-level entities (ideas, issues, features) instead of files and folders.

![Status](https://img.shields.io/badge/status-alpha-yellow)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-AGPL--3.0-green)

---

## Overview

CodeFRAME CLI provides a unified command-line interface for managing AI-powered development workflows across multiple repositories. Instead of context-switching between repos, tools, and dashboards, use a single `cf` command to orchestrate everything.

**Current capabilities:**
- 🤖 **Automated Issue Planning**: Traycer AI integration with intelligent rate limit management
- 📊 **Live Monitoring**: Real-time TUI dashboard for queue status and processing
- 🔄 **Multi-Repo Orchestration**: Scan and manage issues across all your repositories
- ⚡ **Smart Scheduling**: Circuit breakers, retry logic, and slot-based rate limiting
- 🏥 **Health Monitoring**: System health checks for cron, database, and services

**Coming soon:**
- PR review automation
- Cross-repo status tracking
- AI-powered idea generation
- Deployment monitoring
- CodeFRAME agent integration

---

## Core Concepts

CodeFRAME CLI uses an **object-command** pattern inspired by Git and Kubernetes:

```
cf <OBJECT> <COMMAND> [options]
```

### Objects (Entities)

- **issues** - GitHub issues and automated planning
- **repos** - Repository health and status
- **prs** - Pull request management *(coming soon)*
- **ideas** - AI-powered idea generation *(coming soon)*

### Commands (Actions)

Commands are specific to each object. Run `cf <OBJECT> --help` to see available commands.

---

## Quick Start

### Installation

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Install global commands
chmod +x codeframe
cp codeframe ~/.local/bin/
ln -sf ~/.local/bin/codeframe ~/.local/bin/cf

# Configure environment
cp .env.example .env
# Edit .env to add your GitHub token and username
```

### Environment Variables

Create a `.env` file with:

```bash
GITHUB_TOKEN=<your-github-token>      # Needs 'repo' scope
GITHUB_USERNAME=<your-username>       # For issue assignment
```

### First Steps

```bash
# Check system health
cf repos health

# Scan repos for issues needing plans
cf issues create-plan --global

# View the dashboard
cf issues view --live

# Process the queue
cf issues process
```

---

## Command Reference

### Issues Management

Manage GitHub issues with automated Traycer AI planning:

```bash
# View issues dashboard
cf issues view                    # Static dashboard
cf issues view --live             # Live auto-refresh
cf issues view --live --refresh 10  # Custom refresh rate

# Generate plans for issues
cf issues create-plan --global    # Scan all repos for rate-limited issues
cf issues create-plan --repo owner/name  # Scan specific repo (coming soon)

# Process planning queue
cf issues process                 # Process queued issues (respects rate limits)

# Quick status
cf issues status                  # Show queue status and available slots
```

**What it does:**
- Scans your GitHub repos for Traycer rate limit comments
- Queues issues for re-analysis with intelligent timing
- Processes queue while respecting 15-slot rate limit (1 slot/30min)
- Detects external Traycer activity to avoid conflicts
- Toggles issue assignment to trigger Traycer re-analysis

### Repository Health

Monitor system health and repository status:

```bash
# Health check
cf repos health                   # Check cron, database, slots, GitHub CLI

# Repository status
cf repos status                   # (Coming soon) Cross-repo status view
```

**Health check includes:**
- ✓ Cron service status
- ✓ Database connectivity
- ✓ Slot availability
- ✓ GitHub CLI authentication

---

## Architecture

### CLI Design (Object-Command Pattern)

```
src/codeframe/
  ├── cli.py              # Main CLI entry point
  ├── cli_issues.py       # Issues object commands
  ├── cli_repos.py        # Repos object commands
  ├── scanner.py          # Traycer issue scanner
  ├── processor.py        # Queue processor
  ├── dashboard.py        # TUI dashboard
  ├── database.py         # SQLite management
  └── slot_calculator.py  # Rate limit slot inference
```

### Current Components (Traycer Integration)

**Scanner** - Finds rate-limited issues:
- Scans all user-owned GitHub repositories
- Pattern matching: `Rate limit exceeded. Please try after (\d+) seconds.`
- Calculates retry timing with 2-minute buffer
- Uses PyGithub API

**Processor** - Processes queue:
- Toggles GitHub issue assignment to trigger Traycer
- Circuit breaker: Stops after 5 consecutive errors
- Max retries: 3 attempts per issue
- Respects slot availability

**Slot Calculator** - Rate limit intelligence:
- Infers available processing slots from history
- Detects external Traycer activity via GitHub Search API
- Rate limit model: 15 total slots, 1 recharges/30min
- Safe defaults on API failures

**Dashboard** - Live monitoring:
- Rich TUI with auto-refresh
- Shows queue status, top repos, recent activity, errors
- Accessible via `cf issues view`

**Database** - SQLite tracking:
- `queued_issues`: Issues awaiting planning
- `processing_history`: For slot calculation
- `error_log`: Circuit breaker tracking

### Key Design Patterns

**Slot Inference Strategy**: Since we don't have direct access to Traycer's rate limit API, we infer available capacity by tracking processing history. External activity detection via GitHub Search API prevents conflicts.

**Assignment Toggle Triggering**: Traycer re-analyzes issues when assigned. We toggle assignment state (assign if unassigned, unassign→reassign if already assigned) to trigger re-analysis.

**Circuit Breaker Pattern**: Prevents API abuse by stopping after 5 consecutive errors within 5 minutes. Rate limit errors don't trip the breaker (expected behavior).

---

## Automation (Optional)

Set up cron jobs for hands-off operation:

```bash
# Install cron jobs
./install_crontab.sh

# Verify cron is running
cf repos health

# View logs
tail -f logs/scanner.log
tail -f logs/processor.log
```

**Cron schedule:**
- **Scanner**: Daily at 2 AM - finds new rate-limited issues
- **Processor**: Every 32 minutes - processes queue

---

## Development

### Testing

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_database.py -v

# Coverage report
pytest --cov=src --cov-report=term-missing
```

**Testing philosophy:**
- Target: >85% coverage, 100% pass rate
- Integration tests use real GitHub API
- No mocking - test against actual services

### Code Quality

```bash
# Check and format
ruff check src/ && ruff format src/

# Just check
ruff check src/

# Just format
ruff format src/
```

### Database Inspection

```bash
# Interactive SQL
sqlite3 traycer_queue.db

# Quick queries
sqlite3 traycer_queue.db "SELECT repo_name, issue_number, next_retry_at FROM queued_issues;"
sqlite3 traycer_queue.db "SELECT * FROM processing_history ORDER BY processed_at DESC LIMIT 10;"
sqlite3 traycer_queue.db "SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;"
```

### Legacy Commands

The following commands still work for backward compatibility:

```bash
python -m codeframe.scanner       # Same as: cf issues create-plan
python -m codeframe.processor     # Same as: cf issues process
python -m codeframe.dashboard     # Same as: cf issues view
```

---

## What's New (Updated: 2026-01-01)

### 🎉 Major Release: Traycer Queue → CodeFRAME CLI

**Project Evolution:**
- Renamed from "Traycer Queue Manager" to "CodeFRAME CLI"
- Module path: `src/traycer_queue/` → `src/codeframe/`
- Vision: Expand from single-purpose Traycer integration to full autonomous development IDE
- New object-command CLI pattern (`cf <OBJECT> <COMMAND>`)

**New CLI Commands:**
- `cf issues view [--live]` - Dashboard with live monitoring
- `cf issues create-plan` - Scanner
- `cf issues process` - Queue processor
- `cf issues status` - Quick status summary
- `cf repos health` - System health check
- Global `codeframe` and `cf` commands

**New Features:**
- ✨ Live TUI dashboard with auto-refresh
- ✨ External activity detection (prevents rate limit conflicts)
- ✨ System health checks
- ✨ Modular command architecture for easy expansion

### 🐛 Critical Bug Fixes

**Circuit Breaker False Positives** (2026-01-01):
- Fixed: Circuit breaker treating `max_retries` cleanup as real failures
- Impact: Processor runs without false circuit breaker trips

**Retry Timing Not Updated** (2026-01-01):
- Fixed: `next_retry_at` wasn't updated when issues still rate-limited
- Impact: Issues properly wait for rate limits to expire

**Timezone Bug in Slot Calculation** (2026-01-01):
- Fixed: Slot calculator comparing UTC with local time (-7 hour difference)
- Impact: Accurate slot calculation prevents batch processing when no slots available

### 🚀 Enhancements

**External Activity Detection** (2026-01-01):
- Detects when external users trigger Traycer analyses
- Uses GitHub Search API: `gh search issues --commenter "traycerai[bot]"`
- Algorithm: `available_slots = 15 - (our_consumed + external_activity)`
- Prevents slot conflicts and rate limits

---

## Roadmap

### ✅ Phase 1: Traycer Integration (Complete)
- Issue scanning and queuing
- Rate limit management
- TUI dashboard
- External activity detection
- Object-command CLI

### 🚧 Phase 2: Multi-Repo Orchestration (In Progress)
- Cross-repo status view
- Issue state tracking (planning → building → review → deployed)
- PR management commands

### 📋 Phase 3: CodeFRAME Integration (Planned)
- Launch CodeFRAME agents on issues
- Monitor agent progress
- Human-in-the-loop blocker handling

### 🔮 Phase 4: Full IDE (Future)
- Idea generation and repo scaffolding
- Deployment tracking
- Cost/metrics across all projects

---

## Contributing

We welcome contributions! Here's how to add new functionality:

### Adding a New Command

```python
# In cli_issues.py (or relevant object file)
def setup_issues_parser(subparsers):
    # ... existing code ...

    # New command
    new_parser = issues_subparsers.add_parser(
        "new-command",
        help="Brief description",
        description="Detailed description",
    )
    new_parser.set_defaults(func=cmd_issues_new_command)

def cmd_issues_new_command(args):
    """Implementation."""
    # Your logic here
    return 0
```

### Adding a New Object

1. Create `src/codeframe/cli_<object>.py`
2. Implement `setup_<object>_parser(subparsers)` function
3. Import and call in `src/codeframe/cli.py`
4. Add tests to `tests/test_<object>.py`
5. Update CLAUDE.md and README.md

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure `pytest` and `ruff check` pass
5. Submit a pull request

---

## Technical Details

### Configuration Constants

**Rate Limit Timing:**
- `TOTAL_SLOTS = 15`
- `SLOT_RECHARGE_MINUTES = 30`

**Retry Behavior:**
- `RETRY_BUFFER_MINUTES = 2`

**Error Handling:**
- `MAX_RETRIES = 3` (per-issue)
- `CIRCUIT_BREAKER_THRESHOLD = 5` (consecutive errors)

### Database Schema

**queued_issues:**
- `repo_name`, `issue_number`, `rate_limit_seconds`
- `next_retry_at`, `retry_count`

**processing_history:**
- Tracks all processing attempts
- Used for slot calculation

**error_log:**
- Error tracking and circuit breaker logic
- Excludes `max_retries` and `circuit_breaker` from consecutive error counts

---

## Troubleshooting

### Command not found: `cf`

Ensure `~/.local/bin` is in your PATH:

```bash
echo $PATH | grep -q "$HOME/.local/bin" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Rate limits still occurring

Check external activity:

```bash
cf issues status  # Shows available slots
cf repos health   # Verifies slot calculator
```

The system detects external Traycer activity, but if multiple users are triggering Traycer simultaneously, you may need to wait for slots to recharge.

### Circuit breaker tripped

Check error log:

```bash
sqlite3 traycer_queue.db "SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;"
```

Circuit breaker resets automatically after 5 minutes. If errors persist, check GitHub API authentication and network connectivity.

### Database locked errors

Only one processor should run at a time. Check for duplicate cron jobs or manual executions:

```bash
ps aux | grep codeframe
crontab -l | grep codeframe
```

---

## License

AGPL-3.0 (matching [CodeFRAME project](https://github.com/frankbria/codeframe))

---

## Related Projects

- **[CodeFRAME](https://github.com/frankbria/codeframe)** - Autonomous AI development system with multi-agent orchestration
- **[Traycer AI](https://traycer.ai)** - AI-powered issue planning and analysis

---

## Acknowledgments

Built with:
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API integration
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [SQLite](https://www.sqlite.org/) - Database
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter

---

## Support

- **Issues**: [GitHub Issues](https://github.com/frankbria/codeframe-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/frankbria/codeframe-cli/discussions)
- **Email**: frank@codeframe.ai

---

**Star ⭐ this repo if you find it useful!**
