import httpx
import asyncio
from conf import TOKEN, LOCATION_ID


async def get_conversation(conversation_id: str) -> dict:

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Version": "2021-07-28"
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://services.leadconnectorhq.com/conversations/{conversation_id}",
            headers=headers
        )

    return r.json()


async def get_contact(contact_id: str) -> dict:

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Version": "2021-07-28"
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://services.leadconnectorhq.com/contacts/{contact_id}",
            headers=headers
        )

    return r.json()


async def create_contact(sender):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

    payload = {
        "firstName": sender,
        "locationId": LOCATION_ID
    }

    if is_email(sender):
        payload["email"] = sender
    else:
        payload["phone"] = sender

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://services.leadconnectorhq.com/contacts/",
            headers=headers,
            json=payload
        )

    return {
        "status": r.status_code,
        "data": r.json()
    }


async def create_conversation(contact_id):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

    payload = {
        "contactId": contact_id,
        "locationId": LOCATION_ID
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


async def send_inbound_message(conversation_id, message):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
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
