from sources.local import LocalMusicSource
from core.queue import explain_queue


MUSIC_FOLDER = r"C:\Users\Chiru\Music\Music"


def main():

    source = LocalMusicSource(MUSIC_FOLDER)

    tracks = source.get_tracks()

    print(f"Loaded {len(tracks)} track(s).")

    print("\n========================================")
    print("DEEP FOCUS QUEUE")
    print("========================================")

    queue = explain_queue(
        tracks,
        "DEEP_FOCUS"
    )

    for item in queue:

        print(
            f"{item['position']:02d}. "
            f"{item['title']} "
            f"— {item['artist']}"
        )

        print(
            f"    Match: {item['score']}"
        )

        print(
            f"    Energy: {item['profile']['energy']} | "
            f"Intensity: {item['profile']['intensity']} | "
            f"Calm: {item['profile']['calm']} | "
            f"Focus: {item['profile']['focus']}"
        )

        print("----------------------------------------")


if __name__ == "__main__":
    main()