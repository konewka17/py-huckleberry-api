"""Feeding tracking tests for Huckleberry API."""
import time

from google.cloud import firestore

from huckleberry_api import HuckleberryAPI


class TestFeedingTracking:
    """Test feeding tracking functionality."""

    def test_start_and_cancel_feeding(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test starting and canceling feeding."""
        # Start feeding
        api.start_feeding(child_uid, side="left")
        time.sleep(1)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        assert feed_doc.exists
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["activeSide"] == "left"

        # Cancel feeding
        api.cancel_feeding(child_uid)
        time.sleep(1)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is False

    def test_feeding_with_side_switch(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test feeding with side switching."""
        # Start feeding on left
        api.start_feeding(child_uid, side="left")
        time.sleep(2)

        # Switch to right
        api.switch_feeding_side(child_uid)
        time.sleep(2)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["activeSide"] == "right"
        assert data["timer"]["leftDuration"] > 0

        # Complete feeding
        api.complete_feeding(child_uid)
        time.sleep(1)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is False
        assert "lastNursing" in data.get("prefs", {})

    def test_feeding_pause_resume(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test feeding pause and resume."""
        # Start feeding
        api.start_feeding(child_uid, side="right")
        time.sleep(2)

        # Pause
        api.pause_feeding(child_uid)
        time.sleep(1)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["paused"] is True

        # Resume
        api.resume_feeding(child_uid)
        time.sleep(1)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["paused"] is False

        # Cancel to cleanup
        api.cancel_feeding(child_uid)

    def test_resume_feeding_with_explicit_side(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test resuming feeding with explicit side parameter."""
        # Start feeding on left
        api.start_feeding(child_uid, side="left")
        time.sleep(2)

        # Pause
        api.pause_feeding(child_uid)
        time.sleep(1)

        # Resume on right (explicit side)
        api.resume_feeding(child_uid, side="right")
        time.sleep(1)

        feed_doc = api._get_firestore_client().collection("feed").document(child_uid).get()
        data = feed_doc.to_dict()
        assert data is not None
        assert data["timer"]["active"] is True
        assert data["timer"]["paused"] is False
        assert data["timer"]["activeSide"] == "right"

        # Cancel to cleanup
        api.cancel_feeding(child_uid)

    def test_complete_feeding_creates_interval(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test that completing feeding creates interval document."""
        # Start and complete feeding
        api.start_feeding(child_uid, side="left")
        time.sleep(3)
        api.complete_feeding(child_uid)
        time.sleep(2)

        # Check intervals subcollection
        intervals_ref = (
            api._get_firestore_client()
            .collection("feed")
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
        assert "mode" in interval_data
        assert interval_data["mode"] == "breast"
