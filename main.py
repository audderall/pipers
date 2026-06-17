import asyncio
import os
import secrets
from datetime import datetime

import discord
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from core.bump import bump

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
if not API_KEY:
    raise RuntimeError("API_KEY env var is not set." )

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(key: str = Security(api_key_header)):
    if not key or not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key

DISBOARD_APP_ID = "302050872383242240"

app = FastAPI(
    title="pipers api",
    docs_url=None,   
    redoc_url=None,
)

class BumpRequest(BaseModel):
    token: str
    channel_id: str

class BumpResponse(BaseModel):
    success: bool
    channel_id: str
    bumped_at: str
    message: str

@app.get("/")
def root(_: str = Security(require_api_key)):
    return {"status": "ok"}


@app.post("/api/v1/bump", response_model=BumpResponse)
async def bump_endpoint(body: BumpRequest, _: str = Security(require_api_key)):
    """
    Pipers.

    Requires header:  X-API-Key: <your api key>
    Body JSON:        { "token": "<discord user token>", "channel_id": "<channel id>" }
    """
    client = discord.Client()

    result: dict = {}

    @client.event
    async def on_ready():
        try:
            channel_id = await bump(client, body.channel_id, DISBOARD_APP_ID)
            result["channel_id"] = channel_id
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        finally:
            await client.close()

    try:
        await asyncio.wait_for(client.start(body.token), timeout=30)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Discord login timed out")
    except discord.LoginFailure:
        raise HTTPException(status_code=401, detail="Invalid Discord token")
    except Exception as e:
        if result.get("success") is not None:
            pass   
        else:
            raise HTTPException(status_code=500, detail=str(e))

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

    return BumpResponse(
        success=True,
        channel_id=result["channel_id"],
        bumped_at=datetime.now().replace(microsecond=0).isoformat(),
        message=f"Successfully bumped channel {result['channel_id']}",
    )
