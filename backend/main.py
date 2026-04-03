# FASTAPI MODULES
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from models.pit_config import PitConfig
from database import AsyncSessionLocal

# PROJECT MODULES
from helpers import create_contact_db, get_conversation, get_contact, send_message
from imessage import (
    create_tracker,
    get_last_rowid,
    update_last_rowid,
    fetch_new_messages,
    process_messages
)

from database import engine

# PYTHON AND THIRD PARTY MODULES
import asyncio
from contextlib import asynccontextmanager
from pydantic import BaseModel


async def poll_messages():

    while True:
        try:
            last_row = get_last_rowid()
            rows = fetch_new_messages(last_row)

            if rows:
                await process_messages(rows)

                newest_rowid = rows[-1][0]
                update_last_rowid(newest_rowid)

        except Exception as e:
            print("❌ Polling error:", e)

        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tracker()

    task = asyncio.create_task(poll_messages())

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await engine.dispose()


# ---------- APP ----------

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- ROUTES ----------

class ExtensionRequest(BaseModel):
    message: str
    conversationId: str
    locationId: str

@app.post("/webhook")
async def webhook(data: ExtensionRequest):

    conversation = await get_conversation(data.conversationId, data.locationId)

    contact = await get_contact(conversation["contactId"], data.locationId)

    contact_data = contact.get("contact", {})

    sender = contact_data.get("phone") or contact_data.get("email")

    await create_contact_db(data.locationId, contact_data)

    if not sender:
        raise ValueError("No phone or email found in contact")

    await send_message(sender, data.message)

    return {"status": "ok"}


@app.get("/getRowByLocationId/{locationId}")
async def get_row_by_location_id(locationId: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PitConfig).where(PitConfig.location_id == locationId)
        )
        row = result.scalar_one_or_none()

        if not row:
            raise HTTPException(status_code=404, detail="Location not found")

        return {
            "locationId": row.location_id,
            "pitToken": row.pit_token
        }


class PitConfigRequest(BaseModel):
    locationId: str
    pitToken: str


@app.post("/savePitConfig")
async def save_pit_config(data: PitConfigRequest):
    async with AsyncSessionLocal() as session:
        new_config = PitConfig(
            location_id=data.locationId,
            pit_token=data.pitToken
        )
        session.add(new_config)
        await session.commit()
        return {"status": "saved"}
