from agent.graph import musica_graph


def main():

    result = musica_graph.invoke({
        "user_request": "I need deep focus music for coding"
    })

    print()
    print("=" * 60)
    print("MUSICA")
    print("=" * 60)

    print(
        f"Intention: {result['intention']}"
    )

    print(
        f"Response: {result['response']}"
    )

    print()
    print("QUEUE")
    print("-" * 60)

    for index, track in enumerate(
        result["queue"],
        start=1
    ):

        print(
            f"{index:02d}. "
            f"{track.title} — "
            f"{track.artist}"
        )


if __name__ == "__main__":
    main()