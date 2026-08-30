"""
Musica → YouTube Music bridge.

Connects Musica's actual intention-detection + ranking engine (running as
your local FastAPI server) to real playback via the YouTube Music browser
controller. The flow:

    natural language request
        -> Musica /api/queue  (LangGraph: intention detection, ranking)
        -> ranked list of {title, artist, ...}
        -> for each track: search "{title} {artist}" on YouTube Music, play it

IMPORTANT: YouTube's own Next/Previous buttons follow YOUTUBE's recommendation
algorithm, not Musica's ranked order. So in this bridge, `next`/`prev` do NOT
click YouTube's UI buttons — they step through Musica's own queue array and
re-search each track. This is what makes the queue actually "yours" rather
than YouTube's.

Prerequisites:
    1. Your local Musica API must be running:
           uvicorn API.main:app --reload
       (from the project root, so it's reachable at http://127.0.0.1:8000)
    2. pip install requests   (in addition to playwright, already installed)

Run:
    python musica_yt_bridge.py
"""

import requests
from yt_music_controller import YTMusicController

API_BASE = "http://127.0.0.1:8000"


def fetch_musica_queue(user_request: str, limit: int = 10):
    """Call Musica's real ranking engine and return (intention, tracks)."""
    try:
        resp = requests.get(
            f"{API_BASE}/api/queue",
            params={"request": user_request, "limit": limit},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        print(f"Could not reach Musica API at {API_BASE}.")
        print("Start it first: uvicorn API.main:app --reload  (from the project root)")
        return None, []

    if resp.status_code != 200:
        print(f"Musica API returned {resp.status_code}: {resp.text[:300]}")
        return None, []

    data = resp.json()
    intention = data.get("intention")
    tracks = data.get("tracks", [])
    print(f"Musica intention: {intention}  ({len(tracks)} tracks ranked)")
    return intention, tracks


class MusicaSession:
    """Holds Musica's ranked queue and drives real playback for it."""

    def __init__(self, ctrl: YTMusicController):
        self.ctrl = ctrl
        self.tracks = []
        self.index = -1

    def load_queue(self, tracks):
        self.tracks = tracks
        self.index = -1

    def _query_for(self, track):
        title = track.get("title", "")
        artist = track.get("artist", "")
        return f"{title} {artist}".strip()

    def play_index(self, i):
        if not (0 <= i < len(self.tracks)):
            print("No track at that queue position.")
            return
        self.index = i
        track = self.tracks[i]
        print(f"[{i + 1}/{len(self.tracks)}] Searching Musica-ranked track: {track.get('title')} — {track.get('artist')}")
        self.ctrl.search_and_play(self._query_for(track))

    def next(self):
        if not self.tracks:
            print("No Musica queue loaded yet — use: request <your intention>")
            return
        if self.index + 1 >= len(self.tracks):
            print("End of Musica queue.")
            return
        self.play_index(self.index + 1)

    def prev(self):
        if not self.tracks:
            print("No Musica queue loaded yet — use: request <your intention>")
            return
        if self.index - 1 < 0:
            print("Already at the start of the Musica queue.")
            return
        self.play_index(self.index - 1)

    def show_queue(self):
        if not self.tracks:
            print("No Musica queue loaded yet.")
            return
        for i, t in enumerate(self.tracks):
            marker = "->" if i == self.index else "  "
            print(f"{marker} {i + 1:02d}. {t.get('title')} — {t.get('artist')}")


def repl():
    print("Musica x YouTube Music bridge")
    print("Commands: request <intention text> | next | prev | pause | queue | now | quit")
    print("  'request' pulls a fresh ranked queue from Musica and plays track 1.")
    print("  'next'/'prev' step through THAT Musica queue (not YouTube's own recommendations).")

    ctrl = YTMusicController(headless=False)
    session = MusicaSession(ctrl)

    try:
        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue
            if cmd in ("quit", "exit"):
                break
            elif cmd == "pause":
                ctrl.play_pause()
            elif cmd == "next":
                session.next()
            elif cmd == "prev":
                session.prev()
            elif cmd == "now":
                ctrl._print_now_playing()
            elif cmd == "queue":
                session.show_queue()
            elif cmd.startswith("request "):
                intention, tracks = fetch_musica_queue(cmd[len("request "):])
                if tracks:
                    session.load_queue(tracks)
                    session.play_index(0)
            elif cmd.startswith("play "):
                # Manual override — searches directly, outside the Musica queue.
                ctrl.search_and_play(cmd[len("play "):])
            else:
                print("Unknown command. Try: request <text> | next | prev | pause | queue | now | quit")
    finally:
        ctrl.close()


if __name__ == "__main__":
    repl()