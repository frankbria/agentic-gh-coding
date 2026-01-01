# Traycer Queue Manager

Automatically manages GitHub issue re-analysis for Traycer AI rate limits.

## Problem

Traycer AI has rate limits (15 slots, 1 recharges every 30 minutes). When issues are created too quickly, Traycer posts a rate limit error instead of analyzing:

```
Warning: Rate limit exceeded. Please try after 2571 seconds.
```

This tool automatically:
1. Scans your GitHub repos for rate-limited issues
2. Queues them for re-analysis with intelligent timing
3. Processes the queue by toggling issue assignment (triggers Traycer)
4. Respects rate limits and calculates available slots

## Installation

### 1. Clone and Install Dependencies

```bash
cd /home/frankbria/projects/update-gh-issue-plans
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 2. Configure GitHub Access

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
- `GITHUB_TOKEN`: Personal access token with `repo` scope ([create one](https://github.com/settings/tokens))
- `GITHUB_USERNAME`: Your GitHub username

### 3. Create Log Directory

```bash
mkdir -p logs
```

### 4. Set Up Cron Jobs

```bash
crontab -e
```

Add the jobs from `crontab.example` (adjust paths if needed).

## Usage

### Manual Scanning

Scan all your repos for rate-limited issues:

```bash
source .venv/bin/activate
export $(cat .env | xargs)  # Load environment variables
python -m traycer_queue.scanner
```

### Manual Processing

Process queued issues:

```bash
source .venv/bin/activate
export $(cat .env | xargs)
python -m traycer_queue.processor
```

### Automated Operation

Once cron jobs are configured, the system runs automatically:

- **Scanner**: Daily at 2 AM - finds new rate-limited issues
- **Processor**: Every 32 minutes - processes queue (respects slots)

## How It Works

### Slot Calculation

Traycer's rate limit:
- **15 total slots**
- **1 slot recharges every 30 minutes**

The system infers available slots by:
1. Tracking all processing attempts in last 30 minutes
2. Each attempt = 1 consumed slot
3. Available slots = 15 - consumed slots in last 30 min

### Queue Processing

For each queued issue:
1. Check if assigned to you
   - If yes: unassign → reassign (triggers Traycer)
   - If no: assign (triggers Traycer)
2. Wait 2 seconds for Traycer to process
3. Check latest Traycer comment
   - No rate limit error → Success! Remove from queue
   - Rate limit error → Update queue with new timing
   - No comment → Retry later

### Error Handling

- **Retries**: Up to 3 attempts per issue
- **Circuit Breaker**: Stops after 5 consecutive API errors (prevents API abuse)
- **Error Logging**: All errors logged to database (`error_log` table)

## Database

SQLite database (`traycer_queue.db`) with three tables:

- **queued_issues**: Issues awaiting re-analysis
- **processing_history**: Tracks all attempts (for slot calculation)
- **error_log**: Error tracking and circuit breaker

### Inspecting the Database

```bash
sqlite3 traycer_queue.db

# See queued issues
SELECT repo_name, issue_number, next_retry_at FROM queued_issues;

# See processing history
SELECT * FROM processing_history ORDER BY processed_at DESC LIMIT 10;

# See recent errors
SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;
```

## Configuration

### Adjust Rate Limit Timing

Edit `src/traycer_queue/slot_calculator.py`:

```python
SLOT_RECHARGE_MINUTES = 30  # Increase if hitting rate limits
```

Edit `src/traycer_queue/scanner.py`:

```python
RETRY_BUFFER_MINUTES = 2  # Buffer added to retry timing
```

### Adjust Error Thresholds

Edit `src/traycer_queue/processor.py`:

```python
MAX_RETRIES = 3  # Per-issue retry limit
CIRCUIT_BREAKER_THRESHOLD = 5  # Consecutive errors before stopping
```

## Monitoring

### Check Logs

```bash
# Scanner log (daily scans)
tail -f logs/scanner.log

# Processor log (every 32 minutes)
tail -f logs/processor.log
```

### Check Queue Status

```bash
python -c "from src.traycer_queue.database import Database; \
from src.traycer_queue.slot_calculator import SlotCalculator; \
db = Database(); calc = SlotCalculator(db); \
status = calc.calculate_available_slots(); \
print(f'Available slots: {status.available_slots}/{status.total_slots}')"
```

## Troubleshooting

### Issues Not Being Queued

1. Check scanner log for errors: `tail logs/scanner.log`
2. Verify GitHub token has `repo` scope
3. Check database: `sqlite3 traycer_queue.db "SELECT * FROM error_log;"`

### Issues Not Being Processed

1. Check processor log: `tail logs/processor.log`
2. Check available slots: Run queue status command above
3. Verify GitHub username in `.env` matches your GitHub account

### Rate Limits Still Triggering

1. Increase `RETRY_BUFFER_MINUTES` in `scanner.py`
2. Increase `SLOT_RECHARGE_MINUTES` in `slot_calculator.py`
3. Reduce cron job frequency (e.g., every hour instead of every 32 min)

### Circuit Breaker Tripping

Check for systematic API errors:

```bash
sqlite3 traycer_queue.db "SELECT * FROM error_log WHERE error_type != 'rate_limit' ORDER BY timestamp DESC LIMIT 20;"
```

Common causes:
- Invalid GitHub token
- Network issues
- GitHub API downtime

## Development

### Run Tests

```bash
source .venv/bin/activate
pytest
```

### Lint Code

```bash
ruff check src/
ruff format src/
```

## License

MIT
