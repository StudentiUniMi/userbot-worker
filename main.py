import json
import os
from typing import Optional

import telethon
from telethon import TelegramClient, events
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    InviteToChannelRequest,
    EditAdminRequest,
)
from telethon.tl.types import ChatAdminRights

API_ID = os.environ.get("API_ID", 0)
API_HASH = os.environ.get("API_HASH", "")
ALLOWED_CHATS = [int(c) for c in os.environ.get("ALLOWED_CHATS", "").split("|")]

client = TelegramClient("telegram", API_ID, API_HASH)


def decode_packet(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError:
        return None


async def create_group(packet: dict) -> dict:
    group = packet.get("group", {})

    title = group.get("title", None)
    description = group.get("description", None)
    bot = group.get("bot_username", None)

    assert title is not None
    assert description is not None
    assert bot is not None

    mtbot = await client.get_input_entity(bot)
    response = await client(CreateChannelRequest(
        title=title,
        about=description,
        broadcast=False,
        megagroup=True,
    ))
    if len(response.chats) < 1:
        return {"ok": False}

    mtgroup = response.chats[0]
    await client(InviteToChannelRequest(
        channel=mtgroup,
        users=[mtbot, ]
    ))
    await client(EditAdminRequest(
        channel=mtgroup,
        user_id=mtbot.user_id,
        admin_rights=ChatAdminRights(
            change_info=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            manage_call=True,
            other=True,
        ),
        rank="Bot",
    ))
    return {
        "ok": True,
        "group_id": int(f"-100{mtgroup.id}"),
    }


@client.on(events.NewMessage)
async def new_message(event):
    message = event.message
    if not message or message.out or not message.raw_text:
        return

    chat_id = event.chat_id
    if chat_id not in ALLOWED_CHATS:
        return

    packet = decode_packet(message.raw_text)
    if type(packet) != dict:
        return

    command = packet.get("command")
    res = {"ok": False, "error": "Unrecognized command"}
    if command == "create_group":
        try:
            res = await create_group(packet)
        except (telethon.errors.FloodError, telethon.errors.FloodWaitError):
            res = {"ok": False, "error": "FLOOD_WAIT"}
        except telethon.errors.RPCError as e:
            res = {"ok": False, "error": "RPC_ERROR", "message": e.message}
    await event.reply(json.dumps(res))


client.start()
client.run_until_disconnected()
