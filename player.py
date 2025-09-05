"""Audio playback helper built on pygame.mixer.music. Keeps track of:
- current file
- a queue (list of dicts, each with at least {"path": ...})
- a queue index
- paused state
"""

from __future__ import annotations
import pygame
from pathlib import Path
from typing import List, Dict, Optional


class Player:
    """Thin wrapper around pygame.mixer.music for MP3 playback and simple queues."""

    def __init__(self) -> None:
        # Initialize the mixer subsystem (opens audio device)
        pygame.mixer.init()
        self.current_file: Optional[Path] = None
        self.queue: List[Dict[str, str]] = []  # each: {"path": str, "title": str, ...}
        self.queue_index: int = -1
        self.paused: bool = False
        pygame.mixer.music.set_volume(0.7)  # Start at 70% volume

    # ---- low level ----
    def load(self, file_path: Path | str) -> None:
        """Load an MP3 into the mixer (does not start playback)."""
        self.current_file = Path(file_path)
        pygame.mixer.music.load(str(self.current_file))

    def play(self, start_pos: float = 0.0) -> None:
        """Start playback at start_pos seconds (default 0)."""
        if self.current_file is None:
            return
        pygame.mixer.music.play(start=start_pos)
        self.paused = False

    def pause(self) -> None:
        """Toggle pause/unpause."""
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.paused = True

    def stop(self) -> None:
        """Stop playback and clear paused flag."""
        pygame.mixer.music.stop()
        self.paused = False

    def set_volume(self, vol: float) -> None:
        """Set volume in [0.0, 1.0]. Input is clamped to this range."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))

    def is_playing(self) -> bool:
        """True if audio is playing (not paused)."""
        # get_busy() is True while playing OR paused; we add our paused flag.
        return pygame.mixer.music.get_busy() and not self.paused

    # ---- queue / playlist ----
    def play_file_now(self, file_path: Path | str) -> None:
        """Clear the queue and immediately play a single file."""
        self.queue = []
        self.queue_index = -1
        self.load(file_path)
        self.play()

    def load_queue(self, tracks: List[Dict[str, str]]) -> None:
        """Replace the queue with a new list of tracks (dicts with at least 'path')."""
        self.queue = list(tracks)
        self.queue_index = -1

    def play_queue_from_start(self) -> None:
        """Start playing the first item in the queue."""
        if not self.queue:
            return
        self.queue_index = 0
        self._play_current_from_queue()

    def play_index(self, index: int) -> None:
        """Play a specific index in the queue (clamped to valid range)."""
        if not self.queue:
            return
        index = max(0, min(index, len(self.queue) - 1))
        self.queue_index = index
        self._play_current_from_queue()

    def next_in_queue(self) -> None:
        """Advance to the next item; stop if past the end."""
        if not self.queue:
            return
        self.queue_index += 1
        if self.queue_index < len(self.queue):
            self._play_current_from_queue()
        else:
            # No more tracks
            self.stop()
            self.queue_index = -1

    def prev_in_queue(self) -> None:
        """Move to the previous item, clamped to 0."""
        if not self.queue:
            return
        self.queue_index = max(0, self.queue_index - 1)
        self._play_current_from_queue()

    def current_track(self) -> Optional[Dict[str, str]]:
        """Return the current track dict from the queue, or None."""
        if self.queue and 0 <= self.queue_index < len(self.queue):
            return self.queue[self.queue_index]
        return None

    def queue_len(self) -> int:
        """Number of items in the queue."""
        return len(self.queue)

    def _play_current_from_queue(self) -> None:
        """Helper: load & play the track at queue_index."""
        track = self.queue[self.queue_index]
        self.load(track["path"])
        self.play()
