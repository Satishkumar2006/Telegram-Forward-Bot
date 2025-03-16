import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))  # Get from Render environment variables
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")  # Get from BotFather

source_chat = int(os.getenv("SOURCE_CHAT"))  # Source chat ID
destination_channel = int(os.getenv("DESTINATION_CHAT"))  # Destination chat ID

client = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(chats=source_chat))
async def forward_messages(event):
    if event.message.media:
        await client.send_file(destination_channel, event.message.media, caption=event.message.text)
    else:
        await client.send_message(destination_channel, event.message.text)

print("🤖 Bot is running on Render...")
client.run_until_disconnected()
