#(©)Codexbotz

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from bot import Bot
from helper_func import encode, get_message_id, admin, get_shortlink, wrap_with_redirect
from config import SHORTLINK_API, SHORTLINK_URL


@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return

        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        await first_message.reply("❌ Invalid DB Channel message.", quote=True)

    while True:
        try:
            second_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the Last Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post link",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return

        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        await second_message.reply("❌ Invalid DB Channel message.", quote=True)

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)

    tg_link = f"https://t.me/{client.username}?start={base64_string}"

    short_link = await get_shortlink(
        SHORTLINK_URL,
        SHORTLINK_API,
        tg_link
    )

    final_link = await wrap_with_redirect(short_link)

    await second_message.reply_text(
        f"<b>Here is your link</b>\n\n{final_link}",
        quote=True,
        disable_web_page_preview=True
    )


@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward Message from the DB Channel (with Quotes)..\n\nor Send the DB Channel Post link",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return

        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        await channel_message.reply("❌ Invalid DB Channel message.", quote=True)

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")

    tg_link = f"https://t.me/{client.username}?start={base64_string}"

    short_link = await get_shortlink(
        SHORTLINK_URL,
        SHORTLINK_API,
        tg_link
    )

    final_link = await wrap_with_redirect(short_link)

    await channel_message.reply_text(
        f"<b>Here is your link</b>\n\n{final_link}",
        quote=True,
        disable_web_page_preview=True
    )


@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)

    await message.reply(
        "Send all messages you want to include in batch.\n\nPress STOP when you're done.",
        reply_markup=STOP_KEYBOARD
    )

    while True:
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text="Waiting for files/messages...\nPress STOP to finish.",
                timeout=60
            )
        except:
            break

        if user_msg.text and user_msg.text.upper() == "STOP":
            break

        sent = await user_msg.copy(client.db_channel.id, disable_notification=True)
        collected.append(sent.id)

    await message.reply("✅ Batch collection complete.", reply_markup=ReplyKeyboardRemove())

    if not collected:
        await message.reply("❌ No messages were added to batch.")
        return

    string = f"get-{collected[0] * abs(client.db_channel.id)}-{collected[-1] * abs(client.db_channel.id)}"
    base64_string = await encode(string)

    tg_link = f"https://t.me/{client.username}?start={base64_string}"

    short_link = await get_shortlink(
        SHORTLINK_URL,
        SHORTLINK_API,
        tg_link
    )

    final_link = await wrap_with_redirect(short_link)

    await message.reply(
        f"<b>Here is your custom batch link:</b>\n\n{final_link}",
        disable_web_page_preview=True
    )
