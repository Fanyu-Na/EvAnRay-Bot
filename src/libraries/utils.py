from src.libraries.data_base.abstract_handle import abstract
from src.libraries.maimaidx_music import total_list
from src.libraries.diving_fish_request import get_player_plate_data
from pathlib import Path
import aiohttp

def get_cover_path(song_id,is_abstract:bool):
    id = int(song_id)
    if is_abstract:
        file_name,nickname = abstract.get_abstract_file_name(id)
        if nickname != "抽象画未收录":
            CoverPath = 'src/static/abstract_cover/' + f'{file_name}.png'
        else:
            CoverPath = f'src/static/cover/{id}.png'
    else:
        CoverPath = f'src/static/cover/{id}.png'

    if Path(CoverPath).exists():
        return CoverPath
    else:
        if Path('src/static/cover/' + f'{id-10000}.png').exists():
            return 'src/static/cover/' + f'{id-10000}.png'
        if Path('src/static/cover/' + f'{id+10000}.png').exists():
            return 'src/static/cover/' + f'{id+10000}.png'
        return 'src/static/abstract_cover/1000.jpg'
    
def is_int(content:str):
    try:
        content = int(content)
        return True
    except:
        return False
    
def search_song_byid(id,index,list):
    for item in list:
        if item["id"] == id and item['level_index'] == index:
            return item
    return None

def get_user_payload(userData):
    tencent_user_id = userData.get('tencent_user_id',"")
    df_user_id = userData.get('divingfish_user_id',"")
    if (not tencent_user_id) and (not df_user_id):
        return {}
    if tencent_user_id:
        return {"qq": tencent_user_id}
    elif df_user_id:
        return {"username": df_user_id}
    else:
        return {}


def restore_version(versions:list):
    restore_version_list = []
    for version in versions:
        if version == "舞萌DX":
            restore_version_list.append("maimai でらっくす")
        elif version == "舞萌DX 2021":
            restore_version_list.append("maimai でらっくす Splash")
        elif version == "舞萌DX 2022":
            restore_version_list.append("maimai でらっくす UNiVERSE")
        elif version == "maimai でらっくす FESTiVAL":
            restore_version_list.append("maimai でらっくす")
        else:
            restore_version_list.append(version)
    return restore_version_list

    
async def plate_searplayer_version_handle(version, payload, plateType: str, vername: str):
    version_list = total_list.by_version_for_plate(version)


    player_plate_data = await get_player_plate_data(payload)
    print(player_plate_data)
    un_finish_data = {0: [], 1: [], 2: [], 3: [], 4: []}

    for song in version_list:
        songid = int(song['id'])
        for index in range(len(song['level'])):
            song_result = search_song_byid(songid, index, player_plate_data['verlist'])
            if song_result:
                if plateType == '将':
                    if song_result['achievements'] < 100:
                        un_finish_data[index].append(song_result)
                elif plateType == '极':
                    if song_result['fc'] not in ['fc', 'ap', 'fcp', 'app']:
                        un_finish_data[index].append(song_result)
                elif plateType == '神':
                    if song_result['fc'] not in ['ap', 'app']:
                        un_finish_data[index].append(song_result)
                elif plateType == '舞舞':
                    if song_result['fs'] not in ['fsd', 'fsdp']:
                        un_finish_data[index].append(song_result)
                elif plateType == '者':
                    if song_result['achievements'] < 80:
                        un_finish_data[index].append(song_result)
            else:
                un_finish_data[index].append(song)

    # 高难度铺面
    HardSong = ''
    for item in un_finish_data[3]:
        if item.get('achievements', -1) >= 0:
            if item['level'] in ['13+', '14', '14+', '15']:
                socre = str(item['achievements'])
                HardSong += '    ' + str(item['id']) + '.' + item['title'] + '(' + item['level'] + ')   ' + socre + '\n'
        else:
            if item['level'][3] in ['13+', '14', '14+', '15']:
                socre = '未游玩'
                HardSong += ' ' + str(item['id']) + '.' + item['title'] + '(' + item['level'][3] + ')   ' + socre + '\n'
    if vername in ['舞', '霸']:
        for item in un_finish_data[4]:
            if item.get('achievements', -1) >= 0:
                if item['level'] in ['13+', '14', '14+', '15']:
                    socre = str(item['achievements'])
                    HardSong += '    ' + str(item['id']) + '.' + item['title'] + '(' + item[
                        'level'] + ')   ' + socre + '\n'
            else:
                if item['level'][3] in ['13+', '14', '14+', '15']:
                    socre = '未游玩'
                    HardSong += ' ' + str(item['id']) + '.' + item['title'] + '(' + item['level'][
                        3] + ')   ' + socre + '\n'
    ver_mode = vername + plateType
    message_content = f'\n你的{ver_mode}剩余进度如下：\n'
    unfinishSongCount = len(un_finish_data[0]) + len(un_finish_data[1]) + len(un_finish_data[2]) + len(
        un_finish_data[3]) if vername not in ['舞', '者'] else len(un_finish_data[0]) + len(un_finish_data[1]) + len(
        un_finish_data[2]) + len(un_finish_data[3]) + len(un_finish_data[4])
    unfinishGCount = len(un_finish_data[0])
    unfinishYCount = len(un_finish_data[1])
    unfinishRCount = len(un_finish_data[2])
    unfinishPCount = len(un_finish_data[3])
    unfinishREPCount = len(un_finish_data[4])
    if unfinishSongCount == 0:
        return f'您的{ver_mode}进度已经全部完成!!!\n'
    if unfinishGCount == 0:
        message_content += 'Basic难度已经全部完成\n'
    else:
        message_content += f'Basic剩余{str(unfinishGCount)}首\n'
    if unfinishYCount == 0:
        message_content += 'Advanced难度已经全部完成\n'
    else:
        message_content += f'Advanced剩余{str(unfinishYCount)}首\n'
    if unfinishRCount == 0:
        message_content += 'Expert难度已经全部完成\n'
    else:
        message_content += f'Expert剩余{str(unfinishRCount)}首\n'
    if unfinishPCount == 0:
        message_content += f'Master难度已经全部完成\n你已经{t}确认了!!!!\n'
    else:
        message_content += f'Master剩余{str(unfinishPCount)}首\n'
    if vername in ['舞', '霸']:
        if unfinishREPCount == 0:
            message_content += f'Re_Master难度已经全部完成\n你已经{t}确认了!!!!\n'
        else:
            message_content += f'Re_Master剩余{str(unfinishREPCount)}首\n'
    message_content += f'总共剩余{str(unfinishSongCount)}首\n'
    # print(unfinishRCount,unfinishPCount)
    if (unfinishRCount != 0 or unfinishPCount != 0) and vername not in ["舞", "霸"]:
        # print('Join')
        message_content += '未完成高难度谱面还剩下\n'
        message_content += HardSong[0:-1]
    lxzt = (unfinishSongCount // 4) + 1 if unfinishSongCount % 4 != 0 else unfinishSongCount // 4
    dszt = (unfinishSongCount // 3) + 1 if unfinishSongCount % 3 != 0 else unfinishSongCount // 3
    if plateType == "舞舞":
        message_content += f'\n单刷需要{str(dszt)}批西'
    else:
        message_content += f'\n贫瘠状态下需要{str(lxzt)}批西,单刷需要{str(dszt)}批西'
    message_content += '\n加油嗷！！！'
    return message_content