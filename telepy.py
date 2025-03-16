import os  # Import os to read environment variables
from telethon import TelegramClient, events

# Read API credentials from Render's environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Source and destination chats from environment variables
source_chat = os.getenv("SOURCE_CHAT")
destination_channel = os.getenv("DESTINATION_CHAT")

# Initialize the Telegram client
client = TelegramClient("bot_session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def forward_messages(event):
    """ Listens for new messages in the source chat and sends them to the destination channel without forward tags. """
    if event.message.media:
        await client.send_file(destination_channel, event.message.media, caption=event.message.text)
    else:
        await client.send_message(destination_channel, event.message.text)

print("🤖 Bot is running on Render...")
client.start()
client.run_until_disconnected()
