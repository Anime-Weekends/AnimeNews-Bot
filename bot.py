import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import subprocess
import threading
import pymongo
import feedparser
from config import API_ID, API_HASH, BOT_TOKEN, URL_A, START_PIC, MONGO_URI

from webhook import start_webhook

from modules.rss.rss import news_feed_loop


mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["telegram_bot_db"]
user_settings_collection = db["user_settings"]
global_settings_collection = db["global_settings"]


app = Client("GenToolBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


webhook_thread = threading.Thread(target=start_webhook, daemon=True)
webhook_thread.start()


async def escape_markdown_v2(text: str) -> str:
    return text

async def send_message_to_user(chat_id: int, message: str, image_url: str = None):
    try:
        if image_url:
            await app.send_photo(
                chat_id, 
                image_url,
                caption=message,
            )
        else:
            await app.send_message(chat_id, message)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.on_message(filters.command("start"))
async def start(client, message):
    chat_id = message.chat.id
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Uᴘᴅᴀᴛᴇ", url="https://t.me/EmitingStars_Botz"),
            InlineKeyboardButton("Sᴜᴩᴩᴏʀᴛ", url="https://t.me/+HZuPVe0l-F1mM2Jl"),
        ],
        [
            InlineKeyboardButton("Dᴇᴠᴇʟᴏᴩᴇʀ", url="https://t.me/RexySama"),
        ],
    ])

    photo_url = START_PIC

    await app.send_photo(
        chat_id, 
        photo_url,
        caption=(
            f"**<blockquote>Hᴏɪ ᴘʀᴏ {message.from_user.first_name} !!!</blockquote>**\n"
            f"**<blockquote expandable>I ᴀᴍ ᴀɴ ᴀᴜᴛᴏ ᴀɴɪᴍᴇ ɴᴇᴡs ʙᴏᴛ ғᴇᴛᴄʜɪɴɢ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴀɴɪᴍᴇ ɴᴇᴡs ғʀᴏᴍ sᴇʟᴇᴄᴛᴇᴅ sɪᴛᴇs. sᴛᴀʏ ᴜᴘᴅᴀᴛᴇᴅ ᴡɪᴛʜ ɴᴇᴡ ʀᴇʟᴇᴀsᴇs, ɪɴᴅᴜsᴛʀʏ ᴛʀᴇɴᴅs, ᴀɴᴅ ᴍᴏʀᴇ ᴅᴇʟɪᴠᴇʀᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ !</blockquote>**\n"
            f"**<blockquote><a href="https://t.me/EmitingStars_Botz">Eᴍɪᴛɪɴɢ sᴛᴀʀs</a></blockquote>**"
        ),
        reply_markup=buttons
    )


@app.on_message(filters.command("news"))
async def connect_news(client, message):
    chat_id = message.chat.id
    if len(message.text.split()) == 1:
        await app.send_message(chat_id, "<blockquote>Mʏ ʟᴏʀᴅ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴏʀ ᴜsᴇʀɴᴀᴍᴇ (ᴡɪᴛʜᴏᴜᴛ @).</blockquote>")
        return

    channel = " ".join(message.text.split()[1:]).strip()
    global_settings_collection.update_one({"_id": "config"}, {"$set": {"news_channel": channel}}, upsert=True)
    await app.send_message(chat_id, f"<blockquote>Nᴇᴡs ᴄʜᴀɴɴᴇʟ sᴇᴛ ᴛᴏ : @{channel} ɴᴏᴡ ɪ ᴄᴀɴ ᴀʙʟᴇ ᴛᴏ ᴘᴏsᴛ ᴀɴɪᴍᴇ ɴᴇᴡs</blockquote>")

sent_news_entries = set()

async def main():
    await app.start()
    print("Bot is running...")
    asyncio.create_task(news_feed_loop(app, db, global_settings_collection, [URL_A]))
    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
