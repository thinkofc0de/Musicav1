"""
YouTube Music controller — personal "life hack" prototype.

Drives a real logged-in YouTube Music session via Playwright and exposes
play / pause / skip / previous / search-and-play as simple functions.

This is a LOCAL, SINGLE-USER prototype:
- One persistent browser profile stores your login session (cookies) on disk.
- You log in manually once; after that, the script reuses the session.
- Selectors are based on YouTube Music's current DOM structure and WILL
  break when YouTube changes their frontend. Treat this as a hack, not
  a stable integration.

Install:
    pip install playwright
    playwright install chromium

Run interactively:
    python yt_music_controller.py

First run will open a visible Chromium window on the YouTube Music login
page. Log in by hand, then come back to the terminal and press Enter.
Subsequent runs reuse the saved session in ./yt_music_profile/.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

PROFILE_DIR = Path("./yt_music_profile")
BASE_URL = "https://music.youtube.com"

# Selectors — YouTube Music's DOM changes periodically. If these break,
# open devtools on music.youtube.com and re-inspect the player bar.
SEL_PLAY_PAUSE = "ytmusic-player-bar #play-pause-button"
SEL_NEXT = "ytmusic-player-bar #next-button"
SEL_PREV = "ytmusic-player-bar #previous-button"
SEL_NOW_PLAYING_TITLE = "ytmusic-player-bar .title.ytmusic-player-bar"
SEL_NOW_PLAYING_ARTIST = "ytmusic-player-bar .byline.ytmusic-player-bar"
SEL_FIRST_RESULT_PLAY = "ytmusic-shelf-renderer ytmusic-responsive-list-item-renderer:first-child"


class YTMusicController:
    def __init__(self, headless: bool = False):
        self._pw = sync_playwright().start()

        self.context = self._pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            channel="chrome",  # use real installed Chrome, not bundled Chromium
            args=[
                "--disable-blink-features=AutomationControlled",  # hide automation flag Google checks for
            ],
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        self.page.goto(BASE_URL, wait_until="domcontentloaded", timeout=45000)
        self.page.wait_for_load_state("networkidle")

        # Always verify actual login state — never trust folder existence alone
        while not self._is_logged_in():
            print("Not signed in yet (or session expired).")
            print("Log into YouTube Music in the opened browser window.")
            input("Press Enter here ONLY after you see your account avatar top-right...")
            self.page.goto(BASE_URL, wait_until="domcontentloaded", timeout=45000)
            self.page.wait_for_load_state("networkidle")

        print("Confirmed: signed in.")

    def _is_logged_in(self) -> bool:
        """Check for account avatar (logged in) vs Sign in button (logged out)."""
        try:
            # "Sign in" button is visible when logged out
            signed_out = self.page.get_by_text("Sign in", exact=True).count() > 0
            return not signed_out
        except Exception:
            return False

    def search_and_play(self, query: str, wait_s: float = 2.5):
        """Navigate to search results for `query` and click the first result's Play button,
        explicitly ignoring the persistent player bar (which also has a 'Play' button)."""
        url = f"{BASE_URL}/search?q={query.replace(' ', '+')}"
        self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
        self.page.wait_for_url(f"{BASE_URL}/search*", timeout=10000)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)  # let SPA finish swapping in new content
        print(f"  [debug] landed on: {self.page.url}")

        candidates = self.page.get_by_role("button", name="Play", exact=True)
        deadline = time.time() + 8
        count = 0
        while time.time() < deadline and count == 0:
            count = candidates.count()
            if count == 0:
                time.sleep(0.3)

        # DIAGNOSTIC: print what we actually found, so we fix this based on
        # real evidence instead of guessing at YouTube's DOM structure again.
        print(f"  [debug] found {count} button(s) named 'Play':")
        for i in range(min(count, 6)):
            btn = candidates.nth(i)
            try:
                box = btn.bounding_box()
                snippet = btn.evaluate("el => el.outerHTML.slice(0, 140)")
                print(f"    #{i}: pos={box}  html={snippet!r}")
            except Exception as e:
                print(f"    #{i}: (could not inspect: {e})")

        target = candidates.nth(0) if count > 0 else None

        if target is None:
            shot_path = "last_failure.png"
            self.page.screenshot(path=shot_path)
            print(f"No results found for '{query}'")
            print(f"  [debug] page title: {self.page.title()}")
            print(f"  [debug] screenshot saved to {shot_path} — open it to see what the page actually showed")
            return False

        target.click()
        time.sleep(wait_s)
        self._print_now_playing()
        return True

    def _click_by_role_name(self, names, timeout_s=8):
        """Click the first button matching any of the given accessible names.
        Tries each name in order (useful for play/pause which toggles its label)."""
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            for name in names:
                btn = self.page.get_by_role("button", name=name, exact=True)
                if btn.count() > 0:
                    btn.first.click()
                    return True
            time.sleep(0.3)
        return False

    def play_pause(self):
        if not self._click_by_role_name(["Pause", "Play"]):
            print("Could not find a Play/Pause button — is anything loaded in the player?")
            return
        time.sleep(0.5)
        self._print_now_playing()

    def next_track(self):
        if not self._click_by_role_name(["Next"]):
            print("Could not find a Next button.")
            return
        time.sleep(1.5)
        self._print_now_playing()

    def previous_track(self):
        if not self._click_by_role_name(["Previous"]):
            print("Could not find a Previous button.")
            return
        time.sleep(1.5)
        self._print_now_playing()

    def now_playing(self):
        try:
            title = self.page.locator(SEL_NOW_PLAYING_TITLE).first.inner_text(timeout=2000)
            artist = self.page.locator(SEL_NOW_PLAYING_ARTIST).first.inner_text(timeout=2000)
            return {"title": title, "artist": artist}
        except PWTimeout:
            return {"title": None, "artist": None}

    def _print_now_playing(self):
        info = self.now_playing()
        if info["title"]:
            print(f"Now playing: {info['title']} — {info['artist']}")

    def close(self):
        self.context.close()
        self._pw.stop()


def repl():
    print("YouTube Music controller — commands: play <query> | pause | next | prev | now | quit")
    ctrl = YTMusicController(headless=False)
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
                ctrl.next_track()
            elif cmd == "prev":
                ctrl.previous_track()
            elif cmd == "now":
                ctrl._print_now_playing()
            elif cmd.startswith("play "):
                ctrl.search_and_play(cmd[len("play "):])
            else:
                print("Unknown command. Try: play <query> | pause | next | prev | now | quit")
    finally:
        ctrl.close()


if __name__ == "__main__":
    repl()