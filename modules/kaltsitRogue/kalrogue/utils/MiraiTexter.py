#! /usr/bin/env python3
# coding:utf-8
'''用mirai发送消息'''
from os.path import basename
import sys
import os

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
    usage='modules.MiraiTexter',
).register()




@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        # inline_dispatchers=[Twilight([RegexMatch(r'#kr')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), 
        check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def textOut(
    app: Ariadne, 
    group: Group, 
    outtext
):

    if outtext != '':
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(outtext)
        ]))