from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.graph import musica_graph
from core.music.intention import INTENTION_TARGETS


# ============================================================
# APP CONFIG
# ============================================================

app = FastAPI(
    title="Musica",
    description="LangGraph-powered Intelligent Music Orchestration System",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class MusicRequest(BaseModel):
    request: str
    limit: Optional[int] = 10


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Musica",
        "version": "1.0.0",
        "status": "running",
        "engine": "LangGraph",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "musica",
        "engine": "langgraph",
    }


# ============================================================
# INTENTIONS
# ============================================================

@app.get("/api/intentions")
def intentions():
    return {
        "intentions": list(INTENTION_TARGETS.keys())
    }


# ============================================================
# RECOMMEND MUSIC
# ============================================================

@app.post("/api/recommend")
def recommend_music(data: MusicRequest):

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    request = data.request.strip()

    if not request:
        raise HTTPException(
            status_code=400,
            detail="Request cannot be empty.",
        )

    limit = data.limit

    if limit is None:
        limit = 10

    if limit <= 0:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0.",
        )

    # --------------------------------------------------------
    # Execute LangGraph
    # --------------------------------------------------------

    try:

        result = musica_graph.invoke({
            "user_request": request
        })

    except Exception as error:

        print(
            f"[Musica API] LangGraph error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Musica workflow failed: {error}",
        )

    # --------------------------------------------------------
    # Extract result
    # --------------------------------------------------------

    intention = result.get(
        "intention",
        "GENERAL_WORK",
    )

    response = result.get(
        "response",
        "",
    )

    ranked_tracks = result.get(
        "ranked_tracks",
        [],
    )

    queue = result.get(
        "queue",
        [],
    )

    # --------------------------------------------------------
    # Build lookup table
    # --------------------------------------------------------

    ranked_lookup = {
        item["track"].id: item
        for item in ranked_tracks
        if "track" in item
    }

    # --------------------------------------------------------
    # Build API queue
    # --------------------------------------------------------

    tracks = []

    for index, track in enumerate(
        queue[:limit],
        start=1,
    ):

        ranked_item = ranked_lookup.get(
            track.id,
            {},
        )

        tracks.append({
            "position": index,

            "id": track.id,

            "title": track.title,

            "artist": track.artist,

            "album": track.album,

            "duration": track.duration,

            "source": track.source,

            "playback_uri": track.playback_uri,

            "score": ranked_item.get(
                "score"
            ),

            "profile": ranked_item.get(
                "profile"
            ),

            "audio_features": track.audio_features,
        })

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "project": "Musica",

        "engine": "LangGraph",

        "user_request": request,

        "intention": intention,

        "response": response,

        "count": len(tracks),

        "tracks": tracks,
    }


# ============================================================
# GET QUEUE
# ============================================================

@app.get("/api/queue")
def generate_queue(
    request: str,
    limit: Optional[int] = 10,
):

    request = request.strip()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not request:

        raise HTTPException(
            status_code=400,
            detail="Request cannot be empty.",
        )

    if limit is None:
        limit = 10

    if limit <= 0:

        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0.",
        )

    # --------------------------------------------------------
    # Execute LangGraph
    # --------------------------------------------------------

    try:

        result = musica_graph.invoke({
            "user_request": request,
        })

    except Exception as error:

        print(
            f"[Musica API] LangGraph error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Musica workflow failed: {error}",
        )

    # --------------------------------------------------------
    # Extract graph state
    # --------------------------------------------------------

    intention = result.get(
        "intention",
        "GENERAL_WORK",
    )

    response = result.get(
        "response",
        "",
    )

    ranked_tracks = result.get(
        "ranked_tracks",
        [],
    )

    queue = result.get(
        "queue",
        [],
    )

    # --------------------------------------------------------
    # Ranked lookup
    # --------------------------------------------------------

    ranked_lookup = {
        item["track"].id: item
        for item in ranked_tracks
        if "track" in item
    }

    # --------------------------------------------------------
    # Build queue
    # --------------------------------------------------------

    tracks = []

    for index, track in enumerate(
        queue[:limit],
        start=1,
    ):

        ranked_item = ranked_lookup.get(
            track.id,
            {},
        )

        tracks.append({

            "position": index,

            "id": track.id,

            "title": track.title,

            "artist": track.artist,

            "album": track.album,

            "duration": track.duration,

            "source": track.source,

            "playback_uri": track.playback_uri,

            "score": ranked_item.get(
                "score"
            ),

            "profile": ranked_item.get(
                "profile"
            ),

            "audio_features": track.audio_features,
        })

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "project": "Musica",

        "engine": "LangGraph",

        "user_request": request,

        "intention": intention,

        "response": response,

        "count": len(tracks),

        "tracks": tracks,
    }


# ============================================================
# LANGGRAPH DEMO ENDPOINT
# ============================================================

@app.post("/api/langgraph")
def langgraph_demo(data: MusicRequest):

    request = data.request.strip()

    if not request:

        raise HTTPException(
            status_code=400,
            detail="Request cannot be empty.",
        )

    try:

        result = musica_graph.invoke({
            "user_request": request,
        })

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    return {
        "engine": "LangGraph",

        "input": request,

        "graph_result": {
            "intention": result.get(
                "intention"
            ),

            "response": result.get(
                "response"
            ),

            "tracks_loaded": len(
                result.get(
                    "tracks",
                    []
                )
            ),

            "tracks_ranked": len(
                result.get(
                    "ranked_tracks",
                    []
                )
            ),

            "queue_size": len(
                result.get(
                    "queue",
                    []
                )
            ),
        },
    }