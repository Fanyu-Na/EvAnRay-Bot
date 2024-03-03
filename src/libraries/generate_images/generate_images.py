from src.libraries.generate_images.single_music_info import MusicInfo
from src.libraries.generate_images.player_best_50 import BestList,ChartInfo,DrawBest
from src.libraries.generate_images.player_music_score import MusicScore
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
            return None, 400, 0
        if resp.status == 403:
            return None, 403, 0
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
            img_path = f"temp/img/player_best_50/{file_name}_{userData['_id']}.png"
            pic.save(img_path)
            return pic, 0, rating
        else:
            return pic, 0, rating
        
async def generate_player_music_score(music:Music,payload,userData):
    is_abstract = userData.get("is_abstract",True)
    music_version = restore_version([music['basic_info']['from']])
    payload['version'] = [music_version]
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload) as r:
        verlist =  await r.json()
    player_music_score = MusicScore(music.id,verlist,is_abstract)
    if player_music_score.Done:
        file_name = userData.get("tencent_user_id",userData.get("divingfish_user_id","UNKNOW"))
        img_path = f"temp/img/player_music_score/{file_name}_{userData['_id']}.png"
        player_music_score.Img.save(img_path)
    return player_music_score.Done,player_music_score.Img