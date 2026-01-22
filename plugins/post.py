import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import LOGGER, POST_CHANNEL_ID, TUT_VID
from helper_func import admin, encode
from database.database import db

logger = LOGGER(__name__)

def extract_quality(file_name):
    # Match common resolutions
    res_match = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
    if res_match:
        return res_match.group(1).upper()

    # Check for other quality indicators
    if re.search(r'BluRay|BRRip|BDRip', file_name, re.IGNORECASE):
        return "BluRay"
    if re.search(r'WEB-DL|WEBRip', file_name, re.IGNORECASE):
        return "WEB-DL"
    if re.search(r'HDRip|DVDRip', file_name, re.IGNORECASE):
        return "HDRip"

    return "HDR"

def extract_year(file_names):
    years = set()
    for name in file_names:
        match = re.search(r'(19|20)\d{2}', name)
        if match:
            years.add(int(match.group()))
    if not years:
        return "N/A"
    if len(years) == 1:
        return str(list(years)[0])
    return f"{min(years)} - {max(years)}"

def extract_audio(file_names):
    audios = set()
    patterns = {
        'Hindi': r'Hindi',
        'English': r'English|Eng',
        'Tamil': r'Tamil',
        'Telugu': r'Telugu',
        'Malayalam': r'Malayalam',
        'Kannada': r'Kannada',
        'Bengali': r'Bengali',
        'Marathi': r'Marathi',
        'Punjabi': r'Punjabi',
        'Multi': r'Multi',
        'Dual': r'Dual',
        'ESubs': r'ESub|Subtitle'
    }
    for name in file_names:
        for label, pattern in patterns.items():
            if re.search(pattern, name, re.IGNORECASE):
                audios.add(label)

    if not audios:
        return "Hindi"

    # Priority sorting or just alphabetical
    res = sorted(list(audios))
    return " ".join(res)

def extract_genres(file_names):
    genres = set()
    patterns = {
        'Action': r'Action',
        'Adventure': r'Adventure',
        'Animation': r'Animation',
        'Comedy': r'Comedy',
        'Crime': r'Crime',
        'Documentary': r'Documentary',
        'Drama': r'Drama',
        'Family': r'Family',
        'Fantasy': r'Fantasy',
        'History': r'History',
        'Horror': r'Horror',
        'Music': r'Music',
        'Mystery': r'Mystery',
        'Romance': r'Romance',
        'Sci-Fi': r'Sci-Fi|Science Fiction',
        'Thriller': r'Thriller',
        'War': r'War',
        'Western': r'Western'
    }
    for name in file_names:
        for label, pattern in patterns.items():
            if re.search(pattern, name, re.IGNORECASE):
                genres.add(label)

    if not genres:
        return "Drama"

    return " | ".join(sorted(list(genres)))

@Bot.on_message(filters.command("post") & admin)
async def post_command(client: Bot, message: Message):
    # Usage check
    # /post {movie_name} {poster_url}
    # /post {series_name} E01 to E06 {poster_url}

    cmd_text = message.text.split(None, 1)
    if len(cmd_text) < 2:
        return await message.reply_text("<b>Usage:</b>\n\n<b>Movie:</b> /post {movie_name} {poster_url}\n<b>Series:</b> /post {series_name} E01 to E06 {poster_url}")

    full_query = cmd_text[1]

    # Check if it's a series (contains " to ")
    is_series = " to " in full_query.lower() and re.search(r'E\d+', full_query, re.IGNORECASE)

    if is_series:
        # Parse series: {series_name} E{start} to E{end} {poster_url}
        try:
            match = re.search(r'(.+?)\s+(E\d+)\s+to\s+(E\d+)\s+(.+)', full_query, re.IGNORECASE)
            if not match:
                return await message.reply_text("<b>Invalid series format!</b>\nUse: /post {series_name} E01 to E06 {poster_url}")

            series_name = match.group(1).strip()
            start_ep_str = match.group(2).upper()
            end_ep_str = match.group(3).upper()
            poster_url = match.group(4).strip()

            start_ep = int(start_ep_str[1:])
            end_ep = int(end_ep_str[1:])

            if start_ep > end_ep:
                return await message.reply_text("<b>Start episode cannot be greater than end episode!</b>")

            search_msg = await message.reply_text(f"<b>Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ {series_name} {start_ep_str}-{end_ep_str}...</b>")

            # Find files for all episodes in range
            all_files = []
            for ep_num in range(start_ep, end_ep + 1):
                ep_tag = f"E{ep_num:02d}"
                files = await db.find_file(f"{series_name} {ep_tag}")
                all_files.extend(files)

            if not all_files:
                return await search_msg.edit("<b>Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")

            # Grouping files by episode and resolution
            ep_res_groups = {} # {Episode: {Resolution: [link]}}
            res_groups = {} # {Resolution: [file_objects]}

            for file in all_files:
                file_name = file['file_name']
                ep_match = re.search(r'E(\d{2,3})', file_name, re.IGNORECASE)
                if not ep_match: continue
                ep_val = f"E{int(ep_match.group(1)):02d}"

                if ep_val not in ep_res_groups:
                    ep_res_groups[ep_val] = {}

                res = extract_quality(file_name)
                if res not in ep_res_groups[ep_val]:
                    ep_res_groups[ep_val][res] = []

                if res not in res_groups:
                    res_groups[res] = []
                res_groups[res].append(file)

                string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                base64_string = await encode(string)
                link = f"https://t.me/{client.username}?start={base64_string}"
                ep_res_groups[ep_val][res].append(link)

            # Caption and Buttons
            qualities = " + ".join(sorted(list(set(extract_quality(f['file_name']) for f in all_files))))
            years = extract_year([f['file_name'] for f in all_files])
            audios = extract_audio([f.get('caption') or f['file_name'] for f in all_files])
            genres = extract_genres([f.get('caption') or f['file_name'] for f in all_files])

            title = series_name.upper()
            header = f"<b>{title} ({years}) {qualities} {audios}</b>"
            caption = (
                f"{header}\n\n"
                f"<b>⭐ TITLE: {title}\n"
                f"📺 YEAR: {years}\n"
                f"🎥 QUALITY: {qualities}\n"
                f"🎧 AUDIO: {audios}\n"
                f"📁 GENRES: {genres}\n\n"
                f"✨ Join Our Main Channel @Movies8777\n"
                f"━━━━━━━━━━━━━━━━━━━━━━</b>"
            )

            buttons = []
            if len(ep_res_groups) > 1:
                # Multiple episodes: Only show resolution batch buttons
                batch_res_buttons = []
                for res in sorted(res_groups.keys()):
                    res_files = res_groups[res]
                    msg_ids = [f['msg_id'] for f in res_files]
                    first_id = min(msg_ids)
                    last_id = max(msg_ids)

                    batch_string = f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}"
                    batch_base64 = await encode(batch_string)
                    batch_link = f"https://t.me/{client.username}?start={batch_base64}"
                    batch_res_buttons.append(InlineKeyboardButton(f"⚡ {res}", url=batch_link))

                for i in range(0, len(batch_res_buttons), 3):
                    buttons.append(batch_res_buttons[i:i+3])
            else:
                # Single episode: show normal episode buttons
                for ep in sorted(ep_res_groups.keys()):
                    ep_buttons = []
                    for res in sorted(ep_res_groups[ep].keys()):
                        link = ep_res_groups[ep][res][0]
                        ep_buttons.append(InlineKeyboardButton(f"{ep} {res}", url=link))
                    for i in range(0, len(ep_buttons), 3):
                        buttons.append(ep_buttons[i:i+3])

            # Global Batch link
            if all_files:
                msg_ids = [f['msg_id'] for f in all_files]
                first_id = min(msg_ids)
                last_id = max(msg_ids)

                batch_string = f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}"
                batch_base64 = await encode(batch_string)
                batch_link = f"https://t.me/{client.username}?start={batch_base64}"

                buttons.append([InlineKeyboardButton("🎁 Bᴀᴛᴄʜ Dᴏᴡɴʟᴏᴀᴅ (Aʟʟ Eᴘs) 🎁", url=batch_link)])

            buttons.append([InlineKeyboardButton("🍿 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🍿", url=TUT_VID)])

            await client.send_photo(
                chat_id=POST_CHANNEL_ID if POST_CHANNEL_ID else message.chat.id,
                photo=poster_url,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await search_msg.delete()
            await message.reply_text("<b>✅ Series Post Sent!</b>")

        except Exception as e:
            logger.error(f"Error in series post: {e}")
            return await message.reply_text(f"<b>Error:</b> {e}")

    else:
        # Movie: /post {movie_name} {poster_url}
        try:
            if " " not in full_query:
                return await message.reply_text("<b>Poster URL missing!</b>\nUse: /post {movie_name} {poster_url}")

            movie_name, poster_url = full_query.rsplit(None, 1)
            search_msg = await message.reply_text(f"<b>Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ {movie_name}...</b>")

            files = await db.find_file(movie_name)
            if not files:
                return await search_msg.edit("<b>Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")

            # Group by resolution
            res_groups = {}
            for file in files:
                res = extract_quality(file['file_name'])
                if res not in res_groups:
                    res_groups[res] = []

                string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                base64_string = await encode(string)
                link = f"https://t.me/{client.username}?start={base64_string}"
                res_groups[res].append(link)

            # Caption and Buttons
            qualities = " + ".join(sorted(list(set(extract_quality(f['file_name']) for f in files))))
            years = extract_year([f['file_name'] for f in files])
            audios = extract_audio([f.get('caption') or f['file_name'] for f in files])
            genres = extract_genres([f.get('caption') or f['file_name'] for f in files])

            title = movie_name.upper()
            header = f"<b>{title} ({years}) {qualities} {audios}</b>"
            caption = (
                f"{header}\n\n"
                f"<b>⭐ TITLE: {title}\n"
                f"📺 YEAR: {years}\n"
                f"🎥 QUALITY: {qualities}\n"
                f"🎧 AUDIO: {audios}\n"
                f"📁 GENRES: {genres}\n\n"
                f"✨ Join Our Main Channel @Movies8777\n"
                f"━━━━━━━━━━━━━━━━━━━━━━</b>"
            )

            buttons = []
            all_res_buttons = []
            for res in sorted(res_groups.keys()):
                link = res_groups[res][0] # Pick one link per resolution
                all_res_buttons.append(InlineKeyboardButton(f"⚡ {res}", url=link))

            for i in range(0, len(all_res_buttons), 3):
                buttons.append(all_res_buttons[i:i+3])

            buttons.append([InlineKeyboardButton("🍿 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🍿", url=TUT_VID)])

            await client.send_photo(
                chat_id=POST_CHANNEL_ID if POST_CHANNEL_ID else message.chat.id,
                photo=poster_url,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await search_msg.delete()
            await message.reply_text("<b>✅ Movie Post Sent!</b>")

        except Exception as e:
            logger.error(f"Error in movie post: {e}")
            return await message.reply_text(f"<b>Error:</b> {e}")
