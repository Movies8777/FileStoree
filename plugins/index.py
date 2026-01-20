
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import ADMINS, OWNER_ID, CHANNEL_ID
from database.database import db
from helper_func import admin

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("index") & admin)
async def index_command(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a channel ID or username to index.")

    channel = message.command[1]
    try:
        chat = await client.get_chat(channel)
    except Exception as e:
        return await message.reply(f"Error: {e}")

    msg = await message.reply("Indexing started...")
    count = 0

    async for user_message in client.get_chat_history(chat.id):
        if user_message.media:
            try:
                await user_message.copy(CHANNEL_ID)
                count += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await user_message.copy(CHANNEL_ID)
                count += 1
            except Exception:
                pass

        if count % 100 == 0:
            await msg.edit(f"Indexed {count} files...")

    await msg.edit(f"Indexing complete! Total {count} files indexed and copied to DB channel.")
    await db.add_indexed_channel(chat.id)

@Client.on_message((filters.group | filters.channel) & filters.incoming & filters.media)
async def auto_index(client, message):
    if await db.is_channel_indexed(message.chat.id):
        try:
            await message.copy(CHANNEL_ID)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await message.copy(CHANNEL_ID)
        except Exception as e:
            logger.error(f"Auto-index error: {e}")
