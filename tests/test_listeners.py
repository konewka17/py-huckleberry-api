"""Real-time listener tests for Huckleberry API."""
import time
from typing import Any

from huckleberry_api import HuckleberryAPI


class TestRealtimeListeners:
    """Test real-time listener functionality."""

    def test_sleep_listener(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test sleep real-time listener."""
        updates: list[Any] = []

        def callback(data: Any) -> None:
            updates.append(data)

        # Setup listener
        api.setup_realtime_listener(child_uid, callback)
        time.sleep(2)  # Wait for initial snapshot

        # Trigger update
        api.start_sleep(child_uid)
        time.sleep(2)  # Wait for update

        # Cleanup
        api.cancel_sleep(child_uid)
        api.stop_all_listeners()

        # Verify we got updates
        assert len(updates) > 0
        assert updates[-1]["timer"]["active"] is True

    def test_feed_listener(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test feeding real-time listener."""
        updates: list[Any] = []

        def callback(data: Any) -> None:
            updates.append(data)

        # Setup listener
        api.setup_feed_listener(child_uid, callback)
        time.sleep(2)

        # Trigger update
        api.start_feeding(child_uid, side="left")
        time.sleep(2)

        # Cleanup
        api.cancel_feeding(child_uid)
        api.stop_all_listeners()

        # Verify we got updates
        assert len(updates) > 0
        assert updates[-1]["timer"]["active"] is True

    def test_listener_survives_token_refresh(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test that listeners survive token refresh."""
        updates: list[Any] = []

        def callback(data: Any) -> None:
            updates.append(data)

        # Setup listener
        api.setup_realtime_listener(child_uid, callback)
        time.sleep(2)

        initial_count = len(updates)

        # Refresh token (simulates token expiry)
        api.refresh_auth_token()
        time.sleep(2)

        # Trigger update to verify listener still works
        api.start_sleep(child_uid)
        time.sleep(2)

        # Cleanup
        api.cancel_sleep(child_uid)
        api.stop_all_listeners()

        # Verify listener continued to receive updates
        assert len(updates) > initial_count
