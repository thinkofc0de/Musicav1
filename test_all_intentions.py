from sources.local import LocalMusicSource
from core.queue import explain_queue


MUSIC_FOLDER = r"C:\Users\Chiru\Music\Music"

INTENTIONS = [
    "DEEP_FOCUS",
    "GENERAL_WORK",
    "ENERGY_BOOST",
    "RELAXATION",
    "WIND_DOWN",
]


def main():

    source = LocalMusicSource(MUSIC_FOLDER)

    tracks = source.get_tracks()

    print(f"Loaded {len(tracks)} track(s).")

    for intention in INTENTIONS:

        print("\n" + "=" * 60)
        print(f"{intention}")
        print("=" * 60)

        queue = explain_queue(
            tracks,
            intention
        )

        # Show only the top 10 for easy comparison
        for item in queue[:10]:

            print(
                f"{item['position']:02d}. "
                f"{item['title']} "
                f"— {item['artist']}"
            )

            print(
                f"    Match: {item['score']} | "
                f"Energy: {item['profile']['energy']} | "
                f"Intensity: {item['profile']['intensity']} | "
                f"Calm: {item['profile']['calm']} | "
                f"Focus: {item['profile']['focus']}"
            )


if __name__ == "__main__":
    main()