from sources.local import LocalMusicSource


MUSIC_DIRECTORY = r"C:\Users\Chiru\Music\Music\sad"


def main():

    source = LocalMusicSource(
        MUSIC_DIRECTORY
    )

    tracks = source.scan()

    print()
    print(f"Found {len(tracks)} track(s).")
    print()

    for track in tracks:

        print(f"Title: {track.title}")
        print(f"Artist: {track.artist}")
        print(f"Source: {track.source}")
        print(f"Duration: {track.duration}")

        print("Audio Features:")

        for name, value in track.audio_features.items():

            print(f"  {name}: {value}")

        print(f"Path: {track.playback_uri}")

        print("-" * 60)


if __name__ == "__main__":
    main()