#(©)Codeflix_Botz

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from bot import Bot
from config import LOGGER
from helper_func import admin, encode, get_message_id
from database.database import db
import asyncio

logger = LOGGER(__name__)

@Bot.on_message(filters.chat(CHANNEL_ID) & filters.media)
async def auto_index(client: Bot, message: Message):
    # Determine file details
    file_name = "Unknown"
    file_size = 0
    file_type = None
    file_id = None

    if message.document:
        file_name = message.document.file_name
        file_size = message.document.file_size
        file_type = "document"
        file_id = message.document.file_id
    elif message.video:
        file_name = message.video.file_name or (message.caption.split('\n')[0] if message.caption else "Video")
        file_size = message.video.file_size
        file_type = "video"
        file_id = message.video.file_id
    elif message.audio:
        file_name = message.audio.file_name or (message.caption.split('\n')[0] if message.caption else "Audio")
        file_size = message.audio.file_size
        file_type = "audio"
        file_id = message.audio.file_id
    elif message.photo:
        file_name = (message.caption.split('\n')[0] if message.caption else "Photo")
        file_size = message.photo.file_size
        file_type = "photo"
        file_id = message.photo.file_id
    elif message.animation:
        file_name = message.animation.file_name or (message.caption.split('\n')[0] if message.caption else "Animation")
        file_size = message.animation.file_size
        file_type = "animation"
        file_id = message.animation.file_id
    elif message.voice:
        file_name = (message.caption.split('\n')[0] if message.caption else "Voice")
        file_size = message.voice.file_size
        file_type = "voice"
        file_id = message.voice.file_id
    elif message.video_note:
        file_name = "Video Note"
        file_size = message.video_note.file_size
        file_type = "video_note"
        file_id = message.video_note.file_id

    if file_id:
        try:
            await db.add_file(
                file_name=file_name,
                file_size=file_size,
                file_type=file_type,
                file_id=file_id,
                msg_id=message.id,
                caption=message.caption.html if message.caption else None
            )
            logger.info(f"Auto-indexed file: {file_name} (ID: {message.id})")
        except Exception as e:
            logger.error(f"Error in auto-indexing: {e}")


