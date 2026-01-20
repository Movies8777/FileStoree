
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import get_search_results, Media, get_file_details
from helper_func import encode, decode
from config import *

@Client.on_message(filters.group & filters.text & ~filters.command(['start', 'help', 'about']))
async def group_filter(client, message):
    if re.findall(r'((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)', message.text):
        return

    if len(message.text) < 2:
        return

    query = message.text
    files, next_offset, total_results = await get_search_results(message.chat.id, query)

    if not files:
        return

    btn = []
    for file in files:
        file_id = file.file_id
        if len(file_id) > 50:
            # If file_id is too long, we use a short identifier.
            # For simplicity, we'll use the first 50 chars and hope it works,
            # or better, use a database lookup for a shorter key.
            # But the Media model uses file_id as _id.
            # Let's try to just use a unique part of it if possible,
            # or use a different callback prefix.
            pass

        btn.append(
            [InlineKeyboardButton(text=f"{file.file_name} {file.file_size}", callback_data=f"fl#{file_id[:50]}")]
        )

    if next_offset:
        btn.append(
            [InlineKeyboardButton(text="Next ⏩", callback_data=f"next#{query}#{next_offset}")]
        )

    await message.reply_text(
        f"<b>Found {total_results} results for {query}</b>",
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    _, ident, offset = query.data.split("#")
    files, next_offset, total_results = await get_search_results(query.message.chat.id, ident, offset=int(offset))

    btn = []
    for file in files:
        btn.append(
            [InlineKeyboardButton(text=f"{file.file_name} {file.file_size}", callback_data=f"file#{file.file_id}")]
        )

    if next_offset:
        btn.append(
            [InlineKeyboardButton(text="Next ⏩", callback_data=f"next#{ident}#{next_offset}")]
        )

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^fl"))
async def send_file(bot, query):
    _, file_id = query.data.split("#")
    # Search by prefix if we truncated it
    if len(file_id) == 50:
        filter = {'_id': {'$regex': f'^{re.escape(file_id)}'}}
        cursor = Media.find(filter)
        files = await cursor.to_list(length=1)
    else:
        files = await get_file_details(file_id)
    if not files:
        return await query.answer("File not found!", show_alert=True)

    file = files[0]
    try:
        await bot.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file.file_id,
            caption=file.caption or file.file_name
        )
        await query.answer("Check your PM!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)

@Client.on_message(filters.private & filters.text & ~filters.command(['start', 'help', 'about', 'index', 'total']))
async def private_filter(client, message):
    await group_filter(client, message)
