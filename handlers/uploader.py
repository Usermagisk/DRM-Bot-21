# handlers/uploader.py
import os
import asyncio
from pyrogram.types import Message
from pyrogram import Client
from main import LOGGER as LOGS

class Upload_to_Tg:
    def init(self, bot: Client, m: Message, file_path: str, name: str,
                 Thumb=None, path=None, show_msg=None, caption=None):
        self.bot = bot
        self.m = m
        self.file_path = file_path
        self.name = name
        self.Thumb = Thumb
        self.path = path
        self.show_msg = show_msg
        self.caption = caption

    async def upload_video(self):
        try:
            # send as video
            await self.bot.send_chat_action(self.m.chat.id, "upload_video")
            await self.bot.send_video(
                chat_id=self.m.chat.id,
                video=self.file_path,
                caption=self.caption or self.name,
                thumb=self.Thumb if self.Thumb and os.path.exists(self.Thumb) else None,
                supports_streaming=True
            )
            if self.show_msg:
                try:
                    await self.show_msg.delete(True)
                except:
                    pass
        except Exception as e:
            LOGS.error("upload_video error: %s", e)
            raise

    async def upload_doc(self):
        try:
            await self.bot.send_chat_action(self.m.chat.id, "upload_document")
            await self.bot.send_document(
                chat_id=self.m.chat.id,
                document=self.file_path,
                caption=self.caption or self.name
            )
            if self.show_msg:
                try:
                    await self.show_msg.delete(True)
                except:
                    pass
        except Exception as e:
            LOGS.error("upload_doc error: %s", e)
            raise
