import httpx
import asyncio
from database import AsyncSessionLocal
from sqlalchemy import select
from models.pit_config import PitConfig
from models.contact import Contact


async def get_token_by_location_id(location_id: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PitConfig).where(PitConfig.location_id == location_id)
        )
        row = result.scalar_one_or_none()

        if not row:
            raise ValueError("Location ID not found")

        return row.pit_token


async def get_conversation(conversation_id: str, location_id: str) -> dict:

    token = await get_token_by_location_id(location_id)

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28"
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://services.leadconnectorhq.com/conversations/{conversation_id}",
            headers=headers
        )

    return r.json()


async def get_contact(contact_id: str, location_id: str) -> dict:

    token = await get_token_by_location_id(location_id)

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28"
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://services.leadconnectorhq.com/contacts/{contact_id}",
            headers=headers
        )

    return r.json()


async def create_contact_db(location_id: str, contact_data: dict):
    async with AsyncSessionLocal() as session:

        if contact_data.get("phone"):
            contact = Contact(
                location_id=location_id,
                phone_number=contact_data["phone"],
                email=None
            )
        else:
            contact = Contact(
                location_id=location_id,
                phone_number=None,
                email=contact_data.get("email")
            )

        session.add(contact)
        await session.commit()


async def get_location_id_by_email(email: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Contact).where(Contact.email == email)
        )
        contact = result.scalar_one_or_none()

        if not contact:
            raise ValueError("Contact not found")

        return contact.location_id


async def get_location_id_by_phone_number(phone_number: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Contact).where(Contact.phone_number == phone_number)
        )
        contact = result.scalar_one_or_none()

        if not contact:
            raise ValueError("Contact not found")

        return contact.location_id


async def create_contact(sender):

    payload = {
        "firstName": sender,
    }

    if is_email(sender):
        payload["email"] = sender
        payload["locationId"] = await get_location_id_by_email(sender)
    else:
        payload["phone"] = sender
        payload["locationId"] = await get_location_id_by_phone_number(sender)

    token = await get_token_by_location_id(payload["locationId"])

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://services.leadconnectorhq.com/contacts/",
            headers=headers,
            json=payload
        )

    return {
        "status": r.status_code,
        "data": r.json(),
        "locationId": payload["locationId"]
    }


async def create_conversation(contact_id, location_id):

    token = await get_token_by_location_id(location_id)

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

    payload = {
        "contactId": contact_id,
        "locationId": location_id
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://services.leadconnectorhq.com/conversations/",
            headers=headers,
            json=payload
        )

    return {
        "status": r.status_code,
        "data": r.json()
    }


async def send_inbound_message(conversation_id, message, location_id):

    token = await get_token_by_location_id(location_id)

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

    payload = {
        "conversationId": conversation_id,
        "type": "SMS",
        "message": message
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://services.leadconnectorhq.com/conversations/messages/inbound",
            headers=headers,
            json=payload
        )

    return {
        "status": r.status_code,
        "data": r.json()
    }


def is_email(s):
    return "@" in s


async def send_message(sender: str, message: str):

    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{sender}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''

    process = await asyncio.create_subprocess_exec(
        "osascript",
        "-e",
        script
    )

    await process.communicate()
