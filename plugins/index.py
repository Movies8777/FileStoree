
import asyncio
import logging
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, BotMethodInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID, CHANNEL_ID
from database.database import db
from helper_func import admin

logger = logging.getLogger(__name__)

lock = asyncio.Lock()

class Temp:
    CANCEL = False

temp = Temp()

@Client.on_callback_query(filters.regex(r'^index'))
async def index_callback(client: Client, query: CallbackQuery):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing...", show_alert=True)

    data = query.data.split("#")
    if len(data) < 3:
        return await query.answer("Invalid Data")

    action = data[1]
    chat_id = data[2]

    if action == 'reject':
        await query.message.delete()
        return await query.answer("Indexing Rejected")

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)

    try:
        chat_id = int(chat_id)
    except:
        pass

    await query.answer('Starting Indexing...⏳', show_alert=True)
    await query.message.edit(
        "<b><u>ɪɴᴅᴇxɪɴɢ sᴛᴀᴛᴜs</u></b>\n\nStarting process...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )

    await index_files_to_db(chat_id, query.message, client)

@Client.on_message(filters.command("index") & admin)
async def index_command(client: Client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply("Please provide a channel ID/Username or reply to a message to start indexing.")

    if message.reply_to_message:
        if message.reply_to_message.forward_from_chat:
            chat_id = message.reply_to_message.forward_from_chat.id
            last_msg_id = message.reply_to_message.forward_from_message_id
        else:
            chat_id = message.chat.id
            last_msg_id = message.reply_to_message.id
    else:
        content = message.command[1]
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(content)
        if match:
            chat_id = match.group(4)
            last_msg_id = int(match.group(5))
            if chat_id.isnumeric():
                chat_id = int(("-100" + chat_id))
        else:
            chat_id = content
            last_msg_id = None
            try:
                if chat_id.startswith("-100"):
                    chat_id = int(chat_id)
                elif chat_id.isdigit():
                    chat_id = int(chat_id)
            except:
                pass

    try:
        chat = await client.get_chat(chat_id)
    except Exception as e:
        return await message.reply(f"Error: {e}")

    if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP]:
        return await message.reply("Only Channels and Supergroups can be indexed.")

    buttons = [
        [InlineKeyboardButton('Yes, Start Indexing', callback_data=f'index#accept#{chat.id}')],
        [InlineKeyboardButton('Cancel', callback_data='index#reject#0')]
    ]

    await message.reply(
        f"<b><u>ɪɴᴅᴇx ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ</u></b>\n\n"
        f"<b>ᴄʜᴀᴛ:</b> {chat.title}\n"
        f"<b>ɪᴅ:</b> <code>{chat.id}</code>\n\n"
        f"Do you want to index all files from this chat?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def index_files_to_db(chat_id, msg, bot):
    total = 0
    indexed = 0
    skipped = 0
    errors = 0

    async with lock:
        try:
            temp.CANCEL = False
            async for user_message in bot.get_chat_history(chat_id):
                if temp.CANCEL:
                    await msg.edit(f"<b>Indexing Cancelled!</b>\n\n<b>Saved:</b> {indexed}\n<b>Skipped:</b> {skipped}\n<b>Total Scanned:</b> {total}")
                    break

                total += 1
                if user_message.media:
                    try:
                        file = getattr(user_message, user_message.media.value)
                        is_added = await db.add_file(
                            file_id=file.file_id,
                            file_name=getattr(file, "file_name", "Untitled"),
                            file_size=file.file_size,
                            file_type=user_message.media.value,
                            caption=user_message.caption,
                            message_id=user_message.id # This is the original message ID, but we usually want the DB channel ID
                        )

                        if not is_added:
                            skipped += 1
                        else:
                            # Actually we should copy to DB channel first to get the bot's file_id
                            # if we want the bot to serve the file later.
                            # But wait, add_file refactor expects a file_id.
                            # Let's fix this logic: copy first, then add.
                            copied_msg = await user_message.copy(CHANNEL_ID)
                            bot_file = getattr(copied_msg, copied_msg.media.value)
                            # Re-add with bot's file info and message ID
                            await db.add_file(
                                file_id=bot_file.file_id,
                                file_name=getattr(bot_file, "file_name", "Untitled"),
                                file_size=bot_file.file_size,
                                file_type=copied_msg.media.value,
                                caption=copied_msg.caption,
                                message_id=copied_msg.id
                            )
                            indexed += 1
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        # retry logic could be added here if needed
                    except Exception:
                        errors += 1

                if total % 20 == 0:
                    try:
                        await msg.edit(
                            f"<b><u>ɪɴᴅᴇxɪɴɢ ᴘʀᴏɢʀᴇss</u></b>\n\n"
                            f"<b>ᴛᴏᴛᴀʟ sᴄᴀɴɴᴇᴅ:</b> {total}\n"
                            f"<b>ɪɴᴅᴇxᴇᴅ:</b> {indexed}\n"
                            f"<b>sᴋɪᴘᴘᴇᴅ:</b> {skipped}\n"
                            f"<b>ᴇʀʀᴏʀs:</b> {errors}",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
                        )
                    except:
                        pass

        except BotMethodInvalid:
            await msg.edit("Error: Bots cannot index this chat history. Use a Channel.")
        except Exception as e:
            await msg.edit(f"Error: {e}")
        else:
            await msg.edit(f"<b><u>ɪɴᴅᴇxɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇ</u></b>\n\n<b>ᴛᴏᴛᴀʟ sᴄᴀɴɴᴇᴅ:</b> {total}\n<b>ɪɴᴅᴇxᴇᴅ:</b> {indexed}\n<b>sᴋɪᴘᴘᴇᴅ:</b> {skipped}")
            await db.add_indexed_channel(chat_id)

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
