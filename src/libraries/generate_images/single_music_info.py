import re
from PIL import Image,ImageFont,ImageDraw
import requests
from src.libraries.data_base.abstract_handle import abstract

from src.libraries.utils import get_cover_path
from src.libraries.maimaidx_music import total_list,Music
from pathlib import Path
LINE_CHAR_COUNT = 37*2  # 每行字符数：12个中文字符
TABLE_WIDTH = 4

def line_break(line):
    ret = ''
    width = 0
    for c in line:
        if len(c.encode('utf8')) == 3:  # 中文
            if LINE_CHAR_COUNT == width + 1:  # 剩余位置不够一个汉字
                width = 2
                ret += '\n' + c
            else: # 中文宽度加2，注意换行边界
                width += 2
                ret += c
        else:
            if c == '\t':
                space_c = TABLE_WIDTH - width % TABLE_WIDTH  # 已有长度对TABLE_WIDTH取余
                ret += ' ' * space_c
                width += space_c
            elif c == '\n':
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= LINE_CHAR_COUNT:
            ret += '\n'
            width = 0
    if ret.endswith('\n'):
        return ret
    return ret + '\n'



class MusicInfo():
    def __init__(self,song_id:str,is_abstract:bool) -> None:
        self.result = False
        self.local = "src/static/mai/song_info"
        self.abstract_local = "src/static/abstract_cover"
        # self.font_local = "src/static/男朋友字体.ttf"
        self.font_local = "src/static/SourceHanSans_35.otf"
        self.other_font = "src/static/SourceHanSans_37.ttf"
        self.color = (48, 16, 128)
        self.id = song_id
        Music_data:Music = total_list.by_id(song_id)
        if Music_data:
            self.is_abstract = is_abstract
            self.id = Music_data.id
            self.title = Music_data.title
            self.ds = Music_data.ds
            self.level = Music_data.level
            self.genre = Music_data.genre
            self.type = Music_data.type
            self.bpm = Music_data.bpm
            self.version = Music_data.version
            self.charts = Music_data.charts
            # self.release_date = Music_data.release_date
            self.artist = Music_data.artist
            self.diff = Music_data.diff
            self.drawImg()
            self.result = True
        else:
            self.result = False
            

    def drawImg(self):
        # 初始化背景
        self.Img = Image.open(f'{self.local}/background.png').convert('RGBA')
        self.Img =  self.Img.resize((1080,1000))
        self.Draw = ImageDraw.Draw(self.Img)

        # 添加封面
        if self.is_abstract:
            abstract_data = abstract.get_abstract_id_list()
            if int(self.id) in abstract_data:
                file_name,nickname = abstract.get_abstract_file_name(str(self.id))
                filename = file_name
                self.abstract_artist = nickname
                cover = Image.open(f'{self.abstract_local}/{filename}.png')
            else:
                self.abstract_artist = "抽象画未收录"
                # img_path = Path(f"{self.abstract_local}/{str(self.id)}_1.png")
                # if img_path.exists():
                #     cover = Image.open(f'{self.abstract_local}/{str(self.id)}_1.png')
                # else:
                cover = Image.open(get_cover_path(self.id,False))
        else:
            self.abstract_artist = "-"
            cover = Image.open(get_cover_path(self.id,False))
        cover = cover.resize((200,200))
        self.Img.paste(cover,(120,85))

        # 添加title
        font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
        title = self.title

        strList = []
        newStr = ''
        index = 0
        is_splite = 0
        for item in title:
            newStr += item
            if font.getsize(newStr)[0] > 588:
                is_splite = 1
                strList.append(newStr)
                newStr = ''
                # 如果后面长度不没有定长长就返回
                if font.getsize(title[index+1:])[0] <= 588:
                    strList.append(title[index+1:])
                    break

            index += 1
        resTitle = ''
        count = 0
        for item in strList:
            resTitle += item+'\n'
            count += 1
        if not is_splite:
            resTitle = self.title
        self.Draw.text((340,88),resTitle,self.color,font)

        # 添加作者
        font = ImageFont.truetype(self.font_local, 18, encoding='utf-8')
        self.artist = line_break(self.artist)
        self.Draw.text((340,180),self.artist,self.color,font)
        # self.Draw.text((340,200),"抽象画作者:XXXXXXXXXXXXX",self.color,font)

        # 添加铺面类型
        if self.type == "SD":
            songtypeImg = Image.open(f'{self.local}/standard.png').convert('RGBA')
        else:
            songtypeImg = Image.open(f'{self.local}/deluxe.png').convert('RGBA')
        songtypeImg = songtypeImg.resize((75,25))
        self.Img.paste(songtypeImg,(337,271), songtypeImg.split()[3])

        # 添加歌曲id 版本 BPM
        font = ImageFont.truetype(self.other_font, 21, encoding='utf-8')
        lastInfo = f'ID {self.id}          {self.genre}          BPM {self.bpm}'
        self.Draw.text((425,265),lastInfo,self.color,font)

        # BASIC
        # print(1)
        font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')
        content = f'{self.level[0]} ({self.ds[0]})'
        font_x,font_y = font.getsize(content)
        self.Draw.text((165-(font_x/2),448),content,(255,255,255),font)
        chart = self.charts[0]['notes']
        total = sum(chart)
        tap = chart[0]
        hold = chart[1]
        slide = chart[2]
        touch = chart[3] if len(chart) == 5 else "-"
        break_tap = chart[4] if len(chart) == 5 else chart[3]
        font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
        font_x,font_y = font.getsize(str(total))
        self.Draw.text((303-(font_x/2),458-(font_y/2)),str(total),self.color,font)
        font_x,font_y = font.getsize(str(tap))
        self.Draw.text((428-(font_x/2),458-(font_y/2)),str(tap),self.color,font)
        font_x,font_y = font.getsize(str(hold))
        self.Draw.text((553-(font_x/2),458-(font_y/2)),str(hold),self.color,font)
        font_x,font_y = font.getsize(str(slide))
        self.Draw.text((678-(font_x/2),458-(font_y/2)),str(slide),self.color,font)
        font_x,font_y = font.getsize(str(touch))
        self.Draw.text((803-(font_x/2),458-(font_y/2)),str(touch),self.color,font)
        font_x,font_y = font.getsize(str(break_tap))
        self.Draw.text((928-(font_x/2),458-(font_y/2)),str(break_tap),self.color,font)

        # ADV
        font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')
        content = f'{self.level[1]} ({self.ds[1]})'
        font_x,font_y = font.getsize(content)
        self.Draw.text((165-(font_x/2),508),content,(255,255,255),font)
        chart = self.charts[1]['notes']
        total = sum(chart)
        tap = chart[0]
        hold = chart[1]
        slide = chart[2]
        touch = chart[3] if len(chart) == 5 else "-"
        break_tap = chart[4] if len(chart) == 5 else chart[3]
        font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
        font_x,font_y = font.getsize(str(total))
        self.Draw.text((303-(font_x/2),518-(font_y/2)),str(total),self.color,font)
        font_x,font_y = font.getsize(str(tap))
        self.Draw.text((428-(font_x/2),518-(font_y/2)),str(tap),self.color,font)
        font_x,font_y = font.getsize(str(hold))
        self.Draw.text((553-(font_x/2),518-(font_y/2)),str(hold),self.color,font)
        font_x,font_y = font.getsize(str(slide))
        self.Draw.text((678-(font_x/2),518-(font_y/2)),str(slide),self.color,font)
        font_x,font_y = font.getsize(str(touch))
        self.Draw.text((803-(font_x/2),518-(font_y/2)),str(touch),self.color,font)
        font_x,font_y = font.getsize(str(break_tap))
        self.Draw.text((928-(font_x/2),518-(font_y/2)),str(break_tap),self.color,font)

        # EXP
        font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')
        content = f'{self.level[2]} ({self.ds[2]})'
        font_x,font_y = font.getsize(content)
        self.Draw.text((165-(font_x/2),568),content,(255,255,255),font)
        chart = self.charts[2]['notes']
        total = sum(chart)
        tap = chart[0]
        hold = chart[1]
        slide = chart[2]
        touch = chart[3] if len(chart) == 5 else "-"
        break_tap = chart[4] if len(chart) == 5 else chart[3]
        font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
        font_x,font_y = font.getsize(str(total))
        self.Draw.text((303-(font_x/2),578-(font_y/2)),str(total),self.color,font)
        font_x,font_y = font.getsize(str(tap))
        self.Draw.text((428-(font_x/2),578-(font_y/2)),str(tap),self.color,font)
        font_x,font_y = font.getsize(str(hold))
        self.Draw.text((553-(font_x/2),578-(font_y/2)),str(hold),self.color,font)
        font_x,font_y = font.getsize(str(slide))
        self.Draw.text((678-(font_x/2),578-(font_y/2)),str(slide),self.color,font)
        font_x,font_y = font.getsize(str(touch))
        self.Draw.text((803-(font_x/2),578-(font_y/2)),str(touch),self.color,font)
        font_x,font_y = font.getsize(str(break_tap))
        self.Draw.text((928-(font_x/2),578-(font_y/2)),str(break_tap),self.color,font)

        # MAS
        font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')
        content = f'{self.level[3]} ({self.ds[3]})'
        font_x,font_y = font.getsize(content)
        self.Draw.text((165-(font_x/2),628),content,(255,255,255),font)
        chart = self.charts[3]['notes']
        total = sum(chart)
        tap = chart[0]
        hold = chart[1]
        slide = chart[2]
        touch = chart[3] if len(chart) == 5 else "-"
        break_tap = chart[4] if len(chart) == 5 else chart[3]
        font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
        font_x,font_y = font.getsize(str(total))
        self.Draw.text((303-(font_x/2),638-(font_y/2)),str(total),self.color,font)
        font_x,font_y = font.getsize(str(tap))
        self.Draw.text((428-(font_x/2),638-(font_y/2)),str(tap),self.color,font)
        font_x,font_y = font.getsize(str(hold))
        self.Draw.text((553-(font_x/2),638-(font_y/2)),str(hold),self.color,font)
        font_x,font_y = font.getsize(str(slide))
        self.Draw.text((678-(font_x/2),638-(font_y/2)),str(slide),self.color,font)
        font_x,font_y = font.getsize(str(touch))
        self.Draw.text((803-(font_x/2),638-(font_y/2)),str(touch),self.color,font)
        font_x,font_y = font.getsize(str(break_tap))
        self.Draw.text((928-(font_x/2),638-(font_y/2)),str(break_tap),self.color,font)

        # REMAS
        if len(self.level) == 5:
            font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')
            content = f'{self.level[4]} ({self.ds[4]})'
            font_x,font_y = font.getsize(content)
            self.Draw.text((165-(font_x/2),688),content,(195, 70, 231),font)
            chart = self.charts[4]['notes']
            total = sum(chart)
            tap = chart[0]
            hold = chart[1]
            slide = chart[2]
            touch = chart[3] if len(chart) == 5 else "-"
            break_tap = chart[4] if len(chart) == 5 else chart[3]
            font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
            font_x,font_y = font.getsize(str(total))
            self.Draw.text((303-(font_x/2),698-(font_y/2)),str(total),self.color,font)
            font_x,font_y = font.getsize(str(tap))
            self.Draw.text((428-(font_x/2),698-(font_y/2)),str(tap),self.color,font)
            font_x,font_y = font.getsize(str(hold))
            self.Draw.text((553-(font_x/2),698-(font_y/2)),str(hold),self.color,font)
            font_x,font_y = font.getsize(str(slide))
            self.Draw.text((678-(font_x/2),698-(font_y/2)),str(slide),self.color,font)
            font_x,font_y = font.getsize(str(touch))
            self.Draw.text((803-(font_x/2),698-(font_y/2)),str(touch),self.color,font)
            font_x,font_y = font.getsize(str(break_tap))
            self.Draw.text((928-(font_x/2),698-(font_y/2)),str(break_tap),self.color,font)
        else:
            font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')
            content = f'- (-)'
            font_x,font_y = font.getsize(content)
            self.Draw.text((165-(font_x/2),688),content,(195, 70, 231),font)
            total = "-"
            tap = "-"
            hold = "-"
            slide = "-"
            touch = "-"
            break_tap = "-"
            font = ImageFont.truetype(self.font_local, 30, encoding='utf-8')
            font_x,font_y = font.getsize(str(total))
            self.Draw.text((303-(font_x/2),698-(font_y/2)),str(total),self.color,font)
            self.Draw.text((428-(font_x/2),698-(font_y/2)),str(tap),self.color,font)
            self.Draw.text((553-(font_x/2),698-(font_y/2)),str(hold),self.color,font)
            self.Draw.text((678-(font_x/2),698-(font_y/2)),str(slide),self.color,font)
            self.Draw.text((803-(font_x/2),698-(font_y/2)),str(touch),self.color,font)
            self.Draw.text((928-(font_x/2),698-(font_y/2)),str(break_tap),self.color,font)

        # 谱师信息
        font = ImageFont.truetype(self.font_local, 24, encoding='utf-8')

        content = self.charts[2]['charter']
        newStr = ''
        for item in content:
            newStr += item
            if font.getsize(newStr)[0] > 230:
                content = newStr + "..."
                break
        self.Draw.text((271,783),content,self.color,font)
        content = self.charts[3]['charter']
        newStr = ''
        for item in content:
            newStr += item
            if font.getsize(newStr)[0] > 230:
                content = newStr + "..."
                break
        self.Draw.text((271,823),content,self.color,font)
        if len(self.level) == 5:
            content = self.charts[4]['charter']
            newStr = ''
            for item in content:
                newStr += item
                if font.getsize(newStr)[0] > 230:
                    content = newStr + "..."
                    break
            self.Draw.text((271,863),content,self.color,font)
        else:
            self.Draw.text((271,863),"-",self.color,font)
            

        # 歌曲版本
        font_x,font_y = font.getsize(self.version.replace("maimai ","") if len(self.version) > 12 else self.version)
        self.Draw.text((864-(font_x/2),805-(font_y/2)),self.version.replace("maimai ","") if len(self.version) > 12 else self.version,self.color,font)


        font = ImageFont.truetype(self.other_font, 24, encoding='utf-8')
        # 抽象画作者信息
        content = self.abstract_artist
        newStr = ''
        for item in content:
            newStr += item
            if font.getsize(newStr)[0] > 190:
                self.abstract_artist = newStr + "..."
                break
        font_x,font_y = font.getsize(self.abstract_artist)
        self.Draw.text((864-(font_x/2),865-(font_y/2)),self.abstract_artist,self.color,font)

        festlogo = Image.open(f'src/static/mai/pic/UI_CMN_TabTitle_MaimaiTitle_Ver230_ch.png').convert('RGBA')
        festlogo = festlogo.resize((260,125))
        self.Img.paste(festlogo,(-16,-8), festlogo.split()[3])

# def generate_info(song_id:str):
#     infoobject = Info(song_id)
#     infoobject.Img.show()

# generate_info("11518")
