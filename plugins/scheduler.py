import asyncio
import time
import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import LOGGER, START_PIC, OWNER_ID
from helper_func import admin
from database.database import db
from plugins.post import process_post

logger = LOGGER(__name__)

# Scheduler loop
async def scheduler_loop(client: Bot):
    while True:
        try:
            config = await db.get_sched_config()
            if config.get('is_active'):
                now = time.time()
                last_post = config.get('last_post_time', 0)
                interval = config.get('interval', 10800) # Default 3 hours

                if now - last_post >= interval:
                    item = await db.get_next_sched_item()
                    if item:
                        logger.info(f"Processing scheduled post: {item['query']}")
                        # Create a dummy message to reuse process_post logic
                        dummy_message = Message(
                            id=0,
                            client=client,
                            text=f"/post {item['query']}",
                            chat=Message(id=0, chat=None).chat # Not really used but to satisfy internal checks
                        )
                        # We need a better way to call process_post without a real message
                        # Let's adapt process_post or mock enough of the message

                        class MockMessage:
                            def __init__(self, text, client):
                                self.text = text
                                self.command = text.split()[0][1:]
                                self.from_user = type('User', (), {'id': OWNER_ID})()
                                self.chat = type('Chat', (), {'id': OWNER_ID})()
                                self._client = client

                            async def reply_text(self, text, *args, **kwargs):
                                logger.info(f"Scheduler reply: {text}")
                                async def mock_delete(): pass
                                return type('Msg', (), {'edit': self.reply_text, 'delete': mock_delete})()

                            async def reply_photo(self, *args, **kwargs):
                                return await self.reply_text("Photo sent")

                        mock_msg = MockMessage(f"/post {item['query']}", client)

                        try:
                            from plugins.post import process_post
                            await process_post(client, mock_msg, config['target_channel'])
                            await db.mark_sched_done(item['_id'])
                            await db.update_sched_config('last_post_time', now)
                            logger.info(f"Successfully posted scheduled item: {item['query']}")
                        except Exception as e:
                            logger.error(f"Error in scheduled post processing: {e}")
                            # Put it back or mark as error? Mark as pending again if failed?
                            await db.sched_queue_data.update_one({'_id': item['_id']}, {'$set': {'status': 'pending'}})
                    else:
                        pass # Queue empty

        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")

        await asyncio.sleep(60) # Check every minute

@Bot.on_message(filters.command("postlist") & admin)
async def add_post_list(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b>\n/postlist movie1\nmovie2\nSeries S01 E01 to E10 link")

    # Extract list from message text (skipping the command)
    lines = message.text.split('\n')
    # First line might contain the command and the first item
    first_line = lines[0].split(None, 1)
    items = []
    if len(first_line) > 1:
        items.append(first_line[1].strip())

    items.extend([line.strip() for line in lines[1:] if line.strip()])

    for item in items:
        await db.add_to_sched_queue(item)

    await message.reply_text(f"<b>✅ Added {len(items)} items to the scheduled queue.</b>")

@Bot.on_message(filters.command("liststats") & admin)
async def list_stats(client: Bot, message: Message):
    config = await db.get_sched_config()
    queue = await db.get_sched_queue()

    status = "🟢 ACTIVE" if config['is_active'] else "🔴 INACTIVE"
    interval_h = config['interval'] / 3600

    last_post = config.get('last_post_time', 0)
    next_post = "N/A"
    if last_post:
        next_post_time = last_post + config['interval']
        remaining = next_post_time - time.time()
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            h, m = divmod(m, 60)
            next_post = f"{h}h {m}m {s}s"
        else:
            next_post = "Soon"

    text = (
        "<b>📅 Sᴄʜᴇᴅᴜʟᴇᴅ Pᴏsᴛɪɴɢ Dᴀsʜʙᴏᴀʀᴅ</b>\n\n"
        f"<b>Sᴛᴀᴛᴜs:</b> {status}\n"
        f"<b>Iɴᴛᴇʀᴠᴀʟ:</b> {interval_h} hours\n"
        f"<b>Tᴀʀɢᴇᴛ Cʜᴀɴɴᴇʟ:</b> <code>{config['target_channel']}</code>\n"
        f"<b>Qᴜᴇᴜᴇ Sɪᴢᴇ:</b> {len(queue)}\n"
        f"<b>Nᴇxᴛ Pᴏsᴛ Iɴ:</b> {next_post}\n\n"
        "<b>Upᴄᴏᴍɪɴɢ Iᴛᴇᴍs:</b>\n"
    )

    if not queue:
        text += "<i>Queue is empty.</i>"
    else:
        for i, item in enumerate(queue[:5], 1):
            text += f"{i}. <code>{item['query']}</code>\n"
        if len(queue) > 5:
            text += f"<i>... and {len(queue)-5} more</i>"

    buttons = [
        [
            InlineKeyboardButton(f"Sᴛᴀᴛᴜs: {'OFF' if config['is_active'] else 'ON'}", callback_data="sched_toggle"),
            InlineKeyboardButton("Sᴇᴛ Iɴᴛᴇʀᴠᴀʟ", callback_data="sched_set_time")
        ],
        [
            InlineKeyboardButton("Cʟᴇᴀʀ Qᴜᴇᴜᴇ", callback_data="sched_clear"),
            InlineKeyboardButton("Vɪᴇᴡ Fᴜʟʟ Qᴜᴇᴜᴇ", callback_data="sched_view")
        ],
        [
            InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")
        ]
    ]

    await message.reply_photo(photo=START_PIC, caption=text, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex(r'^sched_'))
async def sched_callbacks(client: Bot, query: CallbackQuery):
    if not await admin(client, query.message): # Simplified admin check for callback
        return await query.answer("Admin only!", show_alert=True)

    data = query.data

    if data == "sched_toggle":
        config = await db.get_sched_config()
        new_status = not config['is_active']
        await db.update_sched_config('is_active', new_status)
        await query.answer(f"Scheduler turned {'ON' if new_status else 'OFF'}")
        # Refresh dashboard
        await refresh_dashboard(client, query.message)

    elif data == "sched_set_time":
        buttons = [
            [InlineKeyboardButton("1 Hour", callback_data="sched_interval_3600"),
             InlineKeyboardButton("3 Hours", callback_data="sched_interval_10800")],
            [InlineKeyboardButton("6 Hours", callback_data="sched_interval_21600"),
             InlineKeyboardButton("12 Hours", callback_data="sched_interval_43200")],
            [InlineKeyboardButton("◀ Back", callback_data="sched_back")]
        ]
        await query.message.edit_caption("<b>Select posting interval:</b>", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("sched_interval_"):
        interval = int(data.split("_")[-1])
        await db.update_sched_config('interval', interval)
        await query.answer(f"Interval set to {interval/3600} hours")
        await refresh_dashboard(client, query.message)

    elif data == "sched_clear":
        await db.clear_sched_queue()
        await query.answer("Queue cleared!")
        await refresh_dashboard(client, query.message)

    elif data == "sched_view":
        queue = await db.get_sched_queue()
        if not queue:
            return await query.answer("Queue is empty!", show_alert=True)

        text = "<b>📋 Fᴜʟʟ Sᴄʜᴇᴅᴜʟᴇᴅ Qᴜᴇᴜᴇ:</b>\n\n"
        for i, item in enumerate(queue, 1):
            text += f"{i}. <code>{item['query']}</code>\n"
            if len(text) > 3500: # Telegram limit
                text += "... more items ..."
                break

        buttons = [[InlineKeyboardButton("◀ Back", callback_data="sched_back")]]
        await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "sched_back":
        await refresh_dashboard(client, query.message)

async def refresh_dashboard(client, message):
    config = await db.get_sched_config()
    queue = await db.get_sched_queue()

    status = "🟢 ACTIVE" if config['is_active'] else "🔴 INACTIVE"
    interval_h = config['interval'] / 3600

    last_post = config.get('last_post_time', 0)
    next_post = "N/A"
    if last_post:
        next_post_time = last_post + config['interval']
        remaining = next_post_time - time.time()
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            h, m = divmod(m, 60)
            next_post = f"{h}h {m}m {s}s"
        else:
            next_post = "Soon"

    text = (
        "<b>📅 Sᴄʜᴇᴅᴜʟᴇᴅ Pᴏsᴛɪɴɢ Dᴀsʜʙᴏᴀʀᴅ</b>\n\n"
        f"<b>Sᴛᴀᴛᴜs:</b> {status}\n"
        f"<b>Iɴᴛᴇʀᴠᴀʟ:</b> {interval_h} hours\n"
        f"<b>Tᴀʀɢᴇᴛ Cʜᴀɴɴᴇʟ:</b> <code>{config['target_channel']}</code>\n"
        f"<b>Qᴜᴇᴇ Sɪᴢᴇ:</b> {len(queue)}\n"
        f"<b>Nᴇxᴛ Pᴏsᴛ Iɴ:</b> {next_post}\n\n"
        "<b>Upᴄᴏᴍɪɴɢ Iᴛᴇᴍs:</b>\n"
    )

    if not queue:
        text += "<i>Queue is empty.</i>"
    else:
        for i, item in enumerate(queue[:5], 1):
            text += f"{i}. <code>{item['query']}</code>\n"
        if len(queue) > 5:
            text += f"<i>... and {len(queue)-5} more</i>"

    buttons = [
        [
            InlineKeyboardButton(f"Sᴛᴀᴛᴜs: {'OFF' if config['is_active'] else 'ON'}", callback_data="sched_toggle"),
            InlineKeyboardButton("Sᴇᴛ Iɴᴛᴇʀᴠᴀʟ", callback_data="sched_set_time")
        ],
        [
            InlineKeyboardButton("Cʟᴇᴀʀ Qᴜᴇᴜᴇ", callback_data="sched_clear"),
            InlineKeyboardButton("Vɪᴇᴡ Fᴜʟʟ Qᴜᴇᴜᴇ", callback_data="sched_view")
        ],
        [
            InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")
        ]
    ]

    try:
        await message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass
