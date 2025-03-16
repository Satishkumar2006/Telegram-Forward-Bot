import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

source_chat = os.getenv("SOURCE_CHAT")
destination_channel = os.getenv("DESTINATION_CHAT")

client = TelegramClient("bot_session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def forward_messages(event):
    if event.message.media:
        await client.send_file(destination_channel, event.message.media, caption=event.message.text)
    else:
        await client.send_message(destination_channel, event.message.text)

print("🤖 Bot is running on Render...")
client.start()
client.run_until_disconnected()
