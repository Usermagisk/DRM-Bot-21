import os
import threading
import asyncio
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

    AUTH_USERS = os.environ.get('AUTH_USERS', '7959404410').split(',')
    for i in range(len(AUTH_USERS)):
        AUTH_USERS[i] = int(AUTH_USERS[i])

    GROUPS = os.environ.get('GROUPS', '-1002806996269').split(',')
    for i in range(len(GROUPS)):
        GROUPS[i] = int(GROUPS[i])

    LOG_CH = os.environ.get("LOG_CH", "-1003166167318")

# Logging — use name
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
LOGGER.info("live log streaming to telegram.")

# Store (unchanged)
class Store(object):
    CPTOKEN = "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9..."
    SPROUT_URL = "https://discuss.oliveboard.in/"
    ADDA_TOKEN = ""
    THUMB_URL = "https://telegra.ph/file/84870d6d89b893e59c5f0.jpg"

# Format messages (unchanged)
class Msg(object):
    START_MSG = "/pro"
    TXT_MSG = "Hey <b>{user},\n\nI'm Multi-Talented Robot. I Can Download Many Type of Links.\n\nSend a TXT or HTML file :-</b>"
    ERROR_MSG = "<b>DL Failed ({no_of_files}) :-</b> \n\n<b>Name: </b>{file_name},\n<b>Link:</b> {file_link}\n\n<b>Error:</b> {error}"
    SHOW_MSG = "<b>Downloading :- \n{file_name}\n\nLink :- {file_link}</b>"
    CMD_MSG_1 = "{txt}\n\nTotal Links in File are :- {no_of_links}\n\nSend any Index From [ 1 - {no_of_links} ] :-"
    CMD_MSG_2 = "<b>Uploading :- </b> {file_name}"
    RESTART_MSG = "✅ HI Bhai log\n✅ PATH CLEARED"

# Prefixes and plugins
prefixes = ["/", "~", "?", "!", "."]
plugins = dict(root="plugins")

# Flask app to keep Render free plan alive (use name)
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Main start
if __name__ == "__main__":
    # ensure directories exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    if not os.path.isdir(Config.SESSIONS):
        os.makedirs(Config.SESSIONS)

    # Pyrogram client (no prefixes argument here)
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

    # prepare chat list
    chat_id = []
    for i, j in zip(Config.GROUPS, Config.AUTH_USERS):
        chat_id.append(i)
        chat_id.append(j)

    async def main():
        await PRO.start()
        bot_info = await PRO.get_me()
        LOGGER.info(f"<--- @{bot_info.username} Started --->")

        for i in chat_id:
            try:
                await PRO.send_message(chat_id=i, text="Bot Started! ♾ /pro ")
            except Exception as d:
                print(d)
                continue

        await idle()

    # start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("Shutting down...")
    finally:
        LOGGER.info("<---Bot Stopped--->")
