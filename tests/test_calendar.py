"""Calendar/interval fetching tests for Huckleberry API."""
import time
from datetime import datetime, timezone

from huckleberry_api import HuckleberryAPI


class TestCalendarIntervals:
    """Test calendar interval fetching functionality."""

    def test_get_sleep_intervals(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test fetching sleep intervals for a date range."""
        # Create a sleep interval first
        api.start_sleep(child_uid)
        time.sleep(2)
        api.complete_sleep(child_uid)
        time.sleep(1)

        # Query for intervals in the last hour
        now = datetime.now(timezone.utc)
        start_ts = int(now.timestamp()) - 3600  # 1 hour ago
        end_ts = int(now.timestamp()) + 60  # 1 minute in future

        intervals = api.get_sleep_intervals(child_uid, start_ts, end_ts)

        assert isinstance(intervals, list)
        # Should have at least the interval we just created
        assert len(intervals) >= 1

        # Check structure
        for interval in intervals:
            assert "start" in interval
            assert "duration" in interval
            assert isinstance(interval["start"], (int, float))
            assert isinstance(interval["duration"], (int, float))

    def test_get_feed_intervals(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test fetching feed intervals for a date range."""
        # Create a feed interval first
        api.start_feeding(child_uid, side="left")
        time.sleep(2)
        api.complete_feeding(child_uid)
        time.sleep(1)

        # Query for intervals in the last hour
        now = datetime.now(timezone.utc)
        start_ts = int(now.timestamp()) - 3600
        end_ts = int(now.timestamp()) + 60

        intervals = api.get_feed_intervals(child_uid, start_ts, end_ts)

        assert isinstance(intervals, list)
        assert len(intervals) >= 1

        # Check structure
        for interval in intervals:
            assert "start" in interval
            assert "leftDuration" in interval
            assert "rightDuration" in interval
            assert "is_multi_entry" in interval
            assert isinstance(interval["is_multi_entry"], bool)

    def test_get_diaper_intervals(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test fetching diaper intervals for a date range."""
        # Create a diaper entry first
        api.log_diaper(child_uid, mode="pee")
        time.sleep(1)

        # Query for intervals in the last hour
        now = datetime.now(timezone.utc)
        start_ts = int(now.timestamp()) - 3600
        end_ts = int(now.timestamp()) + 60

        intervals = api.get_diaper_intervals(child_uid, start_ts, end_ts)

        assert isinstance(intervals, list)
        assert len(intervals) >= 1

        # Check structure
        for interval in intervals:
            assert "start" in interval
            assert "mode" in interval
            assert interval["mode"] in ("pee", "poo", "both", "dry", "unknown")

    def test_get_health_entries(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test fetching health/growth entries for a date range."""
        # Create a health entry first
        api.log_growth(child_uid, weight=5.0, units="metric")
        time.sleep(1)

        # Query for entries in the last hour
        now = datetime.now(timezone.utc)
        start_ts = int(now.timestamp()) - 3600
        end_ts = int(now.timestamp()) + 60

        entries = api.get_health_entries(child_uid, start_ts, end_ts)

        assert isinstance(entries, list)
        assert len(entries) >= 1

        # Check structure
        for entry in entries:
            assert "start" in entry
            # Should have at least one measurement field
            has_measurement = "weight" in entry or "height" in entry or "head" in entry
            assert has_measurement

    def test_get_calendar_events(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test fetching all calendar events for a date range."""
        # Query for events in the last hour
        now = datetime.now(timezone.utc)
        start_ts = int(now.timestamp()) - 3600
        end_ts = int(now.timestamp()) + 60

        events = api.get_calendar_events(child_uid, start_ts, end_ts)

        assert isinstance(events, dict)
        assert "sleep" in events
        assert "feed" in events
        assert "diaper" in events
        assert "health" in events

        assert isinstance(events["sleep"], list)
        assert isinstance(events["feed"], list)
        assert isinstance(events["diaper"], list)
        assert isinstance(events["health"], list)

    def test_date_range_filtering(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test that date range filtering works correctly."""
        # Query for a range far in the past (should return empty or fewer results)
        old_start = 0  # Unix epoch
        old_end = 1000000  # Jan 12, 1970

        intervals = api.get_sleep_intervals(child_uid, old_start, old_end)

        # Should return empty list for range in distant past
        assert isinstance(intervals, list)
        assert len(intervals) == 0

    def test_empty_date_range(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test querying with an empty date range."""
        now = int(datetime.now(timezone.utc).timestamp())

        # Start equals end - empty range
        intervals = api.get_sleep_intervals(child_uid, now, now)

        assert isinstance(intervals, list)
        # Should return empty since start < end_timestamp won't match when they're equal
        assert len(intervals) == 0
