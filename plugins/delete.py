from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from helper_func import admin
from database.database import db

@Bot.on_message(filters.command("del_index") & admin & filters.private)
async def del_index_command(client: Bot, message: Message):
    cmd_text = message.text.split(None, 1)
    if len(cmd_text) < 2:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "/del_index all - Delete all indexed files\n"
            "/del_index {query} - Delete specific files matching query"
        )

    query = cmd_text[1].strip()

    if query.lower() == "all":
        total = await db.total_files()
        return await message.reply_text(
            f"<b>⚠️ Confirmation Needed</b>\n\n"
            f"Are you sure you want to delete <b>ALL</b> {total} indexed files from the database?\n\n"
            f"This action cannot be undone!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes, Delete All", callback_data="confirm_del_all")],
                [InlineKeyboardButton("❌ No, Cancel", callback_data="close")]
            ])
        )
    else:
        # Check how many files would be deleted
        files = await db.find_file(query)
        if not files:
            return await message.reply_text(f"No files found matching: <code>{query}</code>")

        count = len(files)
        # Note: find_file is limited to 100, so count might be 100 even if more exist.
        # But for specific movie names, it's usually fine.

        # We'll use the same query for the callback
        return await message.reply_text(
            f"<b>⚠️ Confirmation Needed</b>\n\n"
            f"Found approximately <b>{count}</b> files matching: <code>{query}</code>\n"
            f"Do you want to delete them?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"✅ Delete {count} Files", callback_data=f"confirm_del_spec_{query[:40]}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="close")]
            ])
        )
