"""Tests for database functionality."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from traycer_queue.database import Database


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    database = Database(db_path)
    yield database

    # Cleanup
    db_path.unlink()


def test_add_issue(db):
    """Test adding an issue to the queue."""
    next_retry = datetime.now() + timedelta(minutes=32)
    added = db.add_issue("owner/repo", 123, next_retry)

    assert added is True

    # Adding again should update
    added = db.add_issue("owner/repo", 123, next_retry)
    assert added is False  # Already exists


def test_get_issues_ready_for_processing(db):
    """Test retrieving issues ready for processing."""
    # Add issue ready now
    db.add_issue("owner/repo", 1, datetime.now() - timedelta(minutes=1))

    # Add issue not ready yet
    db.add_issue("owner/repo", 2, datetime.now() + timedelta(hours=1))

    ready_issues = db.get_issues_ready_for_processing()

    assert len(ready_issues) == 1
    assert ready_issues[0]["issue_number"] == 1


def test_remove_issue(db):
    """Test removing an issue from queue."""
    db.add_issue("owner/repo", 123)
    db.remove_issue("owner/repo", 123)

    ready_issues = db.get_issues_ready_for_processing()
    assert len(ready_issues) == 0


def test_log_processing(db):
    """Test logging processing attempts."""
    db.log_processing("owner/repo", 123, success=True)
    db.log_processing("owner/repo", 124, success=False, rate_limit_seconds=2571)

    history = db.get_recent_processing_history(minutes=30)

    assert len(history) == 2
    # SQLite stores booleans as 0/1
    assert history[0]["success"] == 0  # False
    assert history[0]["rate_limit_seconds"] == 2571


def test_log_error(db):
    """Test error logging."""
    db.log_error("api_error", "Something went wrong", "owner/repo", 123)

    errors = db.get_consecutive_errors(limit=10)

    assert len(errors) == 1
    assert errors[0]["error_type"] == "api_error"


def test_increment_retry_count(db):
    """Test incrementing retry count."""
    db.add_issue("owner/repo", 123)
    db.increment_retry_count("owner/repo", 123, "API error")

    issues = db.get_issues_ready_for_processing()

    assert issues[0]["retry_count"] == 1
    assert issues[0]["last_error"] == "API error"
