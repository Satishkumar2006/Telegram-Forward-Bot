import os
import re
import asyncio
from collections import OrderedDict
from telethon import TelegramClient, events

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))  # Destination chat ID

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to store files {episode_number: (document, caption)}
files_dict = OrderedDict()
processing = False  # Flag to prevent multiple processes running at the same time

def extract_number(text):
    """ Extracts episode number from caption or filename. """
    match = re.search(r'(\d+)', text)  # Find episode number in text
    return int(match.group()) if match else float('inf')  # Return episode number or infinity

@client.on(events.NewMessage(incoming=True))
async def handle_files(event):
    global processing
    file_caption = getattr(event.message, "text", None)  # Use text as caption fallback
    file_name = None

    if event.message.document and hasattr(event.message.document, "attributes"):
        for attr in event.message.document.attributes:
            if hasattr(attr, "file_name"):  # Extract file name if available
                file_name = attr.file_name
                break

    # Select best caption (avoid duplicates)
    ordered_caption = file_caption if file_caption else file_name or "Unknown File"

    # Extract episode number
    episode_number = extract_number(ordered_caption)

    # Store in dictionary with sorting
    files_dict[episode_number] = (event.message.document, ordered_caption)

    # Process queue only if not already running
    if not processing:
        processing = True
        await process_queue()

async def process_queue():
    global processing

    while files_dict:
        # Sort files in order
        sorted_keys = sorted(files_dict.keys())

        # Process each file sequentially
        for episode_number in sorted_keys:
            document, caption = files_dict.pop(episode_number)  # Remove from queue
            await client.send_file(DESTINATION_CHAT, document, caption=caption)
            await asyncio.sleep(1)  # Prevent Telegram API flood

    processing = False  # Reset flag

@client.on(events.NewMessage(pattern="/getall"))
async def send_files(event):
    if not files_dict:
        await event.reply("❌ No files stored.")
        return

    sorted_files = sorted(files_dict.keys())  # Sort by episode number
    await event.reply("📤 Sending files in order:")

    for episode_num in sorted_files:
        document, caption = files_dict[episode_num]
        await client.send_file(event.chat_id, document, caption=caption)

print("🤖 Bot is running...")
client.run_until_disconnected()
