from typing import List


def get_quarantine_items() -> List[dict]:
    """
    Service function to retrieve quarantined messages.
    Returns the live MOCK_QUARANTINE store.
    """
    from app import main
    return main.MOCK_QUARANTINE
