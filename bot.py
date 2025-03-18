import os
import re
from telethon import TelegramClient, events

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))  # Get from environment variables

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# List to store files as tuples [(episode_number, message)]
files_list = []

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
    if event.message.document:  # Ensure the message contains a document (file)
        file_caption = getattr(event.message, "message", None) or "Unknown"

        # Get the file name safely
        file_name = "Unknown"
        for attr in event.message.document.attributes:
            if hasattr(attr, "file_name"):  # Extract file name if available
                file_name = attr.file_name
                break  

        ordered_caption = f"{file_caption} | {file_name}"

        # Extract correct episode number
        episode_number = extract_episode_number(file_name)

        # Store the file message with its episode number
        files_list.append((episode_number, event.message))

        # Forward to destination channel with ordered caption
        await client.send_file(DESTINATION_CHAT, event.message.document, caption=ordered_caption)
        print(f"✅ Forwarded: {ordered_caption}")

@client.on(events.NewMessage(pattern="/getall"))
async def send_files(event):
    if not files_list:
        await event.reply("❌ No files stored.")
        return

    # ✅ Ensure correct sorting by episode number
    sorted_files = sorted(files_list, key=lambda x: x[0])

    print("📌 Sorted Order:", [ep[0] for ep in sorted_files])  # Debug print for order

    await event.reply("📤 Sending files in ascending order:")
    for episode_num, message in sorted_files:
        await client.forward_messages(event.chat_id, message)  # Forward stored messages

print("🤖 Bot is running...")
client.run_until_disconnected()
