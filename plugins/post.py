import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import CHANNEL_ID, LOGGER, POST_CHANNEL_ID, TUT_VID, OPENAI_API_KEY
from helper_func import admin, encode
from database.database import db
from plugins.tmdb import search_tmdb, get_movie_details
from openai import AsyncOpenAI

logger = LOGGER(__name__)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# State storage for active sessions
post_sessions = {}

async def generate_ai_caption(details, files):
    file_info = "\n".join([f"- Name: {f['file_name']}, Caption: {f.get('caption', '')}" for f in files])
    title = details['title']
    release_date = details.get('release_date', 'N/A')

    prompt = f"""
Analyze the following movie/show details and file information to create a professional Telegram post caption.

Movie Title: {title}
Release Date: {release_date}

Files:
{file_info}

Format the output EXACTLY like this example:
[Movie Title] ([Year]) [Resolutions] [Audio Source] [Codecs] [Audio Tracks] [Subtitles]

Example:
Glass Onion: A Knives Out Mystery (2022) 720p + 1080p WEBRip x265 10bit HEVC Multi Audio [Hindi DDP 5.1 ~ 448Kbps / HE-AAC 2.0 ~ 128Kbps + English AAC 2.0] ESub

Also provide:
1. Combined Title Caption (A single line summarizing all qualities)
2. Individual Quality Titles (One for each unique resolution found)
3. Audio Tracks list

IMPORTANT: Extract technical details (DDP 5.1, AAC 2.0, x265, HEVC, 10bit, etc.) from the filenames provided. If details are missing, use best guesses based on common patterns.
"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional movie metadata extractor and Telegram post formatter."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return None

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

    backdrop_urls = details.get('backdrop_urls', [])
    if not backdrop_urls:
        # Ask admin for a link
        await search_msg.delete()
        ask = await message.chat.ask("<b>Nᴏ ɪᴍᴀɢᴇs ғᴏᴜɴᴅ ᴏɴ TMDB. Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴅɪʀᴇᴄᴛ ɪᴍᴀɢᴇ ʟɪɴᴋ:</b>", filters=filters.text)
        backdrop_urls = [ask.text]

    post_sessions[message.from_user.id] = {
        'details': details,
        'files': files,
        'images': backdrop_urls,
        'index': 0,
        'query': query
    }

    await show_image_selector(message, message.from_user.id)
    await search_msg.delete()

async def show_image_selector(message, user_id):
    session = post_sessions[user_id]
    images = session['images']
    index = session['index']
    total = len(images)
    url = images[index]
    details = session['details']

    caption = (
        f"<b>{details['title']} ({details['release_date'][:4] if details['release_date'] else 'N/A'})</b>\n\n"
        f"<b>• Type :</b> Clean Landscape\n"
        f"<b>• Language:</b> N/A\n"
        f"<b>• Width:</b> 2048, <b>Height:</b> 1152\n"
        f"<b>• [ <a href='{url}'>Click Here</a> ]</b>"
    )

    buttons = [
        [
            InlineKeyboardButton("<<", callback_data=f"post_img|{user_id}|first"),
            InlineKeyboardButton("<", callback_data=f"post_img|{user_id}|prev"),
            InlineKeyboardButton(f"{index + 1}/{total}", callback_data="none"),
            InlineKeyboardButton(">", callback_data=f"post_img|{user_id}|next"),
            InlineKeyboardButton(">>", callback_data=f"post_img|{user_id}|last"),
        ],
        [
            InlineKeyboardButton("Sᴇʟᴇᴄᴛ", callback_data=f"post_confirm|{user_id}"),
            InlineKeyboardButton("Cʟᴏsᴇ", callback_data=f"post_close|{user_id}")
        ]
    ]

    await message.reply_photo(
        photo=url,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex(r"^post_img\|"))
async def image_selector_callback(client: Bot, query: CallbackQuery):
    _, user_id, action = query.data.split("|")
    user_id = int(user_id)

    if query.from_user.id != user_id:
        return await query.answer("Nᴏᴛ ʏᴏᴜʀ sᴇssɪᴏɴ!", show_alert=True)

    session = post_sessions.get(user_id)
    if not session:
        return await query.answer("Sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ!", show_alert=True)

    images = session['images']
    index = session['index']
    total = len(images)

    if action == "first":
        index = 0
    elif action == "last":
        index = total - 1
    elif action == "prev":
        index = (index - 1) % total
    elif action == "next":
        index = (index + 1) % total

    session['index'] = index
    url = images[index]
    details = session['details']

    caption = (
        f"<b>{details['title']} ({details['release_date'][:4] if details['release_date'] else 'N/A'})</b>\n\n"
        f"<b>• Type :</b> Clean Landscape\n"
        f"<b>• Language:</b> N/A\n"
        f"<b>• Width:</b> 2048, <b>Height:</b> 1152\n"
        f"<b>• [ <a href='{url}'>Click Here</a> ]</b>"
    )

    buttons = [
        [
            InlineKeyboardButton("<<", callback_data=f"post_img|{user_id}|first"),
            InlineKeyboardButton("<", callback_data=f"post_img|{user_id}|prev"),
            InlineKeyboardButton(f"{index + 1}/{total}", callback_data="none"),
            InlineKeyboardButton(">", callback_data=f"post_img|{user_id}|next"),
            InlineKeyboardButton(">>", callback_data=f"post_img|{user_id}|last"),
        ],
        [
            InlineKeyboardButton("Sᴇʟᴇᴄᴛ", callback_data=f"post_confirm|{user_id}"),
            InlineKeyboardButton("Cʟᴏsᴇ", callback_data=f"post_close|{user_id}")
        ]
    ]

    try:
        from pyrogram.types import InputMediaPhoto
        await query.message.edit_media(
            media=InputMediaPhoto(url, caption=caption),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error updating image: {e}")
        await query.answer("Error updating image.")

@Bot.on_callback_query(filters.regex(r"^post_confirm\|"))
async def confirm_post_callback(client: Bot, query: CallbackQuery):
    user_id = int(query.data.split("|")[1])

    if query.from_user.id != user_id:
        return await query.answer("Nᴏᴛ ʏᴏᴜʀ sᴇssɪᴏɴ!", show_alert=True)

    session = post_sessions.get(user_id)
    if not session:
        return await query.answer("Sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ!", show_alert=True)

    await query.answer("Gᴇɴᴇʀᴀᴛɪɴɢ Cᴀᴘᴛɪᴏɴ ᴡɪᴛʜ AI...")
    await query.message.edit_caption("<b>⚡ Gᴇɴᴇʀᴀᴛɪɴɢ Cᴀᴘᴛɪᴏɴ ᴡɪᴛʜ AI... Pʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>")

    details = session['details']
    files = session['files']
    selected_image = session['images'][session['index']]

    ai_caption = await generate_ai_caption(details, files)
    if not ai_caption:
        ai_caption = f"<b>🎬 {details['title']} ({details.get('release_date', '')[:4]})</b>\n\n(AI Gᴇɴᴇʀᴀᴛɪᴏɴ Fᴀɪʟᴇᴅ)"

    # Resolution buttons logic (similar to before)
    res_groups = {}
    for file in files:
        file_name = file['file_name']
        res_match = re.search(r'(\d{3,4}p|4[kK])', file_name, re.IGNORECASE)
        res = res_match.group(1).upper() if res_match else "OTHERS"

        if res not in res_groups:
            res_groups[res] = []

        string = f"get-{file['msg_id'] * abs(client.db_channel.id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        res_groups[res].append((res, link))

    buttons = []
    all_buttons = []
    for res in sorted(res_groups.keys()):
        for res_label, link in res_groups[res]:
            all_buttons.append(InlineKeyboardButton(f"⚡ {res_label}", url=link))

    for i in range(0, len(all_buttons), 3):
        buttons.append(all_buttons[i:i+3])

    buttons.append([InlineKeyboardButton("🍿 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🍿", url=TUT_VID)])

    target_chat = POST_CHANNEL_ID if POST_CHANNEL_ID else query.message.chat.id

    try:
        await client.send_photo(
            chat_id=target_chat,
            photo=selected_image,
            caption=f"<b>{ai_caption}</b>"[:1024],
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await query.message.delete()
        await client.send_message(query.message.chat.id, "<b>✅ Pᴏsᴛ Sᴇɴᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>")
    except Exception as e:
        logger.error(f"Error sending post: {e}")
        await query.message.edit_caption(f"<b>❌ Eʀʀᴏʀ:</b> {e}")

    del post_sessions[user_id]

@Bot.on_callback_query(filters.regex(r"^post_close\|"))
async def close_post_callback(client: Bot, query: CallbackQuery):
    user_id = int(query.data.split("|")[1])
    if query.from_user.id == user_id:
        await query.message.delete()
        if user_id in post_sessions:
            del post_sessions[user_id]
    else:
        await query.answer("Nᴏᴛ ʏᴏᴜʀ sᴇssɪᴏɴ!", show_alert=True)
