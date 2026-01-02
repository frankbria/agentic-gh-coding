# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CodeFRAME CLI** - The next-generation IDE for autonomous AI development.

CodeFRAME CLI orchestrates AI-driven development across repositories, issues, PRs, and deployments. It uses an object-command pattern to work with high-level entities (ideas, issues, features) instead of low-level file operations.

**Current Focus**: Automated GitHub issue planning via Traycer AI integration with intelligent rate limit management.

### Core Philosophy
- **Object-Command Pattern**: `cf <OBJECT> <COMMAND>` (e.g., `cf issues view`, `cf repos health`)
- **AI-First**: Leverage AI agents for issue planning, code review, deployment orchestration
- **Multi-Repo**: Single interface for managing work across all your repositories
- **Autonomous**: Minimize manual intervention through automation and intelligent scheduling

## Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Create required directories
mkdir -p logs

# Configure environment
cp .env.example .env
# Edit .env to add GITHUB_TOKEN and GITHUB_USERNAME

# Install global commands
chmod +x codeframe
cp codeframe ~/.local/bin/
ln -sf ~/.local/bin/codeframe ~/.local/bin/cf
```

### CLI Usage

**Issues Management**:
```bash
# View issues dashboard
cf issues view                    # Static dashboard
cf issues view --live             # Live auto-refresh
cf issues view --live --refresh 10  # Custom refresh rate

# Generate plans for issues
cf issues create-plan --global    # Scan all repos for rate-limited issues

# Process planning queue
cf issues process                 # Process queued issues (respects rate limits)

# Quick status
cf issues status                  # Show queue status and available slots
```

**Repository Health**:
```bash
# Health check
cf repos health                   # Check cron, database, slots, GitHub CLI

# Repository status (coming soon)
cf repos status                   # Cross-repo status view
```

**Legacy Commands** (still supported):
```bash
# Direct Python module execution
python -m codeframe.scanner       # Same as: cf issues create-plan
python -m codeframe.processor     # Same as: cf issues process
python -m codeframe.dashboard     # Same as: cf issues view
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest -v

# Coverage report
pytest --cov=src --cov-report=term-missing
```

### Code Quality
```bash
# Check code style
ruff check src/

# Format code
ruff format src/

# Check and format
ruff check src/ && ruff format src/
```

### Database Inspection
```bash
# Open database
sqlite3 traycer_queue.db

# Check queued issues
sqlite3 traycer_queue.db "SELECT repo_name, issue_number, next_retry_at FROM queued_issues;"

# Check processing history
sqlite3 traycer_queue.db "SELECT * FROM processing_history ORDER BY processed_at DESC LIMIT 10;"

# Check error log
sqlite3 traycer_queue.db "SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;"
```

## Architecture

### CLI Structure (Object-Command Pattern)

**Entry Point** (`src/codeframe/cli.py`):
- Main CLI orchestrator
- Routes commands to object-specific handlers
- Provides `codeframe` and `cf` commands

**Object Handlers**:
- `cli_issues.py` - Issues object commands (view, create-plan, process, status)
- `cli_repos.py` - Repos object commands (health, status)
- *(Future)* `cli_prs.py` - PR management
- *(Future)* `cli_ideas.py` - AI-powered idea generation

### Core Components (Traycer Integration)

**Scanner** (`src/codeframe/scanner.py`):
- Scans all user-owned GitHub repositories for Traycer rate limit comments
- Pattern matching: `Rate limit exceeded. Please try after (\d+) seconds.`
- Calculates retry timing with buffer (comment timestamp + rate limit seconds + 2 min buffer)
- Uses PyGithub to interact with GitHub API

**Processor** (`src/codeframe/processor.py`):
- Processes queued issues by toggling GitHub issue assignment
- Assignment toggle strategy: Unassign→reassign if assigned, assign if not
- Circuit breaker: Stops after 5 consecutive errors within 5 minutes
- Max retries: 3 attempts per issue before removal from queue
- Waits 2 seconds after assignment toggle for Traycer to process

**Slot Calculator** (`src/codeframe/slot_calculator.py`):
- Infers available processing slots from recent history and external Traycer activity
- Rate limit model: 15 total slots, 1 recharges every 30 minutes
- Strategy:
  1. Count our processing attempts in last 30 minutes (consumed slots)
  2. Detect external Traycer activity via GitHub Search API
  3. Adjust available slots: 15 - (our consumed slots + external activity)
- External activity detection uses `gh search issues --commenter "traycerai[bot]"` to find all Traycer comments in last 30 minutes
- Safe defaults: On API failures, assumes 0 external activity (prevents over-estimation of capacity)

**Dashboard** (`src/codeframe/dashboard.py`):
- Rich TUI (Text User Interface) for monitoring queue status
- Displays: queue status, top repositories, recent processing activity, recent errors
- Supports live auto-refresh mode
- Accessible via `cf issues view` or legacy `traycer-dashboard` command

**Database** (`src/codeframe/database.py`):
- SQLite with three tables:
  - `queued_issues`: Issues awaiting re-analysis
  - `processing_history`: All attempts (for slot calculation)
  - `error_log`: Error tracking and circuit breaker
- Context manager pattern for connection handling
- Row factory enabled for dict-like access

### Key Design Patterns

**Object-Command CLI Architecture**: The CLI uses a two-level command structure (object → command) to organize functionality by domain (issues, repos, prs). This allows for natural expansion as new capabilities are added, and follows Git's familiar command pattern.

**Slot Inference Strategy**: The system doesn't have direct access to Traycer's rate limit API, so it infers available capacity by tracking processing history. Each processing attempt consumes a slot for 30 minutes. External activity detection via GitHub Search API prevents conflicts with other users triggering Traycer.

**Assignment Toggle Triggering**: Traycer AI re-analyzes issues when they're assigned. The processor toggles assignment state (assign if unassigned, unassign→reassign if already assigned) to trigger re-analysis. See `processor.py:186-221` for implementation details.

**Circuit Breaker Pattern**: Prevents API abuse by stopping processing after 5 consecutive errors within 5 minutes. Rate limit errors don't trip the breaker (they're expected behavior).

**Modular Command Handlers**: Each object (issues, repos) has its own command handler module, making it easy to add new commands or entire new objects without touching core CLI logic.

### Configuration Constants

**Rate Limit Timing** (`src/codeframe/slot_calculator.py`):
- `TOTAL_SLOTS = 15`
- `SLOT_RECHARGE_MINUTES = 30`

**Retry Behavior** (`src/codeframe/scanner.py`):
- `RETRY_BUFFER_MINUTES = 2` (buffer added to rate limit timing)

**Error Handling** (`src/codeframe/processor.py`):
- `MAX_RETRIES = 3` (per-issue retry limit)
- `CIRCUIT_BREAKER_THRESHOLD = 5` (consecutive errors before stopping)

### Environment Variables

Required in `.env`:
- `GITHUB_TOKEN`: Personal access token with `repo` scope
- `GITHUB_USERNAME`: GitHub username for issue assignment

## File Structure

```
src/codeframe/
  ├── cli.py              # Main CLI entry point (cf/codeframe command)
  ├── cli_issues.py       # Issues object commands
  ├── cli_repos.py        # Repos object commands
  ├── scanner.py          # Traycer issue scanner
  ├── processor.py        # Queue processor
  ├── dashboard.py        # TUI dashboard
  ├── database.py         # SQLite management
  └── slot_calculator.py  # Rate limit slot inference

tests/
  ├── test_database.py    # Database tests
  └── ...

Scripts:
  ├── codeframe           # Global CLI wrapper (symlinked to ~/.local/bin/cf)
  ├── dashboard.sh        # Legacy dashboard launcher
  ├── run_scanner.sh      # Cron wrapper for scanner
  ├── run_processor.sh    # Cron wrapper for processor
  └── install_crontab.sh  # Cron job installer
```

## Automation

The system is designed to run via cron jobs (see `crontab.example`):
- **Scanner**: Daily at 2 AM - finds new rate-limited issues
- **Processor**: Every 32 minutes - processes queue respecting available slots

Installation scripts:
- `install_crontab.sh`: Installs cron jobs from template
- `run_scanner.sh`: Wrapper script for scanner with logging
- `run_processor.sh`: Wrapper script for processor with logging

Logs written to `logs/scanner.log` and `logs/processor.log`.

## Design Decisions & Trade-offs

**CLI Pattern Choice (Object-Command)**:
- **Chosen**: `cf <object> <command>` (e.g., `cf issues view`)
- **Alternative**: Flat commands (e.g., `cf issues-view`)
- **Rationale**: Scalable for multi-domain tool, familiar to Git users, allows natural grouping

**Assignment Toggle Logic** (`processor.py:186-221`):
- **Current**: Unassign→reassign if assigned, assign if not
- **Alternatives**: Always unassign/reassign, use labels/comments as trigger
- **Trade-offs**: Event spam vs. simplicity vs. trigger reliability

**Slot Calculation Refinements** (`slot_calculator.py`):
- **Current**: Counts our processing attempts + external Traycer activity via GitHub Search API
- **Future improvements**: Parse rate_limit_seconds for validation, handle clock skew, dedupe multiple attempts on same issue
- **Trade-offs**: Accuracy vs. complexity vs. robustness

When modifying these areas, consider the documented trade-offs and test with real GitHub API interactions.

## Recent Updates (Updated: 2026-01-01)

### Major Refactoring: Traycer Queue → CodeFRAME CLI

**Project Rename & Expansion**:
- Renamed from "Traycer Queue Manager" to "CodeFRAME CLI"
- Module path changed: `src/traycer_queue/` → `src/codeframe/`
- Package name: `codeframe-cli` (v0.1.0)
- Vision: Expand from single-purpose Traycer integration to full autonomous development IDE

**New CLI Architecture**:
- Introduced object-command pattern (`cf <OBJECT> <COMMAND>`)
- Added modular command handlers: `cli_issues.py`, `cli_repos.py`
- New global commands: `codeframe` and `cf` (symlinked in `~/.local/bin/`)
- Backward compatibility: Legacy Python module execution still works

**New Commands**:
- `cf issues view [--live] [--refresh N]` - Dashboard (replaces `traycer-dashboard`)
- `cf issues create-plan [--global]` - Scanner (replaces direct scanner execution)
- `cf issues process` - Processor
- `cf issues status` - Quick queue status
- `cf repos health` - System health check (cron, database, slots, GitHub CLI)
- `cf repos status` - Multi-repo status (coming soon)

**Future Roadmap Outlined**:
- Phase 2: Multi-repo orchestration, issue state tracking, PR management
- Phase 3: CodeFRAME agent integration, autonomous development
- Phase 4: Idea generation, deployment tracking, cost metrics

### Bug Fixes (2026-01-01)

**Circuit Breaker False Positives**:
- **Issue**: Circuit breaker was treating `max_retries` cleanup as real failures
- **Fix**: Updated `database.py:270` to exclude `max_retries` and `circuit_breaker` from consecutive error checks
- **Impact**: Processor can now run without false circuit breaker trips

**Retry Timing Not Updated**:
- **Issue**: When issues were still rate-limited after processing, `next_retry_at` wasn't updated, causing immediate retries
- **Fix**: Modified `increment_retry_count()` to accept `next_retry_at` parameter and updated processor to calculate new retry time from current time + rate limit seconds
- **Impact**: Issues now properly wait for rate limits to expire before retrying

**Timezone Bug in Slot Calculation**:
- **Issue**: Slot calculator was comparing UTC database timestamps with local MST time, resulting in -7 hour time differences
- **Fix**: Updated `slot_calculator.py` to use `datetime.now(timezone.utc)` for all timestamp comparisons
- **Impact**: Slot calculation now correctly shows consumed slots, preventing batch processing when no slots available

**External Activity Detection** (Enhancement):
- **Issue**: System couldn't detect when external users triggered Traycer analyses, leading to slot conflicts and rate limits
- **Implementation**: Added GitHub Search API integration to detect all Traycer comments in last 30 minutes
- **Algorithm**: `available_slots = 15 - (our_consumed_slots + external_activity)`
- **API Usage**: Uses `gh search issues --commenter "traycerai[bot]"` (1 call per processor run, well within 30 req/min limit)
- **Impact**: Accurate slot calculation prevents rate limit conflicts with external users

## Contributing

When adding new functionality:

1. **New Objects**: Add `cli_<object>.py` with `setup_<object>_parser()` function
2. **New Commands**: Add to existing object handler's subparsers
3. **Core Logic**: Place in appropriate module (scanner.py, processor.py, etc.)
4. **Testing**: Add tests to `tests/test_<module>.py`
5. **Documentation**: Update this CLAUDE.md and README.md

Example adding a new command:
```python
# In cli_issues.py
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

## Important Notes

- **Module Rename**: All imports changed from `traycer_queue` to `codeframe`
- **Database**: Still named `traycer_queue.db` for backward compatibility
- **Legacy Commands**: `traycer-dashboard` still works but may be deprecated
- **Alpha Status**: CLI structure may evolve as new objects/commands are added
- **Testing**: Always test with real GitHub API to verify rate limit handling
