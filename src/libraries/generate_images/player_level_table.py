import requests
from PIL import Image, ImageDraw
import json
import requests
from typing import Dict, List, Optional


class LevelTable(object):
    def __init__(self, level:str,user_music_data):
        self.level = level
        self.user_music_data = user_music_data
        self.level_ds_list = self.read_level_ds_file()[self.level]
        self.get_level_finish_Img()

    def read_level_ds_file(self):
        with open("src/static/完成表/level_ds_list.json", 'r', encoding='utf-8') as fw:
            level_ds_list = json.load(fw)
        return level_ds_list

    def get_level_finish_Img(self):
        for ds in self.level_ds_list:
            for music in self.level_ds_list[ds]:
                for user_data in self.user_music_data:
                    if str(user_data['id']) == music['song_id'] and user_data['level_index'] == music['level_index']:
                        music['achievements'] = user_data['achievements']

    def generate_player_level_table(self):
        sssp = Image.open(f"src/static/完成表/sssp.png").convert('RGBA')
        sss = Image.open(f"src/static/完成表/sss.png").convert('RGBA')
        ssp = Image.open(f"src/static/完成表/ssp.png").convert('RGBA')
        ss = Image.open(f"src/static/完成表/ss.png").convert('RGBA')
        sp = Image.open(f"src/static/完成表/sp.png").convert('RGBA')
        s = Image.open(f"src/static/完成表/s.png").convert('RGBA')
        img = Image.open(f"src/static/完成表/难度完成表/{self.level}.png").convert('RGBA')

        ix = 150
        iy = 180

        for ds in self.level_ds_list: # 不同定数有多少首歌
            count = 0
            rcount = 0
            for music in self.level_ds_list[ds]:
                if not music.get('achievements',0):
                    music['achievements'] = 0
                if music['achievements']>= 100.5:
                    img.paste(sssp, (ix, iy), sssp)
                elif music['achievements']>= 100:
                    img.paste(sss, (ix, iy), sss)
                elif music['achievements']>= 99.5:
                    img.paste(ssp, (ix, iy), ssp)
                elif music['achievements']>= 99:
                    img.paste(ss, (ix, iy), ss)
                elif music['achievements']>= 98:
                    img.paste(sp, (ix, iy), sp)
                elif music['achievements']>= 97:
                    img.paste(s, (ix, iy), s)

                count = count + 1
                rcount = rcount + 1
                ix = ix + 80
                if count == 15 and len(self.level_ds_list[ds]) != rcount:
                    ix = 150
                    iy = iy+85
                    count = 0
            iy = iy + 100
            ix = 150
        return img