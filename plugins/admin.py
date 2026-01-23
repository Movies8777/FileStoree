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
#

import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import admin
from database.database import *



# Commands for adding admins by owner
@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    check = 0
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>You need to provide user ID(s) to add as admin.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/add_admin [user_id]</code> — Add one or more user IDs\n\n"
            "<b>Example:</b>\n"
            "<code>/add_admin 1234567890 9876543210</code>",
            reply_markup=reply_markup
        )

    admin_list = ""
    for id in admins:
        try:
            id = int(id)
        except:
            admin_list += f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n"
            continue

        if id in admin_ids:
            admin_list += f"<blockquote><b>ID <code>{id}</code> already exists.</b></blockquote>\n"
            continue

        id = str(id)
        if id.isdigit() and len(id) == 10:
            admin_list += f"<b><blockquote>(ID: <code>{id}</code>) added.</blockquote></b>\n"
            check += 1
        else:
            admin_list += f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n"

    if check == len(admins):
        for id in admins:
            await db.add_admin(int(id))
        await pro.edit(f"<b>✅ Admin(s) added successfully:</b>\n\n{admin_list}", reply_markup=reply_markup)
    else:
        await pro.edit(
            f"<b>❌ Some errors occurred while adding admins:</b>\n\n{admin_list.strip()}\n\n"
            "<b><i>Please check and try again.</i></b>",
            reply_markup=reply_markup
        )


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
#

@Bot.on_message(filters.command('deladmin') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>Please provide valid admin ID(s) to remove.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/deladmin [user_id]</code> — Remove specific IDs\n"
            "<code>/deladmin all</code> — Remove all admins",
            reply_markup=reply_markup
        )

    if len(admins) == 1 and admins[0].lower() == "all":
        if admin_ids:
            for id in admin_ids:
                await db.del_admin(id)
            ids = "\n".join(f"<blockquote><code>{admin}</code> ✅</blockquote>" for admin in admin_ids)
            return await pro.edit(f"<b>⛔️ All admin IDs have been removed:</b>\n{ids}", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>No admin IDs to remove.</blockquote></b>", reply_markup=reply_markup)

    if admin_ids:
        passed = ''
        for admin_id in admins:
            try:
                id = int(admin_id)
            except:
                passed += f"<blockquote><b>Invalid ID: <code>{admin_id}</code></b></blockquote>\n"
                continue

            if id in admin_ids:
                await db.del_admin(id)
                passed += f"<blockquote><code>{id}</code> ✅ Removed</blockquote>\n"
            else:
                passed += f"<blockquote><b>ID <code>{id}</code> not found in admin list.</b></blockquote>\n"

        await pro.edit(f"<b>⛔️ Admin removal result:</b>\n\n{passed}", reply_markup=reply_markup)
    else:
        await pro.edit("<b><blockquote>No admin IDs available to delete.</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & filters.private & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()

    if not admin_ids:
        admin_list = "<b><blockquote>❌ No admins found.</blockquote></b>"
    else:
        admin_list = "\n".join(f"<b><blockquote>ID: <code>{id}</code></blockquote></b>" for id in admin_ids)

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
    await pro.edit(f"<b>⚡ Current Admin List:</b>\n\n{admin_list}", reply_markup=reply_markup)


@Bot.on_message(filters.command('stats') & filters.private & admin)
async def get_stats(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)

    total_users = await db.total_users_count()
    total_files = await db.total_files()
    total_verify = await db.get_total_verify_count()
    total_ongoing = await db.total_ongoing_count()

    stats_msg = (
        "<b><blockquote>📊 ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs\n\n"
        f"📁 ᴛᴏᴛᴀʟ ғɪʟᴇs : {total_files}\n"
        f"👤 ᴛᴏᴛᴀʟ ᴜsᴇʀs : {total_users}\n"
        f"✅ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴅᴀʏ : {total_verify}\n"
        f"📺 ᴏɴɢᴏɪɴɢ sᴇʀɪᴇs : {total_ongoing}</blockquote></b>"
    )

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
    await pro.edit(stats_msg, reply_markup=reply_markup)


@Bot.on_message(filters.command('add_ongoing') & filters.private & admin)
async def add_ongoing_series(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("<b>Please reply to a photo with series details!</b>\n\n"
                                       "<b>Format:</b>\n"
                                       "<code>/add_ongoing Title | Season | Language | ReleaseDay | TotalEpisodes | StartingEpisode | Qualities(comma separated)</code>")

    try:
        data = message.text.split(None, 1)[1].split('|')
        if len(data) < 6:
            return await message.reply_text("<b>Invalid Format!</b>\n"
                                           "Need at least 6 fields: Title, Season, Language, ReleaseDay, TotalEpisodes, StartingEpisode")

        title = data[0].strip()
        season = data[1].strip()
        language = data[2].strip()
        release_day = data[3].strip()
        total_eps = data[4].strip()
        starting_ep = data[5].strip()
        qualities = data[6].strip() if len(data) > 6 else "720p, 1080p"

        poster = message.reply_to_message.photo.file_id

        await db.add_ongoing(title, season, language, release_day, total_eps, starting_ep, poster, qualities)
        await message.reply_text(f"<b>✅ Successfully added ongoing series:</b>\n\n"
                                f"<b>Title:</b> {title}\n"
                                f"<b>Season:</b> {season}\n"
                                f"<b>Language:</b> {language}\n"
                                f"<b>Release Day:</b> {release_day}\n"
                                f"<b>Total Episodes:</b> {total_eps}\n"
                                f"<b>Current Episode:</b> {starting_ep}\n"
                                f"<b>Qualities:</b> {qualities}")
    except Exception as e:
        await message.reply_text(f"<b>Error:</b> <code>{str(e)}</code>")

@Bot.on_message(filters.command('ongoing') & filters.private & admin)
async def list_ongoing(client: Client, message: Message):
    all_ongoing = await db.get_all_ongoing()
    if not all_ongoing:
        return await message.reply_text("<b>No ongoing series found!</b>")

    buttons = []
    for series in all_ongoing:
        buttons.append([InlineKeyboardButton(f"📺 {series['title']} (S{series['season']} E{series['current_ep']})",
                                             callback_data=f"manage_ongoing_{series['title'][:20]}")])

    buttons.append([InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")])
    await message.reply_text("<b>📺 Oɴɢᴏɪɴɢ Sᴇʀɪᴇs Mᴀɴᴀɢᴇᴍᴇɴᴛ</b>",
                             reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_message(filters.command('del_ongoing') & filters.private & admin)
async def delete_ongoing(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage: /del_ongoing {title}</b>")

    title = message.text.split(None, 1)[1].strip()
    series = await db.get_ongoing(title)
    if not series:
        # Try partial match if exact fails
        all_ongoing = await db.get_all_ongoing()
        for s in all_ongoing:
            if title.lower() in s['title'].lower():
                title = s['title']
                series = s
                break

    if not series:
        return await message.reply_text(f"<b>Series <code>{title}</code> not found!</b>")

    await db.del_ongoing(title)
    await message.reply_text(f"<b>✅ Deleted ongoing series:</b> <code>{title}</code>")


@Bot.on_message(filters.command('file_details') & filters.private & admin)
async def get_file_details(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage: /file_details {filename_or_query}</b>")

    query = message.text.split(None, 1)[1]
    pro = await message.reply("<b>Searching...</b>", quote=True)

    files = await db.find_file(query)
    if not files:
        return await pro.edit("<b>No files found!</b>")

    # Return details for the first matching file for brevity
    file = files[0]

    details = (
        f"<b>📄 Fɪʟᴇ Dᴇᴛᴀɪʟs</b>\n\n"
        f"<b>Nᴀᴍᴇ:</b> <code>{file['file_name']}</code>\n"
        f"<b>Sɪᴢᴇ:</b> <code>{file['file_size']} bytes</code>\n"
        f"<b>Tʏᴘᴇ:</b> <code>{file['file_type']}</code>\n"
        f"<b>Msg ID:</b> <code>{file['msg_id']}</code>\n"
        f"<b>Cᴀᴘᴛɪᴏɴ:</b>\n<blockquote>{file.get('caption', 'No Caption')}</blockquote>"
    )

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
    await pro.edit(details, reply_markup=reply_markup)


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
#