import os
import asyncio
from telethon import TelegramClient, events

# Environment Variables (set these in Railway or your .env file)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHAT = int(os.getenv("SOURCE_CHAT"))  # Source chat ID
DESTINATION_CHAT = int(os.getenv("DESTINATION_CHAT"))  # Destination chat ID

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to store received files
files_dict = {}

# Extract episode number from caption/filename
def extract_number(text):
    import re
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else float('inf')

# Event handler for new files
@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handle_files(event):
    if event.file:  # Ensure it's a file
        file_caption = getattr(event.message, "message", None) or event.file.name or "Unknown"
        episode_num = extract_number(file_caption)

        if episode_num != float('inf'):  # Only store if a number is found
            files_dict[episode_num] = event.message
            await event.reply(f"📂 Saved: {file_caption} (Episode {episode_num})")
        else:
            await event.reply("❌ Could not detect an episode number.")

# Command to forward sorted files
@client.on(events.NewMessage(pattern="/forward"))
async def forward_sorted_files(event):
    if not files_dict:
        await event.reply("⚠️ No files have been received yet.")
        return
    
    sorted_files = sorted(files_dict.items())
    for _, message in sorted_files:
        await client.send_message(DESTINATION_CHAT, file=message.media, caption=message.text or "No Caption")

    await event.reply("✅ Files forwarded in order!")
    files_dict.clear()  # Clear dictionary after forwarding

# Start the bot
print("🤖 Bot is running...")
client.run_until_disconnected()
