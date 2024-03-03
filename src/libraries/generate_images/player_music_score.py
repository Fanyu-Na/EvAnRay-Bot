import re
from PIL import Image,ImageFont,ImageDraw
import requests

from src.libraries.maimaidx_music import total_list
import aiohttp
from src.libraries.utils import get_cover_path

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



levels_name = ['Basic','Advanced','Expert','Master']


class MusicScore():
    def __init__(self,song_id:str,verlist,is_abstract:bool) -> None:
        self.arg = song_id
        songinfo = total_list.by_id(self.arg)
        if songinfo:
            self.is_abstract = is_abstract
            self.artist = songinfo['basic_info'].get('artist','')
            self.id = songinfo.get('id','')
            self.genre = songinfo['basic_info'].get('genre','')
            self.bpm = songinfo['basic_info'].get('bpm','')
            self.songname = songinfo['title']
            basic_info = songinfo['basic_info']
            self.ver = basic_info['from']
            self.levels = songinfo['ds']
            self.type = songinfo['type']
            self.paly_data = {}
            if not verlist.get('message') == 'user not exists':
                song_Info_list = {}
                for item in verlist['verlist']:
                    if item['id'] == int(self.id):
                        song_Info_list[item['level_index']] = item

                for level_index in range(len(self.levels)):
                    if song_Info_list.get(level_index):
                        info = song_Info_list.get(level_index)
                        achievements = info['achievements']
                        fc = info['fc']
                        fs = info['fs']
                        icon = self.getIcon(achievements)
                        self.paly_data[level_index] = {"achievements":achievements,"icon":icon,"fc":fc,"fs":fs,"ds":self.levels[level_index],"type":self.type}
                    else:
                        self.paly_data[level_index] = ''

                self.drawImg()
                self.Done = 1


    def getIcon(self,achievements:str):
        achievements = float(achievements)
        if achievements >= 100.5:
            return 'sssp.png'
        elif achievements >= 100:
            return 'sss.png'
        elif achievements >= 99.5:
            return 'ssp.png'
        elif achievements >= 99:
            return 'ss.png'
        elif achievements >= 98:
            return 'sp.png'
        elif achievements >= 97:
            return 's.png'
        elif achievements >= 94:
            return 'aaa.png'
        elif achievements >= 90:
            return 'aa.png'
        elif achievements >= 80:
            return 'a.png'
        elif achievements >= 75:
            return 'bbb.png'
        elif achievements >= 70:
            return 'bb.png'
        elif achievements >= 60:
            return 'b.png'
        elif achievements >= 50:
            return 'c.png'
        else:
            return 'd.png'

    def drawImg(self):
        textColor = (8,48,96)
        Img = Image.open('src/static/mai/info/InfoBG.png').convert('RGBA')


        # if int(self.id) in sz.get_abstract_id_list():
        #     file_name,nickname = sz.get_abstract_file_name(str(self.id))
        #     cover = Image.open(f'src/static/abstract_cover/{file_name}.png')
        # else:
        #     cover = Image.open(f'src/static/mai/cover/{self.id}.png')

                # 添加封面
        if self.is_abstract:
            cover_path = get_cover_path(self.id,True)
            cover = Image.open(cover_path)
            # abstract_data = sz.get_abstract_id_list()
            # if int(self.id) in abstract_data:
            #     file_name,nickname = sz.get_abstract_file_name(str(self.id))

            #     filename = file_name
            #     self.abstract_artist = nickname
            #     cover = Image.open(f'src/static/abstract_cover/{filename}.png')
            # else:
            #     self.abstract_artist = "抽象化未收录"
            #     cover = Image.open(f'src/static/abstract_cover/{str(self.id)}_1.png')
        else:
            self.abstract_artist = "-"
            cover = Image.open(get_cover_path(self.id,False))

            
        cover = cover.resize((200,200))
        Img.paste(cover,(120,155))
        DrawText = ImageDraw.Draw(Img)


        # 添加title
        font = ImageFont.truetype("src/static/SourceHanSans_37.ttf", 30, encoding='utf-8')
        title = self.songname

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
                if font.getsize(title[index:])[0] <= 588:
                    strList.append(title[index+1:])
                    break

            index += 1
        resTitle = ''
        count = 0
        for item in strList:
            resTitle += item+'\n'
            count += 1
        if not is_splite:
            resTitle = self.songname
        DrawText.text((340,148),resTitle,textColor,font)



        font = ImageFont.truetype("src/static/SourceHanSans_37.ttf", 18, encoding='utf-8')
        artist = line_break(self.artist)
        DrawText.text((340,230),artist,textColor,font)

        if self.type == "SD":
            songtypeImg = Image.open('src/static/mai/info/standard.png').convert('RGBA')
        else:
            songtypeImg = Image.open('src/static/mai/info/deluxe.png').convert('RGBA')

        songtypeImg = songtypeImg.resize((75,25))
        Img.paste(songtypeImg,(337,338), songtypeImg.split()[3])
        id = self.id
        genre = self.genre
        bpm = self.bpm
        lastInfo = f'ID {id}          {genre}          BPM {bpm}'
        font = ImageFont.truetype("src/static/SourceHanSans_37.ttf", 21, encoding='utf-8')
        DrawText.text((425,332),lastInfo,textColor,font)

        festlogo = Image.open(f'src/static/mai/pic/UI_CMN_TabTitle_MaimaiTitle_Ver230_ch.png').convert('RGBA')
        festlogo = festlogo.resize((336,162))
        Img.paste(festlogo,(-36,8), festlogo.split()[3])

        for index in [0,1,2,3,4]:
            if self.paly_data.get(index,0):
                # print(self.paly_data.get(index,0))
                font = ImageFont.truetype("src/static/SourceHanSans_17.ttf", 20, encoding='utf-8')
                achievements = str(self.paly_data[index]['achievements']) + '%'
                achievements = f'{achievements:>9}'
                DrawText.text((350,441+(95*index)),achievements,'white',font)
                raticon = self.paly_data[index]['icon']
                RatIconImg = Image.open('src/static/mai/info/'+raticon)
                RatIconImg = RatIconImg.resize((72,37))
                Img.paste(RatIconImg,(500,440+(95*index)), RatIconImg.split()[3])
                if self.paly_data[index]['fc']:
                    fcicon = self.paly_data[index]['fc']
                    fc = Image.open(f'src/static/mai/info/{fcicon}.png').convert('RGBA')
                    fc = fc.resize((56,56))
                    Img.paste(fc,(646,430+(95*index)), fc.split()[3])
                if self.paly_data[index]['fs']:
                    fsicon = self.paly_data[index]['fs']
                    fs = Image.open(f'src/static/mai/info/{fsicon}.png').convert('RGBA')
                    fs = fs.resize((56,56))
                    Img.paste(fs,(702,430+(95*index)), fs.split()[3])

                font = ImageFont.truetype("src/static/SourceHanSans_17.ttf", 18, encoding='utf-8')

                ds = str(self.paly_data[index]['ds'])
                dstext = f'定数 {ds}'
                x0,y0 = font.getsize(dstext)
                DrawText.text((866-(x0/2),444+(95*index)),dstext,'white',font)
            else:
                if self.paly_data.get(index,0) == '':
                    unPlayImg = Image.open(f'src/static/mai/info/unplay{str(index)}.png')
                    unPlayImg = unPlayImg.resize((660,68))
                    Img.paste(unPlayImg,(300,430+(95*index)), unPlayImg.split()[3])
                else:
                    unPlayImg = Image.open(f'src/static/mai/info/nohave{str(index)}.png')
                    unPlayImg = unPlayImg.resize((660,66))
                    Img.paste(unPlayImg,(300,430+(95*index)), unPlayImg.split()[3])

        self.Img = Img

    def getImg(self):
        if self.Done == 1:
            return self.Img
        else:
            return 0