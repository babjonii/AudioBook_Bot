import aioaria2
import ujson, json
from Bot.helperFx.Schemas.dlSchema import session, DownloadDb
from Bot import books_bot


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

        await books_bot.send_message(
            # message_id=_tl_data["msg_id"],
            chat_id=_tl_data["chat_id"],
            text=text,
            reply_markup=None,
        )
        print(text)


async def on_download_start(trigger, data):
    uri, path, _download, _status, _tl_data = await find_download(trigger, data)
    text = f"downlaod started {path}"
    if _download.download_status == -1:
        _download.download_status = 0
        msg = await books_bot.send_message(
            chat_id=_tl_data["chat_id"],
            text=text,
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
