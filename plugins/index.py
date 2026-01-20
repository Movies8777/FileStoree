
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import Media, save_file
from config import OWNER_ID
from helper_func import admin

logger = logging.getLogger(__name__)

@Client.on_message(filters.command('index') & admin)
async def index_files(bot, message):
    if len(message.command) < 2:
        return await message.reply("<b>Usage: /index <channel_id></b>")

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply("<b>Invalid Channel ID.</b>")

    msg = await message.reply("<b>Indexing started...</b>")

    count = 0
    try:
        async for user_message in bot.get_chat_history(chat_id):
            for file_type in ("document", "video", "audio"):
                media = getattr(user_message, file_type, None)
                if media:
                    media.file_type = file_type
                    media.caption = user_message.caption
                    await save_file(media, message_id=user_message.id, chat_id=chat_id)
                    count += 1
                    break
            if count % 100 == 0:
                await msg.edit(f"<b>Indexed {count} files...</b>")
    except FloodWait as e:
        await asyncio.sleep(e.x)
    except Exception as e:
        logger.exception(e)
        return await msg.edit(f"<b>Error: {e}</b>")

    await msg.edit(f"<b>Successfully indexed {count} files!</b>")

@Client.on_message(filters.command('total') & admin)
async def total_files(bot, message):
    count = await Media.count_documents({})
    await message.reply(f"<b>Total indexed files: {count}</b>")
