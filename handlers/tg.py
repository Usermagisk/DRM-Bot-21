# handlers/tg.py
from main import LOGGER as LOGS, prefixes, Config, Msg
from pyrogram import Client as AFK
from pyrogram.types import Message
from handlers.html import parse_html
import os

class TgHandler:
    def init(self, bot: AFK, m: Message, path: str) -> None:
        self.bot = bot
        self.m = m
        self.path = path

    @staticmethod
    async def error_message(bot: AFK, m: Message, error: str):
        LOGS.error(error)
        await bot.send_message(
            chat_id=Config.LOG_CH,
            text=f"<b>Error:</b> {error}"
        )

    async def linkMsg2(self, List):
        a = ""
        try:
            for data in List:
                if len(f"{a}{data}") > 3500:
                    await self.bot.send_message(
                        chat_id=self.m.chat.id,
                        text=f'Failed files are ({len(List)}) :-\n\n{a}',
                        disable_web_page_preview=True,
                    )
                    a = ""
                a += data
            if a:
                await self.bot.send_message(
                    chat_id=self.m.chat.id,
                    text=f'Failed files are ({len(List)}) :-\n\n{a}',
                    disable_web_page_preview=True,
                )
            List.clear()
        except Exception:
            try:
                await self.m.reply_text("Done")
            except:
                pass
            List.clear()

    async def downloadMedia(self, msg):
        sPath = f"{Config.DOWNLOAD_LOCATION}/FILE/{self.m.chat.id}"
        os.makedirs(sPath, exist_ok=True)
        file = await self.bot.download_media(
            message=msg,
            file_name=f"{sPath}/{msg.id}"
        )
        return file

    async def readTxt(self, x):
        try:
            with open(x, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.split("\n")
            name_links = [i.split(":", 1) for i in content if i != '']
            os.remove(x)
            LOGS.info("Read txt links: %s", len(name_links))
            return name_links
        except Exception as e:
            LOGS.error(e)
            try:
                await self.m.reply_text("Invalid file Input.")
            except:
                pass
            try:
                os.remove(x)
            except:
                pass
            return

    @staticmethod
    def parse_name(rawName):
        name = (
            rawName.replace("/", "_")
            .replace("|", "_")
            .replace(":", "-")
            .replace("*", "")
            .replace("#", "")
            .replace("\t", "")
            .replace(";", "")
            .replace("'", "")
            .replace('"', '')
            .replace("{", "(")
            .replace("}", ")")
            .replace("`", "")
            .replace("__", "_")
            .strip()
        )
        return str(name)

    @staticmethod
    def short_name(name: str):
        return name[:70] if len(name) > 100 else name

    def user_(self):
        try:
            if self.m.from_user is None:
                user = self.m.chat.title
            else:
                user = self.m.from_user.first_name
            return user
        except Exception as e:
            LOGS.error(e)
            return "Group Admin"

    @staticmethod
    def index_(index: int):
        return 0 if int(index) == 0 else int(index) - 1

    @staticmethod
    def resolution_(resolution: str):
        return resolution if resolution in ['144', '180', '240', '360', '480', '720', '1080'] else '360'


class TgClient(TgHandler):
    async def Ask_user(self):
        userr = self.user_()
        await self.bot.send_message(
            self.m.chat.id,
            text=Msg.TXT_MSG.format(user=userr)
        )

        inputFile = await self.bot.listen(self.m.chat.id)
        if not inputFile or not inputFile.document:
            return  # nothing sent
            if inputFile.document.mime_type not in ["text/plain", "text/html"]:
            await self.m.reply_text("Please send only TXT or HTML file")
            return

        txt_name = inputFile.document.file_name.replace("_", " ")
        x = await self.downloadMedia(inputFile)
        try:
            await inputFile.delete(True)
        except:
            pass

        if inputFile.document.mime_type == "text/plain":
            nameLinks = await self.readTxt(x)
            Token = inputFile.caption if inputFile.caption else None
        else:  # html
            nameLinks = parse_html(x)
            Token = None
            try:
                os.remove(x)
            except:
                pass

        await self.bot.send_message(
            self.m.chat.id,
            text=Msg.CMD_MSG_1.format(txt=txt_name, no_of_links=len(nameLinks))
        )
        user_index = await self.bot.listen(self.m.chat.id)
        num = TgClient.index_(index=int(user_index.text))

        await self.bot.send_message(self.m.chat.id, text="Send Caption :-")
        user_caption = await self.bot.listen(self.m.chat.id)
        caption = user_caption.text

        await self.bot.send_message(self.m.chat.id, text="Send Quality (Default is 360) :-")
        user_quality = await self.bot.listen(self.m.chat.id)
        quality = TgClient.resolution_(resolution=user_quality.text)

        thumb_msg = await self.bot.ask(self.m.chat.id, "Send Thumb JPEG/PNG or Telegraph Link or No :-")
        if getattr(thumb_msg, "text", None):
            if thumb_msg.text.lower() == "no":
                Thumb = None
            else:
                Thumb = thumb_msg.text
        elif getattr(thumb_msg, "photo", None):
            Thumb = await self.downloadMedia(thumb_msg)
        else:
            Thumb = None

        return nameLinks, num, caption, quality, Token, txt_name, userr, Thumb
