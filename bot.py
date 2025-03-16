from telethon.sync import TelegramClient

api_id = 21116104
api_hash = "2bc11795b938f35609c1e330628f43c2"
bot_token = "8114074332:AAHOtn13jsxE-h-75cT7xvAUAeFVoEof73o"

client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

async def get_chat_id():
    async for dialog in client.iter_dialogs():
        print(f"Name: {dialog.name}, ID: {dialog.id}")

with client:
    client.loop.run_until_complete(get_chat_id())
