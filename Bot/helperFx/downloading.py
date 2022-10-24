import ujson, aioaria2, emoji, os, pprint, re, asyncio
from Bot.helperFx.Schemas.dlSchema import session, DownloadDb
from Bot import books_bot
from Bot.helperFx.messageTemplates import download_template, post_template
from urllib.parse import unquote, quote
from pyrogram.types import InputMediaPhoto, InputMediaAudio, InputMediaDocument
from Bot import config_obj
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from Bot.plugins.handlers import divide_chunks
from Bot.helperFx.postData import postData, download_file
from pyrogram.errors import FloodWait

clean = re.compile("[^a-zA-Z] ")


async def find_download(trigger, data):
    gid: str = data["params"][0]["gid"]
    uri: str = (await trigger.getFiles(gid))[0]["uris"][0]["uri"]
    path = uri.split("/")[-2]

    _download: DownloadDb = session.query(DownloadDb).filter_by(path=path).first()
    ujson.loads(_download.tl_data)
    return [
        uri,
        path,
        _download,
        ujson.loads(_download.status),
        ujson.loads(_download.tl_data),
    ]


async def on_download_complete(trigger, data):
    uri, path, _download, _status, _tl_data = await find_download(trigger, data)
    _status[uri] = 1
    text = f"downlaod complete {path}"
    _download.status = ujson.dumps(_status)

    if all(item == 1 for item in _status.values()):

        await books_bot.edit_message_text(
            message_id=_tl_data["msg_id"],
            chat_id=_tl_data["chat_id"],
            text=download_template.render(
                **{
                    "name": unquote(path),
                    "emoji": emoji.emojize(":check_mark_button:"),
                    "state": False,
                }
            ),
            reply_markup=None,
        )
        links = ujson.loads(_download.links)
        _meta = await postData(
            {
                "meta": clean.sub(" ", f"{_download.title} {_download.author}"),
                "title": _download.title,
                "author": _download.author,
            }
        )
        pprint.pprint(_meta)
        _links = [
            f"{os.getcwd()}/Downloads/{_download.title}/{unquote(i.split('/')[-1])}"
            for i in links
        ]

        audio_media = [
            InputMediaAudio(
                media=i,
                duration=extractMetadata(createParser(i)).get("duration").seconds,
                title=f"{_download.title} {_links.index(i)+1} ",
                performer=_download.author,
                thumb=download_file(_meta["image"], name=_download.title),
            )
            for i in _links
        ]
        await books_bot.send_photo(
            chat_id=-1001186096459,
            photo=_meta["image"].replace("SL160", "SL300"),
            caption=post_template.render(**_meta),
        )
        for batch in divide_chunks(audio_media, 8):
            pprint.pprint(batch)
            while True:
                try:
                    await books_bot.send_media_group(
                        chat_id=-1001186096459,
                        media=batch,
                    )
                    break
                except FloodWait as e:
                    await asyncio.sleep(e.value)


async def on_download_start(trigger, data):
    uri, path, _download, _status, _tl_data = await find_download(trigger, data)
    text = f"downlaod started {path}"
    if _download.download_status == -1:
        _download.download_status = 0
        msg = await books_bot.send_message(
            chat_id=_tl_data["chat_id"],
            text=download_template.render(
                **{
                    "name": unquote(path),
                    "emoji": emoji.emojize(":stopwatch:"),
                    "state": True,
                }
            ),
            reply_markup=None,
        )
        _tl_data["msg_id"] = msg.id
        print(msg.id)

        print(text)
    _status[uri] = 0
    _download.status = ujson.dumps(_status)
    _download.tl_data = ujson.dumps(_tl_data)
    session.commit()


async def download_pool():
    client: aioaria2.Aria2WebsocketClient = await aioaria2.Aria2WebsocketClient.new(
        "http://127.0.0.1:8070/jsonrpc",
        token="token",
        loads=ujson.loads,
        dumps=ujson.dumps,
    )
    client.onDownloadComplete(on_download_complete)
    client.onDownloadStart(on_download_start)
    return client


# class DownloadManager:
#     def __init__(self):
