import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import CHANNEL_ID, LOGGER, POST_CHANNEL_ID, TUT_VID
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

    # Grouping logic and metadata extraction
    res_groups = {}
    audio_tracks = set()
    year = details.get('release_date', '')[:4] if details.get('release_date') else "N/A"

    for file in files:
        file_name = file['file_name']
        # Regex to find resolution
        res_match = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
        res = res_match.group(1).upper() if res_match else "OTHERS"

        # Audio track extraction (common patterns)
        audios = re.findall(r'(Hindi|Odia|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Marathi|Punjabi|Multi|Dual|Audio)', file_name, re.IGNORECASE)
        for a in audios:
            audio_tracks.add(a.capitalize())

        if res not in res_groups:
            res_groups[res] = []

        # Link generation
        string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"

        res_groups[res].append((res, link))

    # Caption Construction
    title = details['title']
    audios_str = ", ".join(sorted(list(audio_tracks))) if audio_tracks else "Not Specified"

    # Try to find common format info in file names if available
    res_info = "720p BluRay x264 + x265 HEVC Multi Audio"
    for file in files:
        if '1080p' in file['file_name'].lower():
             res_info = "1080p BluRay x264 + x265 HEVC Multi Audio"
             break
        elif '2160p' in file['file_name'].lower() or '4k' in file['file_name'].lower():
             res_info = "2160p 4K UHD BluRay Multi Audio"
             break

    caption = f"<b>{title} ({year}) {res_info}\n\n"
    caption += f"> Audio Tracks: {audios_str} </b>"

    # Button Construction
    buttons = []
    # Collect all resolution links
    for res in sorted(res_groups.keys()):
        row = []
        for res_label, link in res_groups[res]:
            row.append(InlineKeyboardButton(res_label, url=link))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

    # Add How To Download button
    buttons.append([InlineKeyboardButton("How To Download", url=TUT_VID)])

    # Truncate if over 1024 characters
    if len(caption) > 1024:
        caption = caption[:1020] + "..."

    # Send to Post Channel and also to the user who requested
    target_chat = POST_CHANNEL_ID if POST_CHANNEL_ID else message.chat.id

    try:
        if details.get('backdrop_url'):
            post = await client.send_photo(
                chat_id=target_chat,
                photo=details['backdrop_url'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
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
