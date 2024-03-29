#! /usr/bin/env python3
# coding:utf-8
"""
Author: KOneLane
Date: 2022-02-26 10:40:40
LastEditors: KOneLane
LastEditTime: 2022-03-18 10:37:16
Description:
    rebuild from github: https://github.com/Redlnn/signin-image-generator
    edit by KOneLane (AGPL-3.0)
version: V
"""
import asyncio
import os
import random
import sqlite3
import re
import time, datetime
from os.path import basename
from uuid import uuid4

from core.decos import check_group, check_member, DisableModule, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import (blockList, signinfailtext,
                                   signsuccesstext, tietie_level_one, tietie_level_two)
from core.config.BotConfig import AdminConfig, BasicConfig
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight, UnionMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

# 220310加入贴贴功能

channel = Channel.current()
module_name = basename(__file__)[:-3]
Module(
    name='Signin',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Signin',
).register()


class SigninClass:
    """签到数据库、图片操作等
    
    """

    def __init__(self, msg_out) -> None:
        self.filename = BasicConfig().databaseUrl  # 数据库位置
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
        self.msg_out = msg_out

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return con, cur

    def databaseInit(self):
        """建表"""
        con, cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `signin` (  \
                id INTEGER PRIMARY KEY NOT NULL, signin_uid TEXT, name TEXT, \
                exp INTEGER, total_days INTEGER, consecutive_days INTEGER, is_signin_consecutively INTEGER, \
                reliance INTEGER, credit INTEGER, last_signin_time TEXT \
            )")
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time ) VALUES(?,?,?,?,?,?,?,?,?,?)", (
            591016144, str(uuid4()), '凯尔希初始化', 200, 365, 10,
            1, 120, 2000, time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
        )
                    )
        con.commit()
        con.close()
        print('建表成功')

    def __dataSave(self):
        """保存当前用户数据"""
        con, cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time) VALUES(?,?,?,?,?,?,?,?,?,?)", (
            self.signin_box['id'], self.signin_box['signin_uid'], self.signin_box['name'], self.signin_box['exp'], \
            self.signin_box['total_days'], self.signin_box['consecutive_days'],
            self.signin_box['is_signin_consecutively'], \
            self.signin_box['reliance'], self.signin_box['credit'], time.strftime("%Y/%m/%d-%H:%M:%S")
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

    def __signin(self):
        """签到检测+数据增改
        """
        # self.signin_box['already_signin'] = 1
        # 检查签到时间差
        print(self.signin_box['last_signin_time'])
        timeNow = time.strptime(
            (
                    datetime.datetime.strptime(self.signin_box['last_signin_time'], "%Y/%m/%d-%H:%M:%S") -
                    datetime.timedelta(hours=4)
            ).strftime("%Y/%m/%d-%H:%M:%S"),
            "%Y/%m/%d-%H:%M:%S"
        )

        # timeNow = time.strptime(self.signin_box['last_signin_time'], "%Y/%m/%d-%H:%M:%S") 
        point_time = time.strptime(str(timeNow.tm_year) + '-' + str(timeNow.tm_mon) + '-' + str(timeNow.tm_mday),
                                   "%Y-%m-%d")  # 签到的当天00:00:00
        ans = time.time() - time.mktime(point_time)
        print('距离上一次签到时间为:', ans, '秒')
        if (ans > 86400 + 3600 * 4) and (ans < 86400 * 2 + 3600 * 4):  # 凌晨4点刷新
            self.signin_box['consecutive_days'] += 1
            self.signin_box['is_signin_consecutively'] = 1
        elif ans > 86400 * 2 + 3600 * 4:
            self.signin_box['consecutive_days'] = 1
            self.signin_box['is_signin_consecutively'] = 0
        else:
            print('今日已签过到')
            return False

        # 签到后的奖励 
        self.signin_box['exp'] += 1  # 经验
        self.signin_box['reliance'] += 1  # 信赖
        self.signin_box['credit'] += 20  # 信用
        self.signin_box['total_days'] += 1  # 总天数
        return True

    def update_signin_box(self):
        """更新签到数据 - 用于作弊前查询信用"""
        dict_of_text = self.__searchSigninData()
        if dict_of_text is not None:
            """根据查询得到的字典更新数据"""
            self.signin_box.update(dict_of_text)
            return 'done'
        else:
            return ''

    def tietieAction(self):
        """贴贴功能入口"""
        if self.signin_box['text_ori'] in ["#贴贴", '凯尔希贴贴', '老女人贴贴']:
            # 1.查询好感度
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return ''

            # 2.向DarkTemple返回指令
            if 10 <= self.signin_box['reliance'] < 50:
                return 'tietielevel1'
            elif self.signin_box['reliance'] >= 50:
                return 'tietielevel2'
            else:
                return 'reliance_not_enough'

    def signinAction(self):
        """签到功能入口"""
        if self.signin_box['text_ori'] in ["#签到", '#打卡']:
            # 先从数据库中查询签到总天数、连续签到天数、上次签到时间、签到经验值
            dict_of_text = self.__searchSigninData()
            print('查到的记录为：', dict_of_text)
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
                if self.signin_box['name'] != self.signin_box['signin_new_name']:
                    # 假如签到昵称有变化
                    self.signin_box['name'] = self.signin_box['signin_new_name']
            else:
                """第一次进行签到"""
                dict_of_text = {
                    'exp': 0,
                    'total_days': 0,
                    'consecutive_days': 0,
                    'is_signin_consecutively': 0,
                    'reliance': 0,
                    'credit': 0,
                    'last_signin_time': "2021/05/12-00:00:00",
                    # 'already_signin':0,
                }
                self.signin_box.update(dict_of_text)
            # if self.signin_box['already_signin'] != 0:
            #     return ''

            if self.__signin():
                self.__dataSave()
                # 生成签到图
                if self.signin_box['exp'] >= 200: self.signin_box['exp'] = 200

                image_generator_path = os.path.dirname(__file__) + '/signinImageGenerator/main.py'
                if os.path.exists(os.path.dirname(__file__) + '/signinImageGenerator/save_test.png'):
                    os.remove(os.path.dirname(__file__) + '/signinImageGenerator/save_test.png')  # 已存在，则删除
                    asyncio.sleep(1)

                self.signin_box['name'] = self.signin_box['name'].replace(' ', '·')  # 昵称中空格删除
                print('运行路径为：', image_generator_path)
                order = f"python {image_generator_path} \
                    --id={self.signin_box['id']} \
                    --signin_uid={self.signin_box['signin_uid']} \
                    --name={self.signin_box['name']} \
                    --exp={self.signin_box['exp']} \
                    --total_days={self.signin_box['total_days']} \
                    --consecutive_days={self.signin_box['consecutive_days']} \
                    --is_signin_consecutively={self.signin_box['is_signin_consecutively']} \
                    --reliance={self.signin_box['reliance']} \
                    --credit={self.signin_box['credit']} \
                    --last_signin_time={self.signin_box['last_signin_time']}"
                # print(order)
                os.popen(order).readlines()

                return 'text'
            else:
                return ''

    ## ################### ##
    ## -----GM 后台签到----- ##
    ## ################### ##

    def __signinCheat(self, order_input):
        """
        签到检测+数据增改 - 后台版
        """
        # self.signin_box['already_signin'] = 1
        # 检查签到时间差
        # if self.signin_box['id'] != AdminConfig().masterId:
        #     """仅本人可用"""
        #     return False
        print(self.signin_box['last_signin_time'])
        timeNow = time.strptime(
            (
                    datetime.datetime.strptime(self.signin_box['last_signin_time'], "%Y/%m/%d-%H:%M:%S") -
                    datetime.timedelta(hours=4)
            ).strftime("%Y/%m/%d-%H:%M:%S"),
            "%Y/%m/%d-%H:%M:%S"
        )

        # timeNow = time.strptime(self.signin_box['last_signin_time'], "%Y/%m/%d-%H:%M:%S") 
        point_time = time.strptime(str(timeNow.tm_year) + '-' + str(timeNow.tm_mon) + '-' + str(timeNow.tm_mday),
                                   "%Y-%m-%d")  # 签到的当天00:00:00
        ans = time.time() - time.mktime(point_time)
        print('距离上一次签到时间为:', ans, '秒')
        # 忽略时间限制 重打卡
        if order_input in ['resign', 'setluck', 'setopt']:
            ans = 86400 + 3600 * 8  # 默认早上八点打卡
        else:
            # 签到后的奖励
            self.signin_box['exp'] += 1  # 经验
            self.signin_box['reliance'] += 1  # 信赖
            self.signin_box['credit'] += 20  # 信用
            self.signin_box['total_days'] += 1  # 总天数

        if (ans > 86400 + 3600 * 4) and (ans < 86400 * 2 + 3600 * 4):  # 凌晨4点刷新
            print('[TEST]测试 连续签到时间：', self.signin_box['consecutive_days'])
            # self.signin_box['consecutive_days'] += 1
            self.signin_box['is_signin_consecutively'] = 1
        elif ans > 86400 * 2 + 3600 * 4:
            self.signin_box['consecutive_days'] = 1
            self.signin_box['is_signin_consecutively'] = 0
        else:

            print('今日已签过到')
            return False

        return True

    def signinCheat(self):
        """打卡gm指令"""
        if self.msg_out['text_split'][0] in ["#c签到", "#c打卡"] and len(self.msg_out['text_split']) > 1:
            # 先从数据库中查询签到总天数、连续签到天数、上次签到时间、签到经验值
            dict_of_text = self.__searchSigninData()
            print('查到的记录为：', dict_of_text)
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
                if self.signin_box['name'] != self.signin_box['signin_new_name']:
                    # 假如签到昵称有变化
                    self.signin_box['name'] = self.signin_box['signin_new_name']
            else:
                """第一次进行签到"""
                dict_of_text = {
                    'exp': 0,
                    'total_days': 0,
                    'consecutive_days': 0,
                    'is_signin_consecutively': 0,
                    'reliance': 0,
                    'credit': 0,
                    'last_signin_time': "2021/05/12-00:00:00",
                    # 'already_signin':0,
                }
                self.signin_box.update(dict_of_text)
            # if self.signin_box['already_signin'] != 0:
            #     return ''

            if self.__signinCheat(self.msg_out['text_split'][1]):
                self.__dataSave()
                # 生成签到图
                if self.signin_box['exp'] >= 200: self.signin_box['exp'] = 200

                image_generator_path = os.path.dirname(__file__) + '/signinImageGenerator/main.py'
                if os.path.exists(os.path.dirname(__file__) + '/signinImageGenerator/save_test.png'):
                    os.remove(os.path.dirname(__file__) + '/signinImageGenerator/save_test.png')  # 已存在，则删除
                    asyncio.sleep(1)

                self.signin_box['name'] = self.signin_box['name'].replace(' ', '·')  # 昵称中空格删除
                print('运行路径为：', image_generator_path)
                order = f"python {image_generator_path} \
                    --id={self.signin_box['id']} \
                    --signin_uid={self.signin_box['signin_uid']} \
                    --name={self.signin_box['name']} \
                    --exp={self.signin_box['exp']} \
                    --total_days={self.signin_box['total_days']} \
                    --consecutive_days={self.signin_box['consecutive_days']} \
                    --is_signin_consecutively={self.signin_box['is_signin_consecutively']} \
                    --reliance={self.signin_box['reliance']} \
                    --credit={self.signin_box['credit']} \
                    --last_signin_time={self.signin_box['last_signin_time']} \
                    --cheat_code={self.msg_out['text_split'][1]} \
                    --cheat_msg={self.msg_out['text_split'][2]}"
                # print(order)
                os.popen(order).readlines()

                return 'text'
            else:
                return ''

    def testtesttest(self):
        """测试打卡用，删除自己的记录"""
        con, cur = self.__connectSqlite()
        cur.execute(f"DROP TABLE `signin`")
        con.commit()
        con.close()
        self.__searchSigninData()
        self.databaseInit()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                UnionMatch('#签到', '#打卡')
            ])
        ],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Signin(
        app: Ariadne,
        group: Group,
        message: MessageChain,
        member: Member
):
    """【FUNCTION】打卡签到"""
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()

    temp = SigninClass(msg_info_dict)
    outtext = temp.signinAction()

    if (outtext is not None) and (outtext != ''):
        '''【STATUS】打卡成功'''
        pic_dir = os.path.dirname(__file__) + '/signinImageGenerator/save_test.png'
        outtext = random.sample(signsuccesstext, 1)[0]

        await app.send_group_message(group, MessageChain([
            Plain(outtext),
            Image(path=pic_dir)
        ]))

    elif outtext == '':
        '''【STATUS】打卡失败'''
        await app.send_group_message(group, MessageChain([
            Plain(random.sample(signinfailtext, 1)[0]),
        ]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([UnionMatch('#贴贴', '凯尔希贴贴')]),
        ],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def SigninTietie(
        app: Ariadne,
        group: Group,
        message: MessageChain,
        member: Member
):
    """【FUNCTION】贴贴功能"""
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()
    temp = SigninClass(msg_info_dict)

    outtext = temp.tietieAction()
    if outtext == 'tietielevel1':
        '''【STATUS】贴贴lv1成功'''
        await app.send_group_message(group, MessageChain([
            Plain(random.sample(tietie_level_one, 1)[0]),
        ]))
    elif outtext == 'tietielevel2':
        await app.send_group_message(group, MessageChain([
            Plain(random.sample(tietie_level_two, 1)[0]),
        ]))
    elif outtext == 'reliance_not_enough':
        '''【STATUS】贴贴失败'''
        await app.send_group_message(group, MessageChain([
            Image(path=BasicConfig().databaseUrl + 'faces/power.jpg')
        ]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\#c打卡.*').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def signin_cheat(
        app: Ariadne,
        message: MessageChain,
        group: Group,
        member: Member
):
    """打卡作弊功能
    1. 指定概率 TODO
    2. 重新出图 TODO
    """

    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()
    text_list = msg_info_dict['text_split']
    temp = SigninClass(msg_info_dict)

    if member.id not in [AdminConfig().masterId]:
        # 超级用户list
        cheat_order = temp.update_signin_box()
        if cheat_order == 'done' and temp.signin_box['reliance'] < 200:
            # 查不到数据 或 信赖不足200无法使用该功能
            await app.send_group_message(group, MessageChain([
                Plain('无权限。'),
            ]))
            return
    if len(text_list) <= 2:
        '''【STATUS】cheat打卡失败'''
        await app.send_group_message(group, MessageChain([
            Plain('请输入#c打卡 参数(setluck/setopt) 参数内容'),
        ]))

    outtext = temp.signinCheat()

    if (outtext is not None) and (outtext != ''):
        '''【STATUS】打卡成功'''
        pic_dir = os.path.dirname(__file__) + '/signinImageGenerator/save_test.png'
        outtext = random.sample(signsuccesstext, 1)[0]

        await app.send_group_message(group, MessageChain([
            Plain(outtext),
            Image(path=pic_dir)
        ]))

    elif outtext == '':
        '''【STATUS】打卡失败'''
        await app.send_group_message(group, MessageChain([
            Plain(random.sample(signinfailtext, 1)[0]),
        ]))
