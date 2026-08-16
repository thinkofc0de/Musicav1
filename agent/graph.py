from langgraph.graph import StateGraph, START, END

from agent.state import MusicaState

from agent.nodes import (
    understand_intention,
    load_library,
    rank_music,
    build_music_queue,
    generate_response,
)


def create_musica_graph():

    graph = StateGraph(MusicaState)

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
        "understand_intention",
        understand_intention
    )

    graph.add_node(
        "load_library",
        load_library
    )

    graph.add_node(
        "rank_music",
        rank_music
    )

    graph.add_node(
        "build_queue",
        build_music_queue
    )

    graph.add_node(
        "generate_response",
        generate_response
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "understand_intention"
    )

    graph.add_edge(
        "understand_intention",
        "load_library"
    )

    graph.add_edge(
        "load_library",
        "rank_music"
    )

    graph.add_edge(
        "rank_music",
        "build_queue"
    )

    graph.add_edge(
        "build_queue",
        "generate_response"
    )

    graph.add_edge(
        "generate_response",
        END
    )

    return graph.compile()


musica_graph = create_musica_graph()