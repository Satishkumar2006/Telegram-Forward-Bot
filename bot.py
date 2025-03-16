import os
import asyncio
from telethon import TelegramClient, events

# Fetch environment variables from Render
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHAT = int(os.getenv("SOURCE_CHAT"))  # Source chat ID
DEST_CHAT = int(os.getenv("DEST_CHAT"))  # Destination channel ID

# Initialize the Telegram bot client
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def forward_messages(event):
    try:
        # Forward message to the destination channel without tag
        await client.send_message(DEST_CHAT, event.message.text)
        print(f"Forwarded: {event.message.text}")
    except Exception as e:
        print(f"Error: {e}")

print("🤖 Bot is running on Render...")
client.run_until_disconnected()
