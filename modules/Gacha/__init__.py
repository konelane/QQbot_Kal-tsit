#! /usr/bin/env python3
# coding:utf-8
'''
Author: KOneLane
Date: 2022-05-22 14:40:40
LastEditors: KOneLane
LastEditTime: 2022-03-18 10:37:16
Description: 
    rebuild from github: https://github.com/Redlnn/signin-image-generator
    edit by KOneLane (AGPL-3.0)
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

from core.decos import check_group, check_member, DisableModule
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




class GachaClass:
    """凯尔希抽卡功能 连接用户数据库
    
    """
    def __init__(self, msg_out) -> None:
        self.filename = './bot/database/' # 数据库位置
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
        # 卡池
        self.up_list_six = ['能天使','斯卡蒂','山','凯尔希']
        self.up_list_five = ['拉普兰德','雷蛇','普罗旺斯','食铁兽','月禾','赤东']
        # 全部寻访池
        self.limit_list = [
            '年','夕','令',
            '迷迭香','W','浊心斯卡蒂',
            '假日威龙陈','耀骑士临光','归溟幽灵鲨',
        ]
        self.six_list = [
            '能天使','推进之王','伊芙利特','艾雅法拉','安洁莉娜','闪灵','夜莺','星熊','塞雷娅','银灰','斯卡蒂',
            '陈','黑','赫拉格','麦哲伦','莫斯提马','煌','阿','刻俄柏','风笛','傀影','温蒂','早露','铃兰','棘刺',
            '森蚺','史尔特尔','瑕光','泥岩','山','空弦嵯峨','异客','凯尔希','卡涅利安','帕拉斯','水月','琴柳',
            '远牙','焰尾','灵知','老鲤','澄闪','菲亚梅塔','号角','艾丽妮',
        ]
        self.five_list = [
            '白面鸮','凛冬','德克萨斯','芙兰卡','拉普兰德','幽灵鲨','蓝毒','白金','陨星','天火','梅尔','赫默',
            '华法琳','临光','红','雷蛇','可颂','普罗旺斯','守林人','崖心','初雪','真理','空','狮蝎','食铁兽',
            '夜魔','诗怀雅','格劳克斯','星极','送葬人','槐琥','苇草','布洛卡','灰喉','哗','惊蛰','慑砂','巫恋',
            '极境','石棉','月禾','莱恩哈特','断崖','蜜蜡','贾维','安哲拉','燧石','四月','奥斯塔','絮雨','卡夫卡',
            '爱丽丝','乌有','熔泉','赤冬','绮良','羽毛笔','桑葚','灰毫','蚀清','极光','夜半','夏栎','风丸','洛洛',
            '掠风',
        ]
        self.four_list = [
            '夜烟','远山','杰西卡','流星','白雪','清道夫','红豆','杜宾','缠丸','霜叶','慕斯','砾',
            '暗索','末药','调香师','角峰','蛇屠箱','古米','深海色','地灵','阿消','猎蜂','格雷伊','苏苏洛',
            '桃金娘','红云','梅','安比尔','宴','刻刀','波登可','卡达','孑','酸糖','芳汀','泡泡','杰克',
            '松果','豆苗','深靛','罗比菈塔','褐果',
        ]
        self.three_list = [
            '芬','香草','翎羽','玫兰莎','卡缇','米格鲁','克洛丝','炎熔','芙蓉','安赛尔','史都华德','梓兰','空爆',
            '月见夜','斑点','泡普卡',
        ]
        


    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def databaseInit(self):
        """建表"""
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `signin` (  \
                id INTEGER PRIMARY KEY NOT NULL, signin_uid TEXT, name TEXT, \
                exp INTEGER, total_days INTEGER, consecutive_days INTEGER, is_signin_consecutively INTEGER, \
                reliance INTEGER, credit INTEGER, last_signin_time TEXT \
            )")
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time ) VALUES(?,?,?,?,?,?,?,?,?,?)",(
            591016144, str(uuid4()),  '凯尔希初始化', 200, 365, 10, 
            1, 120, 2000, time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
            )
        )
        con.commit()
        con.close()
        print('建表成功')


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
        '''抽卡功能入口'''
        if self.signin_box['text_ori'] in ["#抽卡",'#十连']:
            # 1.查询信用值
            if self.signin_box['id'] in [2238701273]: return 'gacha'
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return ''

            # 2.向DarkTemple返回指令
            if self.signin_box['credit'] >= 10:
                self.signin_box['credit'] -= 10
                self.__dataSave()
                return 'gacha'
            else:
                return '信用不足。'


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
            

        elif gacha_pool == 'limit':
            # 限定池 概率不一样
            # 还没写完
            while len(out_list) >0 :
                rarity = out_list.pop(0)
                if rarity == '4': gacha_list.append(random.choice(self.four_list))
                if rarity == '3': gacha_list.append(random.choice(self.three_list))
                if rarity == '6': 
                    flag = self.random_pick(['pool','else'], [0.7, 0.3])
                    if flag == 'pool': 
                        gacha_list.append(random.choice(self.up_list_six))
                    else: 
                        # TODO 在6★剩余出率【30%】中以5倍权值出率提升）
                        gacha_list.append(random.choice([x for x in self.six_list if x not in self.up_list_six]))
                if rarity == '5': 
                    flag = self.random_pick(['pool','else'], [0.5, 0.5])
                    if flag == 'pool': gacha_list.append(random.choice(self.up_list_five))
                    else: gacha_list.append(random.choice([x for x in self.five_list if x not in self.up_list_five]))

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
                    
        return gacha_list


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

            # 3. 添加角色立绘
            character_dir = os.path.dirname(__file__) + './data/dynamic/char_img/' + opt_dict_temp['pic_id'] + '.png'

            # 4. 添加职业
            profession_dir = os.path.dirname(__file__) + './data/static/profession_img/' + opt_dict_temp['profession'] + '.png'

            
            tmp_img = Pimg.open(rarity_dir) # 需要传的图片
            box = (27+(opt_id)*122, 0, 27+(opt_id)*122+tmp_img.width, tmp_img.height)
            tmp_img = tmp_img.convert('RGBA')
            # print(base_img.size, tmp_img.size)
            r, g, b, a = tmp_img.split()
            base_img.paste(tmp_img, box, mask=a)
            
            
            tmp_img = Pimg.open(character_dir)
            box = (round(27+(opt_id)*122.3),175,round(27+(opt_id)*122.3)+tmp_img.width, 175+tmp_img.height) 
            tmp_img = tmp_img.convert('RGBA')
            r, g, b, a = tmp_img.split()
            base_img.paste(tmp_img, box, mask=a)

             
            tmp_img = Pimg.open(profession_dir)
            box = ( round(34+(opt_id)*122.3),490,round(34+(opt_id)*122.3)+tmp_img.width,490+tmp_img.height)
            tmp_img = tmp_img.convert('RGBA')
            r, g, b, a = tmp_img.split()
            base_img.paste(tmp_img, box, mask=a)

        # base_img.show()
        
        base_img.save(save_path) #保存图片
        return save_path



    def gachaPicMake(self, opt_list):
        '''抽卡图制作'''

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
        '''卡池相关'''







@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                UnionMatch('#抽卡','#十连')
            ]) 
        ],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
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

    if msg_info_dict['text_split'][0] not in ['#抽卡','#十连']:
        return 
    else:
        temp = GachaClass(msg_info_dict)
        outtext = temp.GachaAction()
        if outtext == 'gacha':

            out_dir = temp.gachaPicMake(temp.gachaOperatorChoice('normal'))
            outtext2 = random.sample(text_table,1)[0]

            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),
                Plain('  '+outtext2),
                Image(path=out_dir)
            ]))


        elif outtext == '':
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('这里没有给你的东西，去打卡上班。')
            ]))

        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(outtext)
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
