import os

from telethon import TelegramClient, events

API_ID = os.environ.get("API_ID", 0)
API_HASH = os.environ.get("API_HASH", "")
ALLOWED_CHATS = [int(c) for c in os.environ.get("ALLOWED_CHATS", "").split("|")]
client = TelegramClient("telegram", API_ID, API_HASH)


@client.on(events.NewMessage)
async def new_message(event):
    message = event.message
    if not message or message.out:
        return

    chat_id = event.chat_id
    if chat_id not in ALLOWED_CHATS:
        return

    await event.reply('{"ok": true}')


client.start()
client.run_until_disconnected()
