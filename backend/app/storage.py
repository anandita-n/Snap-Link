from datetime import datetime, timezone
from typing import Dict, List, Optional

class InMemoryStorage:
    def __init__(self):
        # Maps short_code -> dict containing short_code, original_url, clicks, created_at
        self._links: Dict[str, dict] = {}
        # Maps original_url -> short_code (for fast duplicate checking)
        self._url_to_code: Dict[str, str] = {}

    def save_link(self, short_code: str, original_url: str, qr_code: Optional[str] = None) -> dict:
        """
        Saves a short link mapping.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        link_data = {
            "short_code": short_code,
            "original_url": original_url,
            "clicks": 0,
            "created_at": timestamp,
            "qr_code": qr_code
        }
        self._links[short_code] = link_data
        self._url_to_code[original_url] = short_code
        return link_data

    def get_link_by_code(self, short_code: str) -> Optional[dict]:
        """
        Retrieves link data for a given short code.
        """
        return self._links.get(short_code)

    def get_link_by_url(self, original_url: str) -> Optional[dict]:
        """
        Retrieves link data for a given original URL (useful for finding existing shortened links).
        """
        code = self._url_to_code.get(original_url)
        if code:
            return self._links.get(code)
        return None

    def increment_clicks(self, short_code: str) -> bool:
        """
        Increments the click counter for a short code. Returns True if found, False otherwise.
        """
        if short_code in self._links:
            self._links[short_code]["clicks"] += 1
            return True
        return False

    def get_all_links(self) -> List[dict]:
        """
        Returns a list of all shortened links sorted by creation time (latest first).
        """
        return sorted(self._links.values(), key=lambda x: x["created_at"], reverse=True)

    def clear(self):
        """
        Clears the in-memory database (primarily used in unit test setup/teardown).
        """
        self._links.clear()
        self._url_to_code.clear()

# Global storage instance
storage = InMemoryStorage()
