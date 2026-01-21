#(©)Codeflix_Botz

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from bot import Bot
from config import LOGGER
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

    current = 0
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0

    async for msg in client.get_chat_history(chat.id):
        current += 1
        if msg.empty:
            deleted += 1
            continue
        elif not msg.media:
            no_media += 1
            continue

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
            file_name = msg.video.file_name or (msg.caption.split('\n')[0] if msg.caption else "Video")
            file_size = msg.video.file_size
            file_type = "video"
            file_id = msg.video.file_id
        elif msg.audio:
            file_name = msg.audio.file_name or (msg.caption.split('\n')[0] if msg.caption else "Audio")
            file_size = msg.audio.file_size
            file_type = "audio"
            file_id = msg.audio.file_id
        elif msg.photo:
            file_name = (msg.caption.split('\n')[0] if msg.caption else "Photo")
            file_size = msg.photo.file_size
            file_type = "photo"
            file_id = msg.photo.file_id
        elif msg.animation:
            file_name = msg.animation.file_name or (msg.caption.split('\n')[0] if msg.caption else "Animation")
            file_size = msg.animation.file_size
            file_type = "animation"
            file_id = msg.animation.file_id
        elif msg.voice:
            file_name = (msg.caption.split('\n')[0] if msg.caption else "Voice")
            file_size = msg.voice.file_size
            file_type = "voice"
            file_id = msg.voice.file_id
        elif msg.video_note:
            file_name = "Video Note"
            file_size = msg.video_note.file_size
            file_type = "video_note"
            file_id = msg.video_note.file_id
        else:
            unsupported += 1
            continue

        if file_id:
            if await db.file_data.find_one({'file_id': file_id}):
                duplicate += 1
                continue
            try:
                # Copy to DB channel
                copied_msg = await msg.copy(client.db_channel.id)
                # Index in MongoDB
                await db.add_file(file_name, file_size, file_type, file_id, copied_msg.id)
                total_files += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(client.db_channel.id)
                await db.add_file(file_name, file_size, file_type, file_id, copied_msg.id)
                total_files += 1
            except Exception as e:
                logger.error(f"Error indexing message {msg.id}: {e}")
                errors += 1

        if current % 100 == 0:
            try:
                await waiting_msg.edit_text(
                    text=f"Successfully saved <code>{total_files}</code> to database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - <code>{unsupported}</code>)"
                )
            except:
                pass

    await waiting_msg.edit_text(
        text=f"Successfully saved <code>{total_files}</code> to database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - <code>{unsupported}</code>)"
    )


