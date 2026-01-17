"""
Blacklist storage for content moderation.
"""
import json
from pathlib import Path

BLACKLIST_PATH = Path(__file__).parent / "blacklist.json"

def _load_blacklist():
    if not BLACKLIST_PATH.exists():
        return {"blocked_ids": [], "blocked_urls": []}
    try:
        with BLACKLIST_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "blocked_ids": data.get("blocked_ids", []),
                "blocked_urls": data.get("blocked_urls", []),
            }
    except Exception:
        return {"blocked_ids": [], "blocked_urls": []}

def _save_blacklist(data):
    BLACKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BLACKLIST_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "blocked_ids": sorted(set(data.get("blocked_ids", []))),
                "blocked_urls": sorted(set(data.get("blocked_urls", []))),
            },
            f,
            ensure_ascii=True,
            indent=2,
        )

def get_blacklist():
    return _load_blacklist()

def is_blocked(content_id=None, url=None):
    data = _load_blacklist()
    if content_id and content_id in data.get("blocked_ids", []):
        return True
    if url and url in data.get("blocked_urls", []):
        return True
    return False

def add_to_blacklist(content_id=None, url=None):
    data = _load_blacklist()
    if content_id:
        data.setdefault("blocked_ids", []).append(content_id)
    if url:
        data.setdefault("blocked_urls", []).append(url)
    _save_blacklist(data)
    return data

def remove_from_blacklist(content_id=None, url=None):
    data = _load_blacklist()
    if content_id:
        data["blocked_ids"] = [x for x in data.get("blocked_ids", []) if x != content_id]
    if url:
        data["blocked_urls"] = [x for x in data.get("blocked_urls", []) if x != url]
    _save_blacklist(data)
    return data
