from abc import ABC, abstractmethod
from typing import List, Optional

from core.models import MusicaTrack


class MusicSource(ABC):
    """
    Base interface for every music source supported by Musica.

    Local files, Spotify, YouTube Music, JioSaavn, etc.
    will implement this interface.
    """

    @abstractmethod
    def get_tracks(self) -> List[MusicaTrack]:
        """Return all available tracks from this source."""
        pass

    @abstractmethod
    def get_track(self, track_id: str) -> Optional[MusicaTrack]:
        """Return a specific track by its source ID."""
        pass