from pyrogram.types import *
import emoji
from pyrogram import Client, filters
from Bot.helperFx.Schemas.dlSchema import session, DownloadDb
from Bot.helperFx.messageTemplates import audio_item
from Bot.helperFx.onlineBooks import Fla, Get_Links
from Bot import _downloader
import logging
import uuid, asyncio, ujson, json

# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )

# logging.getLogger(__name__)
def divide_chunks(l, n):
    items = []

    for i in range(0, len(l), n):

        items.append(l[i : i + n])
    return items


@Client.on_message(filters.command(["start"], prefixes="/"))
async def handle_start(_, message: Message):
    await message.reply_text("I got books yo!")


@Client.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    Download_Client = _downloader.get()
    user_id = callback_query.from_user.id
    data = callback_query.data
    await client.delete_messages(
        callback_query.message.chat.id,
        [
            callback_query.message.id,
        ],
    )
    download_item: DownloadDb = (
        session.query(DownloadDb).filter_by(key_data=data).first()
    )
    links = await Get_Links(download_item.page)
    download_item.path = links[0].split("/")[-2]
    download_item.links = str(links)
    download_item.status = ujson.dumps({i: {"status": -1} for i in links})
    session.commit()
    asyncio.gather(
        *[
            Download_Client.addUri(
                [link],
                options={"dir": f"./Downloads/{download_item.title}"},
            )
            for link in links
        ]
    )


@Client.on_message(filters.private)
async def handle_query(_, message: Message):

    message.text
    ABooks = await Fla(message.text)
    response = ""
    rows = []
    for book in ABooks:
        _id = str(uuid.uuid4())[:8]
        item = DownloadDb(
            title=book["title"],
            author=book["author"],
            page=book["url"],
            path="x",
            links="x",
            status="x",
            tl_data=ujson.dumps(
                {
                    "user_id": message.from_user.id,
                    "msg_id": message.id,
                    "chat_id": message.chat.id,
                }
            ),
            key_data=_id,
        )
        session.add(item)
        session.commit()
        response = response + audio_item.render(
            **{
                "number": emoji.emojize(f":keycap_{ABooks.index(book)+1}:"),
                "Title": book["title"],
                "Author": book["author"],
            }
        )
        # response = (
        #     response
        #     + f"""{ABooks.index(book)+1}  Title:{book['title']}\n    Author:{book['author']}\n\n"""
        # )

        rows.append(
            InlineKeyboardButton(
                text=emoji.emojize(f":keycap_{ABooks.index(book)+1}:"),
                callback_data=_id,
            )
        )

    await message.reply_text(
        response, reply_markup=InlineKeyboardMarkup(divide_chunks(rows, 3))
    )
