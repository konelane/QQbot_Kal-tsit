'''
Author: KOneLane
Date: 
LastEditors: KOneLane
LastEditTime: 2022-10-12 18:50:16
Description: 
    素材来源于: https://github.com/yuanyan3060/Arknights-Bot-Resource
    灵感来源于：https://github.com/lie5860/ak-guess
    每次更新记得更新以下文件：
        ./resources/character_table.json  -- ./gamedata/excel/character_table.json
        ./resources/handbook_info_table.json  -- ./gamedata/excel/handbook_info_table.json
        ./resources/skin_table.json  -- ./gamedata/excel/skin_table.json
        ./resources/character_list.json    -- 是table的key直接加工的
        代码：
            with open('./character_table.json','r',encoding='utf8')as fp:
                json_data = json.load(fp)
            #     print('这是文件中的json数据：',json_data)
                print('这是读取到文件数据的数据类型：', type(json_data))
                
            json.dump({'list':list(filter(lambda x: x.startswith('char'), list(json_data.keys())))}, open('character_list.json', 'w'))

version: V
'''



import os
import random
import re
import json
import time
from os.path import basename
import pickle

# picture
from io import BytesIO
from typing import Optional, Union
from PIL import Image as PImage, ImageDraw, ImageFilter, ImageFont


from core.decos import DisableModule, check_group, check_member, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from core.Text2Img import generate_img
from database.kaltsitReply import blockList, guessTable
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='AkGuess',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.AkGuess',
).register()


class AkGuess:

    def __init__(self, msg_dict) -> None:
        """初始化猜干员"""
        self.filename = './bot/database/' # 数据库位置
        with open(os.path.dirname(__file__) + './resources/character_table.json','r',encoding='utf8')as fp:
            self.json_data = json.load(fp)
        with open(os.path.dirname(__file__) + './resources/handbook_info_table.json','r',encoding='utf8')as fp:
            self.json_data_drawer = json.load(fp)
        with open(os.path.dirname(__file__) + './resources/skin_table.json','r',encoding='utf8')as fp:
            self.json_data_drawer_list = json.load(fp)
        with open(os.path.dirname(__file__) + './resources/character_list.json','r',encoding='utf8')as fp:
            self.opt_list_random = json.load(fp)

        self.msg_box = {
            'id':msg_dict['id'],
            'name': msg_dict['name'],
            'group_id':msg_dict['group_id'],
            'text_ori':msg_dict['text_ori'],
            'guess_name':msg_dict['text_split'][1],
        }
        self.guess_result = {
            msg_dict['group_id']: {
                'creator_id':msg_dict['id'],
                'guess_time':0,
                'guess_opt':'',
                'already_guessed_list':[]
            }
        } # 据此画图
        self.operator_key = ''
        self.operator_guess_table = {
            '稀有度':0,
            '阵营':'',
            '职业':'',
            '种族':'',
            '画师':'',
            '名称':''
        }
        self.guessReturnMessage = {
            'equal': '对了',
            'smaller': '低了',
            'larger': '高了',
            'wrong': '错了'
        }
        self.answerTable = {
            '稀有度':'',
            '阵营':'',
            '职业':'',
            '种族':'',
            '画师':'',
            '猜测次数':0
        }


    def levelChecker(self, operator_name):
        """根据干员名称，反推星级
        return 返回：所猜干员比正确干员星级高/低
        """
        exists_flag, operator_key = self.operatorChecker(operator_name)
        if (exists_flag == 0) and (operator_key == ''): return 'notExists'
        else:
            return self.checkRarity(operator_key)

    def operatorChecker(self, operator_name):
        exists_flag = 0
        operator_key = ''
        for key, val in self.json_data.items():
            if self.json_data[key]['name'] == operator_name:
                exists_flag = 1
                operator_key = key
                break
        return exists_flag, operator_key


    def checkRarity(self, operator_key_input):
        if self.json_data[operator_key_input]['rarity'] + 1 == self.operator_guess_table['稀有度']:
            return 'equal'
        elif self.json_data[operator_key_input]['rarity'] + 1 > self.operator_guess_table['稀有度']:
            return 'larger'
        elif self.json_data[operator_key_input]['rarity'] + 1 < self.operator_guess_table['稀有度']:
            return 'smaller'


    def checkText(self, textpart, guess_key_input):
        """
        guess_key_input: operator_key
        textpart:
            nationId, profession, race, handbookDict
        """
        if textpart == 'drawName':
            # 230117
            if self.json_data_drawer_list['charSkins'][guess_key_input + '#1']['displaySkin']['drawerList'][0] == \
                self.json_data_drawer_list['charSkins'][self.operator_key + '#1']['displaySkin']['drawerList'][0]:
                return 'equal'
            else: 
                return 'wrong'
        elif textpart == 'race':
            if self.raceFinder(self.operator_key) == self.raceFinder(guess_key_input):
                return 'equal'
            else: 
                return 'wrong'
        else:
            if self.json_data[guess_key_input][textpart] == self.json_data[self.operator_key][textpart] :
                return 'equal'
            else: 
                return 'wrong'


    def initGuessTable(self):
        self.operator_guess_table = {
            '稀有度':int(self.json_data[self.operator_key]['rarity']) + 1,
            '阵营':self.json_data[self.operator_key]['nationId'],
            '职业':self.json_data[self.operator_key]['profession'],
            '种族':self.raceFinder(self.operator_key),
            '画师':self.json_data_drawer_list['charSkins'][self.operator_key + '#1']['displaySkin']['drawerList'][0],
            '名称':self.json_data[self.operator_key]['name']
        }

    def makeAnswerTable(self, opt_guess, guess_operator_key):
        return {
            '猜测干员为': opt_guess,
            '稀有度':self.guessReturnMessage[self.checkRarity(guess_operator_key)],
            '阵营':self.guessReturnMessage[self.checkText('nationId' ,guess_operator_key)],
            '职业':self.guessReturnMessage[self.checkText('profession' ,guess_operator_key)],
            '种族':self.guessReturnMessage[self.checkText('race' ,guess_operator_key)],
            '画师':self.guessReturnMessage[self.checkText('drawName' ,guess_operator_key)],
            '猜测次数':self.guess_temp['guess_time']+1
        }


    def saveGuessMyth(self):
        pickle.dump(self.guess_result, open(self.filename + 'guessMessage.pkl', 'wb'))
        # pickle.dump(self.guess_result, open('D:/goooood/pythondir/bot/database/guessMessage.pkl', 'wb'))

    def loadGuessMyth(self):
        return pickle.load(open(self.filename + 'guessMessage.pkl', 'rb'))
        # return pickle.load(open('D:/goooood/pythondir/bot/database/guessMessage.pkl', 'rb'))

    def helpOut(self):
        return self.operator_key

    def raceFinder(self, operator_key):
        try:
            return str(self.json_data_drawer['handbookDict'][operator_key]['storyTextAudio'][0]['stories'][0]['storyText']).split('\n【种族】')[1].split('\n')[0]
        except:
            return '机器人'


    def outtextProcesser(self):
        out_text = ''
        out_text = out_text.rjust(12, ' ')
        for key, val in self.operator_guess_table.items(): # title
            if key == '画师':
                out_text += key + '|'
            elif key != '名称':
                out_text += key + '|'
        out_text += '\n'

        for item in self.guess_result[self.msg_box['group_id']]['already_guessed_list']: # every_time
            exists_flag, guess_operator_key = self.operatorChecker(item)
            self.answerTable = self.makeAnswerTable(item, guess_operator_key)
            for key, val in self.answerTable.items(): # one_guess_result
                if key == '猜测干员为':
                    out_text += str(self.answerTable[key]).rjust(10-len(self.answerTable[key])*2, ' ') + '：'
                elif key != '猜测次数':
                    out_text += str(self.answerTable[key]) + '|'
            out_text += '\n'
        return out_text[:-2]


    def imageGenerator(self, input_guess_dict):
        '''生成猜测图片 - 根据pkl文件的结果'''
        guess_num=len( input_guess_dict['already_guessed_list'])
        guess_time=input_guess_dict['guess_time']
        # correct or wrong
        if input_guess_dict['already_guessed_list'][guess_num-1] == input_guess_dict['guess_opt']:
            tf_flag = 'right'
        elif input_guess_dict['already_guessed_list'][guess_num-1] != input_guess_dict['guess_opt'] and (guess_time<8):
            tf_flag = 'wrong'
        elif input_guess_dict['already_guessed_list'][guess_num-1] != input_guess_dict['guess_opt'] and guess_time==8:
            tf_flag = 'max'
        size = (880, 220+guess_num*100)
        
        canvas = PImage.new("RGB", size, "#ffffff")
        # load font
        font_path = os.path.dirname(__file__) + "./resources/img/font/OPPOSans-B.ttf"
        save_path = os.path.dirname(__file__)+'./temp.png'

        wrong_logo = PImage.open(os.path.dirname(__file__) + './resources/img/faces/wrong.png')
        up_logo = PImage.open(os.path.dirname(__file__) + './resources/img/faces/up.png')
        down_logo = PImage.open(os.path.dirname(__file__) + './resources/img/faces/down.png')
        correct_logo = PImage.open(os.path.dirname(__file__) + './resources/img/faces/correct.png')
       
        
        wrong_logo = wrong_logo.resize((80, 80))
        wrong_logo = wrong_logo.convert('RGBA')
        up_logo = up_logo.resize((80, 80))
        up_logo = up_logo.convert('RGBA')
        down_logo = down_logo.resize((80, 80))
        down_logo = down_logo.convert('RGBA')
        correct_logo = correct_logo.resize((80, 80))
        correct_logo = correct_logo.convert('RGBA')
        
        # title
        draw = ImageDraw.Draw(canvas)
        font_1 = ImageFont.truetype(font_path, size=16)
        draw.text((20, 35), '猜测干员信息', font=font_1, fill="#000000")
        
        if tf_flag == 'wrong':
            draw.text((20, 55), f'你还有{8-guess_time}/8次机会猜测这位神秘干员', font=font_1, fill="#000000")
        elif tf_flag == 'right':
            draw.text((20, 55), f'猜对了。你一共用了{guess_time}次机会猜测这位神秘干员', font=font_1, fill="#000000")
        elif tf_flag == 'max':
            ans_name = self.operator_guess_table['名称']
            draw.text((20, 55), f'猜了太多次。告诉你答案吧。是 {ans_name}', font=font_1, fill="#000000")

        # head part
        draw = ImageDraw.Draw(canvas)
        font_2 = ImageFont.truetype(font_path, size=20)
        draw.text((50,  105), '稀有度', font=font_2, fill="#000000")
        draw.text((200, 105), '阵营',   font=font_2, fill="#000000")
        draw.text((350, 105), '职业',   font=font_2, fill="#000000")
        draw.text((500, 105), '种族',   font=font_2, fill="#000000")
        draw.text((650, 105), '画师',   font=font_2, fill="#000000")
        draw.text((780, 105), '干员',   font=font_2, fill="#000000")
        
        # guess part 125 + 100*i
        canvas = canvas.convert('RGBA')
        ## 第i个干员 from 0 to 7
        self.operator_key = self.guess_temp['guess_opt']
        for i in range(guess_num):
            font_2 = ImageFont.truetype(font_path, size=20)
            draw = ImageDraw.Draw(canvas)
            draw.text((770, 125 + 100*(i)+25), input_guess_dict['already_guessed_list'][i],   font=font_2, fill="#000000")
            rarity_box = (50  - 10, 135+100*i, 50  + 70, 135+100*i+80)
            nation_box = (200 - 20, 135+100*i, 200 + 60, 135+100*i+80)
            profess_box= (350 - 20, 135+100*i, 350 + 60, 135+100*i+80)
            race_box   = (500 - 20, 135+100*i, 500 + 60, 135+100*i+80)
            drawer_box = (650 - 20, 135+100*i, 650 + 60, 135+100*i+80)
            # add T/F judge
            exists_flag, guess_operator_key = self.operatorChecker(input_guess_dict['already_guessed_list'][i])
            if self.checkRarity(guess_operator_key) == 'larger': canvas.paste(up_logo, rarity_box, up_logo)
            elif self.checkRarity(guess_operator_key) == 'smaller': canvas.paste(down_logo, rarity_box, down_logo)
            else: canvas.paste(correct_logo, rarity_box, correct_logo)
            
            if self.checkText('nationId', guess_operator_key) == 'wrong': canvas.paste(wrong_logo, nation_box, wrong_logo)
            else: canvas.paste(correct_logo, nation_box, correct_logo)

            if self.checkText('profession', guess_operator_key) == 'wrong': canvas.paste(wrong_logo, profess_box, wrong_logo)
            else: canvas.paste(correct_logo, profess_box, correct_logo)

            if self.checkText('race', guess_operator_key) == 'wrong': canvas.paste(wrong_logo, race_box, wrong_logo)
            else: canvas.paste(correct_logo, race_box, correct_logo)

            if self.checkText('drawName', guess_operator_key) == 'wrong': canvas.paste(wrong_logo, drawer_box, wrong_logo)
            else: canvas.paste(correct_logo, drawer_box, correct_logo)

        
        
        # foot part 55
        draw = ImageDraw.Draw(canvas)
        font_5 = ImageFont.truetype(font_path, size=12)
        timestr = time.strftime("%Y/%m/%d/ %p%I:%M:%S", time.localtime())
        draw.text((20, canvas.size[1] - 55), f"Kal'tsit Bot ©2022\n{timestr}", font=font_5, fill="#000000")
        
        
        # 角落加入m3标志
        m3path = os.path.dirname(__file__) + './resources/img/M3.png'
        tmp_img = PImage.open(m3path) # 需要传的图片
        tmp_img = tmp_img.resize((40, 40))
        tmp_img = tmp_img.convert('RGBA')
        box = (180, canvas.size[1]-65, 180 + tmp_img.width, canvas.size[1]-65+tmp_img.height)   # 底图上需要P掉的区域
        canvas.paste(tmp_img, box, tmp_img)
        
        canvas.save(save_path) #保存图片
        return save_path



    def guessAction(self):
        """猜干员总流程"""
        opt_guess = self.msg_box['guess_name']
        self.guess_result.update(self.loadGuessMyth()) # 非第一次则加载记录
        # 1. 新建流程
        if opt_guess == 'new':
            temp_opt_key = random.choice(list(self.opt_list_random['list']))
            if temp_opt_key == 'char_1001_amiya2': temp_opt_key = 'char_1001_amiya' # bug key
            while temp_opt_key in ['char_505_rcast', 'char_504_rguard', 'char_514_rdfend', 'char_507_rsnipe', 'char_506_rmedic']:
                temp_opt_key = random.choice(list(self.opt_list_random['list'])) # 无属性的干员
            
            self.guess_result.update({
                self.msg_box['group_id']: {
                    'creator_id':self.msg_box['id'],
                    'guess_time':0,
                    'guess_opt':temp_opt_key,
                    'already_guessed_list':[]
                }
            }
            )
            
        

        # 2. 查询当前群有无猜测记录
        
        if opt_guess == 'new': 
            self.saveGuessMyth()
            return 'new', None
        

        if self.msg_box['group_id'] in self.guess_result.keys() and self.guess_result[self.msg_box['group_id']]['guess_opt'] != '':
            self.guess_temp = self.guess_result[self.msg_box['group_id']] # 取出答题结果
            self.operator_key = self.guess_temp['guess_opt']
            self.initGuessTable() # 更新正确答案干员的信息在self.operator_guess_table中
        else:
            return 'noRecord', None

        # 2. 查询干员是否正确
        exists_flag, guess_operator_key = self.operatorChecker(opt_guess)
        if (exists_flag == 0) or (guess_operator_key == ''): 
            print('干员不存在')
            return 'notExists', None
        elif guess_operator_key == self.guess_temp['guess_opt']:
            print('猜对了')
            self.answerTable = self.makeAnswerTable(opt_guess, guess_operator_key)

            self.guess_result[self.msg_box['group_id']]['guess_time'] += 1
            self.guess_result[self.msg_box['group_id']]['already_guessed_list'].append(opt_guess)
            # out_text = self.outtextProcesser()
            picture_path = self.imageGenerator(self.guess_result[self.msg_box['group_id']])

            del self.guess_result[self.msg_box['group_id']]
            self.saveGuessMyth()
            return 'rightAnswer', picture_path

        else:
            # 检查不正确，返回各属性值
            self.answerTable = self.makeAnswerTable(opt_guess, guess_operator_key)

            self.guess_result[self.msg_box['group_id']]['guess_time'] += 1
            self.guess_result[self.msg_box['group_id']]['already_guessed_list'].append(opt_guess)
            picture_path = self.imageGenerator(self.guess_result[self.msg_box['group_id']])

            if self.guess_temp['guess_time'] >= 8:
                out_tuple = ('done', picture_path)
                del self.guess_result[self.msg_box['group_id']]
                
                self.saveGuessMyth()
                return out_tuple
            else:
                # 保存结果
                self.saveGuessMyth()
                # out_text = self.outtextProcesser()

                return 'wrong', picture_path



@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#g')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def AkGuessApp(
    app: Ariadne, 
    message: MessageChain,
    group: Group,
    member: Member 
):

    slightly_inittext = MessageProcesser(message,group,member)
    msg_info_dict = slightly_inittext.text_processer()

    guess_obj = AkGuess(msg_info_dict)
    out_cmd, out_dir = guess_obj.guessAction()
    if out_cmd == 'rightAnswer':
        await app.sendGroupMessage(group, MessageChain.create(
            Plain(random.sample(guessTable,1)[0] + '\n'),
            Image(path=out_dir)
        ))
    elif out_cmd =='wrong':
        await app.sendGroupMessage(group, MessageChain.create(
            Plain('错了。' + '\n'),
            Image(path=out_dir)
        ))
    elif out_cmd =='notExists':
        await app.sendGroupMessage(group, MessageChain.create(
            Plain('不存在这个干员。')
        ))
    elif out_cmd =='noRecord':
        await app.sendGroupMessage(group, MessageChain.create(
            Plain('这里没有题。')
        ))
    elif out_cmd =='done':
        await app.sendGroupMessage(group, MessageChain.create(
            Plain('猜了太多次。告诉你答案吧。'),
            Image(path=out_dir)
        ))
    elif out_cmd =='new':
        await app.sendGroupMessage(group, MessageChain.create(
            Plain('好了，你猜吧。')
        ))





# if __name__ =='__main__':
#     msg_dict = {
#         'id':591016144,
#         'name': 'hehe',
#         'group_id':114514,
#         'text_ori':'#g 233',
#         'text_split':['#g','233']

#     }
#     guess_obj = AkGuess(msg_dict)
#     print(guess_obj.guessAction()[1])