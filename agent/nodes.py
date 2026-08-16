import os
from typing import Dict, Any
from pathlib import Path

from sources.local import LocalMusicSource

from core.music.intention import classify_intention
from core.music.music_profile import build_music_profile
from core.queue import rank_tracks

from agent.state import MusicaState


# ============================================================
# NODE 1 — UNDERSTAND USER INTENTION
# ============================================================

def understand_intention(state: MusicaState) -> MusicaState:

    request = state.get("user_request", "").lower()

    # V1 rule-based intention detection.
    # Later this can be replaced with an LLM node.

    if any(word in request for word in [
        "focus",
        "study",
        "concentrate",
        "deep work",
        "coding",
    ]):
        intention = "DEEP_FOCUS"

    elif any(word in request for word in [
        "energy",
        "energetic",
        "motivate",
        "gym",
    ]):
        intention = "ENERGY_BOOST"

    elif any(word in request for word in [
        "relax",
        "calm",
        "peaceful",
    ]):
        intention = "RELAXATION"

    elif any(word in request for word in [
        "sleep",
        "wind down",
        "slow down",
    ]):
        intention = "WIND_DOWN"

    else:
        intention = "GENERAL_WORK"

    print(f"[LangGraph] Intention: {intention}")

    return {
        **state,
        "intention": intention,
    }


# ============================================================
# NODE 2 — LOAD MUSIC LIBRARY
# ============================================================

def load_library(state: MusicaState) -> MusicaState:

    music_directory = (
        Path(__file__).resolve().parent.parent / "music"
    )

    source = LocalMusicSource(
        str(music_directory)
    )

    tracks = source.get_tracks()

    print(
        f"[LangGraph] Loaded {len(tracks)} tracks"
    )

    return {
        **state,
        "tracks": tracks,
    }


# ============================================================
# NODE 3 — RANK TRACKS
# ============================================================

def rank_music(state: MusicaState) -> MusicaState:

    tracks = state.get("tracks", [])
    intention = state.get(
        "intention",
        "GENERAL_WORK"
    )

    ranked = rank_tracks(
        tracks,
        intention
    )

    print(
        f"[LangGraph] Ranked {len(ranked)} tracks "
        f"for {intention}"
    )

    return {
        **state,
        "ranked_tracks": ranked,
    }


# ============================================================
# NODE 4 — BUILD QUEUE
# ============================================================

def build_music_queue(state: MusicaState) -> MusicaState:

    ranked = state.get(
        "ranked_tracks",
        []
    )

    queue = [
        item["track"]
        for item in ranked[:10]
    ]

    print(
        f"[LangGraph] Queue created: {len(queue)} tracks"
    )

    return {
        **state,
        "queue": queue,
    }


# ============================================================
# NODE 5 — GENERATE RESPONSE
# ============================================================

def generate_response(state: MusicaState) -> MusicaState:

    intention = state.get(
        "intention",
        "GENERAL_WORK"
    )

    queue = state.get(
        "queue",
        []
    )

    if not queue:

        response = (
            "I couldn't find suitable tracks "
            "for this intention."
        )

    else:

        response = (
            f"Created a {intention.replace('_', ' ').title()} "
            f"queue with {len(queue)} tracks."
        )

    return {
        **state,
        "response": response,
    }