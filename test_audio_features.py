from core.audio_features import extract_audio_features


AUDIO_FILE = r"C:\Users\Chiru\Music\Music\Sajdaa (PenduJatt.Com.Se).mp3"


def main():
    print("Analyzing:")
    print(AUDIO_FILE)
    print()

    features = extract_audio_features(AUDIO_FILE)

    if features is None:
        print("Could not extract audio features.")
        return

    print("Audio Features")
    print("=" * 40)

    for name, value in features.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()