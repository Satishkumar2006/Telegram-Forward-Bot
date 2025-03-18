import os
import re
from telethon import TelegramClient, events

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))  # Get from environment variables

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to store files {episode_number: message}
files_dict = {}

def extract_number(text):
    """ Extracts episode number from caption or filename. """
    match = re.search(r'\d+', text)  # Find the first number in the text
    return int(match.group()) if match else float('inf')  # Return number or inf if not found

@client.on(events.NewMessage(incoming=True))
async def handle_files(event):
    file_caption = event.message.caption  # Get caption if it exists
    file_name = None

    if event.message.document and hasattr(event.message.document, "attributes"):
        for attr in event.message.document.attributes:
            if hasattr(attr, "file_name"):  # Check if attribute has file_name
                file_name = attr.file_name
                break

    # Choose only one source for caption
    ordered_caption = file_caption if file_caption else file_name

    if not ordered_caption:
        ordered_caption = "Unknown File"

    # Send file with corrected caption
    await client.send_file(DESTINATION_CHAT, event.message.document, caption=ordered_caption)





@client.on(events.NewMessage(pattern="/getall"))
async def send_files(event):
    if not files_dict:
        await event.reply("❌ No files stored.")
        return

    sorted_files = sorted(files_dict.keys())  # Sort by episode number

    await event.reply("📤 Sending files in order:")
    for episode_num in sorted_files:
        await client.forward_messages(event.chat_id, files_dict[episode_num])

print("🤖 Bot is running...")
client.run_until_disconnected()
