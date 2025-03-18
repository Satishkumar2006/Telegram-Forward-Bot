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
    """ Extracts episode number from filenames like 'S01E12' and returns 12 """
    match = re.search(r'S\d+E(\d+)', text)
    return int(match.group(1)) if match else float('inf')

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

        # ✅ Fix: Only use the file name as the caption
        ordered_caption = f"{file_name}"
        episode_number = extract_episode_number(file_name)

        # Put file into queue
        await file_queue.put((episode_number, event.message, ordered_caption))
        print(f"📥 Queued: {ordered_caption}")

async def process_queue():
    """ Continuously processes files from the queue in sorted order. """
    while True:
        if not file_queue.empty():
            queued_files = []
            while not file_queue.empty():
                queued_files.append(await file_queue.get())

            # Sort files by episode number
            sorted_files = sorted(queued_files, key=lambda x: x[0])
            print("📌 Sorted Order:", [ep[0] for ep in sorted_files])

            for episode_num, message, caption in sorted_files:
                await client.send_file(DESTINATION_CHAT, message.document, caption=caption)
                print(f"✅ Sent: {caption}")
                await asyncio.sleep(1)  # ✅ Delay between sending files

        await asyncio.sleep(1)  # ✅ Prevents high CPU usage

async def main():
    client.loop.create_task(process_queue())  # ✅ Start queue processor
    print("🤖 Bot is running...")
    await client.run_until_disconnected()

# ✅ Corrected way to start the event loop
client.loop.run_until_complete(main())
