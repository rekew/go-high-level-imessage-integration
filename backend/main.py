# FASTAPI MODULES
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# PROJECT MODULES
from helpers import get_conversation, get_contact, send_message
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


@app.post("/webhook")
async def webhook(data: ExtensionRequest):
    conversation = await get_conversation(data.conversationId)

    contact = await get_contact(conversation["contactId"])

    contact_data = contact.get("contact", {})

    sender = contact_data.get("phone") or contact_data.get("email")

    if not sender:
        raise ValueError("No phone or email found in contact")

    await send_message(sender, data.message)

    return {"status": "ok"}

@app.get("/getRowByLocationId/{locationId}")
async def get_row_by_location_id(locationId: str):
    return {"locationId": locationId}