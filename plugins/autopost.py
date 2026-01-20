
from pyrogram import Client, filters
from database.database import db
from helper_func import admin

@Client.on_message(filters.command("add_list") & admin)
async def add_list_command(client, message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply("Please reply to a text message containing the list of items (one per line).")

    items = message.reply_to_message.text.split('\n')
    items = [i.strip() for i in items if i.strip()]

    await db.add_to_autopost_list(items)
    await message.reply(f"Added {len(items)} items to the auto-post list.")

@Client.on_message(filters.command("set_autopost_channel") & admin)
async def set_autopost_channel_command(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a channel ID.")

    try:
        channel_id = int(message.command[1])
        await db.update_autopost_settings({'target_channel': channel_id})
        await message.reply(f"Auto-post target channel set to {channel_id}.")
    except ValueError:
        await message.reply("Invalid channel ID. It must be an integer.")

@Client.on_message(filters.command("start_autopost") & admin)
async def start_autopost_command(client, message):
    await db.update_autopost_settings({'is_running': True})
    await message.reply("Auto-posting started (every 3 hours).")

@Client.on_message(filters.command("stop_autopost") & admin)
async def stop_autopost_command(client, message):
    await db.update_autopost_settings({'is_running': False})
    await message.reply("Auto-posting stopped.")

@Client.on_message(filters.command("clear_list") & admin)
async def clear_list_command(client, message):
    await db.clear_autopost_list()
    await message.reply("Auto-post list cleared.")

@Client.on_message(filters.command("autopost_info") & admin)
async def autopost_info_command(client, message):
    settings = await db.get_autopost_settings()
    is_running = settings.get('is_running', False)
    target_channel = settings.get('target_channel', 0)
    current_index = settings.get('current_index', 0)
    total_items = await db.get_autopost_list_count()

    text = f"<b><u>ᴀᴜᴛᴏ-ᴘᴏsᴛ sᴛᴀᴛᴜs</u></b>\n\n"
    text += f"<b>ʀᴜɴɴɪɴɢ:</b> {'✅' if is_running else '❌'}\n"
    text += f"<b>ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ:</b> <code>{target_channel}</code>\n"
    text += f"<b>ǫᴜᴇᴜᴇ sɪᴢᴇ:</b> {total_items}\n"
    text += f"<b>ᴄᴜʀʀᴇɴᴛ ɪɴᴅᴇx:</b> {current_index}\n"

    await message.reply(text)
