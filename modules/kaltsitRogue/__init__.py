#! /usr/bin/env python3
# coding:utf-8
'''
凯尔希文字探索

    需要实现的qq交互能力：
        - 开始故事
        - 移动
        - 搜证
        - 选择选项
        - 保存记录
        - 结束结算
        - 查看状态
        - 使用道具[?]
        - 信用
        - 特殊的全局选项


'''
from os.path import basename
import sys
import os
sys.path.append(os.path.dirname(__file__))

import kalrogue
from kalrogue.main import kalrogueService

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
    name='kalrogue',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.kaltsitRogue',
).register()





class kalrogueAppRequest:
    def __init__(self, msg_out) -> None:
        self.filename = './bot/database/' # 数据库位置
        self.msg_box = {
            'id':msg_out['id'],
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
            'text_split':msg_out['text_split'],
            'text_ori':msg_out['text_ori'],
            'signin_new_name': msg_out['name'],
        }
        

    def main(self):
        # 启动指令
        Service = kalrogueService(self.msg_box)
        order_text = Service.orderTrans()
        out = Service.run(order_text)
        return out


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#kr')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.rogueGroup), DisableModule.require(module_name)],
    )
)
async def Praise(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    

    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   

    if msg_info_dict['text_split'][0] not in ['#kr']:
        return 
    else:
        temp = kalrogueAppRequest(msg_info_dict)
        outtext = temp.main()
        if outtext is not None and outtext != '':
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(outtext)
            ]))
        








