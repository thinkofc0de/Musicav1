from typing import TypedDict, List, Dict, Any, Optional

from core.models import MusicaTrack


class MusicaState(TypedDict, total=False):
    user_request: str

    intention: str

    tracks: List[MusicaTrack]

    ranked_tracks: List[Dict[str, Any]]

    queue: List[MusicaTrack]

    response: str

    error: Optional[str]