#! /usr/bin/env python3
# coding:utf-8
'''
Author: KOneLane
Date: 2022-05-22 14:40:40
LastEditors: KOneLane
LastEditTime: 2022-03-18 10:37:16
Description: 
    素材来源于: https://github.com/yuanyan3060/Arknights-Bot-Resource
    每次更新记得更新以下文件：
        ./data/dynamic/gamedata/character_table.json  -- ./gamedata/excel/character_table.json
        ./data/dynamic/portrait/     -- 素材包根目录
version: V
'''
import asyncio
import os
import random
import sqlite3
import time
from os.path import basename
from uuid import uuid4
import json
from PIL import Image as Pimg
from PIL import ImageFont, ImageDraw

from core.config.BotConfig import AdminConfig, BasicConfig
from core.decos import check_group, check_member, DisableModule, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import (blockList, text_table)

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight, UnionMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema


channel = Channel.current()
module_name = basename(__file__)[:-3]
Module(
    name='Gacha',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Gacha',
).register()

# 卡池类型 | 池子修改 normal newyear fullyear halfyear combine summer
GACHA_POOL = 'summer'


class GachaClass:
    """凯尔希抽卡功能 连接用户数据库
    
    """
    def __init__(self, msg_out) -> None:
        self.filename = BasicConfig().databaseUrl # 数据库位置
        self.signin_box = {
            'id':msg_out['id'],
            'signin_uid':str(uuid4()),
            'name': msg_out['name'],
            'exp':0,
            'total_days':0,
            'consecutive_days':0,
            'is_signin_consecutively':0,
            'reliance':0,
            'credit':0,
            'last_signin_time': "2021/05/12-12:00:00",
            # 'already_signin':0,

            'group_id':msg_out['group_id'],
            'text_ori':msg_out['text_ori'],
            'signin_new_name': msg_out['name'],
        }
        self.TableHeader = [
            'id','signin_uid','name','exp','total_days','consecutive_days',
            'is_signin_consecutively','reliance','credit','last_signin_time',#'already_signin'
        ]
        self.gachaTableHeader = [
            'id', 'u_name', 'gacha_num', 'six', 'six_r', 
            'five', 'five_r', 'four', 'four_r', 'three', 'three_r', 'last_gacha_time'
        ]
        self.gachaTableHeader_ZH = [
             'qq','用户昵称', '抽卡次数', '六星', '六星率', '五星', '五星率', '四星', '四星率', '三星', '三星率', '最后抽卡时间'
        ]

        # 卡池
        self.up_list_six = ['纯烬艾雅法拉','琳琅诗怀雅']
        self.up_list_five = ['青枳']
        # 全部寻访池
        # self.limit_list = [
        #     '年','夕','令',
        #     '迷迭香','W','浊心斯卡蒂',
        #     '假日威龙陈','耀骑士临光','归溟幽灵鲨','百炼嘉维尔',
        # ]
        self.limit_dict = {
            'newyear':['年','夕','令','重岳'],
            'fullyear':['W','浊心斯卡蒂','归溟幽灵鲨','缪尔赛思','迷迭香','耀骑士临光'],
            'summer':['假日威龙陈','百炼嘉维尔','纯烬艾雅法拉'],
            'halfyear':['迷迭香','耀骑士临光','浊心斯卡蒂','缄默德克萨斯']
        }
        


        self.six_list = [
            '能天使','推进之王','伊芙利特','艾雅法拉','安洁莉娜','闪灵','夜莺','星熊','塞雷娅','银灰','斯卡蒂',
            '陈','黑','赫拉格','麦哲伦','莫斯提马','煌','阿','刻俄柏','风笛','傀影','温蒂','早露','铃兰','棘刺',
            '森蚺','史尔特尔','瑕光','泥岩','山','空弦','嵯峨','异客','凯尔希','卡涅利安','帕拉斯','水月','琴柳',
            '远牙','焰尾','灵知','老鲤','澄闪','菲亚梅塔','号角','艾丽妮','黑键','多萝西','鸿雪','玛恩纳','白铁',
            '斥罪','林','焰影苇草','仇白','麒麟X夜刀','伊内丝','霍尔海雅','圣约送葬人','提丰','琳琅诗怀雅'
        ]
        
        self.five_list = [
            '白面鸮','凛冬','德克萨斯','芙兰卡','拉普兰德','幽灵鲨','蓝毒','白金','陨星','天火','梅尔','赫默',
            '华法琳','临光','红','雷蛇','可颂','普罗旺斯','守林人','崖心','初雪','真理','空','狮蝎','食铁兽',
            '夜魔','诗怀雅','格劳克斯','星极','送葬人','槐琥','苇草','布洛卡','灰喉','吽','惊蛰','慑砂','巫恋',
            '极境','石棉','月禾','莱恩哈特','断崖','蜜蜡','贾维','安哲拉','燧石','四月','奥斯塔','絮雨','卡夫卡',
            '爱丽丝','乌有','熔泉','赤冬','绮良','羽毛笔','桑葚','灰毫','蚀清','极光','夜半','夏栎','风丸','洛洛',
            '掠风','晓歌','承曦格雷伊','濯尘芙蓉','但书','明椒','子月','火哨','和弦','铎铃','火龙S黑角','洋灰','玫拉',
            '空构','寒檀','青枳'
        ]
        self.four_list = [
            '夜烟','远山','杰西卡','流星','白雪','清道夫','红豆','杜宾','缠丸','霜叶','慕斯','砾',
            '暗索','末药','调香师','角峰','蛇屠箱','古米','深海色','地灵','阿消','猎蜂','格雷伊','苏苏洛',
            '桃金娘','红云','梅','安比尔','宴','刻刀','波登可','卡达','孑','酸糖','芳汀','泡泡','杰克',
            '松果','豆苗','深靛','罗比菈塔','褐果','铅踝','休谟斯'
        ]
        self.three_list = [
            '芬','香草','翎羽','玫兰莎','卡缇','米格鲁','克洛丝','炎熔','芙蓉','安赛尔','史都华德','梓兰','空爆',
            '月见夜','斑点','泡普卡',
        ]
        self.gachabox = {
            'id':msg_out['id'],
            'u_name': msg_out['name'],
            'gacha_num':0, 
            'six':0, 
            'six_r':0.0, 
            'five':0, 
            'five_r':0.0, 
            'four':0, 
            'four_r':0.0, 
            'three':0, 
            'three_r':0.0 , 
            'last_gacha_time':"2021/05/12-12:00:00", 
        }
        


    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return con,cur



    def __dataSave(self):
        """保存当前用户数据"""
        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time) VALUES(?,?,?,?,?,?,?,?,?,?)",(
            self.signin_box['id'], self.signin_box['signin_uid'],  self.signin_box['name'], self.signin_box['exp'], \
            self.signin_box['total_days'], self.signin_box['consecutive_days'], self.signin_box['is_signin_consecutively'], \
            self.signin_box['reliance'], self.signin_box['credit'], self.signin_box['last_signin_time']
            )
        )
        con.commit()
        con.close()
        pass


    def __searchSigninData(self):
        dict_of_text = None
        con,cur = self.__connectSqlite()
        try:
            cur.execute("SELECT * FROM `signin` WHERE id = ? ",(self.signin_box['id'],))
            test = list(cur.fetchall()[0])

            dict_of_text = dict(zip(self.TableHeader, test))
        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text


    def GachaAction(self):
        """抽卡功能入口"""
        if self.signin_box['text_ori'] in ["#抽卡",'#十连']:
            # 1.查询信用值
            if self.signin_box['id'] in [AdminConfig().masterId]: return 'gacha'
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return ''

            # 2.向DarkTemple返回指令
            if self.signin_box['reliance'] >= 200 and self.signin_box['credit'] >= 5:
                # 满信赖抽卡
                self.signin_box['credit'] -= 5
                self.__dataSave()
                return 'gacha'
            elif self.signin_box['credit'] >= 10:
                self.signin_box['credit'] -= 10
                self.__dataSave()
                return 'gacha'
            else:
                return '你的信用不足。'


    def random_pick(self, some_list, probabilities): 
        x = random.uniform(0,1) 
        cumulative_probability = 0.0 
        for item, item_probability in zip(some_list, probabilities): 
            cumulative_probability += item_probability 
            if x < cumulative_probability:
                break 
        return item 

    def gachaOperatorChoice(self, gacha_pool = 'normal'):
        '''抽卡干员选择'''
        
        gacha_list = []
        out_list = []
        out_dict = {'6':0, '5':0, '4':0, '3':0, }
        for _ in range(10):
            out_one = self.random_pick(['6','5','4','3'], [0.03, 0.08, 0.50, 0.39])
            out_list.append(out_one)
            out_dict[out_one] += 1
        if gacha_pool == 'normal':
            '''标准寻访'''
            while len(out_list) >0 :
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_six))
                    else: gacha_list.append(random.choice([x for x in self.six_list if x not in self.up_list_six]))
                if rarity == '5': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_five))
                    else: gacha_list.append(random.choice([x for x in self.five_list if x not in self.up_list_five]))
            
        ############## 限定 ###################
        elif gacha_pool == 'newyear':
            # 限定池 概率不一样
            # 还没写完
            while len(out_list) >0 :
                temp_opt_list = []
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    flag = self.random_pick(['pool','else'], [0.7, 0.3])
                    if flag == 'pool': 
                        gacha_list.append(random.choice(self.up_list_six))
                    else: 
                        # TODO 在6★剩余出率【30%】中以5倍权值出率提升）
                        temp_opt_list.extend(self.six_list)
                        temp_opt_list.extend([x for x in self.limit_dict['newyear'] if x not in self.up_list_six]*5)
                        gacha_list.append(random.choice(temp_opt_list))
                if rarity == '5': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_five))
                    else: gacha_list.append(random.choice([x for x in self.five_list if x not in self.up_list_five]))

        elif gacha_pool == 'fullyear':
            # 限定池 概率不一样
            # 还没写完
            while len(out_list) >0 :
                temp_opt_list = []
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    flag = self.random_pick(['pool','else'], [0.7, 0.3])
                    if flag == 'pool': 
                        gacha_list.append(random.choice(self.up_list_six))
                    else: 
                        # TODO 在6★剩余出率【30%】中以5倍权值出率提升）
                        temp_opt_list.extend(self.six_list)
                        temp_opt_list.extend([x for x in self.limit_dict['fullyear'] if x not in self.up_list_six]*5)
                        gacha_list.append(random.choice(temp_opt_list))
                if rarity == '5': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_five))
                    else: gacha_list.append(random.choice([x for x in self.five_list if x not in self.up_list_five]))

        elif gacha_pool == 'summer':
            # 限定池 概率不一样
            # 还没写完
            while len(out_list) >0 :
                temp_opt_list = []
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    flag = self.random_pick(['pool','else'], [0.7, 0.3])
                    if flag == 'pool': 
                        gacha_list.append(random.choice(self.up_list_six))
                    else: 
                        # TODO 在6★剩余出率【30%】中以5倍权值出率提升）
                        temp_opt_list.extend(self.six_list)
                        temp_opt_list.extend([x for x in self.limit_dict['summer'] if x not in self.up_list_six]*5)
                        print(temp_opt_list)
                        gacha_list.append(random.choice(temp_opt_list))
                if rarity == '5': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_five))
                    else: gacha_list.append(random.choice([x for x in self.five_list if x not in self.up_list_five]))

        elif gacha_pool == 'halfyear':
            # 限定池 概率不一样
            # 还没写完
            while len(out_list) >0 :
                temp_opt_list = []
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    flag = self.random_pick(['pool','else'], [0.7, 0.3])
                    if flag == 'pool': 
                        gacha_list.append(random.choice(self.up_list_six))
                    else: 
                        # TODO 在6★剩余出率【30%】中以5倍权值出率提升）
                        temp_opt_list.extend(self.six_list)
                        temp_opt_list.extend([x for x in self.limit_dict['halfyear'] if x not in self.up_list_six]*5)
                        gacha_list.append(random.choice(temp_opt_list))
                if rarity == '5': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_five))
                    else: gacha_list.append(random.choice([x for x in self.five_list if x not in self.up_list_five]))


        ############## 联合寻访 ###################
        elif gacha_pool == 'combine':
            # 联合寻访 五星与六星不会歪 ！ 
            while len(out_list) >0 :
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    gacha_list.append(random.choice(self.up_list_six))
                if rarity == '5': 
                    gacha_list.append(random.choice(self.up_list_five))
                    
        return gacha_list, out_dict


    def __mixPicture(self, opt_list, operator_dict_lite):
        """
        opt_id - 十连中的第几位干员
        1位干员图片合并
        """
        save_path = os.path.dirname(__file__)+'./temp.png'
        # 1. 底图
        background_dir = os.path.dirname(__file__) + './data/static/gacha_background_img/2.png'

        base_img = Pimg.open(background_dir)
        base_img.convert('RGBA')

        for opt_id in range(10):
            opt = opt_list.pop(0)
            opt_dict_temp = operator_dict_lite[opt]
             # 2. 添加星级
            rarity_dir = os.path.dirname(__file__) + './data/static/gacha_rarity_img/' + str(opt_dict_temp['rarity']) + '.png'
            rarity_background_dir = os.path.dirname(__file__) + './data/static/gacha_background_img/' + str(opt_dict_temp['rarity']) + '.png'
            
            # 3. 添加角色立绘
            character_dir = os.path.dirname(__file__) + './data/dynamic/portrait/' + opt_dict_temp['pic_id'] + '_1.png'

            # 4. 添加职业
            profession_dir = os.path.dirname(__file__) + './data/static/profession_img/' + opt_dict_temp['profession'] + '.png'

            # 底图
            tmp_img = Pimg.open(rarity_dir) # 需要传的图片
            box = (27+(opt_id)*122, 0, 27+(opt_id)*122+tmp_img.width, tmp_img.height)
            tmp_img = tmp_img.convert('RGBA')
            r, g, b, a = tmp_img.split()
            base_img.paste(tmp_img, box, mask=a)

            # 图片下端
            tmp_img = Pimg.open(rarity_background_dir) # 需要传的图片
            tmp_img = tmp_img.crop((27+(opt_id)*122, 535, 27+(opt_id)*122+tmp_img.width, 535+tmp_img.height))
            box = (27+(opt_id)*122, 535, 27+(opt_id)*122+tmp_img.width, 535+tmp_img.height)
            out = tmp_img.convert('RGBA')
            r, g, b, a = out.split()
            base_img.paste(out, box, mask=a)
            
            # 角色立绘
            tmp_img = Pimg.open(character_dir)
            tmp_img = tmp_img.crop((27, 0, tmp_img.width-27, tmp_img.height)) # 取中间部分的图片
            box = (round(27+(opt_id)*122.3),175,round(27+(opt_id)*122.3)+tmp_img.width, 175+tmp_img.height) 
            tmp_img = tmp_img.convert('RGBA')
            # print(tmp_img.size)
            r, g, b, a = tmp_img.split()
            base_img.paste(tmp_img, box, mask=a)

            # 职业图
            tmp_img = Pimg.open(profession_dir)
            box = ( round(34+(opt_id)*122.3),490,round(34+(opt_id)*122.3)+tmp_img.width,490+tmp_img.height)
            tmp_img = tmp_img.convert('RGBA')
            r, g, b, a = tmp_img.split()
            base_img.paste(tmp_img, box, mask=a)

        # base_img.show()
        # 加一个m3标志
        ## 角落加入m3标志
        base_img.convert('RGBA')
        
        m3path = os.path.dirname(__file__) + './data/static/M3.png'
        tmp_img = Pimg.open(m3path) # 需要传的图片
        tmp_img = tmp_img.resize((40, 40))
        tmp_img = tmp_img.convert('RGBA')
        box = (27, 660, 27+tmp_img.width, 660+tmp_img.height)   # 底图上需要P掉的区域
        base_img.paste(tmp_img, box, tmp_img)
        
        # footer
        font_path = os.path.dirname(__file__) + "./data/static/OPPOSans-B.ttf"
        font_5 = ImageFont.truetype(font_path, size=12)
        draw = ImageDraw.Draw(base_img)
        timestr = time.strftime("%Y/%m/%d/ %p%I:%M:%S", time.localtime())
        draw.text((15, base_img.size[1] - 55), f"Kal'tsit Bot ©2022\n{timestr}", font=font_5, fill="#cccccc")

        # base_img.show()

        base_img.save(save_path) #保存图片
        return save_path



    def gachaPicMake(self, opt_list):
        """抽卡图制作"""

        operator_dict_lite = {}
        '''需求: 名称 星级 图片id 职业'''
        with open(os.path.dirname(__file__) + './data/dynamic/gamedata/character_table.json','r',encoding='utf8')as fp:
            json_data = json.load(fp)

        avaliable_list = []
        avaliable_list.extend(opt_list)

        for key, val in json_data.items():
            if val['name'] not in avaliable_list:
                continue
            operator_dict_lite.update({val['name']:{
                'name':val['name'],
                'profession': val['profession'],
                'rarity':val['rarity'],
                'pic_id':key
            }})
        
        return self.__mixPicture( opt_list, operator_dict_lite)

        
    def gachaPoolSet(self):
        """卡池相关 - 懒"""



    def gachaDataSave(self, gacha_list, star_dict):
        """resource: gacha
        保存十连数据 - 表： gachaData
        表头 - 用户昵称 | qq | 抽卡次数 | 六星 | 六星率 | 五星 | 五星率 | 四星 | 四星率 | 三星 | 三星率 | 最后抽卡时间 |
        表头 - u_name  | id | gacha_num| six | six_r  | five| five_r | four | four_r | three| three_r | last_gacha_time |

        暂时不区分是谁
        """
        dict_of_text = self.gachaDataGet()
        if dict_of_text is None: dict_of_text = self.gachabox
        self.gachabox.update(dict_of_text)

        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `gachaData` ( id, u_name, gacha_num, six, six_r, \
            five, five_r, four, four_r, three, three_r, last_gacha_time) VALUES(?,?,?,?,?, ?,?,?,?,?, ?,?)",(
            self.gachabox['id'], self.gachabox['u_name'], self.gachabox['gacha_num'] + 1, self.gachabox['six'] + star_dict['6'], round((self.gachabox['six'] + star_dict['6'])/(10*(self.gachabox['gacha_num'] + 1)), 4), 
            self.gachabox['five'] + star_dict['5'], round((self.gachabox['five'] + star_dict['5'])/(10*(self.gachabox['gacha_num'] + 1)), 4), 
            self.gachabox['four'] + star_dict['4'], round((self.gachabox['four'] + star_dict['4'])/(10*(self.gachabox['gacha_num'] + 1)), 4),     
            self.gachabox['three'] + star_dict['3'], round((self.gachabox['three'] + star_dict['3'])/(10*(self.gachabox['gacha_num'] + 1)), 4), 
            time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
            )
        )
        con.commit()
        con.close()

        

    def gachaDataGet(self):
        """resource: gacha
        查询十连数据 - 表： gachaData
        表头 - 用户昵称 | qq | 抽卡次数 | 六星 | 六星率 | 五星 | 五星率 | 四星 | 四星率 | 三星 | 三星率 | 最后抽卡时间 |
        表头 - u_name  | id | gacha_num| six | six_r  | five| five_r | four | four_r | three| three_r | last_gacha_time |
        """
        dict_of_text = None
        con,cur = self.__connectSqlite()
        try:
            cur.execute("SELECT * FROM `gachaData` WHERE id = ? ",(self.signin_box['id'],))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.gachaTableHeader, test))

        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text



    def creditRequire(self):
        """查询信用值"""
        if self.signin_box['text_ori'] in ["#信用",'#credit']:
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return 0
        return self.signin_box['credit']



@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                UnionMatch('#抽卡','#十连','#抽卡数据','#数据')
            ]) 
        ],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Gacha_Gacha(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    
    """【FUNCTION】抽卡"""
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   

    if msg_info_dict['text_split'][0] not in ['#抽卡','#十连','#抽卡数据','#数据']:
        return 
    elif msg_info_dict['text_split'][0] in ['#抽卡数据','#数据']:
        temp = GachaClass(msg_info_dict)
        out_dict = temp.gachaDataGet()
        if out_dict is not None:
            outtext = ''
            for i in range(len(temp.gachaTableHeader_ZH)):
                if temp.gachaTableHeader_ZH[i] in ['抽卡次数', '六星', '六星率', '五星', '五星率', '四星', '四星率', '三星', '三星率', '最后抽卡时间']:
                    outtext += temp.gachaTableHeader_ZH[i] +': '+ str(out_dict[temp.gachaTableHeader[i]]) +'\n'

            await app.send_group_message(group, MessageChain([
                Plain(member.name+' 的抽卡记录为: \n'+outtext)
            ]))
        else:
            await app.send_group_message(group, MessageChain([
                Plain('博士 ' + member.name+' 无记录')
            ]))

    else:
        temp = GachaClass(msg_info_dict)
        outtext = temp.GachaAction()
        if outtext == 'gacha':
            gacha_list, star_dict = temp.gachaOperatorChoice(GACHA_POOL) # 池子修改 normal newyear fullyear halfyear combine summer
            out_dir = temp.gachaPicMake(gacha_list)
            temp.gachaDataSave(gacha_list, star_dict)
            outtext2 = random.sample(text_table,1)[0]

            await app.send_group_message(group, MessageChain([
                At(member.id),
                Plain('  '+outtext2),
                Image(path=out_dir)
            ]))


        elif outtext == '':
            await app.send_group_message(group, MessageChain([
                Plain('这里没有给你的东西，去打卡上班。')
            ]))

        else:
            await app.send_group_message(group, MessageChain([
                Plain(outtext)
            ]))



@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                UnionMatch('#信用','#credit')
            ]) 
        ],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Gacha_Gacha(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    
    """【FUNCTION】查信用"""
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   

    if msg_info_dict['text_split'][0] not in ['#信用','#credit']:
        return 
    else:
        temp = GachaClass(msg_info_dict)
        outtext = temp.creditRequire()
        if outtext != 0:
            await app.send_group_message(group, MessageChain([
                Plain('博士的信用点为： ' + str(outtext))
            ]))


        elif outtext == 0:
            await app.send_group_message(group, MessageChain([
                Plain('这里没有给你的东西，去打卡上班。')
            ]))






# if __name__ =='__main__':
#     msg_dict = {
#         'id':591016144,
#         'name': 'hehe',
#         'group_id':114514,
#         'text_ori':'#抽卡',
#     }
#     gacha_obj = GachaClass(msg_dict)
#     print(gacha_obj.gachaOperatorChoice('normal'))
#     gacha_obj.gachaPicMake(['调香师', '梅', '红云', '能天使', '月禾', '地灵', '孑', '远山', '翎羽', '古米']) # 临时用一下
#     gacha_obj.gachaDataSave()