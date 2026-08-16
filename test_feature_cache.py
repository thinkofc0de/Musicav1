from core.audio_features import extract_audio_features
from core.feature_cache import FeatureCache


AUDIO_FILE = r"C:\Users\Chiru\Music\Music\Sajdaa (PenduJatt.Com.Se).mp3"


def main():

    cache = FeatureCache()

    print("Checking cache...")
    
    features = cache.get(AUDIO_FILE)

    if features is not None:

        print("Cache HIT")
        print("Using previously calculated features.")

    else:

        print("Cache MISS")
        print("Analyzing audio...")

        features = extract_audio_features(AUDIO_FILE)

        if features is None:
            print("Audio analysis failed.")
            return

        cache.set(
            AUDIO_FILE,
            features,
        )

        print("Features saved to cache.")

    print()
    print("Features")
    print("=" * 40)

    for name, value in features.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()