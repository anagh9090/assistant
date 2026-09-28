import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

# Your 5 OpenRouter Keys
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
]

# Primary Dolphin-Qwen Model on OpenRouter
TARGET_MODEL = "cognitivecomputations/dolphin-2.9.2-qwen2-7b"

@app.get("/")
async def root():
    return {"status": "online", "model": TARGET_MODEL}
    
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    
    # Force the model to Dolphin Qwen
    body["model"] = TARGET_MODEL

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Loop over keys until one succeeds
        for idx, key in enumerate(API_KEYS):
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://android-dolphin-assistant.local",
                "X-Title": "Android Dolphin Voice Assistant",
            }
            
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=body,
                )

                # If rate-limited (429) or quota exceeded, try the next key
                if response.status_code in (429, 402):
                    continue

                # Stream response back if streaming is enabled
                if body.get("stream", False):
                    return StreamingResponse(
                        response.aiter_bytes(),
                        status_code=response.status_code,
                        media_type="text/event-stream"
                    )

                return response.json()

            except Exception:
                continue

    raise HTTPException(status_code=429, detail="All 5 OpenRouter API keys exhausted.")
