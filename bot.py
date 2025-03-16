from telethon.sync import TelegramClient

api_id = YOUR_API_ID
api_hash = "YOUR_API_HASH"
bot_token = "YOUR_BOT_TOKEN"

client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

async def get_chat_id():
    async for dialog in client.iter_dialogs():
        print(f"Name: {dialog.name}, ID: {dialog.id}")

with client:
    client.loop.run_until_complete(get_chat_id())
