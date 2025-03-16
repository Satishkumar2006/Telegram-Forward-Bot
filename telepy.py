from telethon import TelegramClient, events

# API credentials from https://my.telegram.org/apps
api_id = "21116104"
api_hash = "2bc11795b938f35609c1e330628f43c2"

# Set source and destination chats
source_chat = "https://t.me/ForwardFile1_bot"
destination_channel = "https://t.me/AniHeaven123"

# Initialize the Telegram client
client = TelegramClient("bot_session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def forward_messages(event):
    if event.message.media:
        # Resend media without forward tag
        await client.send_file(destination_channel, event.message.media, caption=event.message.text)
    else:
        # Send text messages without forward tag
        await client.send_message(destination_channel, event.message.text)

print("Bot is running...")
client.start()
client.run_until_disconnected()
