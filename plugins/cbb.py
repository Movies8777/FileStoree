#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import Client 
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from database.database import *
from helper_func import is_admin, get_exp_time, encode
import re

def safe_edit(msg, *args, **kwargs):
    """Safely edit text without MESSAGE_NOT_MODIFIED crashes."""
    try:
        return msg.edit_text(*args, **kwargs)
    except MessageNotModified:
        pass
    except Exception:
        pass


@Bot.on_callback_query(group=1)
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data.startswith("admin_cmds"):
        if not await is_admin(query.from_user.id):
            return await query.answer("You are not authorized to view this!", show_alert=True)

        page = data.split("_")[-1] if "_" in data else "1"
        caption = CMD_TXT_1 if page == "1" else CMD_TXT_2

        buttons = []
        if page == "1":
            buttons.append([InlineKeyboardButton("ɴᴇxᴛ ᴘᴀɢᴇ 〉", callback_data="admin_cmds_2")])
        else:
            buttons.append([InlineKeyboardButton("〈 ʙᴀᴄᴋ ᴘᴀɢᴇ", callback_data="admin_cmds_1")])

        buttons.append([InlineKeyboardButton('‹ ʙᴀᴄᴋ', callback_data='start'),
                        InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')])

        try:
            await query.message.edit_caption(
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)

    elif data == "help":
        await query.message.edit_caption(
            caption=HELP_TXT.format(first=query.from_user.first_name),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_caption(
            caption=ABOUT_TXT.format(first=query.from_user.first_name),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close')]
            ])
        )

    elif data == "start":
        buttons = [
            [
                InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
                InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')
            ]
        ]
        if await is_admin(query.from_user.id):
            buttons.append([
                InlineKeyboardButton("ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs", callback_data="admin_cmds_1"),
                InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats")
            ])

        caption = START_MSG.format(
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        )
        reply_markup = InlineKeyboardMarkup(buttons)

        if query.message.photo or query.message.video:
            try:
                await query.message.edit_caption(caption=caption, reply_markup=reply_markup)
            except:
                await query.message.delete()
                await client.send_photo(chat_id=query.message.chat.id, photo=START_PIC, caption=caption, reply_markup=reply_markup)
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=START_PIC, caption=caption, reply_markup=reply_markup)

    elif data == "stats":
        if not await is_admin(query.from_user.id):
            return await query.answer("You are not authorized!", show_alert=True)

        total_users = await db.total_users_count()
        total_files = await db.total_files()
        total_verify = await db.get_total_verify_count()
        total_ongoing = await db.total_ongoing_count()

        stats_msg = (
            "<b>📊 Bᴏᴛ Sᴛᴀᴛɪsᴛɪᴄs</b>\n\n"
            f"<b>👤 Tᴏᴛᴀʟ Usᴇʀs :</b> <code>{total_users}</code>\n"
            f"<b>📁 Tᴏᴛᴀʟ Fɪʟᴇs :</b> <code>{total_files}</code>\n"
            f"<b>✅ Tᴏᴅᴀʏ Vᴇʀɪғɪᴇᴅ :</b> <code>{total_verify}</code>\n"
            f"<b>📺 Oɴɢᴏɪɴɢ Sᴇʀɪᴇs :</b> <code>{total_ongoing}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

        await query.message.edit_caption(
            caption=stats_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('‹ ʙᴀᴄᴋ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data='close')]
            ])
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


    elif data == "premium":
        await query.message.delete()
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=QR_PIC,
            caption=(
                f"<blockquote><b>👋Hello {query.from_user.username}</b></blockquote>\n\n"
                f"<blockquote><b>🏷 Pricing:</b>\n\n"
                f"● <b>{PRICE1} : For 7 Days Prime Membership</b>\n"
                f"● <b>{PRICE2} : For 1 Month Prime Membership</b>\n"
                f"● <b>{PRICE3} : For 3 Months Prime Membership</b>\n"
                f"● <b>{PRICE4} : For 6 Months Prime Membership</b>\n"
                f"● <b>{PRICE5} : For 1 Year Prime Membership</b></blockquote>\n\n\n"
                f"<blockquote>"
                f"<b>💵 Payment Methods We Accept Now:</b>\n"
                f"┏╼╾╼╾╼╾╼╾━\n"
                f"♲ <b>Gift Card</b>\n"
                f"♲ <b>Crypto</b>\n"
                f"┗╼╾╼╾╼╾╼╾━"
                f"</blockquote>\n\n"
                f"<b>⚠️ Important Notice:</b>\n"
                f"<blockquote>"
                f"Please note that this bot Premium Subscription is non-refundable once purchased.\n"
                f"We recommend reviewing all details carefully before completing your payment."
                f"</blockquote>\n\n\n"

                f"<b>🤙 To Buy: @Goathunterr</b>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Send Giftcard/And payment (ᴀᴅᴍɪɴ)", url=(SCREENSHOT_URL)
                        )
                    ],
                    [
                        InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_to_verify"),
                        InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"),
                    ],
                ]
            )
        )



    elif data == "back_to_verify":
        user_id = query.from_user.id
        verify_status = await db.get_verify_status(user_id)
        shortlink = verify_status.get('link')
        await query.message.delete()

        btn = [
            [InlineKeyboardButton("ᴏᴘᴇɴ ʟɪɴᴋ", url=shortlink),
             InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID)],
            [InlineKeyboardButton("ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")]
        ]
        await client.send_message(
            chat_id=query.message.chat.id,
            text=(
                f"Your token has expired. Please refresh to continue..\n\n"
                f"<b>Token Timeout:</b> {get_exp_time(VERIFY_EXPIRE)}\n\n"
                "<b>What is token?</b>\n"
                f"Pass one ad to use bot for {get_exp_time(VERIFY_EXPIRE)}"
            ),
            reply_markup=InlineKeyboardMarkup(btn)
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "ᴏғғ" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "ongoing_list" or data.startswith("ongoing_list_"):
        if data == "ongoing_list":
            page = 0
        else:
            page = int(data.split("_")[2])

        all_ongoing = await db.get_all_ongoing()
        if not all_ongoing:
            return await query.message.edit_text("<b>No ongoing series found!</b>",
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]]))

        # Pagination logic (10 per page)
        per_page = 10
        total_pages = (len(all_ongoing) + per_page - 1) // per_page
        start = page * per_page
        end = start + per_page

        buttons = []
        for series in all_ongoing[start:end]:
            buttons.append([InlineKeyboardButton(f"📺 {series['title']} (S{series['season']} E{series['current_ep']})",
                                                 callback_data=f"manage_ongoing_{series['title'][:20]}")])

        # Navigation buttons
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️ Bᴀᴄᴋ", callback_data=f"ongoing_list_{page-1}"))
        nav.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="none"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("Nᴇxᴛ ▶️", callback_data=f"ongoing_list_{page+1}"))

        if nav:
            buttons.append(nav)

        buttons.append([InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")])
        await query.message.edit_text("<b>📺 Oɴɢᴏɪɴɢ Sᴇʀɪᴇs Mᴀɴᴀɢᴇᴍᴇɴᴛ</b>",
                                     reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("manage_ongoing_"):
        title_prefix = data.replace("manage_ongoing_", "")
        all_ongoing = await db.get_all_ongoing()
        series = None
        for s in all_ongoing:
            if s['title'].startswith(title_prefix):
                series = s
                break

        if not series:
            return await query.answer("Series not found!", show_alert=True)

        text = (f"<b>📺 Mᴀɴᴀɢɪɴɢ: {series['title']}</b>\n\n"
                f"<b>Sᴇᴀsᴏɴ:</b> {series['season']}\n"
                f"<b>ᴄᴜʀʀᴇɴᴛ Eᴘɪsᴏᴅᴇ:</b> {series['current_ep']}\n"
                f"<b>Tᴏᴛᴀʟ Eᴘɪsᴏᴅᴇs:</b> {series['total_eps']}\n"
                f"<b>Lᴀɴɢᴜᴀɢᴇ:</b> {series['language']}\n"
                f"<b>Rᴇʟᴇᴀsᴇ Dᴀʏ:</b> {series['release_day']}")

        buttons = [
            [InlineKeyboardButton("📤 Pᴏsᴛ Nᴇxᴛ Eᴘɪsᴏᴅᴇ", callback_data=f"post_ongoing_{series['title'][:20]}")],
            [InlineKeyboardButton("➕ Iɴᴄʀᴇᴍᴇɴᴛ Eᴘ", callback_data=f"inc_ep_{series['title'][:20]}"),
             InlineKeyboardButton("➖ Dᴇᴄʀᴇᴍᴇɴᴛ Eᴘ", callback_data=f"dec_ep_{series['title'][:20]}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="ongoing_list_0"),
             InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("inc_ep_") or data.startswith("dec_ep_"):
        is_inc = data.startswith("inc_ep_")
        title_prefix = data.replace("inc_ep_", "").replace("dec_ep_", "")
        all_ongoing = await db.get_all_ongoing()
        series = None
        for s in all_ongoing:
            if s['title'].startswith(title_prefix):
                series = s
                break

        if not series:
            return await query.answer("Series not found!", show_alert=True)

        new_ep = int(series['current_ep']) + (1 if is_inc else -1)
        if new_ep < 0: new_ep = 0

        await db.update_ongoing_ep(series['title'], str(new_ep))
        await query.answer(f"Episode updated to {new_ep}")

        # Refresh management view
        series['current_ep'] = str(new_ep)
        text = (f"<b>📺 Mᴀɴᴀɢɪɴɢ: {series['title']}</b>\n\n"
                f"<b>Sᴇᴀsᴏɴ:</b> {series['season']}\n"
                f"<b>ᴄᴜʀʀᴇɴᴛ Eᴘɪsᴏᴅᴇ:</b> {series['current_ep']}\n"
                f"<b>Tᴏᴛᴀʟ Eᴘɪsᴏᴅᴇs:</b> {series['total_eps']}\n"
                f"<b>Lᴀɴɢᴜᴀɢᴇ:</b> {series['language']}\n"
                f"<b>Rᴇʟᴇᴀsᴇ Dᴀʏ:</b> {series['release_day']}")

        buttons = [
            [InlineKeyboardButton("📤 Pᴏsᴛ Nᴇxᴛ Eᴘɪsᴏᴅᴇ", callback_data=f"post_ongoing_{series['title'][:20]}")],
            [InlineKeyboardButton("➕ Iɴᴄʀᴇᴍᴇɴᴛ Eᴘ", callback_data=f"inc_ep_{series['title'][:20]}"),
             InlineKeyboardButton("➖ Dᴇᴄʀᴇᴍᴇɴᴛ Eᴘ", callback_data=f"dec_ep_{series['title'][:20]}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="ongoing_list_0"),
             InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("post_ongoing_"):
        title_prefix = data.replace("post_ongoing_", "")
        all_ongoing = await db.get_all_ongoing()
        series = None
        for s in all_ongoing:
            if s['title'].startswith(title_prefix):
                series = s
                break

        if not series:
            return await query.answer("Series not found!", show_alert=True)

        # Search for files matching the episode
        ep_tag = f"E{int(series['current_ep']):02d}"
        search_query = f"{series['title']} S{series['season']} {ep_tag}"
        files = await db.find_file(search_query)

        if not files:
            return await query.answer(f"No files found for {series['title']} {ep_tag} in DB! Please upload first.", show_alert=True)

        # Format the caption as requested
        caption = (f"<b>✦ {series['title']}</b>\n\n"
                   f"<b>➥ Season - {series['season']}</b>\n"
                   f"<b>➥ Episode - {series['current_ep']}</b>\n"
                   f"<b>➥ Language - {series['language']}</b>\n\n"
                   f"<blockquote><b>🔔 New Episode Every {series['release_day']}.</b></blockquote>\n\n"
                   f"<blockquote><b>✮ Usᴇ VLC Pʟᴀʏᴇʀ Oʀ Mx Pʟᴀʏᴇʀ To Cʜᴀɴɢᴇ Aᴜᴅɪᴏ Aɴᴅ Sᴜʙᴛɪᴛʟᴇs Fᴏʀ A Bᴇᴛᴛᴇʀ Vɪᴇᴡɪɴɢ Exᴘᴇʀɪᴇɴᴄᴇ.</b></blockquote>")

        # Quality buttons logic mirrored from post.py
        res_groups = {}
        for file in files:
            res_match = re.search(r'(\d{3,4}p|4[kK])', file['file_name'], re.IGNORECASE)
            res = res_match.group(1).lower() if res_match else "hdr"
            if res not in res_groups:
                res_groups[res] = []
            res_groups[res].append(file)

        buttons = []
        def q_sort(q):
            val = re.sub(r'p|k', '', q, flags=re.I)
            return int(val) if val.isdigit() else 0

        all_res_buttons = []
        bot_username = (await client.get_me()).username

        for res in sorted(res_groups.keys(), key=q_sort):
            res_files = res_groups[res]
            if len(res_files) == 1:
                # Single file link
                string = f"get-{res_files[0]['msg_id'] * abs(client.db_channel.id)}"
            else:
                # Batch link for multiple parts of same quality
                msg_ids = [f['msg_id'] for f in res_files]
                string = f"get-{min(msg_ids) * abs(client.db_channel.id)}-{max(msg_ids) * abs(client.db_channel.id)}"

            base64_string = await encode(string)
            link = f"https://t.me/{bot_username}?start={base64_string}"
            all_res_buttons.append(InlineKeyboardButton(f"{res.upper()}", url=link))

        for i in range(0, len(all_res_buttons), 3):
            buttons.append(all_res_buttons[i:i+3])

        buttons.append([InlineKeyboardButton(" [ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ] ", url=TUT_VID)])

        target_chat = -1002096101886 # The ongoing channel
        try:
            await client.send_photo(
                chat_id=target_chat,
                photo=series['poster'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

            # Increment episode after posting
            new_ep = int(series['current_ep']) + 1
            total_eps = int(series['total_eps'])

            if new_ep > total_eps:
                # Series completed! Remove from ongoing list
                await db.del_ongoing(series['title'])
                await query.answer(f"Series {series['title']} completed and removed from list!", show_alert=True)
                # Redirect to ongoing_list_0 logic
                all_ongoing = await db.get_all_ongoing()
                if not all_ongoing:
                    return await query.message.edit_text("<b>No ongoing series found!</b>",
                                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]]))
                page = 0
                per_page = 10
                total_pages = (len(all_ongoing) + per_page - 1) // per_page
                start = page * per_page
                end = start + per_page
                buttons = []
                for series_item in all_ongoing[start:end]:
                    buttons.append([InlineKeyboardButton(f"📺 {series_item['title']} (S{series_item['season']} E{series_item['current_ep']})",
                                                         callback_data=f"manage_ongoing_{series_item['title'][:20]}")])
                nav = []
                if page < total_pages - 1:
                    nav.append(InlineKeyboardButton("Nᴇxᴛ ▶️", callback_data=f"ongoing_list_{page+1}"))
                if nav: buttons.append(nav)
                buttons.append([InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")])
                return await query.message.edit_text("<b>📺 Oɴɢᴏɪɴɢ Sᴇʀɪᴇs Mᴀɴᴀɢᴇᴍᴇɴᴛ</b>", reply_markup=InlineKeyboardMarkup(buttons))

            await db.update_ongoing_ep(series['title'], str(new_ep))
            await query.answer("Successfully posted and incremented episode!", show_alert=True)

            # Refresh view manually to avoid infinite recursion
            series['current_ep'] = str(new_ep)
            text = (f"<b>📺 Mᴀɴᴀɢɪɴɢ: {series['title']}</b>\n\n"
                    f"<b>Sᴇᴀsᴏɴ:</b> {series['season']}\n"
                    f"<b>ᴄᴜʀʀᴇɴᴛ Eᴘɪsᴏᴅᴇ:</b> {series['current_ep']}\n"
                    f"<b>Tᴏᴛᴀʟ Eᴘɪsᴏᴅᴇs:</b> {series['total_eps']}\n"
                    f"<b>Lᴀɴɢᴜᴀɢᴇ:</b> {series['language']}\n"
                    f"<b>Rᴇʟᴇᴀsᴇ Dᴀʏ:</b> {series['release_day']}")

            buttons = [
                [InlineKeyboardButton("📤 Pᴏsᴛ Nᴇxᴛ Eᴘɪsᴏᴅᴇ", callback_data=f"post_ongoing_{series['title'][:20]}")],
                [InlineKeyboardButton("➕ Iɴᴄʀᴇᴍᴇɴᴛ Eᴘ", callback_data=f"inc_ep_{series['title'][:20]}"),
                 InlineKeyboardButton("➖ Dᴇᴄʀᴇᴍᴇɴᴛ Eᴘ", callback_data=f"dec_ep_{series['title'][:20]}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="ongoing_list_0"),
                 InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await query.answer(f"Failed to post: {str(e)}", show_alert=True)

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
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
