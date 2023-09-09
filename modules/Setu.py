#! /usr/bin/env python3
# coding:utf-8
import requests
import random
import sqlite3
from os.path import basename
from uuid import uuid4
import time
import re

from core.config.BotConfig import BasicConfig
from core.decos import DisableModule, check_group, check_member, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import blockList, text_table
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
    name='Setu',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Setu',
).register()


# 加一个setu扣信用功能
class SigninClass:
    """签到数据库、图片操作等
    
    """

    def __init__(self, msg_out) -> None:
        self.filename = BasicConfig().databaseUrl # 数据库位置
        self.signin_box = {
            'id': msg_out['id'],
            'signin_uid': str(uuid4()),
            'name': msg_out['name'],
            'exp': 0,
            'total_days': 0,
            'consecutive_days': 0,
            'is_signin_consecutively': 0,
            'reliance': 0,
            'credit': 0,
            'last_signin_time': "2021/05/12-12:00:00",
            # 'already_signin':0,

            'group_id': msg_out['group_id'],
            'text_ori': msg_out['text_ori'],
            'signin_new_name': msg_out['name'],
        }
        self.TableHeader = [
            'id', 'signin_uid', 'name', 'exp', 'total_days', 'consecutive_days',
            'is_signin_consecutively', 'reliance', 'credit', 'last_signin_time',  # 'already_signin'
        ]

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con, cur)

    def __dataSave(self):
        """保存当前用户数据 - se图功能魔改版"""
        con, cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time) VALUES(?,?,?,?,?,?,?,?,?,?)", (
            self.signin_box['id'], self.signin_box['signin_uid'], self.signin_box['name'], self.signin_box['exp'], \
            self.signin_box['total_days'], self.signin_box['consecutive_days'],
            self.signin_box['is_signin_consecutively'], \
            self.signin_box['reliance'], self.signin_box['credit'], self.signin_box['last_signin_time']
        )
                    )
        con.commit()
        con.close()
        pass

    def __searchSigninData(self):
        dict_of_text = None
        con, cur = self.__connectSqlite()
        try:
            cur.execute("SELECT * FROM `signin` WHERE id = ? ", (self.signin_box['id'],))
            test = list(cur.fetchall()[0])

            dict_of_text = dict(zip(self.TableHeader, test))
        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text

    def setuAction(self):
        """setu功能入口"""
        if self.signin_box['text_ori'] in ["#draw"]:
            # 1.查询信用值
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return ''

            # 2.向DarkTemple返回指令
            if self.signin_box['credit'] >= 5:
                self.signin_box['credit'] -= 5
                self.__dataSave()
                return 'picture'
            else:
                return '博士，信用不足，无法看图。'

    def kalStep(self):
        '''指令 #踩我'''
        if self.signin_box['text_ori'] in ["#踩我"]:
            # 1.查询信用值
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return ''

            # 2.向DarkTemple返回指令
            if self.signin_box['reliance'] >= 50:

                return 'step'
            else:
                return 'kill'


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#draw')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Setu_time(
        app: Ariadne,
        group: Group,
        message: MessageChain,
        member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()

    if msg_info_dict['text_split'][0] not in ['#draw']:
        return
    else:
        temp = SigninClass(msg_info_dict)
        outtext = temp.setuAction()
        if outtext == 'picture':
            link = requests.get(url='https://iw233.cn/api/Random.php').url
            await app.send_group_message(group, MessageChain([
                Plain(random.sample(text_table, 1)[0]),
                Image(url=link)
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
        inline_dispatchers=[Twilight([RegexMatch(r'\#踩我').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Step_me(
        app: Ariadne,
        group: Group,
        message: MessageChain,
        member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()

    if msg_info_dict['text_split'][0] not in ['#踩我']:
        return
    else:
        temp = SigninClass(msg_info_dict)
        outtext = temp.kalStep()
        if outtext == 'step':
            pic_num = random.randint(0, 2)
            if pic_num == 0:
                # cai
                await app.send_group_message(group, MessageChain([
                    Image(path=BasicConfig().databaseUrl + 'kalpics/cai.jpg')
                ]))
            elif pic_num == 1:
                # ding
                await app.send_group_message(group, MessageChain([
                    Image(path=BasicConfig().databaseUrl + 'kalpics/ding.jpg')
                ]))
            elif pic_num == 2:
                # ding
                await app.send_group_message(group, MessageChain([
                    Image(path=BasicConfig().databaseUrl + 'kalpics/cai2.jpg')
                ]))
        elif outtext == 'kill':
            await app.send_group_message(group, MessageChain([
                Image(path=BasicConfig().databaseUrl + 'kalpics/kill.jpg')
            ]))

        elif outtext == '':
            await app.send_group_message(group, MessageChain([
                Plain('这里没有给你的东西，去打卡上班。')
            ]))

        else:
            await app.send_group_message(group, MessageChain([
                Plain(outtext)
            ]))
