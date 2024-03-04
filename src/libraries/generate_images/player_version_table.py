from src.libraries.maimaidx_music import total_list
import requests
from PIL import Image, ImageDraw
from src.libraries.diving_fish_request import get_player_plate_data
from src.libraries.GLOBAL_CONSTANT import version_maps


class PlateTable(object):
    def __init__(self, version:str,mode:str,player_plate_data):
        self.version = version
        self.mode = mode
        self.player_plate_data = player_plate_data
        self.version_list = version_maps.get(self.version)
        self.result_list = total_list.by_version_for_plate(self.version_list)
        self.version_song_info = self.get_player_version_music_record()
        self.generate_plate_data = self.get_generate_plate_data()

    def get_player_version_music_record(self):
        version_song_info = {}
        for music in self.result_list:
            version_song_info[music.id] = {}
            for index ,level in enumerate(music['level']):
                version_song_info[music.id][index] = self.get_music_info(self.player_plate_data,int(music.id),index)
        return version_song_info

    def get_music_info(self,finishs,id:int,level:int):
        result = finishs['verlist']
        for item in result:
            if item['id'] == id and item['level_index'] == level:
                return {'fc':item['fc'],'fs':item['fs'],'achievements':item['achievements']}
        return {}
    
    def get_generate_plate_data(self):
        default_song_list = {
            "15":[],
            "14+":[],
            "14":[],
            "13+":[],
            "13":[],
            "12+":[],
            "12":[],
            "11+":[],
            "11":[],
            "10+":[],
            "10":[],
            "9+":[],
            "9":[],
            "8+":[],
            "8":[],
            "7+":[],
            "7":[],
            "6":[],
            "5":[],
            "4":[],
            "3":[],
            "2":[],
            "1":[]
        }

        for song_info in self.result_list:
            level= song_info.level[3]
            default_song_list[level].append(song_info.id)
        return default_song_list

    def generate_player_version_plate_table(self):
        img = Image.open(f"src/static/完成表/牌子完成表/{self.version}.png").convert('RGBA')
        ji = Image.open(f"src/static/完成表/极.png").convert('RGBA')
        jiang = Image.open(f"src/static/完成表/将.png").convert('RGBA')
        shen = Image.open(f"src/static/完成表/神.png").convert('RGBA')
        wu = Image.open(f"src/static/完成表/舞舞.png").convert('RGBA')
        ix = 130
        iy = 120
        for item in self.generate_plate_data.items():
            if item[1]:
                count = 0
                rcount = 0
                for song in range(0,len(self.generate_plate_data[item[0]])):
                    id = self.generate_plate_data[item[0]][song]

                    if self.version_song_info[id][3]:
                        if self.mode == '将' and self.version_song_info[id][3]['achievements'] >= 100:
                            if self.version_song_info[id][3]['fc'] in ['ap','app']:
                                img.paste(shen, (ix, iy), shen)
                            else:
                                img.paste(jiang, (ix, iy), jiang)
                        elif self.mode == '极' and self.version_song_info[id][3]['fc'] in ['fc','ap','fcp','app']:
                            if self.version_song_info[id][3]['fc'] in ['ap','app']:
                                img.paste(shen, (ix, iy), shen)
                            else:
                                img.paste(ji, (ix, iy), ji)
                        elif self.mode == '神'and self.version_song_info[id][3]['fc'] in ['ap','app']:
                            img.paste(shen, (ix, iy), shen)
                        elif self.mode == '舞舞' and self.version_song_info[id][3]['fs'] in ['fsd','fsdp']:
                            img.paste(wu, (ix, iy), wu)
                        else:
                            pass
                    count = count + 1
                    rcount = rcount + 1
                    ix = ix + 80
                    if count == 10 and len(self.generate_plate_data[item[0]])!= rcount:
                        ix = 130
                        iy = iy+85
                        count = 0
                iy = iy + 100
                ix = 130
        return img