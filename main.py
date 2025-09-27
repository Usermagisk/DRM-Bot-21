import os
import threading
import logging

from flask import Flask
from pyrogram import Client as AFK, idle
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from pyrogram import enums
from pyrogram.types import ChatMember
import tgcrypto
from pyromod import listen
from tglogging import TelegramLogHandler

# Config
class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8496276598:AAEHwjuuBq5MrRzKpOE7zqzfZcxq_IVBSPo")
    API_ID = int(os.environ.get("API_ID", "17640565"))
    API_HASH = os.environ.get("API_HASH", "ff67816c19a48aff1f86204ff61ce786")
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    SESSIONS = "./SESSIONS"

    AUTH_USERS = [int(i) for i in os.environ.get('AUTH_USERS', '7959404410').split(',')]
    GROUPS = [int(i) for i in os.environ.get('GROUPS', '-1002806996269').split(',')]
    LOG_CH = os.environ.get("LOG_CH", "-1003166167318")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        TelegramLogHandler(
            token=Config.BOT_TOKEN,
            log_chat_id=Config.LOG_CH,
            update_interval=2,
            minimum_lines=1,
            pending_logs=200000
        ),
        logging.StreamHandler()
    ]
)

LOGGER = logging.getLogger(__name__)
LOGGER.info("Live log streaming to Telegram enabled.")

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Pyrogram client
plugins = dict(root="plugins")
PRO = AFK(
    "AFK-DL",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=120,
    plugins=plugins,
    workdir=f"{Config.SESSIONS}/",
    workers=2,
)

if __name__ == "__main__":
    # ensure directories exist
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    os.makedirs(Config.SESSIONS, exist_ok=True)

    # start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    async def start_bot():
        await PRO.start()
        bot_info = await PRO.get_me()
        LOGGER.info(f"<--- @{bot_info.username} Started --->")

        chat_id = Config.GROUPS + Config.AUTH_USERS
        for i in chat_id:
            try:
                await PRO.send_message(chat_id=i, text="Bot Started! ♾ /pro ")
            except Exception as d:
                LOGGER.warning(d)
                continue

        await idle()  # wait until Ctrl+C or stop signal
        await PRO.stop()

    import asyncio
    asyncio.get_event_loop().run_until_complete(start_bot())
