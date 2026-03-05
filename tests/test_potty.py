"""Potty tracking tests for Huckleberry API."""
import time

from huckleberry_api import HuckleberryAPI


class TestPottyTracking:
    """Test potty tracking functionality."""

    def test_log_potty_pee(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test logging pee-only potty event."""
        api.log_potty(child_uid, mode="pee", pee_amount="medium")
        time.sleep(1)

        potty_doc = api._get_firestore_client().collection("potty").document(child_uid).get()
        data = potty_doc.to_dict()

        assert data is not None
        assert data["prefs"]["lastPotty"]["mode"] == "pee"

    def test_log_potty_both(self, api: HuckleberryAPI, child_uid: str) -> None:
        """Test logging combined potty event."""
        api.log_potty(
            child_uid,
            mode="both",
            pee_amount="little",
            poo_amount="big",
            color="brown",
            consistency="solid",
        )
        time.sleep(1)

        potty_doc = api._get_firestore_client().collection("potty").document(child_uid).get()
        data = potty_doc.to_dict()

        assert data is not None
        assert data["prefs"]["lastPotty"]["mode"] == "both"
