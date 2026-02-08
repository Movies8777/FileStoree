# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import SHORTLINK_URL, SHORTLINK_API
from helper_func import encode, get_shortlink, wrap_with_redirect, admin

@Bot.on_message(filters.command("spost") & filters.private & admin)
async def special_post(client, message):
    if len(message.command) < 3:
        return await message.reply("<b>Usage: /spost [channel_id] [movie_name]</b>")

    target_channel = message.command[1]
    movie_name = " ".join(message.command[2:])

    msg = await message.reply("<b>Searching...</b>")

    qualities = ["480p", "720p", "1080p", "2160p", "4k"]
    found_files = {}

    # Search in DB channel
    try:
        async for m in client.search_messages(chat_id=client.db_channel.id, query=movie_name):
            if m.document or m.video:
                file = m.document or m.video
                filename = file.file_name.lower() if file.file_name else ""
                # If no filename, check caption
                if not filename and m.caption:
                    filename = m.caption.lower()

                for q in qualities:
                    if q.lower() in filename:
                        if q not in found_files:
                            found_files[q] = m.id
                        break
    except Exception as e:
        return await msg.edit(f"<b>Search Error:</b>\n<code>{e}</code>")

    if not found_files:
        return await msg.edit("<b>No files found for this movie name!</b>")

    buttons = []
    # Sort found qualities based on the order in the 'qualities' list
    sorted_found_qualities = [q for q in qualities if q in found_files]

    for q in sorted_found_qualities:
        m_id = found_files[q]
        converted_id = m_id * abs(client.db_channel.id)
        base64_string = await encode(f"get-{converted_id}")

        # Special link with spcl_ prefix for bypassing verification
        direct_link = f"https://t.me/{client.username}?start=spcl_{base64_string}"

        # Apply shortener if configured
        if SHORTLINK_URL and SHORTLINK_API:
            try:
                direct_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, direct_link)
            except Exception as e:
                print(f"Shortener error: {e}")

        # Apply mask
        final_link = await wrap_with_redirect(direct_link)

        buttons.append(InlineKeyboardButton(q, url=final_link))

    # Arrange buttons in rows of 2
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    try:
        # If target_channel is a numeric ID, convert it to int
        try:
            chat_id = int(target_channel)
        except ValueError:
            chat_id = target_channel

        await client.send_message(
            chat_id=chat_id,
            text=f"<b>{movie_name.upper()}</b>",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await msg.edit(f"<b>Post created successfully in {target_channel}!</b>")
    except Exception as e:
        await msg.edit(f"<b>Error creating post:</b>\n<code>{e}</code>")
