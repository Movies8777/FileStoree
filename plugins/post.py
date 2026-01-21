import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import CHANNEL_ID, LOGGER, POST_CHANNEL_ID
from helper_func import admin, encode
from database.database import db
from plugins.tmdb import search_tmdb, get_movie_details

logger = LOGGER(__name__)

@Bot.on_message(filters.command("post") & admin)
async def post_command(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> /post {movie_name}")

    query = message.text.split(" ", 1)[1]
    search_msg = await message.reply_text("<b>Sᴇᴀʀᴄʜɪɴɢ...</b>")

    files = await db.find_file(query)
    if not files:
        return await search_msg.edit("<b>Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")

    tmdb_result = await search_tmdb(query)
    if not tmdb_result:
        return await search_msg.edit("<b>Nᴏ TMDB ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ!</b>")

    tmdb_id = tmdb_result['id']
    media_type = tmdb_result['media_type']
    details = await get_movie_details(tmdb_id, media_type)

    if not details:
        return await search_msg.edit("<b>Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ TMDB ᴅᴇᴛᴀɪʟs!</b>")

    # Grouping logic
    res_groups = {}
    for file in files:
        file_name = file['file_name']
        # Regex to find resolution
        res_match = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
        res = res_match.group(1).upper() if res_match else "OTHERS"

        if res not in res_groups:
            res_groups[res] = []

        # Link generation
        string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        res_groups[res].append((file_name, link))

    # Caption Construction
    title = details['title']
    rating = details['rating']
    genres = ", ".join(details['genres'])

    caption = f"<b>🍿 {title}</b>\n\n"
    caption += f"<b>⭐ Rᴀᴛɪɴɢ:</b> {rating}/10\n"
    caption += f"<b>🎭 Gᴇɴʀᴇs:</b> {genres}\n\n"

    for res, items in sorted(res_groups.items()):
        caption += f"<b>━━━━━━━━━━━━━━━━━━━━━━\n📥 {res} Lɪɴᴋs\n━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        for name, link in items:
            # Shorten name if too long for caption
            short_name = name[:50] + "..." if len(name) > 50 else name
            caption += f"⚡️ <a href='{link}'>{short_name}</a>\n"
        caption += "\n"

    # Truncate if over 1024 characters
    if len(caption) > 1024:
        caption = caption[:1020] + "..."

    # Send to Post Channel and also to the user who requested
    target_chat = POST_CHANNEL_ID if POST_CHANNEL_ID else message.chat.id

    try:
        if details['poster_url']:
            post = await client.send_photo(
                chat_id=target_chat,
                photo=details['poster_url'],
                caption=caption
            )
        else:
            post = await client.send_message(
                chat_id=target_chat,
                text=caption
            )

        if target_chat != message.chat.id:
            await message.reply_text(f"<b>Pᴏsᴛ Sᴇɴᴛ ᴛᴏ <a href='https://t.me/c/{str(abs(target_chat))[3:]}/{post.id}'>Cʜᴀɴɴᴇʟ</a>!</b>")
        else:
            await search_msg.edit("<b>Pᴏsᴛ Gᴇɴᴇʀᴀᴛᴇᴅ!</b>")

    except Exception as e:
        logger.error(f"Error sending post: {e}")
        await message.reply_text(f"<b>Eʀʀᴏʀ:</b> {e}")

    await search_msg.delete()
