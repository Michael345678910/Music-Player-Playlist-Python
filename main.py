from __future__ import annotations
import random
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from pathlib import Path

# --- Drag-and-drop support ---
# tkinterdnd2 lets users drop files from the OS onto the window.
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # pip install tkinterdnd2
    BaseTk = TkinterDnD.Tk
    DND_AVAILABLE = True
except Exception:
    # If the package is missing, we still run the app, just without DnD.
    BaseTk = tk.Tk
    DND_AVAILABLE = False

# --- Metadata support (ID3 tags and duration) ---
# mutagen reads MP3 tags like Title/Artist and audio length.
try:
    from mutagen.mp3 import MP3  # pip install mutagen
    from mutagen.id3 import ID3
    META_AVAILABLE = True
except Exception:
    META_AVAILABLE = False

from playlist_store import PlaylistStore
from player import Player


APP_TITLE = "MP3 Player with Playlists"
POLL_MS = 500  # Polling interval (ms) to detect when a track finishes.


def fmt_duration(secs: float | int | None) -> str:
    """Format seconds as MM:SS. Return placeholder for unknown."""
    if secs is None:
        return "--:--"
    try:
        secs = int(round(secs))
        m, s = divmod(secs, 60)
        return f"{m:02d}:{s:02d}"
    except Exception:
        return "--:--"


def read_metadata(path: Path) -> tuple[str | None, str | None, str | None]:
    """Return (title, artist, duration_str). Falls back to (None, None, None) if unavailable."""
    if not META_AVAILABLE:
        return None, None, None
    try:
        # MP3(..., ID3=ID3) ensures we can read tag frames like TIT2 (title) and TPE1 (artist).
        audio = MP3(str(path), ID3=ID3)
        title = None
        artist = None
        if audio.tags:
            t = audio.tags.get("TIT2")  # Title frame
            a = audio.tags.get("TPE1")  # Lead artist frame
            title = str(t.text[0]) if t and t.text else None
            artist = str(a.text[0]) if a and a.text else None
        # audio.info.length is the length in seconds (float)
        duration = fmt_duration(getattr(audio.info, "length", None))
        return title, artist, duration
    except Exception:
        # Malformed or missing tags shouldn't crash the app.
        return None, None, None


class App(BaseTk):
    """Main Tkinter application window and UI logic."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x560")
        self.minsize(820, 520)

        # Core components
        self.store = PlaylistStore()   # JSON-backed playlist storage
        self.player = Player()         # Audio playback wrapper

        # UI state
        self.current_file: Path | None = None
        self.shuffle: bool = False
        self.repeat_one: bool = False
        self.shuffle_pool: list[int] = []  # Remaining indices to play in shuffle mode
        self.history: list[int] = []       # Indices already played (for Prev/Next in shuffle)
        self.history_pos: int = -1         # Pointer into history (supports back/forward)

        # Window grid layout: top row controls, bottom row playlist panel
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_top_controls()
        self._build_playlist_panel()
        self._refresh_playlists()

        # Drag-and-drop registration (if available)
        if DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop_files)

        # Start periodic polling to auto-advance tracks when one finishes.
        self.after(POLL_MS, self._poll_playback)

    # ---------------- UI builders ----------------
    def _build_top_controls(self) -> None:
        """Build the top toolbar: transport controls, volume, shuffle/repeat, add-to-playlist."""
        frame = ttk.Frame(self, padding=12)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(8, weight=1)

        # A label that displays the current/now playing file or title
        self.current_label_var = tk.StringVar(value="No file loaded")
        ttk.Label(frame, textvariable=self.current_label_var).grid(row=0, column=0, columnspan=9, sticky="w")

        # Row 1: Load / Play / Pause / Stop
        ttk.Button(frame, text="Load MP3", command=self._on_load_file).grid(row=1, column=0, padx=2, pady=8)
        ttk.Button(frame, text="Play ▶", command=self._on_play).grid(row=1, column=1, padx=2)
        ttk.Button(frame, text="Pause ⏯", command=self._on_pause_toggle).grid(row=1, column=2, padx=2)
        ttk.Button(frame, text="Stop ⏹", command=self._on_stop).grid(row=1, column=3, padx=2)

        # Volume slider (0..100 mapped to 0.0..1.0)
        ttk.Label(frame, text="Volume").grid(row=1, column=4, padx=(20, 4))
        self.vol = tk.DoubleVar(value=70)
        vol_slider = ttk.Scale(frame, from_=0, to=100, variable=self.vol, command=self._on_volume)
        vol_slider.grid(row=1, column=5, padx=4, sticky="ew")
        frame.columnconfigure(5, weight=1)

        # Shuffle toggle (checkbox style)
        self.btn_shuffle = ttk.Checkbutton(frame, text="Shuffle", command=self._toggle_shuffle)
        self.btn_shuffle.state(["!alternate"])  # Ensure it behaves as a regular on/off toggle
        self.btn_shuffle.grid(row=1, column=6, padx=(12, 2))

        # Repeat-one toggle (checkbox style)
        self.repeat_var = tk.BooleanVar(value=False)
        self.btn_repeat = ttk.Checkbutton(frame, text="Repeat One", variable=self.repeat_var, command=self._toggle_repeat)
        self.btn_repeat.grid(row=1, column=7, padx=2)

        # Add currently loaded file to selected playlist
        ttk.Button(frame, text="Add to Playlist…", command=self._on_add_current_to_playlist).grid(row=1, column=8, padx=6)

    def _build_playlist_panel(self) -> None:
        """Build the lower panel: playlist selection, track table, and playlist actions."""
        outer = ttk.Frame(self, padding=12)
        outer.grid(row=1, column=0, sticky="nsew")
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(1, weight=1)

        # Playlist dropdown + management buttons
        left = ttk.Frame(outer)
        left.grid(row=0, column=0, sticky="w")
        ttk.Label(left, text="Playlists:").pack(side=tk.LEFT)
        self.playlist_combo = ttk.Combobox(left, state="readonly", width=28)
        self.playlist_combo.pack(side=tk.LEFT, padx=6)
        # When user selects a different playlist, refresh the tracks table
        self.playlist_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_tracks())

        ttk.Button(left, text="New",    command=self._on_new_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(left, text="Rename", command=self._on_rename_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(left, text="Delete", command=self._on_delete_playlist).pack(side=tk.LEFT, padx=2)

        # Track table shows index, title, duration, and file path
        cols = ("#", "Title", "Duration", "Path")
        self.tree = ttk.Treeview(outer, columns=cols, show="headings")
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        self.tree.heading("#", text="#")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Duration", text="Duration")
        self.tree.heading("Path", text="Path")
        self.tree.column("#", width=40, anchor=tk.CENTER)
        self.tree.column("Title", width=280)
        self.tree.column("Duration", width=90, anchor=tk.CENTER)
        self.tree.column("Path", width=460)

        # Scrollbar for the track table
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=2, sticky="ns")
        self.tree.configure(yscroll=vsb.set)

        # Bottom row: playback and editing controls for the selected playlist
        btns = ttk.Frame(outer)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        btns.columnconfigure(4, weight=1)

        ttk.Button(btns, text="Play Playlist ▶", command=self._on_play_playlist).grid(row=0, column=0, padx=2)
        ttk.Button(btns, text="Prev ⏮",           command=self._on_prev).grid(row=0, column=1, padx=2)
        ttk.Button(btns, text="Next ⏭",           command=self._on_next).grid(row=0, column=2, padx=2)
        ttk.Button(btns, text="Remove Track",     command=self._on_remove_track).grid(row=0, column=3, padx=8)

        if DND_AVAILABLE:
            tip = ttk.Label(outer, text="Tip: Drag & drop MP3 files to add them to the selected playlist.")
            tip.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

    # ---------------- Event handlers ----------------
    def _on_load_file(self) -> None:
        """Ask the user for an MP3 and play it immediately."""
        path = filedialog.askopenfilename(title="Select MP3 file", filetypes=[("MP3 files", "*.mp3")])
        if not path:
            return
        self._play_single(Path(path))

    def _play_single(self, p: Path) -> None:
        """Load a single file for immediate playback and update 'Loaded' label."""
        self.current_file = p
        title, artist, duration = read_metadata(p)
        # Prefer "Title – Artist" if tags exist; otherwise show filename stem
        nice_title = f"{title} – {artist}" if title and artist else (title or p.stem)
        self.current_label_var.set(f"Loaded: {nice_title}")
        self.player.play_file_now(p)

    def _on_play(self) -> None:
        """Resume/Start playback of current file."""
        if self.current_file is None:
            messagebox.showinfo("No file", "Load an MP3 first or play a playlist.")
            return
        self.player.play()

    def _on_pause_toggle(self) -> None:
        """Toggle between pause and unpause."""
        self.player.pause()

    def _on_stop(self) -> None:
        """Stop playback."""
        self.player.stop()

    def _on_volume(self, _evt=None) -> None:
        """Volume slider callback (0..100 mapped to 0.0..1.0)."""
        self.player.set_volume(self.vol.get() / 100.0)

    def _on_add_current_to_playlist(self) -> None:
        """Add the currently loaded file to the selected playlist (with metadata)."""
        if self.current_file is None:
            messagebox.showinfo("No file", "Load an MP3 first.")
            return
        pl = self.playlist_combo.get()
        if not pl:
            messagebox.showinfo("No playlist", "Create/select a playlist first.")
            return
        title, artist, duration = read_metadata(self.current_file)
        display_title = f"{title} – {artist}" if title and artist else (title or self.current_file.stem)
        self.store.add_track(pl, self.current_file, title=display_title, duration=duration)
        self._refresh_tracks()

    def _on_new_playlist(self) -> None:
        """Create a new (empty) playlist."""
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if not name:
            return
        try:
            self.store.create_playlist(name)
            self._refresh_playlists(select=name)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _on_rename_playlist(self) -> None:
        """Rename the currently selected playlist."""
        old = self.playlist_combo.get()
        if not old:
            return
        new = simpledialog.askstring("Rename Playlist", f"Rename '{old}' to:")
        if not new or new == old:
            return
        try:
            self.store.rename_playlist(old, new)
            self._refresh_playlists(select=new)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _on_delete_playlist(self) -> None:
        """Delete the selected playlist (after confirmation)."""
        name = self.playlist_combo.get()
        if not name:
            return
        if messagebox.askyesno("Delete Playlist", f"Delete '{name}'?"):
            self.store.delete_playlist(name)
            self._refresh_playlists()
            self._refresh_tracks()

    def _on_play_playlist(self) -> None:
        """Load the selected playlist into the player and start it."""
        name = self.playlist_combo.get()
        if not name:
            messagebox.showinfo("No playlist", "Create/select a playlist first.")
            return
        tracks = self.store.get_tracks(name)
        if not tracks:
            messagebox.showinfo("Empty playlist", "Add tracks to this playlist first.")
            return

        self.player.load_queue(tracks)

        # Reset shuffle history for a new play session
        self.history = []
        self.history_pos = -1

        if self.shuffle:
            self._init_shuffle_pool()
            self._play_next_shuffle()
        else:
            self.player.play_queue_from_start()
            self._record_history(self.player.queue_index)

        self._update_now_playing_label_from_queue()

    def _on_next(self) -> None:
        """Advance to the next track, honoring repeat-one and shuffle behavior."""
        if self.repeat_one and self.player.queue_len() > 0 and self.player.queue_index != -1:
            # Repeat current track
            self.player.play_index(self.player.queue_index)
            self._record_history(self.player.queue_index)
        elif self.shuffle and self.player.queue_len() > 0:
            # Random next track (but with reproducible history)
            self._play_next_shuffle()
        else:
            # Regular sequential next
            self.player.next_in_queue()
            if self.player.queue_index != -1:
                self._record_history(self.player.queue_index)
        self._update_now_playing_label_from_queue()

    def _on_prev(self) -> None:
        """Go to the previous track. In shuffle, use the history list to step back."""
        if self.shuffle and self.history_pos > 0:
            # Move backward in shuffle history
            self.history_pos -= 1
            idx = self.history[self.history_pos]
            self.player.play_index(idx)
        else:
            # Sequential previous
            self.player.prev_in_queue()
            if self.player.queue_index != -1:
                self._record_history(self.player.queue_index)
        self._update_now_playing_label_from_queue()

    def _on_remove_track(self) -> None:
        """Remove the selected track from the current playlist."""
        name = self.playlist_combo.get()
        if not name:
            return
        sel = self.tree.selection()
        if not sel:
            return
        # First column (#) is 1-based for display; convert to 0-based index
        index = int(self.tree.item(sel[0], "values")[0]) - 1
        self.store.remove_track_at(name, index)
        self._refresh_tracks()

    def _on_drop_files(self, event) -> None:
        """Handle drag-and-drop: parse OS-provided path list and add MP3s."""
        # event.data is a space-separated list of paths; paths with spaces are wrapped in { }.
        raw = event.data
        paths: list[str] = []
        token = ""
        inside = False

        # Small state machine to split by spaces only when not inside { ... }
        for ch in raw:
            if ch == "{":
                inside = True
                token = ""
            elif ch == "}":
                inside = False
                paths.append(token)
                token = ""
            elif ch == " " and not inside:
                if token:
                    paths.append(token)
                    token = ""
            else:
                token += ch
        if token:
            paths.append(token)

        added = 0
        current_pl = self.playlist_combo.get()
        if not current_pl:
            messagebox.showinfo("No playlist", "Create/select a playlist first.")
            return

        for p in paths:
            P = Path(p)
            if P.suffix.lower() != ".mp3":
                continue  # Ignore non-MP3 files quietly
            title, artist, duration = read_metadata(P)
            display_title = f"{title} – {artist}" if title and artist else (title or P.stem)
            self.store.add_track(current_pl, P, title=display_title, duration=duration)
            added += 1

        if added:
            self._refresh_tracks()

    # ---------------- Helpers ----------------
    def _toggle_shuffle(self) -> None:
        """Enable/disable shuffle mode."""
        self.shuffle = not self.shuffle

    def _toggle_repeat(self) -> None:
        """Enable/disable repeat-one mode."""
        self.repeat_one = bool(self.repeat_var.get())

    def _init_shuffle_pool(self) -> None:
        """Create a shuffled list of all track indices (excluding current if set)."""
        n = self.player.queue_len()
        self.shuffle_pool = list(range(n))
        random.shuffle(self.shuffle_pool)
        # If a track is already selected, remove it to avoid immediate repeat.
        if self.player.queue_index in self.shuffle_pool:
            self.shuffle_pool.remove(self.player.queue_index)

    def _play_next_shuffle(self) -> None:
        """Pick the next track via shuffle, respecting back/forward history."""
        # If we previously pressed Prev in shuffle, let Next step forward through history first.
        if 0 <= self.history_pos < len(self.history) - 1:
            self.history_pos += 1
            idx = self.history[self.history_pos]
            self.player.play_index(idx)
            return

        # Otherwise take next from the random pool; when empty, start a new cycle.
        if not self.shuffle_pool:
            self._init_shuffle_pool()
        idx = self.shuffle_pool.pop(0)
        self.player.play_index(idx)
        self._record_history(idx)

    def _record_history(self, idx: int) -> None:
        """Append an index to history, trimming any 'forward' entries if we had gone back."""
        # If we went back and then chose a different path, discard the forward branch.
        if 0 <= self.history_pos < len(self.history) - 1:
            self.history = self.history[: self.history_pos + 1]
        if not self.history or self.history[-1] != idx:
            self.history.append(idx)
        self.history_pos = len(self.history) - 1

    def _refresh_playlists(self, select: str | None = None) -> None:
        """Update playlist dropdown and refresh track table."""
        names = self.store.list_playlists()
        self.playlist_combo["values"] = names
        if select and select in names:
            self.playlist_combo.set(select)
        elif names and not self.playlist_combo.get():
            self.playlist_combo.set(names[0])
        elif not names:
            self.playlist_combo.set("")
        self._refresh_tracks()

    def _refresh_tracks(self) -> None:
        """Reload the track table for the selected playlist."""
        # Clear existing rows
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        name = self.playlist_combo.get()
        if not name:
            return

        tracks = self.store.get_tracks(name)
        for i, t in enumerate(tracks, start=1):
            # Backfill duration/title if missing (non-destructive to disk)
            title = t.get("title") or Path(t["path"]).stem
            duration = t.get("duration")
            if duration is None:
                # Try reading metadata for display; if unavailable use placeholder
                _title, _artist, _dur = read_metadata(Path(t["path"]))
                if _title and _artist:
                    title = f"{_title} – {_artist}"
                duration = _dur or "--:--"

            # Insert row: display index is 1-based
            self.tree.insert("", "end", values=(i, title, duration, t["path"]))

    def _poll_playback(self) -> None:
        """Poll periodically to detect track end and auto-advance if a queue is active."""
        try:
            # If we are not paused, not currently playing, but had a valid queue item, move on.
            if (
                not self.player.paused
                and not self.player.is_playing()
                and self.player.queue_len() > 0
                and self.player.queue_index != -1
            ):
                # Decide next step based on repeat/shuffle mode
                if self.repeat_one:
                    self.player.play_index(self.player.queue_index)
                elif self.shuffle:
                    self._play_next_shuffle()
                else:
                    self.player.next_in_queue()
                self._update_now_playing_label_from_queue()
        finally:
            # Re-arm the poll timer regardless of what happened above
            self.after(POLL_MS, self._poll_playback)

    def _update_now_playing_label_from_queue(self) -> None:
        """Update the 'Now playing' label from the player's current queue entry."""
        tr = self.player.current_track()
        if tr:
            p = Path(tr["path"])
            # Prefer stored title; fall back to metadata or filename
            title = tr.get("title") or p.stem
            if META_AVAILABLE and (not tr.get("title") or " – " not in tr.get("title", "")):
                _t, _a, _ = read_metadata(p)
                if _t and _a:
                    title = f"{_t} – {_a}"
            self.current_label_var.set(f"Now playing: {title}")
            self.current_file = p
        else:
            # No active queue item; show last loaded file or default message
            if self.current_file:
                self.current_label_var.set(f"Loaded: {self.current_file.name}")
            else:
                self.current_label_var.set("No file loaded")


if __name__ == "__main__":
    app = App()
    app.mainloop()
