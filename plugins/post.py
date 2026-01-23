import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import LOGGER, POST_CHANNEL_ID, TUT_VID
from helper_func import admin, encode, clean_title
from database.database import db

logger = LOGGER(__name__)

def extract_quality(file_names):
    qualities = set()
    for name in file_names:
        # Improved resolution regex
        res_match = re.search(r'(\d{3,4}p|4[kK]|2[kK])', name, re.IGNORECASE)
        # Improved source regex
        source_patterns = r'(Bluray|Blu-ray|WEB-DL|Web-DL|WEBDL|Webrip|Web-Rip|Webrip|HDRip|DVDRip|BDRip|BRRip|WEB|HDTV|HDCAM|S-Print|Pre-DVDRip|TS|HC)'
        source_match = re.search(source_patterns, name, re.IGNORECASE)

        res = res_match.group(1).lower() if res_match else ""
        source = source_match.group(1).upper() if source_match else ""

        # Standardize source names
        if source:
            if source in ["WEBRIP", "WEB-RIP", "WEB-DL", "WEBDL", "WEB DL", "WEB"]:
                source = "" # Remove WEB-DL and variants as requested
            elif source in ["BLURAY", "BLU-RAY"]: source = "BluRay"
            elif source in ["BRRIP", "BDRIP"]: source = "BRRip"
            elif source in ["HDRIP"]: source = "HDRip"
            elif source in ["DVDRIP"]: source = "DVDRip"

        q_str = f"{res} {source}".strip()
        if q_str:
            qualities.add(q_str)

    if not qualities:
        return None

    # Sort qualities primarily by resolution
    def q_sort(q):
        res_match = re.search(r'(\d{3,4})', q)
        return int(res_match.group(1)) if res_match else 0

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
    langs = set()
    subs = set()

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
        'Dual': r'Dual'
    }

    sub_patterns = {
        'ESubs': r'ESub|Subtitle',
        'MSubs': r'MSub'
    }

    for name in file_names:
        for label, pattern in patterns.items():
            if re.search(pattern, name, re.IGNORECASE):
                langs.add(label)
        for label, pattern in sub_patterns.items():
            if re.search(pattern, name, re.IGNORECASE):
                subs.add(label)

    if not langs and not subs:
        return None

    res = []
    if langs:
        # Sort languages but keep Hindi first if possible or just alphabetical
        sorted_langs = sorted(list(langs))
        if 'Hindi' in sorted_langs:
            sorted_langs.remove('Hindi')
            sorted_langs.insert(0, 'Hindi')
        res.extend(sorted_langs)

    if subs:
        res.extend(sorted(list(subs)))

    return " - ".join(res)

@Bot.on_message(filters.command("post") & admin)
async def post_command(client: Bot, message: Message):
    # Usage check
    # Movie: /post {movie_name} {poster_url}
    # Series: /post {series_name} S01 E01 to E08 {poster_url}

    cmd_text = message.text.split(None, 1)
    if len(cmd_text) < 2:
        return await message.reply_text("<b>Usage:</b>\n\n<b>Movie:</b> /post {movie_name} {poster_url}\n<b>Series:</b> /post {series_name} S01 E01 to E08 {poster_url}")

    full_query = cmd_text[1]

    # Check if it's a series (contains "S\d+ E\d+ to E\d+")
    series_match = re.search(r'(.+?)\s+(S\d+)\s+(E\d+)\s+to\s+(E\d+)\s+(.+)', full_query, re.IGNORECASE)

    if series_match:
        try:
            series_name = series_match.group(1).strip()
            season_tag = series_match.group(2).upper()
            start_ep_tag = series_match.group(3).upper()
            end_ep_tag = series_match.group(4).upper()
            poster_url = series_match.group(5).strip()

            start_ep = int(start_ep_tag[1:])
            end_ep = int(end_ep_tag[1:])

            if start_ep > end_ep:
                return await message.reply_text("<b>Start episode cannot be greater than end episode!</b>")

            search_msg = await message.reply_text(f"<b>Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ {series_name} {season_tag} {start_ep_tag}-{end_ep_tag}...</b>")

            # Find files
            all_files = []
            for ep_num in range(start_ep, end_ep + 1):
                ep_tag = f"E{ep_num:02d}"
                files = await db.find_file(f"{series_name} {season_tag} {ep_tag}")
                all_files.extend(files)

            if not all_files:
                return await search_msg.edit("<b>Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")

            # Grouping files by episode and quality
            res_groups = {} # {Quality: [file_objects]}
            ep_res_groups = {} # {Ep: {Quality: [link]}}

            for file in all_files:
                file_name = file['file_name']
                ep_match = re.search(r'E(\d{2,3})', file_name, re.IGNORECASE)
                if not ep_match: continue
                ep_val = f"E{int(ep_match.group(1)):02d}"

                if ep_val not in ep_res_groups:
                    ep_res_groups[ep_val] = {}

                # Extract quality for this specific file
                res_m = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
                src_m = re.search(r'(Bluray|WEB-DL|Webrip|HDRip|DVDRip|BDRip|WEB)', file_name, re.IGNORECASE)

                res = res_m.group(1).lower() if res_m else ""
                src = src_m.group(1).upper() if src_m else ""
                if src in ["WEB-DL", "WEBDL", "WEB", "WEBRIP"]:
                    src = ""
                label = f"{res} {src}".strip() or "HDR"

                if label not in ep_res_groups[ep_val]:
                    ep_res_groups[ep_val][label] = []

                if label not in res_groups:
                    res_groups[label] = []
                res_groups[label].append(file)

                string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                base64_string = await encode(string)
                link = f"https://t.me/{client.username}?start={base64_string}"
                ep_res_groups[ep_val][label].append(link)

            # Metadata extraction
            all_metadata_sources = [f['file_name'] for f in all_files] + [f.get('caption', '') for f in all_files]
            qualities = extract_quality(all_metadata_sources)
            years = extract_year(all_metadata_sources)
            audios = extract_audio(all_metadata_sources)

            # Caption Construction
            caption = f"<b>📼 Series: {clean_title(series_name)} {season_tag}\n"
            caption += f"🔢 Episode: {start_ep_tag} to {end_ep_tag}\n"
            if years:
                caption += f"📅 Year: {years}\n"
            if qualities:
                caption += f"🎥 Quality: {qualities}\n"
            if audios:
                caption += f"🔊 Audio: {audios}\n"

            caption += "</b>"

            buttons = []
            if len(ep_res_groups) > 1:
                # Multiple items: Show quality buttons
                def q_sort(q):
                    res_match = re.search(r'(\d{3,4})', q)
                    return int(res_match.group(1)) if res_match else 0

                batch_res_buttons = []
                for res in sorted(res_groups.keys(), key=q_sort):
                    res_files = res_groups[res]
                    msg_ids = [f['msg_id'] for f in res_files]
                    first_id = min(msg_ids)
                    last_id = max(msg_ids)

                    batch_string = f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}"
                    batch_base64 = await encode(batch_string)
                    batch_link = f"https://t.me/{client.username}?start={batch_base64}"
                    batch_res_buttons.append(InlineKeyboardButton(f"{res.upper()}", url=batch_link))

                for i in range(0, len(batch_res_buttons), 3):
                    buttons.append(batch_res_buttons[i:i+3])
            else:
                # Single item: show normal buttons
                for ep in sorted(ep_res_groups.keys()):
                    tag_buttons = []
                    for res in sorted(ep_res_groups[ep].keys()):
                        link = ep_res_groups[ep][res][0]
                        tag_buttons.append(InlineKeyboardButton(f"{ep} {res.upper()}", url=link))
                    for i in range(0, len(tag_buttons), 3):
                        buttons.append(tag_buttons[i:i+3])


            buttons.append([InlineKeyboardButton("Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ", url=TUT_VID)])

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
        # Fallback to old series format or Movie
        # Old Series format: {name} S01 to S03 {link}
        old_series_match = re.search(r'(.+?)\s+(S\d+)\s+to\s+(S\d+)\s+(.+)', full_query, re.IGNORECASE)

        if old_series_match:
            try:
                series_name = old_series_match.group(1).strip()
                start_str = old_series_match.group(2).upper()
                end_str = old_series_match.group(3).upper()
                poster_url = old_series_match.group(4).strip()

                start_val = int(start_str[1:])
                end_val = int(end_str[1:])

                search_msg = await message.reply_text(f"<b>Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ {series_name} {start_str}-{end_str}...</b>")

                all_files = []
                for val in range(start_val, end_val + 1):
                    tag = f"S{val:02d}"
                    files = await db.find_file(f"{series_name} {tag}")
                    all_files.extend(files)

                if not all_files:
                    return await search_msg.edit("<b>Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")

                res_groups = {}
                ep_res_groups = {}

                for file in all_files:
                    file_name = file['file_name']
                    tag_match = re.search(r'S(\d{2})', file_name, re.IGNORECASE)
                    if not tag_match: continue
                    tag_val = f"S{int(tag_match.group(1)):02d}"

                    if tag_val not in ep_res_groups:
                        ep_res_groups[tag_val] = {}

                    res_m = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
                    src_m = re.search(r'(Bluray|WEB-DL|Webrip|HDRip|DVDRip|BDRip|WEB)', file_name, re.IGNORECASE)

                    res = res_m.group(1).lower() if res_m else ""
                    src = src_m.group(1).upper() if src_m else ""
                    if src in ["WEB-DL", "WEBDL", "WEB", "WEBRIP"]:
                        src = ""
                    label = f"{res} {src}".strip() or "HDR"

                    if label not in ep_res_groups[tag_val]:
                        ep_res_groups[tag_val][label] = []

                    if label not in res_groups:
                        res_groups[label] = []
                    res_groups[label].append(file)

                    string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                    base64_string = await encode(string)
                    link = f"https://t.me/{client.username}?start={base64_string}"
                    ep_res_groups[tag_val][label].append(link)

                all_metadata_sources = [f['file_name'] for f in all_files] + [f.get('caption', '') for f in all_files]
                qualities = extract_quality(all_metadata_sources)
                years = extract_year(all_metadata_sources)
                audios = extract_audio(all_metadata_sources)

                season_info = f"{start_str} - {end_str}" if start_str != end_str else start_str
                caption = f"<b>📼 Series: {clean_title(series_name)} {season_info}\n"
                if years:
                    caption += f"📅 Year: {years}\n"
                if qualities:
                    caption += f"🎥 Quality: {qualities}\n"
                if audios:
                    caption += f"🔊 Audio: {audios}\n"
                caption += "</b>"

                buttons = []
                def q_sort(q):
                    res_match = re.search(r'(\d{3,4})', q)
                    return int(res_match.group(1)) if res_match else 0

                batch_res_buttons = []
                for res in sorted(res_groups.keys(), key=q_sort):
                    res_files = res_groups[res]
                    msg_ids = [f['msg_id'] for f in res_files]
                    first_id = min(msg_ids)
                    last_id = max(msg_ids)

                    batch_string = f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}"
                    batch_base64 = await encode(batch_string)
                    batch_link = f"https://t.me/{client.username}?start={batch_base64}"
                    batch_res_buttons.append(InlineKeyboardButton(f"{res.upper()}", url=batch_link))

                for i in range(0, len(batch_res_buttons), 3):
                    buttons.append(batch_res_buttons[i:i+3])


                buttons.append([InlineKeyboardButton("Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ", url=TUT_VID)])

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

                res_groups = {}
                for file in files:
                    res_match = re.search(r'(\d{3,4}p|4[kK])', file['file_name'], re.IGNORECASE)
                    src_m = re.search(r'(Bluray|WEB-DL|Webrip|HDRip|DVDRip|BDRip|WEB)', file['file_name'], re.IGNORECASE)

                    res = res_match.group(1).lower() if res_match else ""
                    src = src_m.group(1).upper() if src_m else ""
                    if src in ["WEB-DL", "WEBDL", "WEB", "WEBRIP"]:
                        src = ""
                    label = f"{res} {src}".strip() or "HDR"

                    if label not in res_groups:
                        res_groups[label] = []

                    string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
                    base64_string = await encode(string)
                    link = f"https://t.me/{client.username}?start={base64_string}"
                    res_groups[label].append(link)

                all_metadata_sources = [f['file_name'] for f in files] + [f.get('caption', '') for f in files]
                qualities = extract_quality(all_metadata_sources)
                years = extract_year(all_metadata_sources)
                audios = extract_audio(all_metadata_sources)

                caption = f"<b>📼 Movie: {clean_title(movie_name)}\n"
                if years:
                    caption += f"📅 Year: {years}\n"
                if qualities:
                    caption += f"🎥 Quality: {qualities}\n"
                if audios:
                    caption += f"🔊 Audio: {audios}\n"
                caption += "</b>"

                buttons = []
                def q_sort(q):
                    res_match = re.search(r'(\d{3,4})', q)
                    return int(res_match.group(1)) if res_match else 0

                all_res_buttons = []
                for res in sorted(res_groups.keys(), key=q_sort):
                    link = res_groups[res][0]
                    all_res_buttons.append(InlineKeyboardButton(f"{res.upper()}", url=link))

                for i in range(0, len(all_res_buttons), 3):
                    buttons.append(all_res_buttons[i:i+3])

                buttons.append([InlineKeyboardButton("Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ", url=TUT_VID)])

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
