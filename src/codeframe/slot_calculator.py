"""Calculates available Traycer AI processing slots based on rate limit history."""

import json
import subprocess
from datetime import datetime, timedelta, timezone
from typing import NamedTuple

from .database import Database


class SlotStatus(NamedTuple):
    """Current rate limit slot status."""

    total_slots: int
    consumed_slots: int
    available_slots: int
    next_slot_available_at: datetime | None


class SlotCalculator:
    """Infers available Traycer AI slots from processing history and rate limit messages."""

    TOTAL_SLOTS = 15
    SLOT_RECHARGE_MINUTES = 30

    def __init__(self, db: Database):
        """Initialize slot calculator.

        Args:
            db: Database instance
        """
        self.db = db

    def _detect_external_traycer_activity(self) -> int:
        """Detect Traycer activity from external sources (not our processor).

        Uses GitHub Search to find all issues with Traycer comments in the last 30 minutes,
        then subtracts our own processing attempts to get external activity count.

        Returns:
            Number of external Traycer processing attempts in last 30 minutes
        """
        try:
            # Calculate timestamp for 30 minutes ago in GitHub's date format
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.SLOT_RECHARGE_MINUTES)
            # GitHub search uses format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ
            timestamp_filter = cutoff_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Use gh search issues with commenter and updated filters
            # This searches across all accessible repositories
            result = subprocess.run(
                [
                    "gh",
                    "search",
                    "issues",
                    "--commenter",
                    "traycerai[bot]",
                    "--updated",
                    f">={timestamp_filter}",
                    "--json",
                    "number",
                    "--limit",
                    "1000",  # GitHub max limit
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            # Parse search results
            search_results = json.loads(result.stdout)
            total_traycer_activity = len(search_results)

            # Get our own processing attempts from history
            history = self.db.get_recent_processing_history(minutes=self.SLOT_RECHARGE_MINUTES)
            our_processing_attempts = len(history)

            # External activity = total activity - our attempts
            external_activity = max(0, total_traycer_activity - our_processing_attempts)

            return external_activity

        except subprocess.TimeoutExpired:
            # If API call times out, assume no external activity (safe default)
            return 0
        except subprocess.CalledProcessError:
            # If gh command fails, assume no external activity (safe default)
            return 0
        except (json.JSONDecodeError, KeyError):
            # If parsing fails, assume no external activity (safe default)
            return 0

    def calculate_available_slots(self) -> SlotStatus:
        """Calculate how many processing slots are currently available.

        Strategy:
        1. Look at processing history from last 30 minutes (our attempts)
        2. Detect external Traycer activity via GitHub Search API
        3. Each processing attempt (ours or external) consumes a slot
        4. Slots recharge 30 minutes after consumption
        5. Available slots = 15 - (our consumed slots + external activity)

        Returns:
            SlotStatus with current availability
        """
        # Get recent processing history (our attempts)
        history = self.db.get_recent_processing_history(minutes=self.SLOT_RECHARGE_MINUTES)

        # Calculate slots consumed by our processing attempts
        consumed_slots = self._calculate_consumed_slots(history)

        # Detect external Traycer activity (other users triggering analyses)
        external_activity = self._detect_external_traycer_activity()

        # Total consumed = our attempts + external activity
        # Note: external_activity is already net of our attempts (see _detect_external_traycer_activity)
        total_consumed = consumed_slots + external_activity

        # Available slots = total - consumed (can't go negative)
        available_slots = max(0, self.TOTAL_SLOTS - total_consumed)

        # Calculate when next slot will be available
        next_available = self._calculate_next_slot_time(history) if available_slots == 0 else None

        return SlotStatus(
            total_slots=self.TOTAL_SLOTS,
            consumed_slots=total_consumed,
            available_slots=available_slots,
            next_slot_available_at=next_available,
        )

    def _calculate_consumed_slots(self, history: list[dict]) -> int:
        """Calculate how many slots are currently consumed.

        This is the core business logic that determines our processing capacity.

        Args:
            history: Processing history from last 30 minutes

        Returns:
            Number of consumed slots (0-15)
        """
        # Current approach: Simple count of recent attempts
        # Each processing attempt consumes a slot for 30 minutes.
        # Future enhancements tracked in GitHub issues:
        # - Parse rate_limit_seconds to validate slot consumption
        # - Handle clock skew between local time and GitHub API time
        # - Deduplicate multiple attempts on same issue within 30min window

        # Use UTC to match SQLite CURRENT_TIMESTAMP
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        consumed = 0

        # Count all processing attempts in last 30 minutes
        for record in history:
            # Parse timestamp (from SQLite, stored as UTC)
            processed_at = datetime.fromisoformat(record["processed_at"])

            # Check if within recharge window
            time_diff = now - processed_at
            if time_diff >= timedelta(0) and time_diff <= timedelta(minutes=self.SLOT_RECHARGE_MINUTES):
                consumed += 1

        return min(consumed, self.TOTAL_SLOTS)  # Cap at total slots

    def _calculate_next_slot_time(self, history: list[dict]) -> datetime | None:
        """Calculate when the next slot will become available.

        Args:
            history: Processing history from last 30 minutes

        Returns:
            Datetime when next slot recharges, or None if slots available
        """
        # Find the oldest processing attempt in the last 30 minutes.
        # Next slot becomes available 30 minutes after that oldest attempt.

        if not history:
            return None

        # Use UTC to match database timestamps
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Find oldest processing attempt within the recharge window
        oldest_time = None
        for record in history:
            processed_at = datetime.fromisoformat(record["processed_at"])
            time_diff = now - processed_at

            # Only consider attempts within recharge window
            if time_diff >= timedelta(0) and time_diff <= timedelta(minutes=self.SLOT_RECHARGE_MINUTES):
                if oldest_time is None or processed_at < oldest_time:
                    oldest_time = processed_at

        if oldest_time:
            return oldest_time + timedelta(minutes=self.SLOT_RECHARGE_MINUTES)

        return None

    def get_processing_window_size(self) -> int:
        """Determine how many issues can be processed in the current batch.

        Returns:
            Number of issues that can be processed now
        """
        status = self.calculate_available_slots()
        return status.available_slots
