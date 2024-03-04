import nonebot
from nonebot.adapters.qq.message import MessageSegment,Message
from nonebot.adapters.qq.event import GroupAtMessageCreateEvent
from nonebot.plugin import on_command, on_shell_command, on_regex
from nonebot.rule import Namespace, ArgumentParser, Rule
from nonebot.params import CommandArg, ShellCommandArgs, RawCommand, EventMessage
from nonebot.adapters.qq.exception import ActionFailed
import traceback
from src.libraries.log import log
from src.libraries.data_base.alias_db_handle import alias
from src.libraries.data_base.abstract_handle import abstract
from src.libraries.data_base.userdata_handle import userdata
from src.libraries.maimaidx_music import total_list
from src.libraries.generate_images.generate_images import generate_music_info,generate_player_best_50,generate_player_music_score,generate_player_version_plate_table,generate_player_level_table
from src.libraries.GLOBAL_CONSTANT import version_maps
from src.libraries.utils import plate_searplayer_version_handle,restore_version,get_user_payload,get_player_rating_ranking
from src.libraries.diving_fish_request import get_user_name_by_tentcent_user_id
from pathlib import Path
import re

config = nonebot.get_driver().config
IMAGE_SERVER_URL = config.image_server_url

search_music_abstract_parser = ArgumentParser()
search_music_abstract_parser.add_argument("music_id")
search_music_abstract_parser.add_argument("-n", "--normal", action='store_false')

# search_player_info_parser = ArgumentParser()
# search_player_info_parser.add_argument("music_id", nargs='+', metavar="music_id")
# search_player_info_parser.add_argument("-n", "--normal", action='store_false')

music_info = on_shell_command("id", parser=search_music_abstract_parser,priority=20)
randomly_filter_music = on_regex(r"^[来整搞弄随]个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?", priority=20)
randomly_music = on_regex(r".*mai.*什么", priority=20)
search_music_by_title = on_command("S", aliases={'s', 'Search','search'}, priority=20)
normal_music_info = on_regex(r"^([绿黄红紫白]?)msong ([0-9]+)", priority=20)
search_music_by_alias = on_regex(r".+是什么歌", priority=20)
search_alias_by_id = on_command('查看别名', priority=20)
ractional_line = on_command('分数线', priority=20)
player_best_50 = on_command('EvAnRay b50', aliases={'B50', 'b50'}, priority=20)
player_version_schedule = on_regex('.(将|极|神|舞舞|者)进度', priority=20)
player_music_score = on_shell_command("info", parser=search_music_abstract_parser,priority=20)
player_rating_ranking = on_command('我有多菜', priority=20)
player_version_table = on_regex('.(将|极|神|舞舞)完成表', priority=20)
player_level_table = on_regex(r'^([0-9]+\+?)完成表', priority=20)


@music_info.handle()
async def _(event: GroupAtMessageCreateEvent, foo: Namespace = ShellCommandArgs()):
    music_id = str(foo.music_id).strip()
    music = total_list.by_id(music_id)
    # print(music)
    is_abstract = foo.normal
    if music:
        if generate_music_info(music,is_abstract):
            try:
                await music_info.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_music_info/{music.id}"))
            except ActionFailed as e:
                await music_info.send(f"code:{e.code},msg:{e.message}")
        else:
            await music_info.send(f"歌曲信息处理异常,请联系EvAnRay管理员。")
    else:
        await music_info.send(f"未查询到此歌曲信息,请检查歌曲ID是否正确。")

@randomly_filter_music.handle()
async def _(event: GroupAtMessageCreateEvent):
    userData = userdata.getUserData(event.get_user_id())
    regex = "[来整搞弄随]个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    # print(res)
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)

        music = music_data.random()
        if music:
            if generate_music_info(music,userData.get("is_abstract",True)):
                try:
                    await randomly_filter_music.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_music_info/{music.id}"))
                except ActionFailed as e:
                    await randomly_filter_music.send(f"code:{e.code},msg:{e.message}")
            else:
                await randomly_filter_music.send(f"歌曲信息处理异常,请联系EvAnRay管理员。")
        else:
            await randomly_filter_music.send(f"当前查询条件下未查询到歌曲。")
    except Exception as e:
        log.info("err: %s" % traceback.format_exc())
        await randomly_filter_music.finish("歌曲信息处理异常,请联系EvAnRay管理员。")

@randomly_music.handle()
async def _(event: GroupAtMessageCreateEvent):
    userData = userdata.getUserData(event.get_user_id())
    music = total_list.random()
    if music:
        if generate_music_info(music,userData.get("is_abstract",True)):
            try:
                await randomly_music.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_music_info/{music.id}"))
            except ActionFailed as e:
                await randomly_music.send(f"code:{e.code},msg:{e.message}")
        else:
            await randomly_music.send(f"歌曲信息处理异常,请联系EvAnRay管理员。")
    else:
        await randomly_music.send(f"当前查询条件下未查询到歌曲。")



@search_music_by_title.handle()
async def _(event: GroupAtMessageCreateEvent, args: Message = CommandArg()):
    music_title = str(args).strip()
    if music_title == "":
        await search_music_by_title.finish("歌曲查询内容不允许为空。")
    
    userData = userdata.getUserData(event.get_user_id())
    res = total_list.filter(title_search=music_title)
    if not res:
        await search_music_by_title.finish(f'未查询到相关歌曲信息:\n关键字:{music_title}')
    serach_result = []
    for music in res:
        ds = '/'.join(str(num) for num in music.ds)
        serach_result.append(f"{music['id']}. {music['title']}-{ds}")
    await search_music_by_title.send("\n"+"\n".join(serach_result))

@normal_music_info.handle()
async def _(event: GroupAtMessageCreateEvent, message: Message = EventMessage()):
    regex = "([绿黄红紫白]?)msong ([0-9]+)"
    groups = re.match(regex, str(message)).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            if music:
                chart = music['charts'][level_index]
                ds = music['ds'][level_index]
                level = music['level'][level_index]
                file_name, nickname = abstract.get_abstract_file_name(music.id)
                file = f"https://download.fanyu.site/abstract/{file_name}.png"
                if len(chart['notes']) == 4:
                    msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}
抽象画作者:{nickname}'''
                else:
                    msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}
抽象画作者:{nickname}'''
                await normal_music_info.send(
                    [
                        MessageSegment.text(f"\n{music['id']}. {music['title']}\n"),
                        MessageSegment.image(file),
                        MessageSegment.text(msg)
                    ]
                )
            else:
                await normal_music_info.send("未查询到此歌曲信息,请检查歌曲ID是否正确。")
            raise Exception("test")
        except Exception:
            log.info("err: %s" % traceback.format_exc())
            await normal_music_info.send("歌曲信息处理异常,请联系EvAnRay管理员。")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        if music:
            file_name, nickname = abstract.get_abstract_file_name(music.id)
            file = f"https://download.fanyu.site/abstract/{file_name}.png"
            await normal_music_info.send(
                [
                    MessageSegment.text(f"\n{music['id']}. {music['title']}\n"),
                    MessageSegment.image(file),
                    MessageSegment.text(f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}\n抽象画作者:{nickname}")
                ]   
            )
        else:
            await normal_music_info.send("未查询到此歌曲信息,请检查歌曲ID是否正确。")

@search_music_by_alias.handle()
async def _(event: GroupAtMessageCreateEvent):
    userData = userdata.getUserData(event.get_user_id())

    regex = "(.+)是什么歌"
    search_alias = re.match(regex, str(event.get_message())).groups()[0].strip()
    result_set = alias.searchMusic(search_alias)
    if len(result_set) == 1:
        music = total_list.by_id(result_set[0])

        if music:
            if generate_music_info(music,userData.get("is_abstract",True)):
                try:
                    await search_music_by_alias.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_music_info/{music.id}"))
                except ActionFailed as e:
                    await search_music_by_alias.send(f"code:{e.code},msg:{e.message}")
            else:
                await search_music_by_alias.send(f"歌曲信息处理异常,请联系EvAnRay管理员。")
        else:
            await search_music_by_alias.send(f'未查询到相关歌曲信息:\n关键字:{search_alias}')
    
    # 如果未找到查询歌曲title
    elif len(result_set) == 0:
        res = total_list.filter(title_search=search_alias)
        if len(res) == 1:
            music = total_list.by_id(res[0].id)
            if music:
                if generate_music_info(music,userData.get("is_abstract",True)):
                    try:
                        await search_music_by_alias.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_music_info/{music.id}"))
                    except ActionFailed as e:
                        await search_music_by_alias.send(f"code:{e.code},msg:{e.message}")
                else:
                    await search_music_by_alias.send(f"歌曲信息处理异常,请联系EvAnRay管理员。")
            else:
                await search_music_by_alias.send(f'歌曲信息处理异常,请联系EvAnRay管理员。')
        if not res:
            await search_music_by_alias.finish(f"没有找到名为{search_alias}的歌曲，可以使用<添加别名 歌曲id 别名>申请添加别名,获得玩家三票同意将添加成功")

        serach_result = []
        for music in res:
            ds = '/'.join(str(num) for num in music.ds)
            serach_result.append(f"{music['id']}. {music['title']}-{ds}")
        await search_music_by_alias.send("\n"+"\n".join(serach_result))
    else:
        serach_result = []
        for result in result_set:
            music = total_list.by_id(result)
            serach_result.append(f'{music.id}.{music.title}')
        serach_result_cotent = "\n".join(serach_result)
        await search_music_by_alias.finish(f"为你查询到以下歌曲信息:\n{serach_result_cotent}")

@search_alias_by_id.handle()
async def _(event: GroupAtMessageCreateEvent, args: Message = CommandArg()):
    music = total_list.by_id(str(args).strip())
    if music:
        aliasnames = alias.searchAlias(str(args).strip())
        if aliasnames:
            result = f'\n{music.id}.{music.title}的别名有'
            for name in aliasnames:
                result += f'\n{name}'
            await search_alias_by_id.send(result)
        else:
            await search_alias_by_id.send(f'{music.id}.{music.title}暂无别名。')
    else:
        await search_alias_by_id.finish(f'未查询到此歌曲信息,请检查歌曲ID是否正确。')

@ractional_line.handle()
async def _(event: GroupAtMessageCreateEvent, args: Message = CommandArg()):
    await ractional_line.finish("分数线功能等待开发中。")

#     r = "([绿黄红紫白])(id)?([0-9]+)"
#     argv = str(args).strip().split(" ")
#     if len(argv) == 1 and argv[0] == '帮助':
#         s = '''此功能为查找某首歌分数线设计。
# 命令格式：分数线 <难度+歌曲id> <分数线>
# 例如：分数线 紫799 100
# 命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
# 以下为 TAP GREAT 的对应表：
# GREAT/GOOD/MISS
# TAP\t1/2.5/5
# HOLD\t2/5/10
# SLIDE\t3/7.5/15
# TOUCH\t1/2.5/5
# BREAK\t5/12.5/25(外加200落)'''
#         await ractional_line.send(Message([{
#             "type": "image",
#             "data": {
#                 "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"
#             }
#         }]))
#     elif len(argv) == 2:
#         try:
#             grp = re.match(r, argv[0]).groups()
#             level_labels = ['绿', '黄', '红', '紫', '白']
#             level_labels2 = ['Basic', 'Advanced',
#                              'Expert', 'Master', 'Re:MASTER']
#             level_index = level_labels.index(grp[0])
#             chart_id = grp[2]
#             line = float(argv[1])
#             music = total_list.by_id(chart_id)
#             chart: Dict[Any] = music['charts'][level_index]
#             tap = int(chart['notes'][0])
#             slide = int(chart['notes'][2])
#             hold = int(chart['notes'][1])
#             touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
#             brk = int(chart['notes'][-1])
#             total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
#             break_bonus = 0.01 / brk
#             break_50_reduce = total_score * break_bonus / 4
#             reduce = 101 - line
#             if reduce <= 0 or reduce >= 101:
#                 raise ValueError
#             await query_score.send(f'''{music['title']} {level_labels2[level_index]}
# 分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
# BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
#         except Exception:
#             await query_score.send("Xray检测到格式错误,输入“分数线 帮助”以查看帮助信息")



@player_best_50.handle()
async def _(event: GroupAtMessageCreateEvent, args: Message = CommandArg(), cmd: str = RawCommand()):
    args = str(args).strip().split(' ')
    userData = userdata.getUserData(event.get_user_id())

    is_abstract = userData.get("is_abstract",True)
    tencent_user_id = userData.get('tencent_user_id',"")
    payload = get_user_payload(userData)
    if not payload:
        await player_best_50.finish("您当前没有绑定水鱼查分器相关信息，请使用【/bind】命令进行水鱼查分器信息绑定。\n例:【/bind EvAnRay】或【/bind QQ号】")

    if len(args) == 1:
        arg = args[0]
        if arg:
            if arg in ["-n", "--normal"]:
                mode = 2
                payload['b50'] = 1
                # payload = {'qq': tencent_user_id, 'b50': 1}
                is_abstract = False
            else:
                mode = 1
                payload = {'username': args[0], 'b50': 1}
                # is_abstract = is_abstract
        # 没有任何参数的请求查询
        else:
            if tencent_user_id:
                mode = 2
                payload['b50'] = 1
                # is_abstract = is_abstract
            else:
                mode = 1
                payload['b50'] = 1
                # is_abstract = is_abstract

    elif len(args) == 2:
        if args[1] in ["-n", "--normal"]:
            mode = 1
            username = args[0]
            payload = {'username': args[0], 'b50': 1}
            is_abstract = False
        else:
            await player_best_50.send("格式出现错误,如需使用-n参数。\n示例:b50 EvAnRay -n")
    else:
        await player_best_50.send("格式出现错误,如需使用-n参数。\n示例:b50 EvAnRay -n")


    img, success, ratingS, file_name = await generate_player_best_50(payload, userData, is_abstract)

    if success == 400:
        if mode == 2:
            await player_best_50.send(
                f"☠你没有绑定查分器哩.....\n或者在使用该指令时添加你的查分器用户名!!!\n例:b50 EvAnRay")
        else:
            await player_best_50.send(f"EvAnRay没有查找到当前用户名,请检查用户名是否正确")
    elif success == 403:
        await player_best_50.send("人家不让俺查,你要查什么嘛，哼！\nps:看置顶 or 精华 or 公告")
    else:
        if ratingS == 0:
            await player_best_50.finish('EvAnRay查到你还没有上传成绩呢,请先上传成绩再来~')
        try:
            await player_best_50.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_player_best_50/{file_name}"))
        except ActionFailed as e:
            await player_best_50.send(f"code:{e.code},msg:{e.message}")


@player_version_schedule.handle()
async def _(event: GroupAtMessageCreateEvent):
    regex = "(.)(将|极|神|舞舞|者)进度"
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        groups = reresult.groups()
        version = version_maps.get(groups[0], [])
        if version:
            version_list = restore_version(version)
            userData = userdata.getUserData(event.get_user_id())
            payload = get_user_payload(userData)
            if not payload:
                await player_version_schedule.finish("您当前没有绑定水鱼查分器相关信息，请使用【/bind】命令进行水鱼查分器信息绑定。\n例:【/bind EvAnRay】或【/bind QQ号】")

            payload['version'] = version_list

            mesage_content = await plate_searplayer_version_handle(version, payload, groups[1], groups[0])

            await player_version_schedule.send(mesage_content)
        else:
            await player_version_schedule.finish(f'未找到{groups[0]}代')
    else:
        await player_version_schedule.send('格式错误')

@player_music_score.handle()
async def _(event: GroupAtMessageCreateEvent, foo: Namespace = ShellCommandArgs()):
    music_id_or_alias = str(foo.music_id).strip()

    music = total_list.by_id(music_id_or_alias)
    if not music:
        result_set = alias.searchMusic(music_id_or_alias)
        if len(result_set) == 1:
            music = total_list.by_id(result_set[0])
        elif len(result_set) > 1:
            music_result = []
            for music_id in result_set:
                music = total_list.by_id(music_id)
                if music:
                    music_result.append(f"{music.id}-{music.title}")
            music_content = '\n'.join(music_result)
            await player_music_score.finish(f"检索到多个关键字【{music_id_or_alias}】,请选择一下歌曲使用歌曲ID进行查询。\n{music_content}")

    if music:
        userData = userdata.getUserData(event.get_user_id())
        payload = get_user_payload(userData)
        if not payload:
            await player_version_schedule.finish("您当前没有绑定水鱼查分器相关信息，请使用【/bind】命令进行水鱼查分器信息绑定。\n例:【/bind EvAnRay】或【/bind QQ号】")

        isDone, file_name = await generate_player_music_score(music, payload, userData)
        if isDone:
            try:
                await player_music_score.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_player_music_score/{file_name}"))
            except ActionFailed as e:
                await player_music_score.send(f"code:{e.code},msg:{e.message}")
        else:
            await player_music_score.finish('歌曲成绩信息处理异常,请联系EvAnRay管理员。')
    else:
        await player_music_score.finish("未查询到此歌曲信息,请检查歌曲ID或者歌曲别名是否正确。")


@player_rating_ranking.handle()
async def _( event: GroupAtMessageCreateEvent, args: Message = CommandArg()):
    arg = str(args).strip()
    if arg == '':
        userData = userdata.getUserData(event.get_user_id())
        user_name = userData.get('user_name')
        if user_name:
            player_rating_ranking_content = await get_player_rating_ranking(user_name)
        else:
            await player_rating_ranking.finish("您当前没有绑定水鱼查分器相关信息，请使用【/bind】命令进行水鱼查分器信息绑定。\n例:【/bind EvAnRay】或【/bind QQ号】")
    else:
        player_rating_ranking_content = await get_player_rating_ranking(user_name)
    await player_rating_ranking.finish(player_rating_ranking_content)



@player_version_table.handle()
async def _(event: GroupAtMessageCreateEvent):
    regex = "(.)(将|极|神|舞舞)完成表"
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        groups = reresult.groups()
        version = version_maps.get(groups[0], [])
        if 0 < len(version) <= 2:
            version_list = restore_version(version)
            userData = userdata.getUserData(event.get_user_id())
            payload = get_user_payload(userData)
            if not payload:
                await player_version_table.finish("您当前没有绑定水鱼查分器相关信息，请使用【/bind】命令进行水鱼查分器信息绑定。\n例:【/bind EvAnRay】或【/bind QQ号】")

            payload['version'] = version_list
            result , file_name = await generate_player_version_plate_table(payload,userData, groups[1], groups[0])
            
            if result:
                try:
                    await player_version_table.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_player_version_plate_table/{file_name}"))
                except ActionFailed as e:
                    await player_version_table.send(f"code:{e.code},msg:{e.message}")
        else:
            await player_version_table.finish(f'EvAnRay暂时不支持{groups[0]}{groups[1]}完成表的制作。')
    else:
        await player_version_table.send('格式错误')



@player_level_table.handle()
async def _(event: GroupAtMessageCreateEvent):
    regex = r'^([0-9]+\+?)完成表'
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        level = reresult.groups()[0]
        userData = userdata.getUserData(event.get_user_id())
        payload = get_user_payload(userData)
        result , file_name = await generate_player_level_table(payload,userData,level)
        if result:
            try:
                await player_level_table.send(MessageSegment.image(f"{IMAGE_SERVER_URL}/get_player_level_table/{file_name}"))
            except ActionFailed as e:
                await player_level_table.send(f"code:{e.code},msg:{e.message}")
    else:
        await player_level_table.send('格式错误')