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

import os
from os import environ,getenv
import logging
from logging.handlers import RotatingFileHandler

#rohit_1888 on Tg
#--------------------------------------------
#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
APP_ID = int(os.environ.get("APP_ID", "")) #Your API ID from my.telegram.org
API_HASH = os.environ.get("API_HASH", "") #Your API Hash from my.telegram.org
#--------------------------------------------

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003646933017")) #Your db channel Id
POST_CHANNEL_ID = int(os.environ.get("POST_CHANNEL_ID", "-1003524332911"))
OWNER = os.environ.get("OWNER", "♚𝖧υηтєʀ⚰️") # Owner username without @
OWNER_ID = int(os.environ.get("OWNER_ID", "8435672368")) # Owner id
ONGOING_CHANNEL_ID = int(os.environ.get("ONGOING_CHANNEL_ID", "-1002096101886"))
#--------------------------------------------
PORT = os.environ.get("PORT", "8001")
#--------------------------------------------
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://hosoy42933:cgAc2eQk22JieEWn@cluster0.hb9xzjp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "ad_database")
#--------------------------------------------
FSUB_LINK_EXPIRY = int(os.getenv("FSUB_LINK_EXPIRY", "120"))  # 0 means no expiry
BAN_SUPPORT = os.environ.get("BAN_SUPPORT", "https://t.me/Spicylinebun")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "200"))
#--------------------------------------------
START_PIC = os.environ.get("START_PIC", "https://i.postimg.cc/4yCmP76g/chdyt.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://i.postimg.cc/mkwB9tVr/hmhg.jpg")

#--------------------------------------------
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 43200)) # Add time in seconds
TUT_VID = os.environ.get("TUT_VID","https://t.me/HowToVerifyy")

#--------------------------------------------
REDIRECT_DOMAIN = os.environ.get("REDIRECT_DOMAIN","https://urlmsk.onrender.com")
#--------------------------------------------
HELP_TXT = "<b><blockquote>ᴛʜɪs ɪs ᴀɴ ғɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @Spicylinebun\n\n❏ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs\n├/start : sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n├/about : ᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ\n└/help : ʜᴇʟᴘ ʀᴇʟᴀᴛᴇᴅ ʙᴏᴛ\n\n sɪᴍᴘʟʏ ᴄʟɪᴄᴋ ᴏɴ ʟɪɴᴋ ᴀɴᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜᴀᴛs ɪᴛ.....!\n\n ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ <a href=https://t.me/Spicylinebun>𝖣𝖾𝖺𝗍𝗁</a></blockquote></b>"
ABOUT_TXT = "<b><blockquote>◈ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/Spicylinebun>𝖫𝗈𝗌𝗍</a>\n◈ ꜰᴏᴜɴᴅᴇʀ ᴏꜰ : <a href=https://t.me/+otXaE3-eu7MzNjU9>𝖫𝗈𝗌𝗍 ɴᴇᴛᴡᴏʀᴋ</a>\n◈ нєηαтєє ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/+1epnsIzoCx43YTk1>нєηαтєє</a>\n◈ sᴇʀɪᴇs ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/+Pf6-2PAsrAczMzQ1>ᴡᴇʙsᴇʀɪᴇs</a>\n◈ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href=https://t.me/Goathunterr>♚𝖧υηтєʀ⚰️ </a></blockquote></b>"
#--------------------------------------------
#--------------------------------------------
START_MSG = os.environ.get("START_MESSAGE", "<b>ʜᴇʟʟᴏ {first}\n\n<blockquote> ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</blockquote></b>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b><blockquote>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b></blockquote>")

CMD_TXT_1 = """<blockquote><b>» ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ:</b></blockquote>

<b>› /stats :</b> sᴛᴀᴛs ᴀɴᴅ ɪɴᴅᴇx ɪɴғᴏ
<b>› /dbroadcast :</b> sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ
<b>› /pbroadcast :</b> sᴇɴᴅ ᴘʜᴏᴛᴏ ᴛᴏ ᴀʟʟ
<b>› /ban :</b> ʙᴀɴ ᴀ ᴜsᴇʀ
<b>› /unban :</b> ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ
<b>› /banlist :</b> ʟɪsᴛ ᴏғ ʙᴀɴɴᴇᴅ ᴜsᴇʀs
<b>› /addchnl :</b> ᴀᴅᴅ ғsᴜʙ ᴄʜᴀɴɴᴇʟ
<b>› /delchnl :</b> ʀᴇᴍᴏᴠᴇ ғsᴜʙ ᴄʜᴀɴɴᴇʟ
<b>› /listchnl :</b> ᴠɪᴇᴡ ғsᴜʙ ᴄʜᴀɴɴᴇʟs
<b>› /fsub_mode :</b> ᴛᴏɢɢʟᴇ ғsᴜʙ ᴍᴏᴅᴇ
<b>› /add_admin :</b> ᴀᴅᴅ ᴀ ɴᴇᴡ ᴀᴅᴍɪɴ
<b>› /deladmin :</b> ʀᴇᴍᴏᴠᴇ ᴀɴ ᴀᴅᴍɪɴ
<b>› /admins :</b> ʟɪsᴛ ᴏғ ᴀʟʟ ᴀᴅᴍɪɴs
<b>› /addpremium :</b> ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ
<b>› /premium_users :</b> ʟɪsᴛ ᴏғ ᴘʀᴇᴍɪᴜᴍs
<b>› /remove_premium :</b> ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ
<b>› /count :</b> ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴄᴏᴜɴᴛ
<b>› /delreq :</b> ᴄʟᴇᴀɴ ᴜɴ-ʀᴇǫ ᴜsᴇʀs
"""

CMD_TXT_2 = """<blockquote><b>» ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ:</b></blockquote>

<b>› /index :</b> ʙᴜʟᴋ ɪɴᴅᴇx ᴄʜᴀɴɴᴇʟ
<b>› /genlink :</b> ʀᴇᴘʟʏ ᴛᴏ ɢᴇɴ ʟɪɴᴋ
<b>› /batch :</b> ɢᴇɴᴇʀᴀᴛᴇ ʙᴀᴛᴄʜ ʟɪɴᴋ
<b>› /dlt_time :</b> sᴇᴛ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>› /add_ongoing :</b> ᴀᴅᴅ ᴏɴɢᴏɪɴɢ sᴇʀɪᴇs
<b>› /ongoing :</b> ᴍᴀɴᴀɢᴇ ᴏɴɢᴏɪɴɢ
<b>› /del_ongoing :</b> ʀᴇᴍᴏᴠᴇ ᴏɴɢᴏɪɴɢ
<b>› /post :</b> ғᴏʀᴍᴀᴛᴛᴇᴅ ᴍᴏᴠɪᴇ/sᴇʀɪᴇs
<b>› /file_details :</b> ᴄʜᴇᴄᴋ ғɪʟᴇ ɪɴ ᴅʙ
<b>› /del_index :</b> ᴅᴇʟᴇᴛᴇ ɪɴᴅᴇxᴇᴅ ғɪʟᴇs
"""
#--------------------------------------------
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>• ʙʏ @Spicylinebun</b>") #set your Custom Caption here, Keep None for Disable Custom Caption
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False #set True if you want to prevent users from forwarding files from bot
#--------------------------------------------
#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", True) == 'True'
#--------------------------------------------
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

#==========================(BUY PREMIUM)====================#

OWNER_TAG = os.environ.get("OWNER_TAG", "𝖫𝗈𝗌𝗍")
UPI_ID = os.environ.get("UPI_ID", "")
QR_PIC = os.environ.get("QR_PIC", "https://image2url.com/images/1765293368028-10fbfce0-7b20-456f-b9eb-cc09ea0fdb22.jpg")
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", f"t.me/Goathunterr")
#--------------------------------------------
#Time and its price
#7 Days
PRICE1 = os.environ.get("PRICE1", "30 rs")
#1 Month
PRICE2 = os.environ.get("PRICE2", "80 rs")
#3 Month
PRICE3 = os.environ.get("PRICE3", "210 rs")
#6 Month
PRICE4 = os.environ.get("PRICE4", "300 rs")
#1 Year
PRICE5 = os.environ.get("PRICE5", "530 rs")

#===================(END)========================#

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
