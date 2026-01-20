
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import OWNER_ID, CHANNEL_ID
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
                copied_msg = await user_message.copy(CHANNEL_ID)

                # Index in DB
                file = getattr(copied_msg, copied_msg.media.value)
                await db.add_file(
                    file_id=file.file_id,
                    file_name=getattr(file, "file_name", "Untitled"),
                    file_size=file.file_size,
                    file_type=copied_msg.media.value,
                    caption=copied_msg.caption,
                    message_id=copied_msg.id
                )

                count += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await user_message.copy(CHANNEL_ID)
                file = getattr(copied_msg, copied_msg.media.value)
                await db.add_file(
                    file_id=file.file_id,
                    file_name=getattr(file, "file_name", "Untitled"),
                    file_size=file.file_size,
                    file_type=copied_msg.media.value,
                    caption=copied_msg.caption,
                    message_id=copied_msg.id
                )
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
            copied_msg = await message.copy(CHANNEL_ID)

            # Index in DB
            file = getattr(copied_msg, copied_msg.media.value)
            await db.add_file(
                file_id=file.file_id,
                file_name=getattr(file, "file_name", "Untitled"),
                file_size=file.file_size,
                file_type=copied_msg.media.value,
                caption=copied_msg.caption,
                message_id=copied_msg.id
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            copied_msg = await message.copy(CHANNEL_ID)
            file = getattr(copied_msg, copied_msg.media.value)
            await db.add_file(
                file_id=file.file_id,
                file_name=getattr(file, "file_name", "Untitled"),
                file_size=file.file_size,
                file_type=copied_msg.media.value,
                caption=copied_msg.caption,
                message_id=copied_msg.id
            )
        except Exception as e:
            logger.error(f"Auto-index error: {e}")
