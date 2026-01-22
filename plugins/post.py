import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import LOGGER, POST_CHANNEL_ID, TUT_VID
from helper_func import admin, encode
from database.database import db

logger = LOGGER(__name__)

def extract_quality(file_names):
    qualities = set()
    for name in file_names:
        res_match = re.search(r'(\d{3,4}p|4[kK])', name, re.IGNORECASE)
        if res_match:
            qualities.add(res_match.group(1).lower())

    if not qualities:
        return None

    # Sort qualities (480p, 720p, 1080p, 4k)
    def q_sort(q):
        val = re.sub(r'p|k', '', q, flags=re.I)
        return int(val) if val.isdigit() else 0

    sorted_q = sorted(list(qualities), key=q_sort)
    return " - ".join(sorted_q)

def extract_year(file_names):
    years = set()
    for name in file_names:
        match = re.search(r'(19|20)\d{2}', name)
        if match:
            years.add(int(match.group()))
    if not years:
        return None
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
        return None

    # Priority sorting or just alphabetical
    res = sorted(list(audios))
    return " ".join(res)

@Bot.on_message(filters.command("post") & admin)
async def post_command(client: Bot, message: Message):
    # Usage check
    # /post {movie_name} {poster_url}
    # /post {series_name} E01 to E06 {poster_url}
    # /post {series_name} S01 to S03 {poster_url}

    cmd_text = message.text.split(None, 1)
    if len(cmd_text) < 2:
        return await message.reply_text("<b>Usage:</b>\n\n<b>Movie:</b> /post {movie_name} {poster_url}\n<b>Series:</b> /post {series_name} E01 to E06 {poster_url}")

    full_query = cmd_text[1]

    # Check if it's a series (contains " to ")
    is_series = " to " in full_query.lower() and re.search(r'[ES]\d+', full_query, re.IGNORECASE)

    if is_series:
        try:
            # Match E01 to E06 or S01 to S03
            match = re.search(r'(.+?)\s+([ES]\d+)\s+to\s+([ES]\d+)\s+(.+)', full_query, re.IGNORECASE)
            if not match:
                return await message.reply_text("<b>Invalid series format!</b>\nUse: /post {series_name} E01 to E06 {poster_url}")

            series_name = match.group(1).strip()
            start_str = match.group(2).upper()
            end_str = match.group(3).upper()
            poster_url = match.group(4).strip()

            is_season = start_str.startswith('S')
            prefix = 'S' if is_season else 'E'

            start_val = int(start_str[1:])
            end_val = int(end_str[1:])

            if start_val > end_val:
                return await message.reply_text("<b>Start value cannot be greater than end value!</b>")

            search_msg = await message.reply_text(f"<b>Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ {series_name} {start_str}-{end_str}...</b>")

            # Find files
            all_files = []
            for val in range(start_val, end_val + 1):
                tag = f"{prefix}{val:02d}"
                files = await db.find_file(f"{series_name} {tag}")
                all_files.extend(files)

            if not all_files:
                return await search_msg.edit("<b>Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")

            # Grouping files by episode/season and resolution
            res_groups = {} # {Resolution: [file_objects]}
            ep_res_groups = {} # {Ep/Season: {Res: [link]}}

            for file in all_files:
                file_name = file['file_name']
                tag_match = re.search(rf'{prefix}(\d{{2,3}})', file_name, re.IGNORECASE)
                if not tag_match: continue
                tag_val = f"{prefix}{int(tag_match.group(1)):02d}"

                if tag_val not in ep_res_groups:
                    ep_res_groups[tag_val] = {}

                # Extract quality for this specific file
                res = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
                res = res.group(1).lower() if res else "hdr"

                if res not in ep_res_groups[tag_val]:
                    ep_res_groups[tag_val][res] = []

                if res not in res_groups:
                    res_groups[res] = []
                res_groups[res].append(file)

                string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                base64_string = await encode(string)
                link = f"https://t.me/{client.username}?start={base64_string}"
                ep_res_groups[tag_val][res].append(link)

            # Metadata extraction
            all_metadata_sources = [f.get('caption') or f['file_name'] for f in all_files]
            qualities = extract_quality(all_metadata_sources)
            years = extract_year(all_metadata_sources)
            audios = extract_audio(all_metadata_sources)

            # Caption Construction
            if start_str == end_str:
                season_info = start_str
            else:
                season_info = f"{start_str} - {end_str}"

            caption = f"<b>📼 Series: {series_name} {season_info}\n"
            if years:
                caption += f"📅 Year: {years}\n"
            if qualities:
                caption += f"🎥 Quality: {qualities} COMBiNED\n"
            if audios:
                caption += f"🔊 Audio: {audios}\n"

            caption += (
                f"\n✨ Join Our Main Channel @Movies8777\n"
                f"━━━━━━━━━━━━━━━━━━━━━━</b>"
            )

            buttons = []
            if len(ep_res_groups) > 1:
                # Multiple items: Show resolution buttons
                def q_sort(q):
                    val = re.sub(r'p|k', '', q, flags=re.I)
                    return int(val) if val.isdigit() else 0

                batch_res_buttons = []
                for res in sorted(res_groups.keys(), key=q_sort):
                    res_files = res_groups[res]
                    msg_ids = [f['msg_id'] for f in res_files]
                    first_id = min(msg_ids)
                    last_id = max(msg_ids)

                    batch_string = f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}"
                    batch_base64 = await encode(batch_string)
                    batch_link = f"https://t.me/{client.username}?start={batch_base64}"
                    batch_res_buttons.append(InlineKeyboardButton(f"⚡ {res.upper()}", url=batch_link))

                for i in range(0, len(batch_res_buttons), 3):
                    buttons.append(batch_res_buttons[i:i+3])
            else:
                # Single item: show normal buttons
                for tag in sorted(ep_res_groups.keys()):
                    tag_buttons = []
                    for res in sorted(ep_res_groups[tag].keys()):
                        link = ep_res_groups[tag][res][0]
                        tag_buttons.append(InlineKeyboardButton(f"{tag} {res.upper()}", url=link))
                    for i in range(0, len(tag_buttons), 3):
                        buttons.append(tag_buttons[i:i+3])

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
                res_match = re.search(r'(\d{3,4}p|4[kK])', file['file_name'], re.IGNORECASE)
                res = res_match.group(1).lower() if res_match else "hdr"
                if res not in res_groups:
                    res_groups[res] = []

                string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                base64_string = await encode(string)
                link = f"https://t.me/{client.username}?start={base64_string}"
                res_groups[res].append(link)

            # Metadata extraction
            all_metadata_sources = [f.get('caption') or f['file_name'] for f in files]
            qualities = extract_quality(all_metadata_sources)
            years = extract_year(all_metadata_sources)
            audios = extract_audio(all_metadata_sources)

            caption = f"<b>📼 Movie: {movie_name}\n"
            if years:
                caption += f"📅 Year: {years}\n"
            if qualities:
                caption += f"🎥 Quality: {qualities} COMBiNED\n"
            if audios:
                caption += f"🔊 Audio: {audios}\n"

            caption += (
                f"\n✨ Join Our Main Channel @Movies8777\n"
                f"━━━━━━━━━━━━━━━━━━━━━━</b>"
            )

            buttons = []
            def q_sort(q):
                val = re.sub(r'p|k', '', q, flags=re.I)
                return int(val) if val.isdigit() else 0

            all_res_buttons = []
            for res in sorted(res_groups.keys(), key=q_sort):
                link = res_groups[res][0]
                all_res_buttons.append(InlineKeyboardButton(f"⚡ {res.upper()}", url=link))

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
