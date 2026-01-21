#(©)Codeflix_Botz

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from bot import Bot
from config import CHANNEL_ID, LOGGER
from helper_func import admin
from database.database import db
from helper_func import encode
import asyncio

logger = LOGGER(__name__)

@Bot.on_message(filters.command("index") & admin & filters.private)
async def index_command(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> /index {channel_id_or_username}")

    source_chat = message.command[1]

    try:
        chat = await client.get_chat(source_chat)
    except Exception as e:
        return await message.reply_text(f"<b>Error:</b> {e}")

    waiting_msg = await message.reply_text("<b>Indexing started... Please wait.</b>")

    count = 0
    total = 0

    async for msg in client.get_chat_history(chat.id):
        total += 1
        if msg.media:
            # Determine file details
            file_name = "Unknown"
            file_size = 0
            file_type = None
            file_id = None

            if msg.document:
                file_name = msg.document.file_name
                file_size = msg.document.file_size
                file_type = "document"
                file_id = msg.document.file_id
            elif msg.video:
                file_name = msg.video.file_name or "Video"
                file_size = msg.video.file_size
                file_type = "video"
                file_id = msg.video.file_id
            elif msg.audio:
                file_name = msg.audio.file_name
                file_size = msg.audio.file_size
                file_type = "audio"
                file_id = msg.audio.file_id

            if file_id:
                try:
                    # Copy to DB channel
                    copied_msg = await msg.copy(client.db_channel.id)
                    # Index in MongoDB
                    await db.add_file(file_name, file_size, file_type, file_id, copied_msg.id)
                    count += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    copied_msg = await msg.copy(client.db_channel.id)
                    await db.add_file(file_name, file_size, file_type, file_id, copied_msg.id)
                    count += 1
                except Exception as e:
                    logger.error(f"Error indexing message {msg.id}: {e}")

        if total % 100 == 0:
            try:
                await waiting_msg.edit_text(f"<b>Indexing in progress...</b>\n\n<b>Processed:</b> {total}\n<b>Indexed:</b> {count}")
            except:
                pass

    await waiting_msg.edit_text(f"<b>Indexing Completed!</b>\n\n<b>Total processed:</b> {total}\n<b>Files indexed:</b> {count}")


@Bot.on_message(filters.command("stats") & admin & filters.private)
async def stats_command(client: Bot, message: Message):
    files = await db.total_files()
    users = len(await db.full_userbase())

    text = f"""<b>📊 Bot Statistics</b>

<b>Total Users:</b> <code>{users}</code>
<b>Total Files Indexed:</b> <code>{files}</code>
"""
    await message.reply_text(text)


@Bot.on_message(filters.command("search") & admin & filters.private)
async def search_command(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> /search {file_name}")

    query = " ".join(message.command[1:])
    results = await db.find_file(query)

    if not results:
        return await message.reply_text("<b>No files found matching your search.</b>")

    text = f"<b>🔍 Search Results for:</b> <code>{query}</code>\n\n"
    for file in results[:10]: # Limit to 10 for display
        base64_string = await encode(f"get-{file['msg_id'] * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"

        text += f"<b>📄 Name:</b> <code>{file['file_name']}</code>\n"
        text += f"<b>📏 Size:</b> <code>{file['file_size']} bytes</code>\n"
        text += f"<b>🔗 Link:</b> {link}\n\n"

    if len(results) > 10:
        text += f"<i>...and {len(results) - 10} more results.</i>"

    await message.reply_text(text, disable_web_page_preview=True)
