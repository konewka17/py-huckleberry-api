"""Sleep tracking tests for Huckleberry API."""
import time

from google.cloud import firestore

from huckleberry_api import HuckleberryAPI


class TestSleepTracking:
    """Test sleep tracking functionality."""

    def test_start_and_cancel_sleep(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test starting and canceling sleep."""
        # Start sleep
        api.start_sleep(child_uid)
        time.sleep(1)  # Wait for Firebase to propagate

        # Get current state
        sleep_doc = api._get_firestore_client().collection("sleep").document(child_uid).get()
        assert sleep_doc.exists
        data = sleep_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["paused"] is False

        # Cancel sleep
        api.cancel_sleep(child_uid)
        time.sleep(1)

        sleep_doc = api._get_firestore_client().collection("sleep").document(child_uid).get()
        data = sleep_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is False

    def test_start_pause_resume_complete_sleep(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test full sleep cycle: start, pause, resume, complete."""
        # Start sleep
        api.start_sleep(child_uid)
        time.sleep(2)

        # Pause sleep
        api.pause_sleep(child_uid)
        time.sleep(1)

        sleep_doc = api._get_firestore_client().collection("sleep").document(child_uid).get()
        data = sleep_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["paused"] is True

        # Resume sleep
        api.resume_sleep(child_uid)
        time.sleep(1)

        sleep_doc = api._get_firestore_client().collection("sleep").document(child_uid).get()
        data = sleep_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["paused"] is False

        # Complete sleep
        api.complete_sleep(child_uid)
        time.sleep(1)

        sleep_doc = api._get_firestore_client().collection("sleep").document(child_uid).get()
        data = sleep_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is False
        assert "lastSleep" in data.get("prefs", {})

    def test_complete_sleep_creates_interval(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test that completing sleep creates interval document."""
        # Start and complete sleep quickly
        api.start_sleep(child_uid)
        time.sleep(3)  # Sleep for at least 3 seconds to have meaningful duration
        api.complete_sleep(child_uid)
        time.sleep(2)

        # Check intervals subcollection
        intervals_ref = (
            api._get_firestore_client()
            .collection("sleep")
            .document(child_uid)
            .collection("intervals")
        )

        # Get most recent interval
        recent_intervals = (
            intervals_ref
            .order_by("start", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )

        intervals_list = list(recent_intervals)
        assert len(intervals_list) > 0

        interval_data = intervals_list[0].to_dict()
        assert interval_data is not None
        assert "start" in interval_data
        assert "duration" in interval_data
        assert interval_data["duration"] >= 3  # At least 3 seconds
