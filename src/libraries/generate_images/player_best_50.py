# Author: xyb, Diving_Fish
import asyncio,requests
import os,io
import math
from typing import Optional, Dict, List, Tuple
import random
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import total_list
# from src.libraries.plate import Plate
# from src.libraries.openList import sz
from src.libraries.utils import get_cover_path
from pathlib import Path
import time
import hashlib
import json

# from maimaidx_music import total_list


scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')
comb = ' fc fcp ap app'.split(' ')
isfs = ' fs fsp fsd fsdp'.split(' ')
whatscore = 'd c b bb bbb a aa aaa s s+ ss ss+ sss sss+'.split(' ')
proxies = {"http": "http://117.50.184.62:808", "https": "http://117.50.184.62:808"}


class ChartInfo(object):
    def __init__(self, idNum:str, diff:int, tp:str, achievement:float, ra:int, comboId:int, scoreId:int,
                 title:str, ds:float, lv:str, fs:int,dxscore:int):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.dxscore = dxscore
        if achievement >= 100.5:
          self.ra = int(ds * 22.4 * 100.5 / 100)
        elif achievement > 100:
          self.ra = int(ds * 21.6 * achievement / 100)
        elif achievement > 99.5:
          self.ra = int(ds * 21.1 * achievement / 100)
        elif achievement > 99:
          self.ra = int(ds * 20.8 * achievement / 100)
        elif achievement > 98:
          self.ra = int(ds * 20.3 * achievement / 100)
        elif achievement > 97:
          self.ra = int(ds * 20 * achievement / 100)
        elif achievement > 94:
          self.ra = int(ds * 16.8 * achievement / 100)
        elif achievement > 90:
          self.ra = int(ds * 15.2 * achievement / 100)
        elif achievement > 80:
          self.ra = int(ds * 13.6 * achievement / 100)
        elif achievement > 75:
          self.ra = int(ds * 12.0 * achievement / 100)
        elif achievement > 70:
          self.ra = int(ds * 11.2 * achievement / 100)
        elif achievement > 60:
          self.ra = int(ds * 9.6 * achievement / 100)
        elif achievement > 50:
          self.ra = int(ds * 8 * achievement / 100)
        else:
          self.ra = 0
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv
        self.fs = fs

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra
    

    @classmethod
    def sp_from_json(cls,data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        fs = ['', 'fs','fsp','fsd','fsdp']
        fsi = fs.index(data['fs'])
        # idNum=total_list.by_title(data["title"]).id,

        return cls(
            idNum = data['song_id'],
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"],
            fs=fsi,
            dxscore = data["dxScore"]
        )

    @classmethod
    def from_json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        fs = ['', 'fs','fsp','fsd','fsdp']
        fsi = fs.index(data['fs'])
        # idNum=total_list.by_title(data["title"]).id,

        return cls(
            idNum = str(data['song_id']),
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"],
            fs=fsi,
            dxscore = data["dxScore"]
        )


class BestList(object):

    def __init__(self, size:int):
        self.data = []
        self.size = size

    def push(self, elem:ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while(len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


class DrawBest(object):
    def __init__(self, sdBest:BestList, dxBest:BestList, userName:str, musicRating:int, rankRating:int, userData,is_abstract:bool):
        self.start = time.perf_counter()
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userName = self._stringQ2B(userName)
        Rating = 0
        for num in range(0, len(sdBest)):
            chartInfo = sdBest[num]
            Rating += chartInfo.ra
        for num in range(0, len(dxBest)):
            chartInfo = dxBest[num]
            Rating += chartInfo.ra
        self.playerRating = Rating
        self.musicRating = musicRating
        self.rankRating = rankRating
        # self.plate = plate
        # self.QQ = 
        self.userData = userData
        self.pic_dir = 'src/static/mai/pic/'
        self.cover_dir = 'src/static/mai/cover/'
        self.img = Image.open(self.pic_dir + 'BG3.png')


        # 竖着
        self.ROWS_IMG = []
        for i in range(12):
            self.ROWS_IMG.append(170 + 140 * i)

        # 横着
        self.COLOUMS_IMG = []
        for i in range(12):
            self.COLOUMS_IMG.append(35 + 370 * i)
        self.f1 = time.perf_counter()
        self.draw(is_abstract)

    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e: # 转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _coloumWidth(self, s:str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s:str, len:int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)

    def _resizePic(self, img:Image.Image, time:float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))

    def _findRaPic(self) -> str:
        num = '10'
        if self.playerRating >= 15000:
            num = '10'
        elif self.playerRating >= 14000:
            num = '09'
        elif self.playerRating >= 13000:
            num = '08'
        elif self.playerRating >= 12000:
            num = '07'
        elif self.playerRating >= 10000:
            num = '06'
        elif self.playerRating >= 7000:
            num = '05'
        elif self.playerRating >= 4000:
            num = '04'
        elif self.playerRating >= 2000:
            num = '03'
        elif self.playerRating >= 1000:
            num = '02'
        else:
            num = '01'
        return f'UI_CMN_DXRating_S_{num}.png'

    def _drawRating(self, ratingBaseImg:Image.Image):
        COLOUMS_RATING = [105, 122, 140, 158, 175]
        theRa = int(self.playerRating)
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i], 12), mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg
    
    def _get_dxscore_type(self,dxscorepen):
        if dxscorepen <= 90:
            return "star-1.png"
        elif dxscorepen <= 93:
            return "star-2.png"
        elif dxscorepen <= 95:
            return "star-3.png"        
        elif dxscorepen <= 97:
            return "star-4.png"        
        else:
            return "star-5.png"

    def _drawBestList(self, img:Image.Image, sdBest:BestList, dxBest:BestList,is_abstract:bool):
        itemW = 135
        itemH = 88
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (217, 197, 233)]
        levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        level_index = 'BSC ADV EXP MST MST_Re'.split(' ')
        imgDraw = ImageDraw.Draw(img)
        titleFontName = 'src/static/adobe_simhei.otf'
        # 画标准 35个

        for num in range(0, len(sdBest)):
            i = num // 5  #  需要多少行
            j = num % 5    # 一行有几个
            chartInfo = sdBest[num]
            
            # 判断使用什么难道的成绩背景
            # pngPath = f'src/static/mai/pic/UI_TST_MBase_{level_index[chartInfo.diff]}.png'
            pngPath = f'src/static/mai/pic/XP_UI_MSS_MBase_{level_index[chartInfo.diff]}.png'
            temp = Image.open(pngPath).convert('RGBA')
            temp = self._resizePic(temp, 0.25)

            # #封面
            # if int(chartInfo.idNum) in sz.get_abstract_id_list():
            #     file_name,nickname = sz.get_abstract_file_name(chartInfo.idNum)
            #     CoverPath = 'src/static/abstract_cover/' + f'{file_name}.png'
            # else:
            #     CoverPath = self.cover_dir + f'{chartInfo.idNum}.png'
            # #默认
            # if not os.path.exists(CoverPath):
            #     CoverPath = self.cover_dir + '1000.png'
            CoverPath = get_cover_path(chartInfo.idNum,is_abstract)

            CoverDraw = Image.open(CoverPath).convert('RGBA')
            CoverDraw = CoverDraw.resize((86, 86), Image.ANTIALIAS)
            # CoverDraw = self._resizePic(CoverDraw, 0.36)
            # CoverDraw = circle_corner(CoverDraw ,6)
            temp.paste(CoverDraw, (16, 14), CoverDraw.split()[3])

            # DX/标准
            ModePath = self.pic_dir + f'UI_UPE_Infoicon_StandardMode.png'
            if chartInfo.tp == "DX":
                ModePath = self.pic_dir + f'UI_UPE_Infoicon_DeluxeMode.png'
            GameType = Image.open(ModePath).convert('RGBA')
            GameType = self._resizePic(GameType, 0.4)
            temp.paste(GameType, (14, 100), GameType.split()[3])

            tempDraw = ImageDraw.Draw(temp)

            # 歌名
            font = ImageFont.truetype(titleFontName, 18, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 16:
                title = self._changeColumnWidth(title, 14) + '...'
            tempDraw.text((119, 12), title, 'white', font)
            # 歌的id
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 14, encoding='utf-8')
            song_id = chartInfo.idNum
            tempDraw.text((120, 31), f'id: {song_id}', 'white', font)

            # 星星
            start_mun = chartInfo.dxscore / (sum(total_list.by_id(str(chartInfo.idNum)).charts[chartInfo.diff]['notes'])*3) *100
            start_path = self.pic_dir + self._get_dxscore_type(start_mun)
            GameType = Image.open(start_path).convert('RGBA')
            GameType = self._resizePic(GameType, 0.9)
            temp.paste(GameType, (225, 64), GameType.split()[3])

            # 成绩图标
            rankImg = Image.open(self.pic_dir + f'UI_TTR_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.35)
            temp.paste(rankImg, (220, 32), rankImg.split()[3])

            # FC/AP图标
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'{comb[chartInfo.comboId]}.png').convert('RGBA')
            else:
                comboImg = Image.open(self.pic_dir + f'fc_dummy.png').convert('RGBA')
            comboImg = self._resizePic(comboImg, 0.4)
            # 横向位置和竖直位置
            temp.paste(comboImg, (210, 86), comboImg.split()[3])

            # FSD/FS图标
            if chartInfo.fs:
                comboImg = Image.open(self.pic_dir + f'{isfs[chartInfo.fs]}.png').convert('RGBA')
            else:
                comboImg = Image.open(self.pic_dir + f'fs_dummy.png').convert('RGBA')
            comboImg = self._resizePic(comboImg, 0.4)
            # 横向位置和竖直位置
            temp.paste(comboImg, (252, 86), comboImg.split()[3])

            # Base 完成率 Ra
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 28, encoding='utf-8')
            # 完成度
            tempDraw.text((118, 47), f"{str(format(chartInfo.achievement, '.4f'))[0:-5]}", '#fadf62', font)

            font = ImageFont.truetype('src/static/adobe_simhei.otf', 16, encoding='utf-8')
            # 小数部分
            index = str(chartInfo.achievement).split('.')[0]
            # print(str(chartInfo.achievement).split('.'))
            achievement_f = "0" if len(str(chartInfo.achievement).split('.')) != 2 else str(chartInfo.achievement).split('.')[1]
            if int(index) < 100:
              tempDraw.text((150, 57), '. '+achievement_f, '#fadf62', font)
            else:
              tempDraw.text((167, 57), '. '+achievement_f, '#fadf62', font)

            # 下方
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 11, encoding='utf-8')
            # Base -> Rating
            tempDraw.text((125, 85), f"定数\n{format(chartInfo.ds, '.1f')}", '#000000', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 20, encoding='utf-8')
            tempDraw.text((151, 85), f'>', '#000000', font)
            tempDraw.text((164, 86), f'{chartInfo.ra}', '#000000', font)

            temp = self._resizePic(temp,1.2)

            img.paste(temp, (self.COLOUMS_IMG[j], self.ROWS_IMG[i]+50), temp)

        # DX铺面
        for num in range(0, len(dxBest)):
            i = num // 5 #5
            j = num % 5 #5
            chartInfo = dxBest[num]


            # 判断使用什么难道的成绩背景
            # pngPath = f'src/static/mai/pic/UI_TST_MBase_{level_index[chartInfo.diff]}.png'
            pngPath = f'src/static/mai/pic/XP_UI_MSS_MBase_{level_index[chartInfo.diff]}.png'
            temp = Image.open(pngPath).convert('RGBA')
            temp = self._resizePic(temp, 0.25)

            # #封面
            # if int(chartInfo.idNum) in sz.get_abstract_id_list():
            #     file_name,nickname = sz.get_abstract_file_name(chartInfo.idNum)
            #     CoverPath = 'src/static/abstract_cover/' + f'{file_name}.png'
            # else:
            #     CoverPath = self.cover_dir + f'{chartInfo.idNum}.png'
            # #默认
            # if not os.path.exists(CoverPath):
            #     CoverPath = self.cover_dir + '1000.jpg'
            CoverPath = get_cover_path(chartInfo.idNum,is_abstract)

            CoverDraw = Image.open(CoverPath).convert('RGBA')
            CoverDraw = CoverDraw.resize((86, 86), Image.ANTIALIAS)
            # CoverDraw = self._resizePic(CoverDraw, 0.36)
            # CoverDraw = circle_corner(CoverDraw ,6)
            temp.paste(CoverDraw, (16, 14), CoverDraw.split()[3])

            # DX/标准
            ModePath = self.pic_dir + f'UI_UPE_Infoicon_StandardMode.png'
            if chartInfo.tp == "DX":
                ModePath = self.pic_dir + f'UI_UPE_Infoicon_DeluxeMode.png'
            GameType = Image.open(ModePath).convert('RGBA')
            GameType = self._resizePic(GameType, 0.4)
            temp.paste(GameType, (14, 100), GameType.split()[3])

            tempDraw = ImageDraw.Draw(temp)

            # 歌名
            font = ImageFont.truetype(titleFontName, 18, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 16:
                title = self._changeColumnWidth(title, 14) + '...'
            tempDraw.text((119, 12), title, 'white', font)
            # 歌的id
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 14, encoding='utf-8')
            song_id = chartInfo.idNum
            tempDraw.text((120, 31), f'id: {song_id}', 'white', font)

            # 星星
            start_mun = chartInfo.dxscore / (sum(total_list.by_id(str(chartInfo.idNum)).charts[chartInfo.diff]['notes'])*3) *100
            start_path = self.pic_dir + self._get_dxscore_type(start_mun)
            GameType = Image.open(start_path).convert('RGBA')
            GameType = self._resizePic(GameType, 0.9)
            temp.paste(GameType, (225, 64), GameType.split()[3])

            # 成绩图标
            rankImg = Image.open(self.pic_dir + f'UI_TTR_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.35)
            temp.paste(rankImg, (220, 32), rankImg.split()[3])

            # FC/AP图标
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'{comb[chartInfo.comboId]}.png').convert('RGBA')
            else:
                comboImg = Image.open(self.pic_dir + f'fc_dummy.png').convert('RGBA')
            comboImg = self._resizePic(comboImg, 0.4)
            # 横向位置和竖直位置
            temp.paste(comboImg, (210, 86), comboImg.split()[3])

            # FSD/FS图标
            if chartInfo.fs:
                comboImg = Image.open(self.pic_dir + f'{isfs[chartInfo.fs]}.png').convert('RGBA')
            else:
                comboImg = Image.open(self.pic_dir + f'fs_dummy.png').convert('RGBA')
            comboImg = self._resizePic(comboImg, 0.4)
            # 横向位置和竖直位置
            temp.paste(comboImg, (252, 86), comboImg.split()[3])

            # Base 完成率 Ra
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 28, encoding='utf-8')
            # 完成度
            tempDraw.text((118, 47), f"{str(format(chartInfo.achievement, '.4f'))[0:-5]}", '#fadf62', font)

            font = ImageFont.truetype('src/static/adobe_simhei.otf', 16, encoding='utf-8')
            # 小数部分
            index = str(chartInfo.achievement).split('.')[0]
            # print(str(chartInfo.achievement).split('.'))
            achievement_f = "0" if len(str(chartInfo.achievement).split('.')) != 2 else str(chartInfo.achievement).split('.')[1]
            if int(index) < 100:
              tempDraw.text((150, 57), '. '+achievement_f, '#fadf62', font)
            else:
              tempDraw.text((167, 57), '. '+achievement_f, '#fadf62', font)
            # 下方
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 11, encoding='utf-8')
            # Base -> Rating
            tempDraw.text((125, 85), f"定数\n{format(chartInfo.ds, '.1f')}", '#000000', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 20, encoding='utf-8')
            tempDraw.text((151, 85), f'>', '#000000', font)
            tempDraw.text((164, 86), f'{chartInfo.ra}', '#000000', font)

            temp = self._resizePic(temp,1.2)


            img.paste(temp, (self.COLOUMS_IMG[j], self.ROWS_IMG[i+8]-30),temp)


    def GetRankLogo(self, rankRating):
        RankImage = '00.png'
        if rankRating < 1000:
            RankImage = '00.png'
        elif rankRating == 1000:
            RankImage = '01.png'
        elif rankRating == 1200:
            RankImage = '02.png'
        elif rankRating == 1400:
            RankImage = '03.png'
        elif rankRating == 1500:
            RankImage = '04.png'
        elif rankRating == 1600:
            RankImage = '05.png'
        elif rankRating == 1700:
            RankImage = '06.png'
        elif rankRating == 1800:
            RankImage = '07.png'
        elif rankRating == 1850:
            RankImage = '08.png'
        elif rankRating == 1900:
            RankImage = '09.png'
        elif rankRating == 1950:
            RankImage = '10.png'
        elif rankRating == 2000:
            RankImage = '11.png'
        elif rankRating == 2010:
            RankImage = '12.png'
        elif rankRating == 2020:
            RankImage = '13.png'
        elif rankRating == 2030:
            RankImage = '14.png'
        elif rankRating == 2040:
            RankImage = '15.png'
        elif rankRating == 2050:
            RankImage = '16.png'
        elif rankRating == 2060:
            RankImage = '17.png'
        elif rankRating == 2070:
            RankImage = '18.png'
        elif rankRating == 2080:
            RankImage = '19.png'
        elif rankRating == 2090:
            RankImage = '20.png'
        elif rankRating == 2100:
            RankImage = '21.png'
        return RankImage

    def draw(self,is_abstract:bool):
        # WaterMarkBg = Image.open(self.pic_dir + 'UI_CMN_MiniDialog_01.png').convert('RGBA')
        # WaterMarkBg = self._resizePic(WaterMarkBg, 0.6)
        # WaterMarkDraw = ImageDraw.Draw(WaterMarkBg)
        # Font = ImageFont.truetype('src/static/msyh.ttc' , 21 , encoding='utf-8')
        # MarkStr = ' This Designed by\n  GeneYP & Ryan'
        # WaterMarkDraw.text((80,55) , MarkStr , 'black' , Font)
        # self.img.paste(WaterMarkBg, (1550, 45), mask=WaterMarkBg.split()[3])

        # festLogo = Image.open(self.pic_dir + 'UI_CMN_TabTitle_MaimaiTitle_Ver214.png').convert('RGBA')
        # festLogo = self._resizePic(festLogo, 0.6)
        # self.img.paste(festLogo, (40, 35), mask=festLogo.split()[3])

        self.f2 = time.perf_counter()

        festLogo = Image.open(f'src/static/mai/pic/UI_CMN_TabTitle_MaimaiTitle_Ver230_ch.png').convert('RGBA')
        festLogo = festLogo.resize((432,208))
        self.img.paste(festLogo,(-19,0), festLogo.split()[3])


        # 姓名框
        Plate = self.userData.get("plate","")
        if Plate:
            if Path('src/static/mai/god_plate/'+Plate+'.png').exists():
                temp = Image.open('src/static/mai/god_plate/'+Plate+'.png').convert('RGBA')
                temp = temp.resize((942, 152),Image.ANTIALIAS)
                self.img.paste(temp,(389,36),temp)
            else:
                temp = Image.open('src/static/mai/default_plate/'+str(random.randint(1,124))+'.png').convert('RGBA')
                temp = temp.resize((942, 152),Image.ANTIALIAS)
                self.img.paste(temp,(390,36),temp)
        else:
            temp = Image.open('src/static/mai/default_plate/'+str(random.randint(1,124))+'.png').convert('RGBA')
            temp = temp.resize((942, 152),Image.ANTIALIAS)
            self.img.paste(temp,(390,36),temp)

        # 头像
        Icon = self.userData.get("Icon","默认头像")
        temp = Image.open(self.pic_dir + f'{Icon}.png').convert('RGBA')
        temp = temp.resize((124, 124),Image.ANTIALIAS)
        self.img.paste(temp,(405,49),temp)
                # r = requests.get(f'http://q1.qlogo.cn/g?b=qq&nk={self.QQ}&s=640')
                # temp = Image.open(io.BytesIO(r.content)).convert('RGBA')
                # temp = temp.resize((124, 124),Image.ANTIALIAS)
                # self.img.paste(temp,(405,49),temp)
        # else:
        #     temp = Image.open(self.pic_dir + f'{Icon}.png').convert('RGBA')
        #     temp = temp.resize((124, 124),Image.ANTIALIAS)
        #     self.img.paste(temp,(405,49),temp)
            
            

        # 头像框覆盖
        temp = Image.open(self.pic_dir + '头像框.png').convert('RGBA')
        self.img.paste(temp,(403,47),temp)

        # Rating
        RankLogo = Image.open(self.pic_dir + self._findRaPic()).convert('RGBA')
        # RankLogo = self._resizePic(RankLogo, 0.55)
        RankLogo = RankLogo.resize((212, 40),Image.ANTIALIAS)
        RankLogo = self._drawRating(RankLogo)
        self.img.paste(RankLogo, (546, 49),RankLogo)

        # 段位        
        temp = Image.open(self.pic_dir + self.GetRankLogo(self.rankRating)).convert('RGBA')
        temp = temp.resize((87, 36),Image.ANTIALIAS)
        self.img.paste(temp, (772, 51),temp)

        # 姓名
        Name = Image.open(self.pic_dir + '姓名背景.png').convert('RGBA')
        Name = Name.resize((320, 50))
        DXLogo = Image.open(self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        DXLogo = DXLogo.resize((36, 26),Image.ANTIALIAS)
        Name.paste(DXLogo,(270,8),DXLogo)
        namePlateDraw = ImageDraw.Draw(Name)
        font1 = ImageFont.truetype('src/static/msyh.ttc', 27, encoding='unic')
        namePlateDraw.text((15, 2), ' '.join(list(self.userName)), 'black', font1)
        self.img.paste(Name, (543, 93),Name)

        # 称号
        shougouImg = Image.open(self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        shougouImg = shougouImg.resize((313,29))
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype('src/static/adobe_simhei.otf', 17, encoding='utf-8')
        playCountInfo = f'MaiMai DX Rating'
        shougouImgW, shougouImgH = shougouImg.size
        playCountInfoW, playCountInfoH = shougouDraw.textsize(playCountInfo, font2)
        textPos = ((shougouImgW - playCountInfoW - font2.getoffset(playCountInfo)[0]) / 2, 5)
        shougouDraw.text((textPos[0] - 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text(textPos, playCountInfo, 'white', font2)
        shougouImg = self._resizePic(shougouImg, 1.05)
        self.img.paste(shougouImg,(546,145),shougouImg)
        
        self.f3 = time.perf_counter()
        self._drawBestList(self.img, self.sdBest, self.dxBest,is_abstract)
        self.f4 = time.perf_counter()

    def getDir(self):
        # self.img = self.img.convert("RGB")
        return self.img.convert("RGB")

    def getRatingS(self):
        return int(self.playerRating)


def computeRa(ds: float, achievement:float) -> int:
    if achievement >= 50 and achievement < 60:
        baseRa = 6.0
    elif achievement < 70:
        baseRa = 7.0
    elif achievement < 75:
        baseRa = 7.5
    elif achievement < 80:
        baseRa = 8.5
    elif achievement < 90:
        baseRa = 9.5
    elif achievement < 94:
        baseRa = 10.5
    elif achievement < 97:
        baseRa = 12.5
    elif achievement < 98:
        baseRa = 12.7
    elif achievement < 99:
        baseRa = 13.0
    elif achievement < 99.5:
        baseRa = 13.2
    elif achievement < 100:
        baseRa = 13.5
    elif achievement < 100.5:
        baseRa = 14.0
    else:
        baseRa = 5.0

    return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)


async def generate_b50(payload: Dict,userData,is_abstract:int) -> (Optional[Image.Image], bool, int):  # -> Tuple[Optional[Image.Image], bool]:
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
            plate = obj['plate']

        pic = DrawBest(sd_best, dx_best, obj["nickname"], obj["rating"] + obj["additional_rating"],obj["additional_rating"],is_abstract).getDir()
        return pic, 0, rating