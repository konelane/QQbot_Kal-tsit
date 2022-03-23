#! /usr/bin/env python3
# coding:utf-8
# 包括：查卡、查突变
import datetime
import random
import sqlite3
from os.path import basename

from core.decos import DisableModule, check_group, check_member
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import blockList
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
    name='DatabaseSearch',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.DatabaseSearch',
).register()




class CardSearch:
    def __init__(self,card_name):
        self.name = card_name
        self.filename = './bot/database/' # 初始化权限文件路径
        self.cardTextHeader = [
            'id','name','desc'
        ] # 整张表的表头
        self.cardDatasHeader = [
            'id','ot','setcode','type','atk','def','level','race','attribute','category'
        ]

        self.showHeader = [
            'name',#'atk','def','level','race', # 其他好像有问题
            'desc'
        ] # 需要字段的表头

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)

    def __searchCard(self):
        (con,cur) = self.__connectSqlite()
        cur = con.cursor()

        try:
            cur.execute("SELECT * FROM cardTexts WHERE name = ?",(self.name,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.cardTextHeader,test))

            cur.execute("SELECT * FROM cardDatas WHERE id = ?",(dict_of_text['id'],))
            test = list(cur.fetchall()[0])
            dict_of_text.update(dict(zip(self.cardDatasHeader,test)))
            print(dict_of_text)
            return dict_of_text
        except:
            print(self.name)
            return 'error'

    def cardTextReturn(self):
        msg_dict = self.__searchCard() # 拿到数据字典
        if msg_dict == 'error':
            cardText = '查无此卡'
        else:
            cardText = '\n'.join([str(x)+':'+str(msg_dict[x]) for x in self.showHeader if msg_dict[x]]) # 只返回非空值
        return cardText
        



class StarCraftPVE:
    """
    查询每周突变
    """
    def __init__(self, searchtext):
        self.name = searchtext
        self.filename = './bot/database/' # 初始化权限文件路径
        self.TableHeader = [
            '突变名称','编号','地图','因子一','因子二','因子三'
        ]
        
        ## 基准日
        self.start_number = 70
        self.date_of_base = {'year':2022,'month':2,'day':14}

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def NextTubian(self, k=0):
        """以某一周为起点，查询之后的突变"""
        (con,cur) = self.__connectSqlite()
        cur = con.cursor()
        date2 = datetime.datetime.today()
        interval = date2 -   datetime.datetime(2022,2,14) # 两日期差距
        newID = interval.days // 7 + self.start_number + 1 + k # 未来k周突变
        print(newID)
        try:
            cur.execute("SELECT * FROM starcraftpve WHERE 编号 = ?",(newID,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.TableHeader, test))
            print(dict_of_text)
            msg_dict = dict_of_text
        except:
            print(self.name)
            msg_dict = 'error'
        if msg_dict == 'error':
            cardText = '查不到该突变'
        else:
            cardText = '\n'.join([str(x)+':'+str(msg_dict[x]) for x in self.TableHeader if msg_dict[x]]) # 只返回非空值
        return cardText


    def TubianSearch(self):
        """按照突变名称查询突变"""
        (con,cur) = self.__connectSqlite()
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM starcraftpve WHERE 突变名称 = ?",(self.name,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.TableHeader, test))
            print(dict_of_text)
            msg_dict = dict_of_text
        except:
            print(self.name)
            msg_dict = 'error'

        if msg_dict == 'error':
            cardText = '查不到该突变'
        else:
            cardText = '\n'.join([str(x)+':'+str(msg_dict[x]) for x in self.TableHeader if msg_dict[x]]) # 只返回非空值
        return cardText


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#查卡')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def YGOsearch(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()    

    if msg_info_dict['text_split'][0] != '#查卡':
        return 
    else:
        textall = ' '.join([x for x in msg_info_dict['text_split'][1::]]) # 空格连接
        temp = CardSearch(textall)
        out_text = temp.cardTextReturn()
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(out_text)
        ]))





@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#sc')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def StarcraftPVE(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()    

    if msg_info_dict['text_split'][0] != '#sc':
        return 
    else:
        if len(msg_info_dict['text_split']) == 1: # 即使用#sc查本周突变的
            temp = StarCraftPVE('下周突变')
            out_text = temp.NextTubian()
        elif len(msg_info_dict['text_split'][1])>2:
            temp = StarCraftPVE(msg_info_dict['text_split'][1])
            out_text = temp.TubianSearch()
        else:
            temp = StarCraftPVE('第k周后的突变')
            out_text = temp.NextTubian(int(msg_info_dict['text_split'][1])-1)
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(out_text)
        ]))
