from pyrogram import Client
import configparser, asyncio
import os, contextvars
from Bot import _downloader, books_bot
from Bot.helperFx.downloading import download_pool


async def get_download_client():
    print(_downloader)
    return _downloader


async def main():
    x = await download_pool()
    _downloader.set(x)
    print(_downloader)
    await books_bot.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
