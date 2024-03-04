
from nonebot.adapters.qq.message import MessageSegment,Message
from nonebot.adapters.qq.event import GroupAtMessageCreateEvent
from nonebot.params import CommandArg, ShellCommandArgs, RawCommand, EventMessage

from nonebot.plugin import on_message,on_command
from src.libraries.diving_fish_request import get_player_best_50
from src.libraries.utils import is_int
from src.libraries.data_base.userdata_handle import userdata


bind_user = on_command('bind', priority=20)



@bind_user.handle()
async def _(event: GroupAtMessageCreateEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    query = str(args).strip()
    if is_int(query):
        player_best_50_resp = await get_player_best_50({"qq":query})
        if player_best_50_resp.status == 200:
            player_best_50_result = await player_best_50_resp.json()
            userdata.bindTencentUserId(user_id,query,player_best_50_result.get('username'))
            await bind_user.finish(f"绑定成功,查询到查分器用户名为:{player_best_50_result.get('nickname','')}")
    
    player_best_50_resp = await get_player_best_50({"username":query})
    if player_best_50_resp.status == 200:
        player_best_50_result = await player_best_50_resp.json()
        userdata.bindDivingFishUserId(user_id,query,player_best_50_result.get('username'))
        await bind_user.finish(f"绑定成功,查询到查分器用户名为:{player_best_50_result.get('nickname','')}")
    elif player_best_50_resp.status == 400:
        await bind_user.finish(f"绑定失败,未查询到水鱼查分器用户名:{query}")
    elif player_best_50_resp.status == 403:
        await bind_user.finish(f"绑定失败,此用户禁止其他人查询成绩:{query}")
    else:
        await bind_user.finish(f"发生未知错误信息,请联系EvAnRay管理员查看。")

