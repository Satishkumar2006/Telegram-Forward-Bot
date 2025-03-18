import os
import re
from telethon import TelegramClient, events

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to store files {episode_number: message}
files_dict = {}

def extract_number(text):
    """ Extracts episode number from caption or filename. """
    match = re.search(r'\d+', text)  # Find the first number in the text
    return int(match.group()) if match else float('inf')  # Return number or inf if not found

@client.on(events.NewMessage(incoming=True))
@client.on(events.NewMessage(incoming=True))
async def handle_files(event):
    if event.file:  # Check if it's a file
        file_caption = getattr(event.message, "message", None) or event.file.name or "Unknown"
        episode_num = extract_number(file_caption)

        if episode_num != float('inf'):  # Only store if a number is found
            files_dict[episode_num] = event.message
            await event.reply(f"📂 Saved: {file_caption} (Episode {episode_num})")
        else:
            await event.reply("❌ Could not detect an episode number.")

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
