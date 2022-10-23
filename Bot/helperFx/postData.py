from fuzzywuzzy import fuzz
import asyncio
import aiohttp, re, pprint, asyncio
from pyrogram import Client
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from aria2p.utils import human_readable_bytes, human_readable_timedelta


def bar(current, total, client, message: Message, name, start):
    now = time.time()
    time_delta = now - start
    info = {}

    if round(time_delta % 10.00) == 0:
        speed = current / time_delta
        info["title"] = name
        info["current"] = human_readable_bytes(current)
        info["total"] = human_readable_bytes(total)
        info["speed"] = human_readable_bytes(speed)

        percentage = current * 100 / total
        elapsed_time = round(time_delta) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        progress = "[{0}{1}] {2}%".format(
            "".join(["█" for i in range(math.floor(percentage / 5))]),
            "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )

        info["animation"] = progress
        info["eta"] = TimeFormatter(milliseconds=time_to_completion)
        user_id = message.chat.id
        mes_id = message.message_id
        prev_text = message.text
        new_text = get_upload_template(info)
        if prev_text != new_text:
            try:
                m = client.edit_message_text(
                    chat_id=user_id, message_id=mes_id, text=new_text, parse_mode="html"
                )
            except FloodWait as e:
                pass
            except Exception as e:
                print(str(e))
                time.sleep(1)
                pass


async def get_metadata(query):

    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        resp = await session.get(
            f"https://digitalbooks.api86.workers.dev/?query={query}"
        )
        rez = await resp.json()
        print(rez)
        return [
            {
                "image": i["Images"]["Primary"]["Medium"]["URL"],
                "genres": [
                    j["ContextFreeName"] for j in i["BrowseNodeInfo"]["BrowseNodes"]
                ],
                "title": i["ItemInfo"]["Title"]["DisplayValue"],
                "authors": [
                    a["Name"]
                    for a in i["ItemInfo"]["ByLineInfo"]["Contributors"]
                    if a["Role"] == "Author"
                ],
                "locale": i["ItemInfo"]["Title"]["Locale"],
            }
            for i in rez["SearchResult"]["Items"]
        ]


async def postData(query, client: Client):

    datas = await get_metadata(query["meta"])
    results = []
    for data in datas:

        # print("-" * 100)
        # pprint.pprint(data)
        authors_score = max(
            [
                fuzz.ratio(query["author"], author.lower()) / 100
                for author in data["authors"]
            ]
        )
        title_score = fuzz.ratio(query["title"].lower(), data["title"].lower()) / 100
        results.append(sum([authors_score, title_score]))
        # print(
        #     , data["title"], authors_score, title_score
        # )
    metadata = datas[results.index(max(results))]
    # await client.send_audio(,)


# asyncio.run(
#     postData(
#         {
#             "meta": "CHRISTINA LAUREN  DATING YOU  HATING You",
#             "title": "DATING YOU HATING You",
#             "author": "CHRISTINA LAUREN",
#         }
#     )
# )
