#(©)Codexbotz

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
import asyncio
from pyrogram.errors import FloodWait
from helper_func import encode, get_message_id, admin
from config import LOGGER

logger = LOGGER(__name__)

@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue


    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True)
    logger.info(f"User {message.from_user.id} generated a batch link: {f_msg_id} to {s_msg_id}")


@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>Usage:</b> Reply to any message with /genlink to get its link.")

    reply_text = await message.reply_text("Please Wait...!", quote = True)
    msg_id = await get_message_id(client, message.reply_to_message)

    if not msg_id:
        try:
            post_message = await message.reply_to_message.copy(chat_id = client.db_channel.id, disable_notification=True)
            msg_id = post_message.id
            # Index in MongoDB
            await index_message(message.reply_to_message, msg_id)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            post_message = await message.reply_to_message.copy(chat_id = client.db_channel.id, disable_notification=True)
            msg_id = post_message.id
            await index_message(message.reply_to_message, msg_id)
        except Exception as e:
            print(e)
            return await reply_text.edit_text("Something went Wrong while copying to DB Channel..!")

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", disable_web_page_preview = True)
    logger.info(f"User {message.from_user.id} generated a link for msg_id {msg_id}")


async def index_message(msg, db_msg_id):
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
        from database.database import db
        await db.add_file(file_name, file_size, file_type, file_id, db_msg_id, msg.caption if msg.caption else None)
