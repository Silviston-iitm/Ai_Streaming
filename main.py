from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from llm_service import stream_llm_response
import json
import time

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class StreamRequest(BaseModel):
    prompt: str
    stream: bool = True


def sse_format(data: dict):
    """Format data as SSE event."""
    return f"data: {json.dumps(data)}\n\n"


@app.post("/stream")
async def stream_endpoint(req: StreamRequest):
    if not req.stream:
        return JSONResponse({"error": "Streaming must be true"})

    async def event_generator():
        start_time = time.time()
        chunk_count = 0

        try:
            for token in stream_llm_response(req.prompt):
                chunk_count += 1

                yield sse_format({
                    "choices": [
                        {"delta": {"content": token}}
                    ]
                })

                # Ensure progressive delivery
                if chunk_count >= 5:
                    pass

            # End of stream
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield sse_format({"error": str(e)})
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
