import sqlite3
from conf import CHAT_DB_PATH
from helpers import create_contact, create_conversation, get_conversation, send_inbound_message


def create_tracker():
    conn = sqlite3.connect("tracker.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tracker (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_rowid INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute(
        "INSERT OR IGNORE INTO tracker (id, last_rowid) VALUES (1, 0)"
    )
    conn.commit()
    conn.close()


def get_last_rowid():
    conn = sqlite3.connect("tracker.db")
    row = conn.execute(
        "SELECT last_rowid FROM tracker WHERE id = 1"
    ).fetchone()
    conn.close()
    return row[0]


def update_last_rowid(rowid: int):
    conn = sqlite3.connect("tracker.db")
    conn.execute(
        "UPDATE tracker SET last_rowid = ? WHERE id = 1",
        (rowid,)
    )
    conn.commit()
    conn.close()


def fetch_new_messages(since_rowid: int):
    conn = sqlite3.connect(f"file:{CHAT_DB_PATH}?mode=ro", uri=True)

    rows = conn.execute("""
        SELECT m.rowid, m.text, h.id AS sender
        FROM message m
        JOIN handle h ON m.handle_id = h.rowid
        WHERE m.rowid > ?
          AND m.is_from_me = 0
          AND m.text IS NOT NULL
        ORDER BY m.rowid ASC
    """, (since_rowid,)).fetchall()

    conn.close()
    return rows


async def process_messages(rows):

    for rowid, text, sender in rows:
        sender_clean = sender.strip()

        response = await create_contact(sender)

        data = response["data"]

        contact_id = None

        if response["status"] in (200, 201):
            contact_id = data.get("contact", {}).get("id")

        elif response["status"] == 400:
            contact_id = data.get("meta", {}).get("contactId")

        if not contact_id:
            raise Exception(f"Failed to get contactId: {data}")

        location_id = response["locationId"]

        response = await create_conversation(contact_id, location_id)

        data = response["data"]

        conversation_id = ""

        if response["status"] == 400:
            conversation_id = data.get("conversationId")
        elif response["status"] in (200, 201):
            conversation_id = data.get("conversation", {}).get("id")

        response = await send_inbound_message(conversation_id, text, location_id)
