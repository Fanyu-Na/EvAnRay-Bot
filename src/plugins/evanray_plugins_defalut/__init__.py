
from nonebot.adapters.qq.message import MessageSegment
from nonebot.adapters.qq.event import GroupAtMessageCreateEvent
from nonebot.plugin import on_command
from pathlib import Path
import base64

ping = on_command("ping")
@ping.handle()
async def __(event:GroupAtMessageCreateEvent):
    await ping.finish([MessageSegment.image("http://43.139.85.91:8081/abstract/10188_1.png"),"Pong!!"]) 