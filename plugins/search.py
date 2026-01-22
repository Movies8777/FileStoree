# (©)Codeflix_Botz
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from bot import Bot
from config import *
from helper_func import is_subscribed, encode
from database.database import db
import asyncio

@Bot.on_message(filters.private & filters.text & ~filters.regex("^/"))
async def search_handler(client: Client, message: Message):
    # Check force sub
    if not await is_subscribed(client, message.from_user.id):
        try:
            from plugins.start import not_joined
            return await not_joined(client, message)
        except Exception as e:
            print(f"Error importing not_joined: {e}")
            return await message.reply("Please join our channel to use this bot.")

    query = message.text.strip()
    if len(query) < 3:
        return

    search_msg = await message.reply_text("<b>Sᴇᴀʀᴄʜɪɴɢ...</b>")
    files = await db.find_file(query)

    if not files:
        return await search_msg.edit("<b>Nᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ!</b>")

    buttons = []
    for file in files[:10]: # Limit to 10 results for better UI
        msg_id = file['msg_id']
        file_name = file['file_name']

        # Generate the unique start link
        string = f"get-{msg_id * abs(client.db_channel.id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        buttons.append([InlineKeyboardButton(f"📁 {file_name[:50]}", url=link)])

    # Add How To Download button
    buttons.append([InlineKeyboardButton("🍿 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🍿", url=TUT_VID)])

    text = f"<b>🔎 Sᴇᴀʀᴄʜ Rᴇsᴜʟᴛs Fᴏʀ '{query}'</b>\n"
    text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    if len(files) > 10:
        text += f"<i>Sʜᴏᴡɪɴɢ ᴛᴏᴘ 10 ʀᴇsᴜʟᴛs ᴏᴜᴛ ᴏғ {len(files)}:</i>"
    else:
        text += f"<i>Fᴏᴜɴᴅ {len(files)} ʀᴇsᴜʟᴛs:</i>"

    await search_msg.edit(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
