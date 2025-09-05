"""JSON-backed storage for playlists.

Structure example on the disk (playlists.json):
{
  "playlists": {
    "Favorites": [
      {"path": "C:/music/track1.mp3", "title": "Bohemian Rhapsody – Queen", "duration": "05:55"},
      {"path": "C:/music/track2.mp3", "title": "track2"}
    ]
  }
}
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List


class PlaylistStore:
    """Simple JSON persistence for playlists."""

    def __init__(self, db_path: Path | str = "playlists.json") -> None:
        self.db_path = Path(db_path)
        # Top-level dict with a single key "playlists".
        self.data: Dict[str, Dict[str, List[Dict[str, str]]]] = {"playlists": {}}
        self._load()

    def _load(self) -> None:
        """Load playlists.json from disk (create file if it doesn't exist)."""
        if self.db_path.exists():
            try:
                self.data = json.loads(self.db_path.read_text(encoding="utf-8"))
                # Guard against corrupt or unexpected structure
                if "playlists" not in self.data or not isinstance(self.data["playlists"], dict):
                    self.data = {"playlists": {}}
            except Exception:
                # Corrupt/unreadable file → reset to empty
                self.data = {"playlists": {}}
        else:
            self._save()

    def _save(self) -> None:
        """Write current data to disk in a human-readable way."""
        self.db_path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- playlist operations ----
    def list_playlists(self) -> List[str]:
        """Alphabetical list of playlist names."""
        return sorted(self.data["playlists"].keys())

    def create_playlist(self, name: str) -> None:
        """Create a new empty playlist with a unique, non-empty name."""
        name = name.strip()
        if not name:
            raise ValueError("Playlist name cannot be empty.")
        if name in self.data["playlists"]:
            raise ValueError("A playlist with that name already exists.")
        self.data["playlists"][name] = []
        self._save()

    def delete_playlist(self, name: str) -> None:
        """Delete a playlist (no-op if it doesn't exist)."""
        if name in self.data["playlists"]:
            del self.data["playlists"][name]
            self._save()

    def rename_playlist(self, old: str, new: str) -> None:
        """Rename an existing playlist to a new unique name."""
        new = new.strip()
        if not new:
            raise ValueError("New name cannot be empty.")
        if old not in self.data["playlists"]:
            return
        if new in self.data["playlists"] and new != old:
            raise ValueError("A playlist with that name already exists.")
        self.data["playlists"][new] = self.data["playlists"].pop(old)
        self._save()

    # ---- track operations ----
    def get_tracks(self, playlist: str) -> List[Dict[str, str]]:
        """Return a shallow copy (list) of tracks for a playlist (empty if missing)."""
        return list(self.data["playlists"].get(playlist, []))

    def add_track(
        self,
        playlist: str,
        path: Path | str,
        title: str | None = None,
        duration: str | None = None,
    ) -> None:
        """Append a track entry to a playlist with optional title/duration."""
        if playlist not in self.data["playlists"]:
            raise ValueError("Playlist does not exist.")
        p = Path(path)
        title = title or p.stem
        item: Dict[str, str] = {"path": str(p), "title": title}
        if duration:
            item["duration"] = duration
        self.data["playlists"][playlist].append(item)
        self._save()

    def update_track_at(self, playlist: str, index: int, **fields: str) -> None:
        """Update fields of a track at index (only for provided non-None fields)."""
        if playlist not in self.data["playlists"]:
            return
        tracks = self.data["playlists"][playlist]
        if 0 <= index < len(tracks):
            tracks[index].update({k: v for k, v in fields.items() if v is not None})
            self._save()

    def remove_track_at(self, playlist: str, index: int) -> None:
        """Remove a track by index (if valid)."""
        if playlist not in self.data["playlists"]:
            return
        tracks = self.data["playlists"][playlist]
        if 0 <= index < len(tracks):
            tracks.pop(index)
            self._save()
