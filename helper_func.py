#(©)CodeFlix_Bots
#rohit_1888 on Tg #Dont remove this line

import base64
import re
import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, MessageOriginType
from config import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from shortzy import Shortzy
from pyrogram.errors import FloodWait
from database.database import *



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

#used for cheking if a user is admin ~Owner also treated as admin level
async def is_admin(user_id: int):
    try:
        return any([user_id == OWNER_ID, await db.admin_exist(user_id)])
    except Exception as e:
        print(f"! Exception in is_admin: {e}")
        return False

async def check_admin(filter, client, update):
    if not update.from_user:
        return False
    return await is_admin(update.from_user.id)


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

async def is_subscribed(client, user_id):
    channel_ids = await db.show_channels()

    if not channel_ids:
        return True

    if user_id == OWNER_ID:
        return True

    for cid in channel_ids:
        if not await is_sub(client, user_id, cid):
            # Retry once if join request might be processing
            mode = await db.get_channel_mode(cid)
            if mode == "on":
                await asyncio.sleep(2)  # give time for @on_chat_join_request to process
                if await is_sub(client, user_id, cid):
                    continue
            return False

    return True


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

async def is_sub(client, user_id, channel_id):
    try:
        member = await client.get_chat_member(channel_id, user_id)
        status = member.status
        #print(f"[SUB] User {user_id} in {channel_id} with status {status}")
        return status in {
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER
        }

    except UserNotParticipant:
        mode = await db.get_channel_mode(channel_id)
        if mode == "on":
            exists = await db.req_user_exist(channel_id, user_id)
            #print(f"[REQ] User {user_id} join request for {channel_id}: {exists}")
            return exists
        #print(f"[NOT SUB] User {user_id} not in {channel_id} and mode != on")
        return False

    except Exception as e:
        print(f"[!] Error in is_sub(): {e}")
        return False

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


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_origin:
        if message.forward_origin.type == MessageOriginType.CHANNEL:
            if message.forward_origin.chat.id == client.db_channel.id:
                return message.forward_origin.message_id
        return 0
    elif message.text:
        # Handles:
        # https://t.me/c/123456789/10
        # https://t.me/username/10
        # https://t.me/c/123456789/10?single
        pattern = r"https://t.me/(?:c/)?([^/?\s]+)/(\d+)"
        matches = re.search(pattern, message.text)
        if not matches:
            return 0

        channel_id = matches.group(1)
        msg_id = int(matches.group(2))

        if channel_id.isdigit():
            # Private channel ID in link is usually without -100 prefix
            full_channel_id = f"-100{channel_id}"
            if full_channel_id == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id

        # Also check if it's the exact database channel ID if it was provided directly
        if str(channel_id) == str(client.db_channel.id).replace("-100", ""):
            return msg_id

    return 0


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time


def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)} {period_name}'
    return result

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


async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

async def subscribed_filter(filter, client, update):
    if not update.from_user:
        return False
    return await is_subscribed(client, update.from_user.id)

subscribed = filters.create(subscribed_filter)
admin = filters.create(check_admin)

async def wrap_with_redirect(short_url):
    encoded = await encode(short_url)
    return f"{REDIRECT_DOMAIN}/?r={encoded}"

def clean_title(title):
    # Strip Telegram handles (e.g., @Codeflix_Bots)
    title = re.sub(r'@\w+', '', title)

    # Strip common quality, codec, and release tags
    tags = [
        r'\d{3,4}p', r'\d[kK]', r'x26[45]', r'HEVC', r'10bit', r'HDR(?:ip)?',
        r'Bluray', r'Blu-ray', r'WEB-DL', r'Webrip', r'WEBDL', r'DVDRip', r'BDRip', r'BRRip',
        r'Dual Audio', r'Multi-Audio', r'Multi', r'Hindi', r'English', r'ESub', r'MSub',
        r'HDCAM', r'S-Print', r'Pre-DVDRip', r'TS', r'HC', r'WEB', r'HDTV', r'60fps'
    ]
    for tag in tags:
        title = re.sub(rf'\b{tag}\b', '', title, flags=re.IGNORECASE)

    # Strip year (19xx or 20xx)
    title = re.sub(r'\(?(19|20)\d{2}\)?', '', title)

    # Strip season/episode tags (S01, E01, EP01, Season 1, Episode 1)
    title = re.sub(r'(S\d+|E\d+|EP\d+|Season\s?\d+|Episode\s?\d+|ESub|MSub)', '', title, flags=re.IGNORECASE)

    # Strip brackets and parentheses and their contents (e.g., [Dual Audio])
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title)

    # Remove common separators and extra whitespace
    title = re.sub(r'[|.\-_:]', ' ', title)
    # Remove single characters left over (like 's' from 'Season')
    title = re.sub(r'\b[a-zA-Z]\b', '', title)
    # Remove common file extensions
    title = re.sub(r'\b(mkv|mp4|avi|srt)\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+', ' ', title).strip()

    return title


#rohit_1888 on Tg :

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
