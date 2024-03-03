
from nonebot.adapters.qq.message import MessageSegment
from nonebot.adapters.qq.event import GroupAtMessageCreateEvent
from nonebot.plugin import on_command
from pathlib import Path
import base64
import traceback

from src.libraries.log import log


ping = on_command("error")
@ping.handle()
async def __(event:GroupAtMessageCreateEvent):
    try:
        raise Exception("自定义异常")
    except Exception:
        log.info("err: %s" % traceback.format_exc())

    await ping.finish([MessageSegment.image("https://download.fanyu.site/abstract/10188_1.png"),"Pong!!"]) 