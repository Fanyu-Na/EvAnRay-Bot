from src.libraries.generate_images.single_music_info import MusicInfo
from src.libraries.generate_images.player_best_50 import BestList,ChartInfo,DrawBest
from src.libraries.generate_images.player_music_score import MusicScore
from src.libraries.generate_images.player_version_table import PlateTable
from src.libraries.generate_images.player_level_table import LevelTable
from src.libraries.GLOBAL_CONSTANT import version_maps,ALL_VERSION_LIST
from src.libraries.diving_fish_request import get_player_plate_data
from src.libraries.maimaidx_music import Music
from typing import Optional, Dict, List, Tuple
from src.libraries.utils import restore_version
import aiohttp

def generate_music_info(music,is_abstract):
    song_info_result = MusicInfo(music.id, is_abstract)
    if song_info_result.result:
        img_path = f"temp/img/music_info/{music.id}.png"
        song_info_result.Img.save(img_path)
        return True
    else:
        return False

async def generate_player_best_50(payload,userData,is_abstract):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400, 0,""
        if resp.status == 403:
            return None, 403, 0,""
        sd_best = BestList(35)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        rating = int(str(obj["rating"]))
        for c in sd:
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_best.push(ChartInfo.from_json(c))

        if obj['plate']:
            userData['plate'] = obj['plate']

        pic = DrawBest(sd_best, dx_best, obj["nickname"], obj["rating"] + obj["additional_rating"],obj["additional_rating"],userData,is_abstract).getDir()
        if pic:
            file_name = userData.get("tencent_user_id",userData.get("divingfish_user_id","UNKNOW"))
            file_name = f"{file_name}_{userData['_id']}"
            img_path = f"temp/img/player_best_50/{file_name}.png"
            pic.save(img_path)
            return pic, 0, rating, file_name
        else:
            return pic, 0, rating, file_name
        
async def generate_player_music_score(music:Music,payload,userData):
    is_abstract = userData.get("is_abstract",True)
    music_version = restore_version([music['basic_info']['from']])
    payload['version'] = [music_version]
    verlist =  await get_player_plate_data(payload)
    player_music_score = MusicScore(music.id,verlist,is_abstract)
    if player_music_score.Done:
        file_name = userData.get("tencent_user_id",userData.get("divingfish_user_id","UNKNOW"))
        file_name = f"{file_name}_{userData['_id']}"
        img_path = f"temp/img/player_music_score/{file_name}.png"
        player_music_score.Img.save(img_path)
    return player_music_score.Done,file_name

async def generate_player_version_plate_table(payload,userData,plateType: str, vername: str):
    # is_abstract = userData.get("is_abstract",True)
    music_version = version_maps.get(vername)
    music_version = list(restore_version(music_version))
    print(vername,music_version)
    payload['version'] = [music_version]
    verlist = await get_player_plate_data(payload)
    player_version_plate_table_Img = PlateTable(vername,plateType,verlist).generate_player_version_plate_table()
    file_name = userData.get("tencent_user_id",userData.get("divingfish_user_id","UNKNOW"))
    file_name = f"{file_name}_{userData['_id']}_{vername}{plateType}"
    img_path = f"temp/img/player_version_plate_table/{file_name}.png"
    player_version_plate_table_Img.save(img_path)
    return player_version_plate_table_Img,file_name

async def generate_player_level_table(payload,userData,level):
    payload['version'] = [ALL_VERSION_LIST]
    user_music_data = await get_player_plate_data(payload)
    player_level_table_Img = LevelTable(level,user_music_data['verlist']).generate_player_level_table()
    file_name = userData.get("tencent_user_id",userData.get("divingfish_user_id","UNKNOW"))
    file_name = f"{file_name}_{userData['_id']}_{level}"
    img_path = f"temp/img/player_level_table/{file_name}.png"
    player_level_table_Img.save(img_path)
    return player_level_table_Img,file_name
    