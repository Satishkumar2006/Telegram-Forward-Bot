import os
import re
import asyncio
from collections import deque
from telethon import TelegramClient, events

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))  # Get from environment variables

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Queue to store files before sending
file_queue = deque()
files_dict = {}  # Dictionary to store {episode_number: message}

def extract_number(text):
    """ Extracts episode number from caption or filename. """
    match = re.search(r'\d+', text)  # Find the first number in the text
    return int(match.group()) if match else float('inf')  # Return number or inf if not found

@client.on(events.NewMessage(incoming=True))
async def handle_files(event):
    file_caption = getattr(event.message, "text", None)  # Use text as caption fallback
    file_name = None

    if event.message.document and hasattr(event.message.document, "attributes"):
        for attr in event.message.document.attributes:
            if hasattr(attr, "file_name"):  # Extract file name if available
                file_name = attr.file_name
                break

    # Use only one source for caption (avoid duplication)
    ordered_caption = file_caption if file_caption else file_name or "Unknown File"
    
    # Extract episode number
    episode_number = extract_number(ordered_caption)
    files_dict[episode_number] = event.message  # Store file in dictionary

    # Add file to queue
    file_queue.append((episode_number, event.message.document, ordered_caption))

    # Process the queue in order
    await process_queue()

async def process_queue():
    global file_queue

    # Sort queue before sending
    file_queue = deque(sorted(file_queue, key=lambda x: x[0]))  # Sort by episode number

    while file_queue:
        episode_num, document, caption = file_queue.popleft()  # Get next file
        await client.send_file(DESTINATION_CHAT, document, caption=caption)
        await asyncio.sleep(1)  # Prevent flooding Telegram API

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
