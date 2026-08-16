from core.music.intention import (
    INTENTION_TARGETS,
    classify_intention,
    intention_score,
    explain_intention,
)


def main():

    # Example profile from one of your analyzed tracks
    profile = {
        "energy": 0.5027,
        "intensity": 0.43,
        "calm": 0.57,
        "focus": 0.9043,
    }

    print("========================================")
    print("INTENTION ANALYSIS")
    print("========================================")

    # --------------------------------------------------------
    # Best matching intention
    # --------------------------------------------------------

    result = classify_intention(profile)

    print("\nBest Intention:")
    print(result["intention"])

    print("\nScore:")
    print(result["score"])

    print("\nExplanation:")
    print(explain_intention(result["intention"]))

    # --------------------------------------------------------
    # All intention compatibility scores
    # --------------------------------------------------------

    print("\n========================================")
    print("ALL INTENTION SCORES")
    print("========================================")

    for intention in INTENTION_TARGETS:

        score = intention_score(
            profile,
            intention
        )

        print(
            f"{intention:15} -> {score}"
        )


if __name__ == "__main__":
    main()