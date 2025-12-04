"""Growth tracking tests for Huckleberry API."""
import time

from huckleberry_api import HuckleberryAPI


class TestGrowthTracking:
    """Test growth tracking functionality."""

    def test_log_growth_metric(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test logging growth measurement in metric units."""
        api.log_growth(
            child_uid,
            weight=5.2,
            height=52.0,
            head=35.0,
            units="metric"
        )
        time.sleep(1)

        # Verify it was logged by checking health collection
        health_doc = api._get_firestore_client().collection("health").document(child_uid).get()
        data = health_doc.to_dict()
        assert data is not None
        assert "lastGrowthEntry" in data.get("prefs", {})

    def test_log_growth_imperial(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test logging growth measurement in imperial units."""
        api.log_growth(
            child_uid,
            weight=11.5,
            height=20.5,
            head=13.8,
            units="imperial"
        )
        time.sleep(1)

        health_doc = api._get_firestore_client().collection("health").document(child_uid).get()
        data = health_doc.to_dict()
        assert data is not None
        assert "lastGrowthEntry" in data.get("prefs", {})

    def test_get_growth_data(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test retrieving growth data."""
        growth_data = api.get_growth_data(child_uid)
        # Returns a dict
        assert isinstance(growth_data, dict)
        # May be empty if no growth data exists
        if growth_data:
            # Check for expected fields from GrowthData TypedDict
            assert "weight" in growth_data or "height" in growth_data or "head" in growth_data
