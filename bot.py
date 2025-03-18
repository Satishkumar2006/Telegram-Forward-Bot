import os
import re
import asyncio
from telethon import TelegramClient, events

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Queue to store files before sending them
file_queue = asyncio.Queue()

def extract_episode_number(text):
    """
    Extracts episode number from filenames like:
    'Kingdom - S01E12 - The Ultimate Sword-Blow [MCR] [75CA4A20].mkv'
    Only extracts '12' from 'S01E12'.
    """
    match = re.search(r'S\d+E(\d+)', text)  # Find 'S01E12' and extract '12'
    return int(match.group(1)) if match else float('inf')  # Default to a high number if not found

@client.on(events.NewMessage(incoming=True))
async def handle_files(event):
    if event.message.document:
        file_caption = getattr(event.message, "message", None) or "Unknown"

        # Get file name safely
        file_name = "Unknown"
        for attr in event.message.document.attributes:
            if hasattr(attr, "file_name"):
                file_name = attr.file_name
                break  

        ordered_caption = f"{file_caption} | {file_name}"
        episode_number = extract_episode_number(file_name)

        # Put file into queue
        await file_queue.put((episode_number, event.message, ordered_caption))
        print(f"📥 Queued: {ordered_caption}")

async def process_queue():
    """ Continuously processes files from the queue in sorted order. """
    while True:
        if not file_queue.empty():
            # Extract all queued files
            queued_files = []
            while not file_queue.empty():
                queued_files.append(await file_queue.get())

            # Sort files by episode number
            sorted_files = sorted(queued_files, key=lambda x: x[0])
            print("📌 Sorted Order:", [ep[0] for ep in sorted_files])

            for episode_num, message, caption in sorted_files:
                await client.send_file(DESTINATION_CHAT, message.document, caption=caption)
                print(f"✅ Sent: {caption}")
                await asyncio.sleep(3)  # ✅ Delay between sending files

        await asyncio.sleep(1)  # ✅ Prevents high CPU usage

# Start queue processing in the background
async def main():
    await client.start()
    client.loop.create_task(process_queue())  # Start queue worker
    print("🤖 Bot is running...")
    await client.run_until_disconnected()

asyncio.run(main())
