from typing import Dict, Any


# ============================================================
# INTENTION PROFILES
# ============================================================

INTENTION_PROFILES = {

    "DEEP_FOCUS": {
        "targets": {
            "energy": 0.45,
            "intensity": 0.35,
            "calm": 0.70,
            "focus": 0.90,
        },

        "weights": {
            "energy": 0.20,
            "intensity": 0.30,
            "calm": 0.20,
            "focus": 0.30,
        },
    },

    "GENERAL_WORK": {
        "targets": {
            "energy": 0.55,
            "intensity": 0.45,
            "calm": 0.60,
            "focus": 0.75,
        },

        "weights": {
            "energy": 0.25,
            "intensity": 0.25,
            "calm": 0.20,
            "focus": 0.30,
        },
    },

    "ENERGY_BOOST": {
        "targets": {
            "energy": 0.80,
            "intensity": 0.75,
            "calm": 0.30,
            "focus": 0.45,
        },

        "weights": {
            "energy": 0.35,
            "intensity": 0.40,
            "calm": 0.10,
            "focus": 0.15,
        },
    },

    "RELAXATION": {
        "targets": {
            "energy": 0.35,
            "intensity": 0.25,
            "calm": 0.85,
            "focus": 0.65,
        },

        "weights": {
            "energy": 0.20,
            "intensity": 0.30,
            "calm": 0.35,
            "focus": 0.15,
        },
    },

    "WIND_DOWN": {
        "targets": {
            "energy": 0.30,
            "intensity": 0.20,
            "calm": 0.90,
            "focus": 0.55,
        },

        "weights": {
            "energy": 0.25,
            "intensity": 0.30,
            "calm": 0.35,
            "focus": 0.10,
        },
    },
}


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

# Keep this name available in case other parts of Musica
# currently import INTENTION_TARGETS.

INTENTION_TARGETS = {
    intention: profile["targets"]
    for intention, profile in INTENTION_PROFILES.items()
}


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def _distance(
    profile: Dict[str, float],
    target: Dict[str, float],
    weights: Dict[str, float] | None = None,
) -> float:
    """
    Calculate weighted distance between a music profile
    and an intention target.

    Lower distance = better match.

    If weights are provided, each musical dimension can
    contribute differently to the final distance.
    """

    dimensions = [
        "energy",
        "intensity",
        "calm",
        "focus",
    ]

    total = 0.0

    for dimension in dimensions:

        actual = float(
            profile.get(
                dimension,
                0.0,
            )
        )

        desired = float(
            target.get(
                dimension,
                0.0,
            )
        )

        weight = (
            float(weights.get(dimension, 0.0))
            if weights is not None
            else 1.0
        )

        total += (
            abs(actual - desired)
            * weight
        )

    return total


# ============================================================
# BEST INTENTION
# ============================================================

def classify_intention(
    profile: Dict[str, float],
) -> Dict[str, Any]:
    """
    Determine which listening intention best matches
    a music profile.

    Returns:

        {
            "intention": "...",
            "score": 0.0,
            "alternatives": [...]
        }

    Lower score = better match.
    """

    results = []

    for intention, configuration in INTENTION_PROFILES.items():

        target = configuration["targets"]
        weights = configuration["weights"]

        distance = _distance(
            profile,
            target,
            weights,
        )

        results.append({
            "intention": intention,
            "score": round(
                distance,
                4,
            ),
        })

    results.sort(
        key=lambda item: item["score"]
    )

    best = results[0]

    return {
        "intention": best["intention"],
        "score": best["score"],
        "alternatives": results[1:],
    }


# ============================================================
# INTENTION COMPATIBILITY
# ============================================================

def intention_score(
    profile: Dict[str, float],
    intention: str,
) -> float:
    """
    Return a normalized compatibility score.

    1.0 = excellent match
    0.0 = poor match

    Each intention has its own dimension weights.
    """

    intention = intention.upper()

    if intention not in INTENTION_PROFILES:

        raise ValueError(
            f"Unknown intention: {intention}. "
            f"Available intentions: "
            f"{list(INTENTION_PROFILES.keys())}"
        )

    configuration = INTENTION_PROFILES[
        intention
    ]

    target = configuration["targets"]
    weights = configuration["weights"]

    distance = _distance(
        profile,
        target,
        weights,
    )

    # --------------------------------------------------------
    # Because the weights sum to 1.0, the maximum possible
    # weighted distance is also 1.0.
    # --------------------------------------------------------

    score = 1.0 - distance

    return round(
        max(
            0.0,
            min(
                1.0,
                score,
            ),
        ),
        4,
    )


# ============================================================
# HUMAN-READABLE INTENTION
# ============================================================

def explain_intention(
    intention: str,
) -> str:
    """
    Convert an internal intention name into a
    human-readable label.
    """

    descriptions = {

        "DEEP_FOCUS":
            "Deep Focus — low distraction and sustained concentration",

        "GENERAL_WORK":
            "General Work — balanced background music for productivity",

        "ENERGY_BOOST":
            "Energy Boost — energetic music for increasing momentum",

        "RELAXATION":
            "Relaxation — calm music for reducing mental intensity",

        "WIND_DOWN":
            "Wind Down — very calm music for slowing down",
    }

    intention = intention.upper()

    return descriptions.get(
        intention,
        "Unknown intention",
    )