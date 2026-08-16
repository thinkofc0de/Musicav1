from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf


# ============================================================
# AUDIO ANALYSIS SETTINGS
# ============================================================

# FFT analysis settings.
#
# 2048 samples gives a reasonable balance between:
# - frequency resolution
# - computational cost
#
# We analyze the song in overlapping frames rather than
# calculating spectral features from the entire song at once.

FRAME_SIZE = 2048
HOP_SIZE = 1024

# Rolloff means the frequency below which this percentage
# of the spectral energy is contained.
ROLLOFF_PERCENTAGE = 0.85


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _frame_audio(
    audio: np.ndarray,
    frame_size: int,
    hop_size: int,
) -> np.ndarray:
    """
    Split audio into overlapping frames.

    Returns:
        2D NumPy array with shape:

            (number_of_frames, frame_size)

    If the audio is shorter than one frame, zero-padding
    is applied.
    """

    if len(audio) == 0:
        return np.empty((0, frame_size))

    # --------------------------------------------------------
    # Pad short audio
    # --------------------------------------------------------

    if len(audio) < frame_size:

        padded = np.zeros(frame_size)

        padded[:len(audio)] = audio

        return padded.reshape(1, -1)

    # --------------------------------------------------------
    # Number of frames
    # --------------------------------------------------------

    num_frames = 1 + (
        (len(audio) - frame_size) // hop_size
    )

    frames = np.empty(
        (num_frames, frame_size),
        dtype=audio.dtype,
    )

    for i in range(num_frames):

        start = i * hop_size
        end = start + frame_size

        frames[i] = audio[start:end]

    return frames


def _spectral_features(
    mono: np.ndarray,
    sample_rate: int,
) -> dict:
    """
    Calculate spectral features from an audio signal.

    Features:
        - spectral_centroid
        - spectral_bandwidth
        - spectral_rolloff

    The calculation is performed frame-by-frame and the
    resulting values are averaged across the song.

    Returns:
        Dictionary containing spectral features.
    """

    if len(mono) == 0:
        return {
            "spectral_centroid": 0.0,
            "spectral_bandwidth": 0.0,
            "spectral_rolloff": 0.0,
        }

    # --------------------------------------------------------
    # Create overlapping frames
    # --------------------------------------------------------

    frames = _frame_audio(
        mono,
        FRAME_SIZE,
        HOP_SIZE,
    )

    if len(frames) == 0:
        return {
            "spectral_centroid": 0.0,
            "spectral_bandwidth": 0.0,
            "spectral_rolloff": 0.0,
        }

    # --------------------------------------------------------
    # Apply Hann window
    # --------------------------------------------------------

    window = np.hanning(FRAME_SIZE)

    windowed_frames = frames * window

    # --------------------------------------------------------
    # Real FFT
    # --------------------------------------------------------

    spectrum = np.abs(
        np.fft.rfft(
            windowed_frames,
            axis=1,
        )
    )

    # Convert magnitude to power.
    power = np.square(spectrum)

    # Frequency corresponding to each FFT bin.
    frequencies = np.fft.rfftfreq(
        FRAME_SIZE,
        d=1.0 / sample_rate,
    )

    # Prevent division by zero for silent frames.
    power_sum = np.sum(
        power,
        axis=1,
    )

    valid = power_sum > 1e-12

    # If every frame is silent, return zeros.
    if not np.any(valid):

        return {
            "spectral_centroid": 0.0,
            "spectral_bandwidth": 0.0,
            "spectral_rolloff": 0.0,
        }

    valid_power = power[valid]
    valid_power_sum = power_sum[valid]

    # --------------------------------------------------------
    # Spectral Centroid
    # --------------------------------------------------------
    #
    # Represents the "center of mass" of the spectrum.
    #
    # Higher value generally means more energy is concentrated
    # toward higher frequencies.
    #
    # This is NOT a direct measure of brightness or emotion.
    #

    centroid = (
        np.sum(
            valid_power * frequencies,
            axis=1,
        )
        / valid_power_sum
    )

    # --------------------------------------------------------
    # Spectral Bandwidth
    # --------------------------------------------------------
    #
    # Measures how spread out the spectrum is around
    # its centroid.
    #

    bandwidth = np.sqrt(
        np.sum(
            valid_power
            * (
                frequencies[None, :]
                - centroid[:, None]
            ) ** 2,
            axis=1,
        )
        / valid_power_sum
    )

    # --------------------------------------------------------
    # Spectral Rolloff
    # --------------------------------------------------------
    #
    # Find the frequency below which 85% of spectral power
    # is contained.
    #

    cumulative_power = np.cumsum(
        valid_power,
        axis=1,
    )

    threshold = (
        valid_power_sum
        * ROLLOFF_PERCENTAGE
    )

    rolloff_indices = np.argmax(
        cumulative_power >= threshold[:, None],
        axis=1,
    )

    rolloff = frequencies[
        rolloff_indices
    ]

    # --------------------------------------------------------
    # Aggregate across frames
    # --------------------------------------------------------

    return {
        "spectral_centroid": float(
            np.mean(centroid)
        ),

        "spectral_bandwidth": float(
            np.mean(bandwidth)
        ),

        "spectral_rolloff": float(
            np.mean(rolloff)
        ),
    }


# ============================================================
# MAIN FEATURE EXTRACTION
# ============================================================

def extract_audio_features(
    file_path: str,
) -> Optional[dict]:
    """
    Extract measurable audio features from a music file.

    V2.1 keeps all V1 features and adds:

        - spectral_centroid
        - spectral_bandwidth
        - spectral_rolloff

    The spectral features are calculated frame-by-frame
    using an FFT and then averaged across the track.

    Returns:
        Dictionary containing audio characteristics,
        or None if the file cannot be analyzed.
    """

    path = Path(file_path)

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not path.exists():

        print(
            f"[Audio Features] File not found: {path}"
        )

        return None

    try:

        # ----------------------------------------------------
        # Read audio
        # ----------------------------------------------------

        audio, sample_rate = sf.read(
            str(path),
            always_2d=True,
        )

        if audio.size == 0:

            print(
                f"[Audio Features] Empty audio file: "
                f"{path.name}"
            )

            return None

        # ----------------------------------------------------
        # Basic information
        # ----------------------------------------------------

        channels = audio.shape[1]

        # ----------------------------------------------------
        # Convert stereo/multichannel → mono
        # ----------------------------------------------------

        mono = audio.mean(axis=1)

        if len(mono) == 0:

            print(
                f"[Audio Features] Empty mono signal: "
                f"{path.name}"
            )

            return None

        # ----------------------------------------------------
        # Duration
        # ----------------------------------------------------

        duration = (
            len(mono) / sample_rate
        )

        # ----------------------------------------------------
        # RMS Energy
        # ----------------------------------------------------

        rms_energy = float(
            np.sqrt(
                np.mean(
                    np.square(mono)
                )
            )
        )

        # ----------------------------------------------------
        # Peak Amplitude
        # ----------------------------------------------------

        peak_amplitude = float(
            np.max(
                np.abs(mono)
            )
        )

        # ----------------------------------------------------
        # Zero Crossing Rate
        # ----------------------------------------------------

        signs = np.signbit(mono)

        zero_crossings = np.count_nonzero(
            signs[1:] != signs[:-1]
        )

        zero_crossing_rate = float(
            zero_crossings
            / max(len(mono) - 1, 1)
        )

        # ----------------------------------------------------
        # Spectral Features
        # ----------------------------------------------------

        spectral = _spectral_features(
            mono,
            int(sample_rate),
        )

        # ----------------------------------------------------
        # Return feature dictionary
        # ----------------------------------------------------

        return {
            # -----------------------------------------------
            # Existing V1 features
            # -----------------------------------------------

            "duration": round(
                duration,
                3,
            ),

            "sample_rate": int(
                sample_rate
            ),

            "channels": int(
                channels
            ),

            "rms_energy": round(
                rms_energy,
                6,
            ),

            "peak_amplitude": round(
                peak_amplitude,
                6,
            ),

            "zero_crossing_rate": round(
                zero_crossing_rate,
                6,
            ),

            # -----------------------------------------------
            # V2.1 spectral features
            # -----------------------------------------------

            "spectral_centroid": round(
                spectral[
                    "spectral_centroid"
                ],
                3,
            ),

            "spectral_bandwidth": round(
                spectral[
                    "spectral_bandwidth"
                ],
                3,
            ),

            "spectral_rolloff": round(
                spectral[
                    "spectral_rolloff"
                ],
                3,
            ),
        }

    except Exception as e:

        print(
            f"[Audio Features] Could not analyze "
            f"{path.name}: {e}"
        )

        return None