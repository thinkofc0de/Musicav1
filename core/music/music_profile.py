from dataclasses import dataclass, asdict
from typing import Optional

from core.models import MusicaTrack


# ============================================================
# MUSIC PROFILE
# ============================================================

@dataclass
class MusicProfile:
    """
    Higher-level musical profile derived from measurable
    audio features available on a MusicaTrack.

    Values are normalized to the range 0.0 - 1.0.
    """

    energy: float
    intensity: float
    calm: float
    focus: float

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# HELPERS
# ============================================================

def _clamp(value: float) -> float:
    """Keep a value between 0.0 and 1.0."""

    return max(0.0, min(1.0, value))


def _normalize_rms(
    rms: Optional[float],
) -> float:
    """
    Convert RMS energy into a practical 0-1 range.

    This remains intentionally conservative because RMS
    depends heavily on recording/mastering level.
    """

    if rms is None:
        return 0.5

    return _clamp(rms / 0.40)


def _normalize_zcr(
    zcr: Optional[float],
) -> float:
    """
    Normalize zero-crossing rate.

    Higher ZCR generally represents more rapid waveform
    changes and can contribute to perceived intensity.
    """

    if zcr is None:
        return 0.5

    return _clamp(zcr / 0.15)


def _normalize_centroid(
    centroid: Optional[float],
) -> float:
    """
    Normalize spectral centroid.

    Approximate useful musical range:
        500 Hz  -> 0.0
        5000 Hz -> 1.0

    This is treated as a spectral-brightness proxy,
    NOT as a direct measure of emotion.
    """

    if centroid is None:
        return 0.5

    return _clamp(
        (centroid - 500.0) / 4500.0
    )


def _normalize_bandwidth(
    bandwidth: Optional[float],
) -> float:
    """
    Normalize spectral bandwidth.

    Wider bandwidth generally indicates that energy is
    distributed across a broader frequency range.

    Approximate useful range:
        500 Hz  -> 0.0
        5000 Hz -> 1.0
    """

    if bandwidth is None:
        return 0.5

    return _clamp(
        (bandwidth - 500.0) / 4500.0
    )


def _normalize_rolloff(
    rolloff: Optional[float],
) -> float:
    """
    Normalize spectral rolloff.

    Higher rolloff generally means more spectral energy
    extends into higher frequencies.

    Approximate useful range:
        1000 Hz  -> 0.0
        10000 Hz -> 1.0
    """

    if rolloff is None:
        return 0.5

    return _clamp(
        (rolloff - 1000.0) / 9000.0
    )


# ============================================================
# PROFILE CONSTRUCTION
# ============================================================

def build_music_profile(
    track: MusicaTrack,
) -> MusicProfile:
    """
    Convert measurable audio features into a higher-level
    MusicProfile.

    Current measurable inputs:

        RMS
        Zero-crossing rate
        Spectral centroid
        Spectral bandwidth
        Spectral rolloff

    The resulting profile contains:

        energy
        intensity
        calm
        focus
    """

    features = track.audio_features or {}

    # --------------------------------------------------------
    # Raw features
    # --------------------------------------------------------

    rms = features.get("rms_energy")
    zcr = features.get("zero_crossing_rate")

    centroid = features.get(
        "spectral_centroid"
    )

    bandwidth = features.get(
        "spectral_bandwidth"
    )

    rolloff = features.get(
        "spectral_rolloff"
    )

    # --------------------------------------------------------
    # Normalize measurable features
    # --------------------------------------------------------

    normalized_rms = _normalize_rms(rms)
    normalized_zcr = _normalize_zcr(zcr)

    normalized_centroid = _normalize_centroid(
        centroid
    )

    normalized_bandwidth = _normalize_bandwidth(
        bandwidth
    )

    normalized_rolloff = _normalize_rolloff(
        rolloff
    )

    # ========================================================
    # ENERGY
    # ========================================================
    #
    # RMS remains the strongest contributor because it is
    # the most direct measurement we currently have for
    # overall signal energy.
    #
    # Spectral characteristics provide a smaller contribution.
    #

    energy = (
        normalized_rms * 0.75
        + normalized_centroid * 0.10
        + normalized_rolloff * 0.10
        + normalized_bandwidth * 0.05
    )

    energy = _clamp(energy)

    # ========================================================
    # INTENSITY
    # ========================================================
    #
    # Intensity represents how sonically "active" the track is.
    #
    # RMS + ZCR are the primary components.
    # Spectral bandwidth and high-frequency content add
    # additional information.
    #

    intensity = (
        normalized_rms * 0.50
        + normalized_zcr * 0.20
        + normalized_centroid * 0.10
        + normalized_bandwidth * 0.10
        + normalized_rolloff * 0.10
    )

    intensity = _clamp(intensity)

    # ========================================================
    # CALM
    # ========================================================
    #
    # Calm is currently the inverse of intensity.
    #
    # This remains a heuristic and should not be interpreted
    # as an objective measurement of emotional calmness.
    #

    calm = _clamp(
        1.0 - intensity
    )

    # ========================================================
    # FOCUS
    # ========================================================
    #
    # Focus should not simply be a copy of energy.
    #
    # We currently favor:
    #
    #   - moderate energy
    #   - lower intensity
    #   - moderate spectral brightness
    #   - moderate spectral spread
    #
    # This is still a heuristic.
    #

    energy_focus = (
        1.0
        - abs(energy - 0.45) / 0.55
    )

    intensity_focus = (
        1.0
        - intensity
    )

    spectral_focus = (
        1.0
        - abs(
            normalized_centroid - 0.45
        )
    )

    bandwidth_focus = (
        1.0
        - abs(
            normalized_bandwidth - 0.45
        )
    )

    focus = (
        energy_focus * 0.40
        + intensity_focus * 0.30
        + spectral_focus * 0.15
        + bandwidth_focus * 0.15
    )

    focus = _clamp(focus)

    # ========================================================
    # RETURN PROFILE
    # ========================================================

    return MusicProfile(
        energy=round(
            energy,
            4,
        ),

        intensity=round(
            intensity,
            4,
        ),

        calm=round(
            calm,
            4,
        ),

        focus=round(
            focus,
            4,
        ),
    )