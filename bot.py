import os
import asyncio
from collections import defaultdict
from telethon import TelegramClient, events

# 🔹 Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHAT = int(os.getenv("SOURCE_CHAT"))
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))

# 🔹 Create Telegram bot client
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Dictionary to store files before forwarding
file_storage = defaultdict(list)

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handle_files(event):
    """Handles incoming files, sorts them, and forwards them in order."""

    # 🔹 Extract file name or caption
    file_caption = event.message.text or (event.message.document and event.message.document.attributes[0].file_name)
    if not file_caption:
        return  # Ignore messages without captions or filenames

    # 🔹 Store file with extracted name
    file_storage[SOURCE_CHAT].append((file_caption, event.message))

    # 🔹 Sort files in ascending order based on filename
    file_storage[SOURCE_CHAT].sort(key=lambda x: x[0])

    # 🔹 Forward files in order
    for _, msg in file_storage[SOURCE_CHAT]:
        await client.send_message(DESTINATION_CHAT, file=msg.document, caption=msg.text)
    
    # 🔹 Clear the storage after forwarding
    file_storage[SOURCE_CHAT].clear()

print("🤖 Bot is running...")
client.run_until_disconnected()
