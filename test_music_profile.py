from sources.local import LocalMusicSource
from core.music_profile import build_music_profile


MUSIC_DIRECTORY = r"C:\Users\Chiru\Music\Music\sad"


def main():

    source = LocalMusicSource(
        MUSIC_DIRECTORY
    )

    tracks = source.scan(limit=9)

    print()
    print(f"Found {len(tracks)} track(s).")
    print()

    for track in tracks:

        profile = build_music_profile(track)

        print(f"Title: {track.title}")
        print(f"Artist: {track.artist}")

        print()
        print("Music Profile:")

        print(f"  Energy:    {profile.energy}")
        print(f"  Intensity: {profile.intensity}")
        print(f"  Calm:      {profile.calm}")
        print(f"  Focus:     {profile.focus}")

        print()
        print("-" * 60)


if __name__ == "__main__":
    main()